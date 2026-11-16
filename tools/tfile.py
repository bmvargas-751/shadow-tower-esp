#!/usr/bin/env python3
"""Contenedor .T de Shadow Tower: u16 n, luego n+1 u16 = sector de inicio
de cada entrada (sectores de 2048 bytes). Entrada i = [s[i], s[i+1])."""
import struct, sys

def entries(data):
    n = struct.unpack_from('<H', data, 0)[0]
    s = struct.unpack_from(f'<{n+1}H', data, 2)
    out = []
    for i in range(n):
        a, b = s[i], s[i+1]
        out.append((i, a, b - a, data[a*2048:b*2048]))
    return out

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    for i, a, n, blob in entries(d):
        if n:
            print(f'{i:4d} sec={a:5d} n={n:3d} {blob[:24].hex(" ")}')
