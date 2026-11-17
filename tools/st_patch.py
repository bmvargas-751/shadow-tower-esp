#!/usr/bin/env python3
"""Parche xdelta de la traducción (fase 8) y su paquete de entrega.

Uso (desde la raíz del proyecto):
  st_patch.py [VERSIÓN]   → ../shadow-tower-esp-local/dist/shadow-tower-esp-VERSIÓN.zip
                            (la versión, por defecto, es la primera de CHANGELOG.md)

Pasos:
  1. Comprueba que original.bin es la imagen USA esperada (SHA-1).
  2. Arma la imagen traducida con st_build.
  3. Crea el parche con xdelta3 y lo aplica de vuelta sobre original.bin para comprobar que da la misma imagen.
  4. Arma la carpeta y el .zip: parche, .cue, LEEME.txt (de tools/release/) y CHANGELOG.md.

xdelta3 se busca en $XDELTA3 o en el PATH. El paquete no lleva nada del juego: solo el parche.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import st_build  # noqa: E402

LOCAL = st_build.LOCAL
ORIGINAL = os.path.join(LOCAL, 'original.bin')
DIST = os.path.join(LOCAL, 'dist')
ORIGINAL_SHA1 = 'df441bf08b7079f8b3d36f1188f7eedd8cb73c50'
TEMPLATE = os.path.join(HERE, 'release', 'LEEME.txt')
CHANGELOG = os.path.join(ROOT, 'CHANGELOG.md')


def hashes(path):
    sha1, md5, crc = hashlib.sha1(), hashlib.md5(), 0
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            sha1.update(block)
            md5.update(block)
            crc = zlib.crc32(block, crc)
    return {'sha1': sha1.hexdigest(), 'md5': md5.hexdigest(), 'crc32': f'{crc:08x}'}


def xdelta3():
    exe = os.environ.get('XDELTA3') or shutil.which('xdelta3')
    if not exe:
        sys.exit('falta xdelta3 (sudo apt install xdelta3, o XDELTA3=/ruta/al/xdelta3)')
    return exe


def changelog_version():
    for line in open(CHANGELOG, encoding='utf-8'):
        m = re.match(r'## \[?([0-9][^\]\s]*)', line)
        if m:
            return m.group(1)
    sys.exit('CHANGELOG.md no tiene ninguna versión («## 1.0 …»)')


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else changelog_version()
    exe = xdelta3()
    orig = hashes(ORIGINAL)
    if orig['sha1'] != ORIGINAL_SHA1:
        sys.exit(f'original.bin no es la imagen USA esperada (SHA-1 {orig["sha1"]})')

    name = f'shadow-tower-esp-{version}'
    img = st_build.build(name)
    out = os.path.join(DIST, name)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    patch = os.path.join(out, name + '.xdelta')
    subprocess.run([exe, '-e', '-9', '-S', 'none', '-f', '-s', ORIGINAL, img, patch], check=True)

    # comprobación: el parche aplicado sobre el original da la misma imagen
    check = os.path.join(DIST, name + '.check.bin')
    subprocess.run([exe, '-d', '-f', '-s', ORIGINAL, patch, check], check=True)
    new = hashes(img)
    got = hashes(check)
    os.remove(check)
    assert got == new, 'el parche aplicado no da la imagen armada'

    with open(os.path.join(out, name + '.cue'), 'w', newline='\r\n') as w:
        w.write(f'FILE "{name}.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    leeme = open(TEMPLATE, encoding='utf-8').read()
    for k, v in {'VERSION': version, 'NAME': name,
                 'ORIG_SHA1': orig['sha1'], 'ORIG_MD5': orig['md5'], 'ORIG_CRC32': orig['crc32'],
                 'NEW_SHA1': new['sha1'], 'NEW_MD5': new['md5'], 'NEW_CRC32': new['crc32']}.items():
        leeme = leeme.replace('{' + k + '}', v)
    assert '{' not in leeme, 'LEEME.txt tiene un marcador sin reemplazar'
    with open(os.path.join(out, 'LEEME.txt'), 'w', encoding='utf-8', newline='\r\n') as w:
        w.write(leeme)
    shutil.copyfile(CHANGELOG, os.path.join(out, 'CHANGELOG.md'))

    zpath = os.path.join(DIST, name + '.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(out)):
            z.write(os.path.join(out, fn), f'{name}/{fn}')
    os.remove(img)
    os.remove(os.path.splitext(img)[0] + '.cue')
    print(f'parche: {os.path.getsize(patch):,} bytes; imagen traducida SHA-1 {new["sha1"]}')
    print(f'paquete: {zpath}')


if __name__ == '__main__':
    main()
