#!/usr/bin/env python3
"""Dibujador de Shadow Tower: vuelve a dibujar el texto traducido en las imágenes (TALKMSG, EQUIP, CRT).

Uso (desde la raíz del proyecto):
  st_render.py glyphs                     arma las plantillas de color de cada letra (carpeta local)
  st_render.py test                       redibuja el inglés con los cortes originales y compara celda por celda
  st_render.py preview CLAVE "texto" OUT  dibuja un texto en la imagen de CLAVE (p. ej. talk#0030) y guarda un PNG
  st_render.py import [--en]              de translation/ a ../shadow-tower-esp-local/build/files/
  st_render.py roundtrip                  import --en y compara byte por byte con el original

Las plantillas salen de las imágenes del juego, así que viven en ../shadow-tower-esp-local/glyphs/ (no en el repo).
Cada plantilla guarda el brillo relativo (0..1) de cada píxel; al dibujar se elige el índice de la paleta de la
imagen con el brillo más parecido. Un texto que no cambió conserva la imagen original sin tocarla.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import st_image as SI  # noqa: E402
import tfile  # noqa: E402

LOCAL = SI.LOCAL
GLYPH_DIR = os.path.join(LOCAL, 'glyphs')
OUT = os.path.join(LOCAL, 'build', 'files')

# Caja de texto por fuente (TECH.md): x inicial, máximo de caracteres por renglón y de renglones.
LIMITS = {'talk': {'cols': 33, 'rows': 5}, 'equip': {'rows': 5}, 'crt': {'rows': 5}}
EQUIP_X = 9  # equip/crt: las celdas empiezan en x = 9
BASELINE = {'talk': 10, 'equip': 9}  # fila de la línea de base dentro de la celda


def lum_rel(t):
    cl = t['clut']['colors']
    idx = [v for x in t['pixels'] for v in (x & 15, x >> 4)]
    m = max(SI.lum(cl[v]) for v in set(idx)) or 1
    return [SI.lum(cl[v]) / m for v in idx], m


# --- Plantillas ---------------------------------------------------------------------
def build_glyphs():
    os.makedirs(GLYPH_DIR, exist_ok=True)
    for gname, fonts in (('talk', ['talk']), ('equip', ['equip', 'crt'])):
        rd = SI.Reader(fonts[0])
        votes = collections.defaultdict(collections.Counter)
        pw, ch = SI.FONTS[fonts[0]][2], SI.FONTS[fonts[0]][3]
        for font in fonts:
            for _, t in SI.images(font):
                W, H = t['w'], t['h']
                rel, _ = lum_rel(t)
                px = SI.binarize(t)
                vp, oy = SI.vgrid(px, W, H, ch)
                if vp != ch:
                    continue  # solo imágenes con el paso normal
                for r, o, cs in SI.lines(t, font):
                    top = oy + r * vp
                    # línea de base del renglón: la fila inferior más común de las celdas
                    bottoms = collections.Counter(max(y for y in range(ch) if any(c[y * pw + x] for x in range(pw)))
                                                  for c in cs if any(c))
                    if not bottoms:
                        continue
                    top += bottoms.most_common(1)[0][0] - BASELINE[gname]
                    if top < 0 or top + ch > H:
                        continue
                    for k, c in enumerate(cs):
                        lab = rd.labels.get(SI.key(c))
                        if not lab or lab == SI.UNKNOWN or len(lab) != 1:
                            continue
                        x0 = o + k * pw
                        cell = tuple(0 if x == 0 else round(rel[(top + y) * W + x0 + x] * 8)
                                     for y in range(ch) for x in range(pw))
                        votes[lab][cell] += 1
        glyphs = {c: [v / 8 for v in cnt.most_common(1)[0][0]] for c, cnt in votes.items()}
        glyphs[' '] = [0.0] * (pw * ch)
        add_spanish(glyphs, gname, pw, ch)
        json.dump({'pw': pw, 'ch': ch, 'glyphs': glyphs},
                  open(os.path.join(GLYPH_DIR, f'{gname}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        print(gname, len(glyphs), 'letras:', ''.join(sorted(glyphs)))


def _grid(g, pw):
    return [g[i:i + pw] for i in range(0, len(g), pw)]


def _flat(rows):
    return [v for r in rows for v in r]


def _top(rows):
    return next((y for y, r in enumerate(rows) if any(v > 0.3 for v in r)), len(rows))


# Letras dibujadas a mano para la letra de los diálogos (celda 6×12; la columna 0 queda vacía).
# «#» = trazo (0.85, el brillo habitual de la fuente), «+» = medio tono (0.45). Cada dibujo empieza en la
# fila indicada: mayúsculas y dígitos en la 2, minúsculas en la 5 (línea de base en la 10).
TALK_NEW = {
    'R': (2, ['####.', '#...#', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#', '#...#']),
    'J': (2, ['....#', '....#', '....#', '....#', '....#', '....#', '#...#', '#...#', '.###.']),
    'Q': (2, ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#']),
    'X': (2, ['#...#', '#...#', '.#.#.', '.#.#.', '..#..', '.#.#.', '.#.#.', '#...#', '#...#']),
    'Z': (2, ['#####', '....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....', '#####']),
    'z': (5, ['#####', '...#.', '..#..', '.#...', '#....', '#####']),
    '0': (2, ['.###.', '#...#', '#..##', '#.#.#', '#.#.#', '##..#', '#...#', '#...#', '.###.']),
    '1': (2, ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.']),
    '2': (2, ['.###.', '#...#', '....#', '....#', '...#.', '..#..', '.#...', '#....', '#####']),
    '3': (2, ['.###.', '#...#', '....#', '....#', '..##.', '....#', '....#', '#...#', '.###.']),
    '4': (2, ['...#.', '..##.', '.#.#.', '.#.#.', '#..#.', '#####', '...#.', '...#.', '...#.']),
    '5': (2, ['#####', '#....', '#....', '####.', '....#', '....#', '....#', '#...#', '.###.']),
    '6': (2, ['.###.', '#....', '#....', '####.', '#...#', '#...#', '#...#', '#...#', '.###.']),
    '8': (2, ['.###.', '#...#', '#...#', '#...#', '.###.', '#...#', '#...#', '#...#', '.###.']),
    '9': (2, ['.###.', '#...#', '#...#', '#...#', '.####', '....#', '....#', '....#', '.###.']),
    ':': (5, ['.....', '.##..', '.##..', '.....', '.##..', '.##..']),
    ';': (5, ['.....', '.##..', '.##..', '.....', '.##..', '.##..', '..#..']),
    '-': (7, ['####.']),
    '"': (2, ['.#.#.', '.#.#.']),
    '(': (2, ['...#.', '..#..', '.#...', '.#...', '.#...', '.#...', '.#...', '..#..', '...#.']),
    ')': (2, ['.#...', '..#..', '...#.', '...#.', '...#.', '...#.', '...#.', '..#..', '.#...']),
    '/': (2, ['....#', '....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....', '#....']),
}
# Marcas para componer las letras españolas: (fila inicial, dibujo).
TALK_MARKS = {
    'acute_low': (2, ['...#.', '..#..']),      # sobre minúsculas (altura x desde la fila 5)
    'acute_cap': (0, ['...#.', '..#..']),      # sobre mayúsculas (desde la fila 2)
    'tilde_low': (2, ['.##.#', '#..#.']),
    'tilde_cap': (0, ['.##.#', '#..#.']),
    'diaer_low': (3, ['.#.#.']),
    'diaer_cap': (0, ['.#.#.']),
}
EQUIP_MARKS = {  # mayúsculas de 10 px: la marca va en la fila 0, sin lugar para dos filas
    'acute': (0, ['.....', '...##.'[:5]]),
}


def _paint(cell, pw, row0, art, col0=1):
    cell = list(cell)
    for dy, line in enumerate(art):
        for dx, ch_ in enumerate(line):
            if ch_ in '#+':
                x, y = col0 + dx, row0 + dy
                if 0 <= x < pw and 0 <= y * pw + x < len(cell):
                    cell[y * pw + x] = 0.85 if ch_ == '#' else 0.45
    return cell


def add_spanish(G, gname, pw, ch):
    """Letras que faltan y letras españolas (TECH.md). Los dibujos son propios, no del juego."""
    if gname == 'talk':
        for c, (row0, art) in TALK_NEW.items():
            if c not in G:
                G[c] = _paint([0.0] * (pw * ch), pw, row0, art)
        # i sin punto: se borra todo lo que está por encima de la altura x (fila 5)
        dotless = [0.0 if (k // pw) < 5 else v for k, v in enumerate(G['i'])]
        for base, acc, low in (('a', 'á', 1), ('e', 'é', 1), ('o', 'ó', 1), ('u', 'ú', 1),
                               ('A', 'Á', 0), ('E', 'É', 0), ('I', 'Í', 0), ('O', 'Ó', 0), ('U', 'Ú', 0)):
            row0, art = TALK_MARKS['acute_low' if low else 'acute_cap']
            G[acc] = _paint(G[base], pw, row0, art)
        G['í'] = _paint(dotless, pw, *TALK_MARKS['acute_low'])
        G['ñ'] = _paint(G['n'], pw, *TALK_MARKS['tilde_low'])
        G['Ñ'] = _paint(G['N'], pw, *TALK_MARKS['tilde_cap'])
        G['ü'] = _paint(G['u'], pw, *TALK_MARKS['diaer_low'])
        G['Ü'] = _paint(G['U'], pw, *TALK_MARKS['diaer_cap'])
        G['¿'] = _paint([0.0] * (pw * ch), pw, 5, ['..#..', '.....', '..#..', '.#...', '#....', '#...#', '.###.'])
        G['¡'] = _paint([0.0] * (pw * ch), pw, 5, ['..#..', '.....', '..#..', '..#..', '..#..', '..#..', '..#..'])
    else:
        # mayúsculas de 10 px (filas 1–9): se quita la fila más redundante de la letra (la más parecida a
        # su vecina) para bajarla un píxel y dejar dos filas arriba para la marca
        def squeeze(g):
            rows = [g[y * pw:(y + 1) * pw] for y in range(ch)]
            ink = [y for y, r in enumerate(rows) if any(v > 0.3 for v in r)]
            y0, y1 = ink[0], ink[-1]
            best = min(range(y0 + 1, y1), key=lambda y: (sum(abs(a - b) for a, b in zip(rows[y], rows[y - 1])),
                                                         abs(y - (y0 + y1) / 2)))
            body = rows[y0:best] + rows[best + 1:y1 + 1]
            new = [[0.0] * pw for _ in range(ch)]
            for k, r in enumerate(body):
                new[y1 - len(body) + 1 + k] = list(r)
            return [v for r in new for v in r]
        # una sola fila de marca (fila 0) y la fila 1 vacía, para que no se pegue a la letra
        marks = {'acute': ['.....##'], 'tilde': ['..#####'], 'diaer': ['..##.##']}
        for base, acc, m in [(b, a, 'acute') for b, a in zip('AEIOU', 'ÁÉÍÓÚ')] + [('N', 'Ñ', 'tilde'), ('U', 'Ü', 'diaer')]:
            if base in G:
                G[acc] = _paint(squeeze(G[base]), pw, 0, marks[m], col0=0)


def load_glyphs(font):
    gname = SI.GLYPHS.get(font, font)
    return json.load(open(os.path.join(GLYPH_DIR, f'{gname}.json'), encoding='utf-8'))


# --- Maquetado --------------------------------------------------------------------
def wrap(text, cols):
    out = []
    for para in text.split('\n'):
        line = ''
        for w in para.split(' '):
            if len(w) > cols:
                raise ValueError(f'palabra de {len(w)} caracteres, el renglón admite {cols}: {w}')
            cand = w if not line else line + ' ' + w
            if len(cand) <= cols:
                line = cand
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


def layout(font, t, text):
    """[(x, y, renglón)] y el paso de celda; error si no entra."""
    pw, ch = SI.FONTS[font][2], SI.FONTS[font][3]
    if font == 'talk':
        cols = LIMITS['talk']['cols']
        lines = wrap(text, cols)
        n = max(len(l) for l in lines)
        k = int((123 - 3 * n) / 6 + 0.5 + 1e-9) if (123 - 3 * n) >= 0 else 0
        x0 = 5 + 6 * k
        x0 = min(x0, 227 - n * 6)
        while x0 < 0:
            x0 += 6
    else:
        cols = (t['w'] - EQUIP_X) // pw
        lines = wrap(text, cols)
        x0 = EQUIP_X
    if len(lines) > LIMITS[font]['rows']:
        raise ValueError(f'{len(lines)} renglones, el máximo es {LIMITS[font]["rows"]}')
    return [(x0, r * ch, l) for r, l in enumerate(lines)]


def render(font, t, text):
    """Bytes de píxeles nuevos (4 bpp) para el TIM t con el texto dibujado."""
    G = load_glyphs(font)
    pw, ch, glyphs = G['pw'], G['ch'], G['glyphs']
    W, H = t['w'], t['h']
    cl = t['clut']['colors']
    idx = [v for x in t['pixels'] for v in (x & 15, x >> 4)]
    bg = collections.Counter(idx).most_common(1)[0][0]
    rel, _ = lum_rel(t)
    # índice de paleta para cada brillo relativo: el más parecido entre los que usa la imagen
    used = sorted(set(idx))
    shades = sorted({(round(rel[i], 3), v) for i, v in enumerate(idx) if v in used})
    lv = {}
    for r, v in shades:
        lv.setdefault(r, v)
    levels = sorted(lv.items())

    def index_for(x):
        return min(levels, key=lambda rv: abs(rv[0] - x))[1]
    new = [bg] * (W * H)
    for x0, y0, line in layout(font, t, text):
        for k, c in enumerate(line):
            if c not in glyphs:
                raise ValueError(f'la letra no tiene «{c}»')
            g = glyphs[c]
            for y in range(ch):
                for x in range(pw):
                    v = g[y * pw + x]
                    if v > 0.05:
                        X, Y = x0 + k * pw + x, y0 + y
                        if 0 <= X < W and 0 <= Y < H:
                            new[Y * W + X] = index_for(v)
    return bytes(new[i] | (new[i + 1] << 4) for i in range(0, len(new), 2))


# --- Comandos ---------------------------------------------------------------------
def all_images():
    """{clave: (font, archivo, entrada, sector, TIM)}"""
    out = {}
    for font in SI.FONTS:
        fn = SI.FONTS[font][0]
        ents = {i: a for i, a, n, b in tfile.entries(open(os.path.join(SI.ORIG, fn), 'rb').read())}
        for i, t in SI.images(font):
            out[f'{SI.FONTS[font][4]}#{i:04d}'] = (font, fn, i, ents[i], t)
    return out


def source():
    p = os.path.join(LOCAL, 'image_source.jsonl')
    return {r['key']: r['en'] for r in map(json.loads, open(p, encoding='utf-8'))}


def translations(use_en):
    if use_en:
        return source()
    out = {}
    tdir = os.path.join(SI.ROOT, 'translation')
    for dp, _, fs in os.walk(tdir):
        for f in fs:
            if f.endswith('.jsonl'):
                for line in open(os.path.join(dp, f), encoding='utf-8'):
                    if line.strip():
                        x = json.loads(line)
                        out[x['key']] = x['es']
    return out


def import_(use_en=False):
    src, tr = source(), translations(use_en)
    imgs = all_images()
    files = {}
    changed = 0
    errors = []
    for key, (font, fn, i, sector, t) in imgs.items():
        if fn not in files:
            files[fn] = bytearray(open(os.path.join(SI.ORIG, fn), 'rb').read())
        if key not in tr or key not in src or tr[key] == src[key]:
            continue
        try:
            pix = render(font, t, tr[key])
        except ValueError as e:
            errors.append(f'{key}: {e}')
            continue
        assert len(pix) == len(t['pixels'])
        off = sector * 2048 + t['pix_off']
        files[fn][off:off + len(pix)] = pix
        changed += 1
    for fn, data in files.items():
        p = os.path.join(OUT, fn)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data)
    for e in errors:
        print('ERROR', e)
    print(f'{changed} imágenes redibujadas; {len(errors)} errores; archivos en {OUT}')
    return not errors


def roundtrip():
    import_(use_en=True)
    ok = True
    for fn in sorted({SI.FONTS[f][0] for f in SI.FONTS}):
        same = open(os.path.join(SI.ORIG, fn), 'rb').read() == open(os.path.join(OUT, fn), 'rb').read()
        print(f'{fn}: {"idéntico" if same else "DISTINTO"}')
        ok &= same
    return ok


def test():
    """Redibuja el inglés con los cortes originales y compara las celdas binarizadas."""
    tot = collections.Counter()
    for font in SI.FONTS:
        rd = SI.Reader(font)
        pw, ch = SI.FONTS[font][2], SI.FONTS[font][3]
        same = cells = 0
        for i, t in SI.images(font):
            W, H = t['w'], t['h']
            px = SI.binarize(t)
            vp, _ = SI.vgrid(px, W, H, ch)
            if vp != ch:
                continue
            orig_lines = SI.lines(t, font)
            text = '\n'.join(''.join(rd.classify(c)[0] for c in cs).rstrip() for _, _, cs in orig_lines)
            if not orig_lines or '{' in text:
                continue
            G = load_glyphs(font)
            new = [0] * (W * H)
            for r, o, cs in orig_lines:
                line = ''.join(rd.classify(c)[0] for c in cs)
                for k, c in enumerate(line):
                    g = G['glyphs'].get(c)
                    if not g:
                        continue
                    for y in range(ch):
                        for x in range(pw):
                            if g[y * pw + x] > 0.3:
                                X, Y = o + k * pw + x, r * ch + y
                                if X < W and Y < H:
                                    new[Y * W + X] = 1
            for r, o, cs in orig_lines:
                for k, c in enumerate(cs):
                    if not any(c):
                        continue
                    nc = tuple(0 if x == 0 else new[(r * ch + y) * W + o + k * pw + x]
                               for y in range(ch) for x in range(pw))
                    cells += 1
                    same += sum(a == b for a, b in zip(nc, c)) >= len(c) - 4
        print(f'{font}: {same}/{cells} celdas iguales (±4 píxeles) = {100 * same / max(cells, 1):.1f} %')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'glyphs':
        build_glyphs()
    elif cmd == 'test':
        test()
    elif cmd == 'preview':
        from PIL import Image
        key, text, out = sys.argv[2], sys.argv[3], sys.argv[4]
        font, fn, i, sector, t = all_images()[key]
        t = dict(t)
        t['pixels'] = render(font, t, text)
        import tim
        tim.to_image(t).resize((t['w'] * 3, t['h'] * 3), Image.NEAREST).save(out)
        print(out)
    elif cmd == 'import':
        sys.exit(0 if import_('--en' in sys.argv) else 1)
    elif cmd == 'roundtrip':
        sys.exit(0 if roundtrip() else 1)
    else:
        sys.exit(__doc__)
