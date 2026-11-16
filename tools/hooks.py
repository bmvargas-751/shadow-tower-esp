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
    if _prefix(key) in IMAGE_FONTS:
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


def check(key, item, es):
    """Texto en imágenes: que entre en la caja (renglones y ancho, T-3)."""
    if _prefix(key) not in IMAGE_FONTS or missing_chars(key, es):
        return []
    import st_render
    font, _fn, _i, _sector, t = _images()[key]
    try:
        st_render.layout(font, t, es)
    except ValueError as e:
        return [('caja', 'T-3', str(e))]
    return []
