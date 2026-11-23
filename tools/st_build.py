#!/usr/bin/env python3
"""Imagen completa con la traducción (fase 7) para DuckStation.

Uso (desde la raíz del proyecto):
  st_build.py [NOMBRE]   → ../local/shadow-tower/test/NOMBRE.{bin,cue} (por defecto shadow-tower-esp)

Pasos:
  1. Reconstruye los 9 archivos con translation/ (st_text: texto codificado; st_exe: tablas de posición de los
     menús en ST.EXE; st_render: diálogos y descripciones; st_intro: introducción) en
     ../local/shadow-tower/build/files.
  2. Copia original.bin y reemplaza esos archivos (psxpatch recalcula EDC/ECC).
  3. Comprueba que lo que quedó en la imagen es lo que se escribió.
No toca original.bin ni translation/.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import psxpatch  # noqa: E402
import st_exe  # noqa: E402
import st_intro  # noqa: E402
import st_render  # noqa: E402
import st_text  # noqa: E402

LOCAL = st_text.LOCAL
TEST = os.path.join(LOCAL, 'test')


def rebuild():
    st_text.import_()
    st_exe.import_()
    ok = st_render.import_()
    ok = st_intro.import_() and ok
    if not ok:
        sys.exit('hay errores al redibujar; no se arma la imagen')
    files = list(st_text.FILES) + sorted({v[1] for v in st_render.all_images().values()})
    files.append(os.path.relpath(st_intro.OUT, st_text.OUT))
    files.append('ST.EXE')  # tablas de posición de los menús (st_exe)
    return {f: os.path.join(st_text.OUT, f) for f in files}


def main():
    build(sys.argv[1] if len(sys.argv) > 1 else 'shadow-tower-esp')


def build(name):
    """Arma TEST/NAME.{bin,cue} con la traducción y devuelve la ruta del .bin."""
    files = rebuild()
    os.makedirs(TEST, exist_ok=True)
    img = os.path.join(TEST, name + '.bin')
    shutil.copyfile(os.path.join(LOCAL, 'original.bin'), img)
    for iso_path, src in files.items():
        psxpatch.put(img, iso_path, src)
    with open(os.path.join(TEST, name + '.cue'), 'w') as w:
        w.write(f'FILE "{name}.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    with open(img, 'rb') as f:
        seen = set()
        for p, lba, sz in psxpatch.psxiso.walk(f):
            if p in files:
                assert psxpatch.psxiso.read_extent(f, lba, sz) == open(files[p], 'rb').read(), p
                seen.add(p)
    assert seen == set(files), sorted(set(files) - seen)
    print(f'{len(files)} archivos en la imagen: {img}')
    return img


if __name__ == '__main__':
    main()
