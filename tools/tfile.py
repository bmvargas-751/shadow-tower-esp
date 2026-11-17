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


# Suma de verificación de cada entrada (ST.EXE, rutina en 0x80015B80): 0x12345678 más la suma de todas las
# palabras de 32 bits de la entrada salvo la última, que guarda el resultado. Si no coincide, el juego se cae.
def checksum(blob):
    w = struct.unpack_from(f'<{len(blob) // 4}I', blob)
    return (0x12345678 + sum(w[:-1])) & 0xFFFFFFFF


def fix_checksums(data, orig):
    """Recalcula la suma de las entradas de `data` (bytearray de un .T) que difieren de `orig`. Devuelve cuántas."""
    n = 0
    for (i, a, cnt, blob), (_, _, _, old) in zip(entries(bytes(data)), entries(orig)):
        if cnt <= 0 or blob == old:
            continue
        struct.pack_into('<I', data, (a + cnt) * 2048 - 4, checksum(blob))
        n += 1
    return n
