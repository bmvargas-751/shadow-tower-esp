#!/usr/bin/env python3
"""Imagen de prueba combinada para DuckStation (no toca translation/).

Uso (desde la raíz del proyecto):
  st_testbuild.py   → ../shadow-tower-esp-local/test/shadow-tower-prueba-2.{bin,cue}

Qué prueba:
  1. Letras nuevas en la fuente del texto codificado (STAT.T entrada 0): Á en el código 168 y É en el 300;
     «STATUS» → «STÁTUS» y «MAGIC LEFT» → «MAGIC LÉFT».
  2. Más espacio para los nombres de objetos (STAT.T entrada 3): la lámina de la fuente se achica de 256 a 64
     filas y su bloque se mueve de 0x4600 a 0xA600 (la cabecera apunta ahí); un relleno de 4 KB en la casilla
     vacía 171 empuja los nombres de los objetos 171 en adelante más allá del límite viejo.
       - todos los nombres bien → el juego respeta el puntero y lee todo el bloque: hay lugar de sobra
       - todos con basura → no respeta el puntero de la fuente (o la altura del TIM)
       - solo los de número alto mal → no lee el texto más allá de 0x4600
  3. Texto en imágenes redibujado: todos los diálogos, descripciones de equipo y de criaturas y las 6 pantallas
     de la introducción llevan una frase de prueba con tildes y su clave.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import psxpatch  # noqa: E402
import st_image  # noqa: E402
import st_intro  # noqa: E402
import st_render  # noqa: E402
import st_text  # noqa: E402
import tfile  # noqa: E402
import tim  # noqa: E402

LOCAL = st_text.LOCAL
TEST = os.path.join(LOCAL, 'test')
BUILD = os.path.join(TEST, 'build2')
NAME = 'shadow-tower-prueba-2'

NEW_FONT_PTR = 0xA600
NEW_FONT_H = 64
FILLER_SLOT = 171
FILLER_UNITS = 2040  # u16 de relleno (≈ 4 KB)


# --- 1. Letras nuevas en la lámina de la entrada 0 -------------------------------------
def font_pixels(entry, ptr):
    t = tim.parse(entry, ptr + 8)
    return t, t['pix_off']


def put_glyph(entry, ptr, src_code, dst_code):
    """Copia la letra src_code a la celda dst_code (fuente A: celdas 6×12, 42 por fila) y le pone tilde."""
    t, base = font_pixels(entry, ptr)
    stride = t['w'] // 2

    def get(x, y):
        b = entry[base + y * stride + x // 2]
        return (b >> 4) if x & 1 else (b & 15)

    def put(x, y, v):
        i = base + y * stride + x // 2
        b = entry[i]
        entry[i] = (b & 0x0F) | (v << 4) if x & 1 else (b & 0xF0) | v

    sx, sy = (src_code % 42) * 6, (src_code // 42) * 12
    dx, dy = (dst_code % 42) * 6, (dst_code // 42) * 12
    for y in range(12):
        for x in range(6):
            put(dx + x, dy + y, get(sx + x, sy + y))
    put(dx + 3, dy, 1)
    put(dx + 4, dy, 1)


# --- 2. Fuente de la entrada 3 más atrás y más chica ----------------------------------
def relocate_font(entry, new_ptr, new_h):
    """Mueve el bloque [u32 0][u32 tamaño][TIM] de 0x4600 a new_ptr con el TIM recortado a new_h filas."""
    old = st_text.TEXT_END
    t = tim.parse(entry, old + 8)
    tim_off = old + 8
    img_hdr = t['pix_off'] - 12  # u32 largo, x, y, w16, h
    head = bytes(entry[tim_off:img_hdr])  # cabecera del TIM y paleta
    ln, x, y, w16, h = struct.unpack_from('<I4H', entry, img_hdr)
    pix = bytes(entry[t['pix_off']:t['pix_off'] + w16 * 2 * new_h])
    new_tim = head + struct.pack('<I4H', 12 + len(pix), x, y, w16, new_h) + pix
    block = struct.pack('<II', 0, len(new_tim)) + new_tim
    assert new_ptr + len(block) <= len(entry), 'no entra'
    # borrar el bloque viejo y escribir el nuevo
    entry[old:] = bytes(len(entry) - old)
    entry[new_ptr:new_ptr + len(block)] = block
    struct.pack_into('<I', entry, 0, new_ptr)


def rebuild_text(entry, font, texts, prefix, text_end, filler=None):
    """Como st_text.rebuild_entry, pero con otro final de la zona de texto y un relleno opcional."""
    sl = st_text.slots(bytes(entry))
    data = bytearray()
    offs = []
    for i, units in enumerate(sl):
        offs.append(len(data))
        if filler and i == filler[0]:
            data += struct.pack(f'<{filler[1]}H', *([0x20] * (filler[1] - 3) + [0, 1, 0xFFFF]))
            continue
        if units is None:
            continue
        key = f'{prefix}#{i:04d}'
        new = st_text.build_string(texts[key], units, font, key) if key in texts else units
        data += struct.pack(f'<{len(new)}H', *new)
    offs.append(len(data))
    assert st_text.TEXT_BASE + len(data) <= text_end, 'el texto no entra'
    struct.pack_into(f'<{st_text.NSLOTS}H', entry, 4, *offs)
    entry[st_text.TEXT_BASE:text_end] = bytes(data) + bytes(text_end - st_text.TEXT_BASE - len(data))
    return len(data)


def build_stat():
    src = {}
    import json
    for r in map(json.loads, open(st_text.source_path(), encoding='utf-8')):
        src[r['key']] = r['en']
    d = bytearray(open(os.path.join(st_text.ORIG, 'ST/COM/STAT.T'), 'rb').read())
    ents = tfile.entries(bytes(d))
    # entrada 0: Á y É
    _, a0, n0, _ = ents[0]
    e0 = bytearray(d[a0 * 2048:(a0 + n0) * 2048])
    put_glyph(e0, st_text.TEXT_END, 0x21, 168)
    put_glyph(e0, st_text.TEXT_END, 0x25, 300)
    st_text.EXTRA_A.update({'Á': 168, 'É': 300})
    texts = {}
    for k, v in src.items():
        if k.startswith('stat/00#') and v in ('STATUS', 'MAGIC LEFT'):
            texts[k] = {'STATUS': 'STÁTUS', 'MAGIC LEFT': 'MAGIC LÉFT'}[v]
    rebuild_text(e0, 'A', texts, 'stat/00', st_text.TEXT_END)
    d[a0 * 2048:(a0 + n0) * 2048] = e0
    print('STAT.T entrada 0: Á (168) y É (300);', len(texts), 'cadenas cambiadas')
    # entrada 3: fuente movida y relleno
    _, a3, n3, _ = ents[3]
    e3 = bytearray(d[a3 * 2048:(a3 + n3) * 2048])
    relocate_font(e3, NEW_FONT_PTR, NEW_FONT_H)
    used = rebuild_text(e3, 'A', {}, 'stat/03', NEW_FONT_PTR, filler=(FILLER_SLOT, FILLER_UNITS))
    d[a3 * 2048:(a3 + n3) * 2048] = e3
    print(f'STAT.T entrada 3: fuente en {NEW_FONT_PTR:#x} ({NEW_FONT_H} filas); texto hasta '
          f'{st_text.TEXT_BASE + used:#x} (antes el límite era {st_text.TEXT_END:#x})')
    out = {}
    for f in ('ST/COM/STAT.T', 'ST/VS/STAT.T'):
        p = os.path.join(BUILD, f)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(d)
        out[f] = p
    return out


# --- 3. Texto en imágenes -------------------------------------------------------------
def test_texts():
    src = st_render.source()
    out = {}
    for k in src:
        p, n = k.split('#')
        if p == 'talk':
            out[k] = f'Prueba {p} {n}: ¿Qué tal, niño? ¡Ánimo! El pingüino azul sabe dónde está la llave: Zona 3 (puerta 7).'
        elif p in ('equip', 'crt'):
            out[k] = f'PRUEBA {p.upper()} {n} - ÁCIDO, ÉXITO, ÍNDICE, ÓXIDO, ÚLTIMO, ÑANDÚ, PINGÜINO.\nLARGO 89 CM'
    return out


def build_images():
    st_render.OUT = BUILD
    tr = test_texts()
    st_render.translations = lambda use_en: tr
    assert st_render.import_(), 'errores al dibujar'
    st_intro.OUT = os.path.join(BUILD, st_intro.MIC)
    intro = {f'intro#{i}': f'Pantalla {i + 1}: ¿Qué guarda\nla torre? ¡Ánimo, niño!' for i in range(st_intro.NSCREENS)}
    st_intro.translations = lambda use_en: intro
    assert st_intro.import_(), 'errores en la introducción'
    files = {fn: os.path.join(BUILD, fn) for fn in sorted({st_image.FONTS[f][0] for f in st_image.FONTS})}
    files[st_intro.MIC] = st_intro.OUT
    return files


def main():
    os.makedirs(TEST, exist_ok=True)
    files = build_stat()
    files.update(build_images())
    img = os.path.join(TEST, NAME + '.bin')
    shutil.copyfile(os.path.join(LOCAL, 'original.bin'), img)
    for iso_path, src in files.items():
        psxpatch.put(img, iso_path, src)
    with open(os.path.join(TEST, NAME + '.cue'), 'w') as w:
        w.write(f'FILE "{NAME}.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    # verificación: lo que quedó en la imagen es lo que se escribió
    with open(img, 'rb') as f:
        for p, lba, sz in psxiso_walk(f):
            if p in files:
                assert psxpatch.psxiso.read_extent(f, lba, sz) == open(files[p], 'rb').read(), p
    print(f'Listo: {img}')


def psxiso_walk(f):
    return psxpatch.psxiso.walk(f)


if __name__ == '__main__':
    main()
