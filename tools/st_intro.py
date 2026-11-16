#!/usr/bin/env python3
"""Introducción de Shadow Tower (ST/OPTXT/OPTXT.MIC): 6 pantallas de texto con letra de máquina de escribir.

Uso (desde la raíz del proyecto):
  st_intro.py rows                       muestra cuántas pantallas y renglones hay (sin el texto)
  st_intro.py preview N "texto" OUT.png  dibuja un texto en la pantalla N
  st_intro.py import [--en]              de translation/ a ../shadow-tower-esp-local/build/files/
  st_intro.py roundtrip                  import --en y compara byte por byte

Formato de OPTXT.MIC: bloques [u32 tamaño][TIM] desde el byte 0; los 6 primeros TIM son las pantallas
de texto (4 bpp 256×240) y el séptimo, el fondo (16 bpp 320×240, sin texto).

El inglés se transcribió a mano (6 pantallas, 11 renglones) en ../shadow-tower-esp-local/optxt_transcript.json.
El español se dibuja con Special Elite (tools/fonts/, licencia Apache 2.0) en celdas fijas de 9 px, como una
máquina de escribir, cada renglón centrado y a la altura de los renglones del original. Una pantalla cuyo texto
no cambió conserva su imagen original.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tim  # noqa: E402

ROOT = os.path.dirname(HERE)
LOCAL = os.path.join(os.path.dirname(ROOT), 'shadow-tower-esp-local')
MIC = 'ST/OPTXT/OPTXT.MIC'
ORIG = os.path.join(LOCAL, 'files', MIC)
OUT = os.path.join(LOCAL, 'build', 'files', MIC)
TRANSCRIPT = os.path.join(LOCAL, 'optxt_transcript.json')
FONT = os.path.join(HERE, 'fonts', 'SpecialElite-Regular.ttf')
FONT_SIZE = 14
PITCH = 9          # paso de la máquina de escribir (px)
LINE_STEP = 17     # distancia entre renglones en el original
MAX_COLS = 256 // PITCH  # 28 caracteres = 252 px
MAX_ROWS = 3
NSCREENS = 6
PREFIX = 'intro'
# Letras que se pueden escribir (Special Elite las tiene todas)
CHARSET = set(chr(c) for c in range(0x20, 0x7F)) | set('áéíóúüñÁÉÍÓÚÜÑ¿¡«»—…')


def screens(data):
    """[(desplazamiento del TIM, TIM)] de las pantallas de texto."""
    out = []
    off = 0
    while off < len(data) and len(out) < NSCREENS:
        size = int.from_bytes(data[off:off + 4], 'little')
        t = tim.parse(data, off + 4) if size else None
        if not t:
            break
        out.append((off + 4, t))
        off += 4 + size
    return out


def lum(c):
    return max(c & 31, (c >> 5) & 31, (c >> 10) & 31)


def text_rows(t):
    """Filas (y0, y1) de los renglones del original y el índice de fondo."""
    idx = [v for x in t['pixels'] for v in (x & 15, x >> 4)]
    bg = collections.Counter(idx).most_common(1)[0][0]
    W = t['w']
    ys = sorted({i // W for i, v in enumerate(idx) if v != bg})
    bands = []
    for y in ys:
        if bands and y <= bands[-1][1] + 2:
            bands[-1][1] = y
        else:
            bands.append([y, y])
    return bands, bg


def source_rows():
    tr = json.load(open(TRANSCRIPT, encoding='utf-8'))
    return [{'key': f'{PREFIX}#{i}', 'en': '\n'.join(lines),
             'note': f'Introducción, pantalla {i + 1} de {len(tr)}; texto sobre fondo negro, renglones centrados'}
            for i, lines in enumerate(tr)]


def layout(text, t):
    lines = text.split('\n')
    if len(lines) > MAX_ROWS:
        raise ValueError(f'{len(lines)} renglones, el máximo es {MAX_ROWS}')
    for l in lines:
        if len(l) > MAX_COLS:
            raise ValueError(f'renglón de {len(l)} caracteres, el máximo es {MAX_COLS}')
    bands, _ = text_rows(t)
    # misma altura que el original: centrado vertical alrededor del centro de los renglones originales
    center = (bands[0][0] + bands[-1][1]) / 2 if bands else t['h'] / 2
    total = (len(lines) - 1) * LINE_STEP
    tops = [round(center - total / 2 + r * LINE_STEP - 7) for r in range(len(lines))]
    return list(zip(tops, lines))


def render(t, text):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(FONT, FONT_SIZE)
    W, H = t['w'], t['h']
    g = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(g)
    for top, line in layout(text, t):
        x0 = (W - len(line) * PITCH) // 2
        for k, ch in enumerate(line):
            if ch not in CHARSET:
                raise ValueError(f'la letra no tiene «{ch}»')
            w = font.getlength(ch)
            dr.text((x0 + k * PITCH + (PITCH - w) / 2, top), ch, font=font, fill=255)
    cl = t['clut']['colors']
    _, bg = text_rows(t)
    levels = sorted((lum(c), i) for i, c in enumerate(cl))
    lv = [(l / 31, i) for l, i in levels]

    def index_for(v):
        if v < 0.06:
            return bg
        return min(lv, key=lambda p: abs(p[0] - v))[1]
    idx = [index_for(v / 255) for v in g.getdata()]
    return bytes(idx[i] | (idx[i + 1] << 4) for i in range(0, len(idx), 2))


def translations(use_en):
    if use_en:
        return {r['key']: r['en'] for r in source_rows()}
    out = {}
    tdir = os.path.join(ROOT, 'translation')
    for dp, _, fs in os.walk(tdir):
        for f in fs:
            if f.endswith('.jsonl'):
                for line in open(os.path.join(dp, f), encoding='utf-8'):
                    if line.strip():
                        x = json.loads(line)
                        if x['key'].startswith(PREFIX + '#'):
                            out[x['key']] = x['es']
    return out


def import_(use_en=False):
    data = bytearray(open(ORIG, 'rb').read())
    src = {r['key']: r['en'] for r in source_rows()}
    tr = translations(use_en)
    changed, errors = 0, []
    for i, (off, t) in enumerate(screens(bytes(data))):
        key = f'{PREFIX}#{i}'
        if key not in tr or tr[key] == src.get(key):
            continue
        try:
            pix = render(t, tr[key])
        except ValueError as e:
            errors.append(f'{key}: {e}')
            continue
        data[t['pix_off']:t['pix_off'] + len(pix)] = pix
        changed += 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'wb').write(data)
    for e in errors:
        print('ERROR', e)
    print(f'introducción: {changed} pantallas redibujadas, {len(errors)} errores')
    return not errors


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'rows':
        for r in source_rows():
            print(r['key'], r['en'].count('\n') + 1, 'renglones')
    elif cmd == 'preview':
        from PIL import Image
        n, text, out = int(sys.argv[2]), sys.argv[3], sys.argv[4]
        off, t = screens(open(ORIG, 'rb').read())[n]
        t = dict(t)
        t['pixels'] = render(t, text)
        tim.to_image(t).resize((t['w'] * 2, t['h'] * 2), Image.NEAREST).save(out)
        print(out)
    elif cmd == 'import':
        sys.exit(0 if import_('--en' in sys.argv) else 1)
    elif cmd == 'roundtrip':
        assert len(screens(open(ORIG, 'rb').read())) == NSCREENS, 'no se encontraron las 6 pantallas'
        ok = import_(True) and open(ORIG, 'rb').read() == open(OUT, 'rb').read()
        print(f'{MIC}: {"idéntico" if ok else "DISTINTO"}')
        sys.exit(0 if ok else 1)
    else:
        sys.exit(__doc__)
