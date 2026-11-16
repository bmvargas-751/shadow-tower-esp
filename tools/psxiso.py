#!/usr/bin/env python3
"""Lector ISO9660 para imágenes de PS1 en MODE2/2352 (una pista).

Uso:
  psxiso.py list IMAGEN.bin
  psxiso.py extract IMAGEN.bin CARPETA_SALIDA

Solo lee: no modifica la imagen. Los archivos XA/STR (Form 2) se extraen
con los 2048 bytes de datos de cada sector, igual que los demás; sirven
para inventario, no para reconstruir audio o video.
"""
import os
import struct
import sys

SECTOR = 2352
DATA_OFF = 24  # sync(12) + header(4) + subheader(8)


def read_sector(f, lba):
    f.seek(lba * SECTOR + DATA_OFF)
    return f.read(2048)


def read_extent(f, lba, size):
    out = bytearray()
    n = (size + 2047) // 2048
    for i in range(n):
        out += read_sector(f, lba + i)
    return bytes(out[:size])


def parse_dir(f, lba, size, path=""):
    data = read_extent(f, lba, size)
    i = 0
    while i < len(data):
        ln = data[i]
        if ln == 0:
            i = (i // 2048 + 1) * 2048  # salto al siguiente sector
            continue
        rec = data[i:i + ln]
        ext = struct.unpack_from("<I", rec, 2)[0]
        sz = struct.unpack_from("<I", rec, 10)[0]
        flags = rec[25]
        nlen = rec[32]
        name = rec[33:33 + nlen]
        i += ln
        if name in (b"\x00", b"\x01"):
            continue
        name = name.decode("ascii").split(";")[0]
        full = f"{path}/{name}" if path else name
        if flags & 2:
            yield from parse_dir(f, ext, sz, full)
        else:
            yield full, ext, sz


def walk(f):
    pvd = read_sector(f, 16)
    assert pvd[1:6] == b"CD001", "no es ISO9660"
    root = pvd[156:156 + 34]
    ext = struct.unpack_from("<I", root, 2)[0]
    sz = struct.unpack_from("<I", root, 10)[0]
    return list(parse_dir(f, ext, sz))


def main():
    cmd, img = sys.argv[1], sys.argv[2]
    with open(img, "rb") as f:
        files = walk(f)
        if cmd == "list":
            for p, lba, sz in files:
                print(f"{lba:8d} {sz:10d} {p}")
        elif cmd == "extract":
            out = sys.argv[3]
            for p, lba, sz in files:
                dst = os.path.join(out, p)
                os.makedirs(os.path.dirname(dst) or out, exist_ok=True)
                with open(dst, "wb") as o:
                    o.write(read_extent(f, lba, sz))
            print(f"{len(files)} archivos extraídos en {out}")


if __name__ == "__main__":
    main()
