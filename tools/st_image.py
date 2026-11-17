#!/usr/bin/env python3
"""Adaptador de Shadow Tower: texto dibujado en imágenes (diálogos y descripciones de equipo).

Uso (desde la raíz del proyecto):
  st_image.py clusters FUENTE           lista los dibujos de celda (huella, apariciones, etiqueta)
  st_image.py sheet FUENTE SALIDA.png   lámina numerada de los dibujos sin etiqueta (para etiquetar)
  st_image.py export                    escribe el texto reconocido en ../shadow-tower-esp-local/image_source.jsonl
  st_image.py report                    cuántas celdas no se reconocen con seguridad

FUENTE: talk (TALKMSG.T, celdas 6×12), equip (EQUIP.T, celdas 10×10) o crt (CRT.T, misma letra que equip).

Cómo reconoce (ver TECH.md):
  - Cada imagen es un TIM de 4 bpp con su propia paleta; el píxel se pasa a brillo y se umbraliza.
  - Grilla de paso fijo; el origen x se elige renglón por renglón (el que deja más bordes de celda vacíos).
  - La columna 0 de cada celda se ignora: ahí caen restos del signo de la celda anterior.
  - Cada dibujo se identifica por su huella (sha1 de los bits). Las etiquetas (huella → letra) están en
    tools/glyph_labels/; los píxeles no se guardan en el repo, se leen del juego.
  - Un dibujo sin etiqueta se asigna a la plantilla etiquetada más parecida (distancia de Hamming);
    si está lejos, sale como {?} para revisarlo.
"""
import collections
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tfile  # noqa: E402
import tim  # noqa: E402

ROOT = os.path.dirname(HERE)
LOCAL = os.path.join(os.path.dirname(ROOT), 'shadow-tower-esp-local')
ORIG = os.path.join(LOCAL, 'files')
LABELS = os.path.join(HERE, 'glyph_labels')

FONTS = {
    # nombre: (archivo, tamaños de imagen aceptados o None, paso x, alto de celda, prefijo de clave)
    'talk': ('ST/COM/TALKMSG.T', None, 6, 12, 'talk'),
    'equip': ('ST/COM/EQUIP.T', {(256, 50), (240, 50)}, 10, 10, 'equip'),
    # CRT.T: cada entrada trae un retrato (TIM 16 bpp) y luego la descripción (TIM 4 bpp 256×50)
    'crt': ('ST/COM/CRT.T', {(256, 50)}, 10, 10, 'crt'),
}
GLYPHS = {'talk': 'talk', 'equip': 'equip', 'crt': 'equip'}  # crt usa la misma letra que equip
THRESHOLDS = (12, 16, 20, 24)  # brillo (0..31) desde el que un píxel es tinta; se elige por imagen
SHIFTS = (0, -1, 1, -2, 2)      # corrimientos verticales que se prueban al comparar con plantillas
MAX_DIST = 6        # distancia de Hamming máxima para asignar un dibujo sin etiqueta
UNKNOWN = '{?}'


def lum(c):
    return max(c & 31, (c >> 5) & 31, (c >> 10) & 31)


def images(font):
    fn, sizes, *_ = FONTS[font]
    for i, a, n, blob in tfile.entries(open(os.path.join(ORIG, fn), 'rb').read()):
        if n <= 0:
            continue
        for t in embedded(blob) if font == 'crt' else [tim.parse(blob)]:
            if not t or t['bpp'] != 4:
                continue
            if sizes and (t['w'], t['h']) not in sizes:
                continue
            yield i, t


def embedded(blob):
    """TIM incrustados en una entrada (cada uno precedido por su tamaño en un u32)."""
    out = []
    for off in range(0, len(blob) - 8, 4):
        if blob[off:off + 4] == b'\x10\x00\x00\x00':
            t = tim.parse(blob, off)
            if t and 0 < t['w'] <= 1024 and 0 < t['h'] <= 512 and off + t['size'] <= len(blob):
                t['offset'] = off
                out.append(t)
    return out


def binarize(t, thr=THRESHOLDS[0]):
    cl = t['clut']['colors']
    return [1 if lum(cl[v]) >= thr else 0 for x in t['pixels'] for v in (x & 15, x >> 4)]


def vgrid(px, W, H, ch):
    """Paso y origen verticales de la imagen: los que dejan más filas de borde vacías (preferencia: ch)."""
    rows = [any(px[y * W + x] for x in range(W)) for y in range(H)]
    ink = [y for y in range(H) if rows[y]]
    if not ink:
        return ch, 0
    y0, y1 = ink[0], ink[-1]
    best = None
    for p in range(ch - 2, ch + 3):
        for oy in range(p):
            b = [y for y in range(oy, y1 + 2, p) if y >= y0 - 2]
            if len(b) < 2:
                continue
            sc = sum(1 for y in b if y < H and not rows[y]) / len(b)
            cand = (sc, -abs(p - ch), -oy, p, oy)
            if best is None or cand > best:
                best = cand
    return (best[3], best[4]) if best else (ch, 0)


def lines(t, font, thr=THRESHOLDS[0]):
    """[(renglón, origen, [celdas])]; cada celda es una tupla de bits (ch filas) con la columna 0 en cero."""
    _, _, pw, ch, _ = FONTS[font]
    W, H = t['w'], t['h']
    px = binarize(t, thr)
    vp, oy = vgrid(px, W, H, ch)
    out = []
    for r, top in enumerate(range(oy, H, vp)):
        rows = [top + y for y in range(min(vp, ch))]
        rows = [y for y in rows if y < H]
        col = [any(px[y * W + x] for y in rows) for x in range(W)]
        if not any(col):
            continue
        best = max(range(pw), key=lambda o: (sum(1 for x in range(o, W, pw) if not col[x]), -o))
        # las celdas arrancan antes del origen si hace falta (con origen 9, la primera celda empieza en x = −1:
        # ahí está la primera letra de los renglones de equipo y criaturas); lo que cae fuera es vacío
        start = best - pw * ((best + pw - 1) // pw)
        cs = []
        for x0 in range(start, W - pw + 1, pw):
            cs.append(tuple(0 if (x == 0 or y >= len(rows) or not 0 <= x0 + x < W) else px[rows[y] * W + x0 + x]
                            for y in range(ch) for x in range(pw)))
        out.append((r, start, cs))
    return out


def shift(cell, dy, pw, ch):
    if dy == 0:
        return cell
    out = [0] * (pw * ch)
    for y in range(ch):
        if 0 <= y + dy < ch:
            out[(y + dy) * pw:(y + dy + 1) * pw] = cell[y * pw:(y + 1) * pw]
    return tuple(out)


def key(cell):
    return hashlib.sha1(bytes(cell)).hexdigest()[:16]


def load_labels(font):
    p = os.path.join(LABELS, f'{GLYPHS.get(font, font)}.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def clusters(font):
    u = collections.Counter()
    for _, t in images(font):
        for _, _, cs in lines(t, font):
            for c in cs:
                if any(c):
                    u[c] += 1
    return u


class Reader:
    def __init__(self, font):
        self.font = font
        self.pw, self.ch = FONTS[font][2], FONTS[font][3]
        self.labels = load_labels(font)
        self.templates = [(c, self.labels[key(c)]) for c in clusters(font)
                          if self.labels.get(key(c)) not in (None, UNKNOWN)]
        self.stats = collections.Counter()

    def classify(self, cell):
        """(carácter, tipo): tipo = vacío | etiqueta | parecido | dudoso."""
        if not any(cell):
            return ' ', 'vacío'
        lab = self.labels.get(key(cell))
        if lab is not None and lab != UNKNOWN:
            return lab, 'etiqueta'
        if lab == UNKNOWN:
            return UNKNOWN, 'dudoso'
        best = None
        for dy in SHIFTS:
            c = shift(cell, dy, self.pw, self.ch)
            for tc, ch in self.templates:
                d = sum(a != b for a, b in zip(tc, c))
                if best is None or d < best[0]:
                    best = (d, ch)
        if best and best[0] <= MAX_DIST:
            return best[1], 'parecido'
        return UNKNOWN, 'dudoso'

    def read(self, t):
        """Lee la imagen con el umbral que deja menos dudas."""
        best = None
        for thr in THRESHOLDS:
            kinds = collections.Counter()
            text = []
            for _, _, cs in lines(t, self.font, thr):
                row = []
                for c in cs:
                    ch, k = self.classify(c)
                    kinds[k] += 1
                    row.append(ch)
                text.append(''.join(row).rstrip())
            score = (kinds['dudoso'], -kinds['etiqueta'])
            if best is None or score < best[0]:
                best = (score, text, kinds)
            if kinds['dudoso'] == 0 and kinds['parecido'] == 0:
                break
        self.stats.update({k: v for k, v in best[2].items() if k != 'vacío'})
        return best[1]


STAT_LINE = re.compile(r"^[A-Z][A-Z .'-]* [0-9][0-9'\"%+.-]*$")


def join(a, b):
    return a + b if a.endswith('-') else a + ' ' + b


def layout(font, lines_):
    """Renglones visuales → texto para traducir.

    talk: un párrafo (el dibujador vuelve a cortar los renglones).
    equip: la prosa en un párrafo; cada línea de datos («LENGTH 3'9"», «CRITICAL 5») en su renglón.
    """
    ls = [l.strip() for l in lines_ if l.strip()]
    if not ls:
        return ''
    if font == 'talk':
        out = ls[0]
        for l in ls[1:]:
            out = join(out, l)
        return out
    out = [ls[0]]
    for l in ls[1:]:
        prev = out[-1]
        if not prev.endswith('.') and not STAT_LINE.match(prev) and not STAT_LINE.match(l):
            out[-1] = join(prev, l)
        else:
            out.append(l)
    return '\n'.join(out)


def export():
    rows = []
    for font in FONTS:
        rd = Reader(font)
        prefix = FONTS[font][4]
        for i, t in images(font):
            text = rd.read(t)
            if not any(text):
                continue
            rows.append({'key': f'{prefix}#{i:04d}', 'en': layout(font, text),
                         'note': f'{os.path.basename(FONTS[font][0])} entrada {i}, imagen {t["w"]}×{t["h"]}'})
        print(font, dict(rd.stats))
    import st_intro
    rows += st_intro.source_rows()
    # quién habla en cada caja (el juego no lo dice; lo dedujo el perfilador, ver characters/)
    hp = os.path.join(ROOT, 'characters', 'hablantes.json')
    if os.path.exists(hp):
        who = json.load(open(hp, encoding='utf-8'))
        for r in rows:
            if r['key'] in who:
                r['speaker'] = who[r['key']]
    p = os.path.join(LOCAL, 'image_source.jsonl')
    with open(p, 'w', encoding='utf-8') as w:
        for r in rows:
            w.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'{len(rows)} textos en {p}')


def sheet(font, out, only_unlabeled=True):
    from PIL import Image, ImageDraw
    _, _, pw, ch, _ = FONTS[font]
    labels = load_labels(font)
    u = clusters(font)
    sel = [(c, n) for c, n in u.most_common() if not (only_unlabeled and key(c) in labels)]
    S, cols = 5, 10
    cw, chh = pw * S + 40, ch * S + 8
    img = Image.new('RGB', (cols * cw, max(1, (len(sel) + cols - 1) // cols) * chh), (40, 40, 90))
    dr = ImageDraw.Draw(img)
    for k, (c, n) in enumerate(sel):
        g = Image.new('L', (pw, ch))
        g.putdata([255 if p else 0 for p in c])
        x, y = (k % cols) * cw, (k // cols) * chh
        dr.text((x + 2, y + 2), str(k), fill=(255, 255, 0))
        img.paste(g.resize((pw * S, ch * S), Image.NEAREST).convert('RGB'), (x + 34, y + 4))
    img.save(out)
    with open(out + '.keys.json', 'w') as w:
        json.dump([key(c) for c, _ in sel], w)
    print(f'{len(sel)} dibujos en {out} (huellas en {out}.keys.json)')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'clusters':
        labels = load_labels(sys.argv[2])
        for c, n in clusters(sys.argv[2]).most_common():
            print(key(c), n, labels.get(key(c), ''))
    elif cmd == 'sheet':
        sheet(sys.argv[2], sys.argv[3], '--all' not in sys.argv)
    elif cmd == 'export':
        export()
    elif cmd == 'report':
        for f in FONTS:
            rd = Reader(f)
            for _, t in images(f):
                rd.read(t)
            print(f, dict(rd.stats))
    else:
        sys.exit(__doc__)
