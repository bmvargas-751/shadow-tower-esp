#!/usr/bin/env python3
"""Lee un save state de DuckStation (versión 94, datos en zstd) y extrae la VRAM.

Uso: dsstate.py ESTADO.sav SALIDA_VRAM.bin
La VRAM se ubica buscando los píxeles de un TIM conocido del juego (ver find_vram)."""
import ctypes, struct, sys

def decompress(fn):
    d = open(fn, 'rb').read()
    assert d[:4] == b'DUCC', 'no es un estado de DuckStation'
    f = struct.unpack_from('<12I', d, 0xa8)
    comp, csize, usize, off = f[8], f[9], f[10], f[11]
    data = d[off:off + csize]
    if comp == 0:
        return data
    assert comp == 2, f'compresión {comp} no soportada'
    z = ctypes.CDLL('libzstd.so.1')
    z.ZSTD_decompress.restype = ctypes.c_size_t
    z.ZSTD_isError.restype = ctypes.c_uint
    out = ctypes.create_string_buffer(usize)
    n = z.ZSTD_decompress(out, ctypes.c_size_t(usize), data, ctypes.c_size_t(len(data)))
    assert not z.ZSTD_isError(n), 'error de zstd'
    return out.raw[:n]

def find_vram(state, tim_pixels, x, y, w16):
    """tim_pixels: bytes de una fila o más de un TIM; x,y: su posición en VRAM (en unidades de 16 bits)."""
    row = tim_pixels[:w16 * 2]
    i = state.find(row)
    while i >= 0:
        base = i - (y * 1024 + x) * 2
        if base >= 0 and base + 1024 * 512 * 2 <= len(state):
            return base
        i = state.find(row, i + 1)
    return None

if __name__ == '__main__':
    s = decompress(sys.argv[1])
    print(len(s))
