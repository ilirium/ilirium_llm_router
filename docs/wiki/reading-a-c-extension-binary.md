# Reading a C extension whose wheel ships no sources

**Read this when you need to know what a compiled Python extension actually does** — does it release
the GIL, does it call the library function you think it calls, is that flag really passed — **and the
installed package contains only a `.so`.** Most binary wheels do. Guessing from the documentation is
how a design ends up resting on a claim nobody checked.

**Everything below was run on this machine, 2026-08-19**, against
`zstandard 0.25.0`'s `backend_c.cpython-313-darwin.so`, macOS 25.6, arm64, Python 3.13. Output is
verbatim.

---

## Why the binary is better evidence than the source tree

A source tree tells you what **would** be compiled. The installed binary is what **will run**. They
differ whenever the build had options, a different upstream version was vendored, or the wheel was
produced from a branch you are not reading.

**It is also usually the only option.** A wheel is a build artefact; C sources are not required to be
in it, and frequently are not.

**Cheaper things to try first**, in order — this technique is the fallback, not the opening move:

1. The project's **sdist** or repository, if the version matches exactly.
2. `pip download --no-binary :all: <pkg>`, which forces the source distribution.
3. A **pure-Python fallback backend**, if the package has one — *but see the trap below.*

**The trap:** a package with both a C and a CFFI backend puts readable Python in front of you, and it
is describing **the backend you are not running**. Check which one loads before believing anything it
says.

## Step 0 — which object actually loads

Selection logic is in the package's `__init__.py`, and is often overridable by an environment
variable. Establish this first, or every later step answers about the wrong file.

```
file …/zstandard/backend_c.cpython-313-darwin.so
→ Mach-O 64-bit bundle arm64
```

## Step 1 — what does it import? The cheapest useful cut

**Undefined symbols are the functions the extension gets from outside**, which for a Python extension
means the CPython C API. This alone answers many questions, because **a function that is never
imported can never be called.**

```
nm -u backend_c.cpython-313-darwin.so | grep PyEval
→ _PyEval_RestoreThread
  _PyEval_SaveThread
```

**That two-line output is already most of the GIL answer.** `Py_BEGIN_ALLOW_THREADS` and
`Py_END_ALLOW_THREADS` are macros that expand to exactly these two calls, and macros do not survive
compilation — **the symbols do.** If neither appeared, the extension could not release the GIL
anywhere, and you would be finished in one command.

**The absence of a symbol is strong evidence; its presence is weak** — it says the capability exists
somewhere in the file, not that the path you care about uses it. That is what the next step is for.

## Step 2 — disassemble the function you care about

```
otool -tV backend_c.cpython-313-darwin.so
```

`-t` is the text section, **`-V` symbolises it**, and that flag is the whole trick:

```
000000000008c690   bl  0x90774 ; symbol stub for: _PyEval_SaveThread
000000000008c694   mov x21, x0
000000000008c698   ldr x0, [x20, #0x20]
000000000008c69c   add x1, sp, #0x28
000000000008c6a0   add x2, sp, #0x10
000000000008c6a4   mov w3, #0x2
000000000008c6a8   bl  _ZSTD_compressStream2
000000000008c6ac   mov x20, x0
000000000008c6b0   mov x0, x21
000000000008c6b4   bl  0x90768 ; symbol stub for: _PyEval_RestoreThread
```

**That is the macro pair, wrapped around the real work, read off the shipped file.** No source needed.

**`otool -tV` resolves the stub targets for you.** This is worth stating loudly because it is easy to
do a great deal of unnecessary work here: this repository's first pass at the same question computed
stub indices by hand from the `__stubs` section address and entry size, and cross-referenced them
against the indirect symbol table. **That arithmetic was never required** — the annotation was in the
output all along. Use it, and keep Step 3 as a cross-check.

### Two call shapes, and the difference is informative

- **`bl 0x…` with a `symbol stub for:` comment** — a call *out* of the binary, resolved by the dynamic
  linker. All CPython API calls look like this.
- **`bl _SomeName` with no stub** — a direct call to something **inside** this binary.

`_ZSTD_compressStream2` above is the second kind, which tells you **libzstd is statically linked into
the extension** rather than loaded from a system library. That is a fact about deployment you did not
have to go looking for.

## Step 3 — the cross-check, and the fallback when `-V` fails

`otool -Iv` prints the indirect symbol tables **with the stub address beside each name**:

```
Indirect symbols for (__TEXT,__stubs) 92 entries
address            index name
0x0000000000090768  4119 _PyEval_RestoreThread
0x0000000000090774  4120 _PyEval_SaveThread
```

Match the `bl` target address against the left column. **Note there are several such tables** — here
`__stubs` (92), `__DATA_CONST,__got` (16), `__DATA,__la_symbol_ptr` (92) — and the same symbol appears
in more than one, so match on the section your call actually targets rather than on the name alone.

## Step 4 — check the whole file, not the one function you looked at

One function is an anecdote. Sweeping every function turns it into a property — and for
acquire/release pairs there is a second question worth more than the first: **are they balanced?** An
unbalanced pair leaks thread state, which is a bug of a completely different severity from merely
failing to parallelise.

```
otool -tV lib.so | awk '
  /^_[A-Za-z_]+:$/          {fn=$0}
  /_PyEval_SaveThread/      {s[fn]++}
  /_PyEval_RestoreThread/   {r[fn]++}
  END { for (f in s) { n++; if (s[f]!=r[f]) { bad++; print "UNBALANCED", f, s[f], r[f] } }
        print n " functions release the GIL; " bad " unbalanced" }'

→ 21 functions release the GIL; 0 unbalanced
```

**Twenty lines of `awk` against a stripped binary, and it answers a question the documentation does
not address at all.**

## On Linux, ELF instead of Mach-O

Same shape, different tools. **Not run on this machine and therefore not verified here:**

| Task | macOS | Linux |
|---|---|---|
| File type | `file` | `file` |
| Imported symbols | `nm -u` | `nm -D --undefined-only` |
| Shared libraries needed | `otool -L` | `ldd`, `readelf -d` |
| Symbolised disassembly | `otool -tV` | `objdump -d` |
| The indirection table | `otool -Iv` (stubs) | `readelf -r` (PLT/GOT relocations) |

`objdump -d` annotates PLT calls with the symbol name in much the same way, so the method transfers
almost unchanged.

## What this establishes, and what it does not

**Establishes:** the code path exists in the file that will run, on this architecture, at this
version. For a question like *does it release the GIL around the library call*, that is a complete
answer.

**Does not establish:**

- **That the path is taken.** You read one function; a wrapper may not call it. Confirm which entry
  point your code reaches.
- **Anything about another platform or version.** Symbol layout, inlining and even which functions
  exist change between builds. **Re-derive after an upgrade** rather than carrying the finding forward.
- **Performance.** A released GIL is not a free core. *Released* and *scales* are separate claims
  needing separate evidence, and conflating them is the more common error of the two.

**And it can be defeated.** Aggressive inlining can fold a small wrapper into its caller, link-time
optimisation can reorder things past recognition, and a fully stripped binary loses the local symbol
names that make Step 4's sweep possible — the *imported* ones survive, since the dynamic linker needs
them, which is why Step 1 is the most robust step here.

## Reading list

- `nm(1)`, `otool(1)`, `objdump(1)` — `man nm`, and Apple's developer documentation
- Mach-O file format, including `__stubs` and the indirect symbol table — <https://github.com/aidansteele/osx-abi-macho-file-format-reference>
- Extending Python with C, where `Py_BEGIN_ALLOW_THREADS` is introduced — <https://docs.python.org/3/extending/extending.html>
- Thread State and the GIL, the C API reference for the macro pair — <https://docs.python.org/3/c-api/threads.html>
- Python binary wheels, and what a wheel is required to contain — <https://packaging.python.org/en/latest/specifications/binary-distribution-format/>
- Arm 64-bit instruction set, for reading the disassembly — <https://developer.arm.com/documentation/ddi0487/latest/>

*All six were checked from this machine on 2026-08-19 and returned 200.*

## Where these claims came from

**Every command above was run on this machine on 2026-08-19** and the output is verbatim. The
worked example is the finding recorded in
`../milestone-2-corpus/phase-10-body-store/notes.md`, Task 4, and the conclusion it supports is
summarised in `zstandard-and-libzstd.md`.

**What expires:** the addresses, the symbol names, the 21, and the tool flags. **What does not:** that
`nm -u` answers capability questions in one command, that `otool -tV` resolves stubs so you never need
the index arithmetic, and that a balance check over the whole file is worth more than a careful read
of one function.
