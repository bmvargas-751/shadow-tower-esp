#!/usr/bin/env python3
"""Lector de imágenes TIM de PS1 (4, 8 y 16 bits)."""
import struct

def parse(b, off=0):
    """Devuelve dict con bpp, clut, x, y, w (en píxeles), h, pixels (bytes) y size total; None si no es TIM."""
    if len(b) < off + 8 or struct.unpack_from('<I', b, off)[0] != 0x10:
        return None
    flag = struct.unpack_from('<I', b, off + 4)[0]
    mode = flag & 7
    if mode > 3 or flag & ~0xF:
        return None
    p = off + 8
    clut = None
    if flag & 8:
        ln, cx, cy, cw, ch = struct.unpack_from('<I4H', b, p)
        clut = dict(x=cx, y=cy, w=cw, h=ch,
                    colors=struct.unpack_from(f'<{cw*ch}H', b, p + 12))
        p += ln
    ln, x, y, w, h = struct.unpack_from('<I4H', b, p)
    bpp = {0: 4, 1: 8, 2: 16, 3: 24}[mode]
    pw = w * 16 // bpp
    return dict(bpp=bpp, clut=clut, x=x, y=y, w=pw, h=h,
                pix_off=p + 12, pixels=b[p + 12:p + ln], size=p + ln - off)

def to_image(t, clut_row=0):
    from PIL import Image
    w, h, pix = t['w'], t['h'], t['pixels']
    if t['bpp'] == 4:
        idx = [v for byte in pix for v in (byte & 15, byte >> 4)]
    elif t['bpp'] == 8:
        idx = list(pix)
    else:
        raise ValueError('solo 4/8 bits')
    cols = t['clut']['colors'][clut_row * t['clut']['w']:] if t['clut'] else None
    def rgb(c):
        return ((c & 31) * 8, ((c >> 5) & 31) * 8, ((c >> 10) & 31) * 8)
    pal = [rgb(c) for c in cols] if cols else [(i * 17,) * 3 for i in range(256)]
    img = Image.new('RGB', (w, h))
    img.putdata([pal[i] if i < len(pal) else (255, 0, 255) for i in idx[:w * h]])
    return img
