"""Hooks del kit para Shadow Tower (ver loc.json y lockit/checks.py del kit)."""
import functools
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import st_text  # noqa: E402

CODE = re.compile(r'\{[^{}]*\}')
IMAGE_FONTS = {'talk': 'talk', 'equip': 'equip', 'crt': 'crt'}


def _prefix(key):
    return key.rsplit('#', 1)[0]


def _text_font(key):
    for p, _files, _e, _base, font, _copies in st_text.BLOCKS:
        if p == _prefix(key):
            return font
    return None


@functools.lru_cache(maxsize=None)
def _image_glyphs(font):
    import st_render
    return set(st_render.load_glyphs(font)['glyphs'])


@functools.lru_cache(maxsize=1)
def _images():
    import st_render
    return st_render.all_images()


def missing_chars(key, es):
    """Caracteres de la traducción que la fuente de ese texto no tiene (T-5)."""
    if _prefix(key) == 'intro':
        import st_intro
        have = st_intro.CHARSET
    elif _prefix(key) in IMAGE_FONTS:
        have = _image_glyphs(IMAGE_FONTS[_prefix(key)])
    else:
        font = _text_font(key)
        if font is None:
            return []
        have = set(st_text.encmap(font))
    seen = []
    for c in CODE.sub('', es).replace('\n', ''):
        if c not in have and c not in seen:
            seen.append(c)
    return seen


# Anchos medidos en el juego (prueba 0.9.0, 2026-11-17): (prefijos, casillas, máximo de caracteres por renglón).
# Un código {XXXX} cuenta como una letra.
WIDTHS = [
    (('stat/03', 'stat/04'), range(0, 640), 25, 'nombre de objeto (lista ITEM y panel del objeto)'),
    (('stat/03', 'stat/04'), range(640, 1100), 37, 'descripción de USE ITEM'),
    (('stat/00',), range(900, 915), 8, 'etiqueta de la pantalla EQUIP (el objeto empieza en la columna 9)'),
    (('stat/00',), range(915, 916), 10, 'cabecera de peso de la pantalla EQUIP'),
    (('stat/00',), range(209, 215), 12, 'botón, columna izquierda de BUTTON CONFIGURATION'),
    (('stat/00',), range(215, 221), 11, 'botón, columna derecha de BUTTON CONFIGURATION'),
]


def _width_check(key, es):
    prefix, n = _prefix(key), int(key.rsplit('#', 1)[1])
    for prefixes, slots, limit, what in WIDTHS:
        if prefix in prefixes and n in slots:
            longest = max(len(CODE.sub('x', line)) for line in es.split('\n'))
            if longest > limit:
                return [('ancho', 'T-3', f'{what}: {longest} caracteres, el máximo es {limit}')]
    return []


def check(key, item, es):
    """Ancho de los textos con límite medido (T-3) y texto en imágenes: que entre en la caja (renglones y ancho)."""
    found = _width_check(key, es)
    if found:
        return found
    if _prefix(key) == 'intro' and not missing_chars(key, es):
        import st_intro
        try:
            n = int(key.rsplit('#', 1)[1])
            st_intro.layout(es, st_intro.screens(open(st_intro.ORIG, 'rb').read())[n][1])
        except ValueError as e:
            return [('caja', 'T-3', str(e))]
        return []
    if _prefix(key) not in IMAGE_FONTS or missing_chars(key, es):
        return []
    import st_render
    font, _fn, _i, _sector, t = _images()[key]
    try:
        st_render.layout(font, t, es)
    except ValueError as e:
        return [('caja', 'T-3', str(e))]
    return []
