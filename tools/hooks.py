"""Hooks del kit para Shadow Tower (ver loc.json y lockit/checks.py del kit)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import st_text  # noqa: E402

CODE = re.compile(r'\{[^{}]*\}')


def _font(key):
    prefix = key.rsplit('#', 1)[0]
    for p, _files, _e, _base, font, _copies in st_text.BLOCKS:
        if p == prefix:
            return font
    return None


def missing_chars(key, es):
    """Caracteres de la traducción que la fuente de ese texto no tiene (T-5)."""
    font = _font(key)
    if font is None:
        return []
    have = st_text.encmap(font)
    seen = []
    for c in CODE.sub('', es).replace('\n', ''):
        if c not in have and c not in seen:
            seen.append(c)
    return seen
