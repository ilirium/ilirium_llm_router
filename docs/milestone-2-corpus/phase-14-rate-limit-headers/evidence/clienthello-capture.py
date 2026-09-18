"""Capture and parse one TLS ClientHello. It is plaintext and arrives before cert validation,
so a listener with no certificate at all still sees it -- the client then fails, which is fine."""
import socket, sys, hashlib

GREASE = {0x0a0a,0x1a1a,0x2a2a,0x3a3a,0x4a4a,0x5a5a,0x6a6a,0x7a7a,
          0x8a8a,0x9a9a,0xaaaa,0xbaba,0xcaca,0xdada,0xeaea,0xfafa}

def u16(b, i): return (b[i] << 8) | b[i+1]

def parse(data):
    assert data[0] == 0x16, "not a TLS handshake record"
    i = 5                      # skip record header
    assert data[i] == 0x01, "not a ClientHello"
    ver = u16(data, i+4)
    i += 4 + 2 + 32            # type+len, version, random
    i += 1 + data[i]           # session id
    n = u16(data, i); i += 2
    ciphers = [u16(data, i+k) for k in range(0, n, 2)]; i += n
    i += 1 + data[i]           # compression methods
    exts, curves, fmts = [], [], []
    if i < len(data):
        total = u16(data, i); i += 2
        end = i + total
        while i < end:
            et, el = u16(data, i), u16(data, i+2); i += 4
            exts.append(et)
            if et == 0x000a:   # supported_groups
                gl = u16(data, i)
                curves = [u16(data, i+2+k) for k in range(0, gl, 2)]
            if et == 0x000b:   # ec_point_formats
                fmts = list(data[i+1:i+1+data[i]])
            i += el
    keep = lambda xs: [x for x in xs if x not in GREASE]
    return ver, keep(ciphers), keep(exts), keep(curves), fmts

def ja3(ver, ciphers, exts, curves, fmts):
    s = ",".join(["-".join(map(str, x)) for x in
                  ([ver], ciphers, exts, curves, fmts)])
    return s, hashlib.md5(s.encode()).hexdigest()

srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", int(sys.argv[1]))); srv.listen(1); srv.settimeout(60)
print(f"listening on {sys.argv[1]}", flush=True)
conn, _ = srv.accept()
data = conn.recv(8192)
conn.close(); srv.close()
ver, ciphers, exts, curves, fmts = parse(data)
_, h = ja3(ver, ciphers, exts, curves, fmts)
print(f"LABEL={sys.argv[2]}")
print(f"  ja3_hash   : {h}")
print(f"  ciphers    : {len(ciphers)} -> {ciphers}")
print(f"  extensions : {len(exts)} -> {exts}")
print(f"  curves     : {curves}")
