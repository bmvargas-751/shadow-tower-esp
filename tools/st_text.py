#!/usr/bin/env python3
"""Adaptador de Shadow Tower: texto codificado (nombres, estados, menús) de STAT.T, FDAT.T y VS_ETC.T.

Uso (desde la raíz del proyecto):
  st_text.py export                  escribe el original en el `source` de loc.json
  st_text.py import [--en]           de translation/ a ../shadow-tower-esp-local/build/files/
                                     (--en: sin traducción, con el inglés; para la ida y vuelta)
  st_text.py roundtrip               export + import --en y compara byte por byte con el original

Formato de un bloque de texto (ver TECH.md), relativo a su comienzo:
  0x0000  u32 = 0x4600 (largo del bloque)
  0x0004  u16[1536] desplazamientos en bytes, relativos a 0x0C04; casilla i = [off[i], off[i+1])
  0x0C04  cadenas en u16: renglones terminados en 0000 0001, la cadena cierra con FFFF
  ...     ceros hasta 0x4600
En STAT.T, después del bloque viene la fuente de esa entrada (TIM 4 bpp 256×256).
"""
import collections
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tfile  # noqa: E402

ROOT = os.path.dirname(HERE)
LOCAL = os.path.join(os.path.dirname(ROOT), 'shadow-tower-esp-local')
ORIG = os.path.join(LOCAL, 'files')
OUT = os.path.join(LOCAL, 'build', 'files')

TEXT_BASE = 0x0C04
TEXT_END = 0x4600
NSLOTS = 1536

# --- Mapas de caracteres -------------------------------------------------------
# Fuente A (entradas 0 y 3): código = celda; celdas 6×12, 42 por fila.
FONT_A = {0x02 + i: c for i, c in enumerate('0123456789')}
FONT_A.update({0x0C: '+', 0x0D: '-', 0x0E: '*', 0x0F: '/', 0x10: '.', 0x11: ',', 0x12: '?',
               0x13: '!', 0x14: '#', 0x15: '%', 0x16: "'", 0x17: '(', 0x18: ')', 0x1A: '|',
               0x1B: ':', 0x1C: ';', 0x1D: '<', 0x1E: '>', 0x1F: '"', 0x20: ' ',
               0x3B: '[', 0x3C: ']', 0x3E: '='})
FONT_A.update({0x21 + i: c for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')})

# Fuente B (entradas 1, 2, 4, 8, 10): celda = código − 2; celdas 12×10, 18 por fila.
# Solo lo seguro; el resto de los signos (flechas, «lb», extras por entrada) sale como {XXXX}.
FONT_B = {0x03: '-', 0x0E: '/', 0x10: '+', 0x12: '.', 0x31: ' '}
FONT_B.update({0x04 + i: c for i, c in enumerate('0123456789')})
FONT_B.update({0x17 + i: c for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')})

# Letras españolas de la fuente A (TECH.md, prueba 6/7). El juego solo dibuja como letras normales los códigos
# de las filas 0 y 1 de la lámina (2–83); ahí no hay lugar libre salvo las celdas 25 y 61, así que se reusan
# celdas de signos que ninguna cadena usa ni el juego arma solo: * # | ; [ ] =
SPANISH_A = {'É': 0x19, 'Á': 0x3D, 'Í': 0x1A, 'Ó': 0x1C, 'Ú': 0x3B, 'Ñ': 0x3C, 'Ü': 0x3E, '¿': 0x14, '¡': 0x0E}
for _c in SPANISH_A.values():
    FONT_A.pop(_c, None)
EXTRA_A = dict(SPANISH_A)
# Fuente B (con serifas): sus 3 filas están llenas, pero el juego dibuja también la fila 3 (prueba 7: la Á en el
# código 56 se vio; la celda 0, código 2, no sirve). Sin ¿ ni ¡: la fuente B no trae ? ni ! de base.
# Signos de la fuente B que cambian de una lámina a otra (dibujados el 2026-11-17): solo los que se leen en la
# lámina de la propia entrada y su uso en el original lo confirma. El guion 0x11 es igual en todas las láminas.
# stat/04 queda fuera: sus códigos ({0035} en KING'S, {0036}/{0037} en SOUL POD) no coinciden con su lámina,
# así que el juego la dibuja con otra; se decide al verla en pantalla.
FONT_B.update({0x11: '-'})
FONT_B_ENTRY = {'stat/02': {0x32: "'"}, 'stat/08': {0x33: "'"}, 'vs_etc/15': {0x33: "'"}}
SPANISH_B = {'Á': 56, 'É': 57, 'Í': 58, 'Ó': 59, 'Ú': 60, 'Ñ': 61, 'Ü': 62}
EXTRA_B = dict(SPANISH_B)
# Láminas donde se dibujan las letras nuevas (cada pantalla usa la de alguna entrada)
FONT_A_SHEETS = {'ST/COM/STAT.T': [0, 3], 'ST/VS/STAT.T': [0, 3]}
FONT_B_SHEETS = {'ST/COM/STAT.T': [1, 2, 4, 8, 10], 'ST/VS/STAT.T': [1, 2, 4, 8, 10], 'ST/VS/VS_ETC.T': [15]}

# Bloques de texto: (prefijo de clave, archivos donde se escribe, entrada .T, desplazamiento, fuente, copias)
# Son todos los del juego (búsqueda del 2026-11-16 en todos los .T). VS/STAT.T es copia de COM/STAT.T;
# la entrada 10 de STAT.T es copia de la 2.
STAT = ['ST/COM/STAT.T', 'ST/VS/STAT.T']
BLOCKS = [
    ('stat/00', STAT, 0, 0, 'A', []),
    ('stat/01', STAT, 1, 0, 'B', []),
    ('stat/02', STAT, 2, 0, 'B', [10]),
    ('stat/03', STAT, 3, 0, 'A', []),
    ('stat/04', STAT, 4, 0, 'B', []),
    ('stat/08', STAT, 8, 0, 'B', []),
    ('fdat/480', ['ST/COM/FDAT.T'], 480, 0x7488, 'A', []),
    ('vs_etc/15', ['ST/VS/VS_ETC.T'], 15, 0, 'B', []),
]
FILES = sorted({f for b in BLOCKS for f in b[1]})

LINE_END = (0x0000, 0x0001)
STR_END = 0xFFFF


def charmap(font, prefix=None):
    if font == 'A':
        return FONT_A
    return {**FONT_B, **FONT_B_ENTRY.get(prefix, {})}


def encmap(font, prefix=None):
    # el primer código de cada signo manda (el guion sigue siendo 0x03, como antes)
    m = {}
    for k, c in charmap(font, prefix).items():
        m.setdefault(c, k)
    m.update(EXTRA_A if font == 'A' else EXTRA_B)
    return m


# --- Lectura -------------------------------------------------------------------
def slots(entry, base=0):
    assert struct.unpack_from('<I', entry, base)[0] > TEXT_BASE, 'no es un bloque de texto'
    offs = struct.unpack_from(f'<{NSLOTS}H', entry, base + 4)
    out = []
    for i in range(NSLOTS - 1):
        a, b = offs[i], offs[i + 1]
        out.append(list(struct.unpack_from(f'<{(b - a) // 2}H', entry, base + TEXT_BASE + a)) if b > a else None)
    return out


def split_lines(units):
    """u16 de una cadena (con su FFFF) → lista de renglones (listas de u16), y si el último renglón cierra."""
    assert units and units[-1] == STR_END, 'cadena sin FFFF'
    body = units[:-1]
    lines, cur, i = [], [], 0
    while i < len(body):
        if tuple(body[i:i + 2]) == LINE_END:
            lines.append(cur)
            cur = []
            i += 2
        else:
            cur.append(body[i])
            i += 1
    return lines, cur  # cur: resto sin terminador (normalmente vacío)


def decode_line(units, font, prefix=None):
    m = charmap(font, prefix)
    return ''.join(m.get(u, f'{{{u:04X}}}') for u in units)


def to_text(lines, rest, font, prefix=None):
    text = [decode_line(l, font, prefix) for l in lines]
    while text and text[-1] == '':
        text.pop()
    # rest (códigos de control después del último renglón) no se muestra: el import lo conserva
    return '\n'.join(text)


# --- Escritura -----------------------------------------------------------------
def encode_line(s, font, key):
    m = encmap(font, key.split('#')[0])
    out, i = [], 0
    while i < len(s):
        if s[i] == '{':
            j = s.index('}', i)
            out.append(int(s[i + 1:j], 16))
            i = j + 1
        else:
            if s[i] not in m:
                raise SystemExit(f'{key}: la fuente {font} no tiene «{s[i]}»')
            out.append(m[s[i]])
            i += 1
    return out


def build_string(text, orig_units, font, key):
    lines, rest = split_lines(orig_units)
    new = text.split('\n') if text != '' else []
    if len(new) > len(lines):
        raise SystemExit(f'{key}: {len(new)} renglones; el original tiene {len(lines)}')
    new += [''] * (len(lines) - len(new))
    units = []
    for k, line in enumerate(new):
        # un renglón que en el original no cambia se copia tal cual (conserva códigos raros)
        if decode_line(lines[k], font, key.split('#')[0]) == line:
            units += lines[k]
        else:
            units += encode_line(line, font, key)
        units += LINE_END
    return units + rest + [STR_END]


def _pack(sl, font, texts, prefix, dedupe):
    """Cadenas y desplazamientos. Con dedupe, las casillas con el mismo texto apuntan a una sola copia.
    POR PROBAR EN EL JUEGO (prueba 6): que el juego lea cada casilla hasta su FFFF y no calcule largos ni casillas
    vacías restando desplazamientos."""
    data = bytearray()
    offs = []
    seen = {}
    for i, units in enumerate(sl):
        if units is None:
            offs.append(len(data))
            continue
        key = f'{prefix}#{i:04d}'
        new_units = build_string(texts[key], units, font, key) if key in texts else units
        blob = struct.pack(f'<{len(new_units)}H', *new_units)
        if dedupe and blob in seen:
            offs.append(seen[blob])
            continue
        offs.append(len(data))
        seen.setdefault(blob, len(data))
        data += blob
    offs.append(len(data))
    return data, offs


def _monotonic_fix(offs, end):
    """Con casillas compartidas, el largo de la casilla i ya no es off[i+1] - off[i]; se supone (por probar) que el
    juego lee hasta el FFFF. La última casilla y la cola siguen marcando el final de los datos."""
    offs = list(offs)
    offs[-1] = end
    return offs


def rebuild_entry(entry, font, texts, prefix, base=0):
    sl = slots(entry, base)
    data, offs = _pack(sl, font, texts, prefix, dedupe=False)
    if TEXT_BASE + len(data) > TEXT_END:
        # no entra: las casillas repetidas comparten una sola copia (los desplazamientos dejan de ser crecientes,
        # pero cada casilla sigue apuntando a su texto)
        data, offs = _pack(sl, font, texts, prefix, dedupe=True)
        offs = _monotonic_fix(offs, len(data))
    if TEXT_BASE + len(data) > TEXT_END:
        raise SystemExit(f'{prefix}: el texto no cabe ({TEXT_BASE + len(data):#x} > {TEXT_END:#x}); '
                         f'sobran {TEXT_BASE + len(data) - TEXT_END} bytes')
    out = bytearray(entry)
    struct.pack_into(f'<{NSLOTS}H', out, base + 4, *offs)
    out[base + TEXT_BASE:base + TEXT_END] = bytes(data) + bytes(TEXT_END - TEXT_BASE - len(data))
    return bytes(out)


# --- Comandos ------------------------------------------------------------------
def load_cfg():
    return json.load(open(os.path.join(ROOT, 'loc.json'), encoding='utf-8'))


def source_path():
    """El original del texto codificado: el primer archivo de `source` en loc.json."""
    src = load_cfg()['source']
    return os.path.normpath(os.path.join(ROOT, src[0] if isinstance(src, list) else src))


def export():
    src = source_path()
    rows = []
    for prefix, files, e, base, font, _ in BLOCKS:
        ents = tfile.entries(open(os.path.join(ORIG, files[0]), 'rb').read())
        name = os.path.basename(files[0])
        for i, units in enumerate(slots(ents[e][3], base)):
            if units is None:
                continue
            lines, rest = split_lines(units)
            rows.append({'key': f'{prefix}#{i:04d}', 'en': to_text(lines, rest, font, prefix),
                         'note': f'{name} entrada {e}, casilla {i}, fuente {font}, {len(lines)} renglones'})
    os.makedirs(os.path.dirname(src), exist_ok=True)
    with open(src, 'w', encoding='utf-8') as w:
        for r in rows:
            w.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'{len(rows)} textos en {src}')
    return rows


def load_translation(use_en):
    if use_en:
        return {r['key']: r['en'] for r in map(json.loads, open(source_path(), encoding='utf-8'))}
    out = {}
    tdir = os.path.join(ROOT, load_cfg()['translation'])
    for dp, _, fs in os.walk(tdir):
        for f in fs:
            if f.endswith('.jsonl'):
                for line in open(os.path.join(dp, f), encoding='utf-8'):
                    if line.strip():
                        x = json.loads(line)
                        out[x['key']] = x['es']
    return out


def _cell_a(code):
    return (code % 42) * 6, (code // 42) * 12


def draw_spanish_a(entry):
    """Dibuja las letras de SPANISH_A en la lámina de una entrada de fuente A (bytearray, se modifica)."""
    import tim
    ptr = struct.unpack_from('<I', entry, 0)[0]
    t = tim.parse(bytes(entry), ptr + 8)
    base, stride, bg = t['pix_off'], t['w'] // 2, 15

    def get(x, y):
        b = entry[base + y * stride + x // 2]
        return (b >> 4) if x & 1 else (b & 15)

    def put(x, y, v):
        i = base + y * stride + x // 2
        entry[i] = (entry[i] & 0x0F) | (v << 4) if x & 1 else (entry[i] & 0xF0) | v

    def glyph(code):
        x0, y0 = _cell_a(code)
        return [[get(x0 + x, y0 + y) for x in range(6)] for y in range(12)]

    def ink(g):
        c = collections.Counter(v for r in g for v in r if v != bg)
        return c.most_common(1)[0][0]

    def store(code, g):
        x0, y0 = _cell_a(code)
        for y in range(12):
            for x in range(6):
                put(x0 + x, y0 + y, g[y][x])

    marks = {'acute': [(3, 0), (4, 0)], 'tilde': [(1, 0), (2, 0), (3, 0), (4, 0)], 'diaer': [(1, 0), (4, 0)]}
    for ch, (b, m) in {'Á': (0x21, 'acute'), 'É': (0x25, 'acute'), 'Í': (0x29, 'acute'), 'Ó': (0x2F, 'acute'),
                       'Ú': (0x35, 'acute'), 'Ñ': (0x2E, 'tilde'), 'Ü': (0x35, 'diaer')}.items():
        g = glyph(b)
        v = ink(g)
        for x, y in marks[m]:
            g[y][x] = v
        store(SPANISH_A[ch], g)
    for ch, b, mirror in (('¿', 0x12, True), ('¡', 0x13, False)):
        g = glyph(b)
        rows = [y for y in range(12) if any(p != bg for p in g[y])]
        y0, y1 = rows[0], rows[-1]
        new = [list(r) for r in g]
        for y in range(y0, y1 + 1):
            src = g[y0 + y1 - y]
            new[y] = src[::-1] if mirror else list(src)
        store(SPANISH_A[ch], new)


def draw_spanish_b(entry):
    """Dibuja las letras de SPANISH_B en la lámina de una entrada de fuente B (celdas 12×10, celda = código − 2)."""
    import tim
    ptr = struct.unpack_from('<I', entry, 0)[0]
    t = tim.parse(bytes(entry), ptr + 8)
    base, stride, bg = t['pix_off'], t['w'] // 2, 15

    def get(x, y):
        b = entry[base + y * stride + x // 2]
        return (b >> 4) if x & 1 else (b & 15)

    def put(x, y, v):
        i = base + y * stride + x // 2
        entry[i] = (entry[i] & 0x0F) | (v << 4) if x & 1 else (entry[i] & 0xF0) | v

    def xy(code):
        c = code - 2
        return (c % 18) * 12, (c // 18) * 10

    marks = {'acute': [(6, 0), (7, 0)], 'tilde': [(3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0)],
             'diaer': [(3, 0), (4, 0), (7, 0), (8, 0)]}
    letters = {'Á': (0x17, 'acute'), 'É': (0x1B, 'acute'), 'Í': (0x1F, 'acute'), 'Ó': (0x25, 'acute'),
               'Ú': (0x2B, 'acute'), 'Ñ': (0x24, 'tilde'), 'Ü': (0x2B, 'diaer')}
    def squeeze(g):
        """Baja la letra un píxel quitando su fila más redundante, para dejar la fila 1 vacía bajo la marca."""
        rows = [y for y in range(10) if any(v != bg for v in g[y])]
        y0, y1 = rows[0], rows[-1]
        if y0 >= 2:
            return g
        cand = range(y0 + 1, y1)
        drop = min(cand, key=lambda y: (sum(a != b for a, b in zip(g[y], g[y - 1])), abs(y - (y0 + y1) / 2)))
        body = g[y0:drop] + g[drop + 1:y1 + 1]
        new = [[bg] * 12 for _ in range(10)]
        for k, r in enumerate(body):
            new[y1 - len(body) + 1 + k] = list(r)
        return new

    for ch, (b, m) in letters.items():
        sx, sy = xy(b)
        dx, dy = xy(SPANISH_B[ch])
        g = squeeze([[get(sx + x, sy + y) for x in range(12)] for y in range(10)])
        ink = collections.Counter(v for r in g for v in r if v != bg).most_common(1)[0][0]
        for x, y in marks[m]:
            g[y][x] = ink
        for y in range(10):
            for x in range(12):
                put(dx + x, dy + y, g[y][x])


def uses_spanish(texts, font):
    pre = {p for p, _f, _e, _b, f, _c in BLOCKS if f == font}
    letters = SPANISH_A if font == 'A' else SPANISH_B
    return any(k.rsplit('#', 1)[0] in pre and any(c in letters for c in v) for k, v in texts.items())


def uses_spanish_a(texts):
    return uses_spanish(texts, 'A')


def import_(use_en=False):
    texts = load_translation(use_en)
    data = {f: bytearray(open(os.path.join(ORIG, f), 'rb').read()) for f in FILES}
    for prefix, files, e, base, font, copies in BLOCKS:
        src = data[files[0]]
        ents = tfile.entries(bytes(src))
        new = rebuild_entry(ents[e][3], font, texts, prefix, base)
        for f in files:
            ents_f = tfile.entries(bytes(data[f]))
            for target in [e] + copies:
                _, a, n, blob = ents_f[target]
                assert len(new) == len(blob)
                data[f][a * 2048:(a + n) * 2048] = new
    for font, sheets, draw in (('A', FONT_A_SHEETS, draw_spanish_a), ('B', FONT_B_SHEETS, draw_spanish_b)):
        if not uses_spanish(texts, font):
            continue
        for f, wanted in sheets.items():
            for i, a, n, _ in tfile.entries(bytes(data[f])):
                if i in wanted:
                    ent = bytearray(data[f][a * 2048:(a + n) * 2048])
                    draw(ent)
                    data[f][a * 2048:(a + n) * 2048] = ent
    for f in FILES:
        tfile.fix_checksums(data[f], open(os.path.join(ORIG, f), 'rb').read())
        p = os.path.join(OUT, f)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data[f])
    print(f'{len(FILES)} archivos reconstruidos en {OUT} ({len(texts)} textos disponibles)')


def roundtrip():
    export()
    import_(use_en=True)
    ok = True
    for f in FILES:
        same = open(os.path.join(ORIG, f), 'rb').read() == open(os.path.join(OUT, f), 'rb').read()
        print(f'{f}: {"idéntico" if same else "DISTINTO"}')
        ok &= same
    return ok


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'export':
        export()
    elif cmd == 'import':
        import_('--en' in sys.argv)
    elif cmd == 'roundtrip':
        sys.exit(0 if roundtrip() else 1)
    else:
        sys.exit(__doc__)
