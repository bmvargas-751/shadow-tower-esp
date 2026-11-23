#!/usr/bin/env python3
"""Tablas de posición de los ejecutables: las x de algunos menús están precalculadas con el largo del inglés.

Uso (desde la raíz del proyecto):
  st_exe.py show        muestra cada tabla: valores originales y los que salen de la traducción
  st_exe.py import      escribe los ejecutables parcheados en ../local/shadow-tower/build/files/
  st_exe.py roundtrip   import con el inglés: los ejecutables tienen que salir idénticos

El juego no mide el texto que dibuja: cada pantalla copia una tabla fija de x (16 bits por opción) y suma una
constante (TECH.md, «Prueba 0.9.0 en el juego»). Cada tabla se busca por su contenido original en cada ejecutable
(puede haber copias, p. ej. en VS.EXE) y se recalcula con el largo del español:
  center  centra con el largo nuevo (mismo centro que el original; 3,5 px por letra en la fuente A)
  left    alinea a la izquierda: todas en la x donde quedaría centrada la opción más larga
  right   alinea a la derecha (ancho = 11 px por letra + 3, fuente B)
"""
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import st_text  # noqa: E402

LOCAL = st_text.LOCAL
ORIG = os.path.join(LOCAL, 'files')
OUT = st_text.OUT
EXES = ['ST.EXE', 'VS.EXE']
CODE = re.compile(r'\{[^{}]*\}')


def keys(prefix, first, n):
    return [f'{prefix}#{i:04d}' for i in range(first, first + n)]


# (nombre, claves en el orden de la tabla, modo, valores originales)
TABLES = [
    ('menú principal', keys('stat/00', 11, 8), 'left', (37, 47, 20, 20, 30, 41, 34, 37)),
    ('OPTIONS', keys('stat/00', 201, 6), 'left', (15, 12, 12, 19, 19, 5)),
    ('BUTTON CONFIGURATION, izquierda', keys('stat/00', 209, 6), 'center', (26, 36, 20, 16, 20, 16)),
    ('BUTTON CONFIGURATION, derecha', keys('stat/00', 215, 6), 'center', (27, 20, 17, 20, 34, 16)),
    ('BUTTON CONFIGURATION, abajo', keys('stat/00', 221, 2), 'center', (10, 37)),
    ('tipo de criatura (ficha)', keys('stat/01', 150, 16), 'right',
     (113, 58, 36, 36, 58, 135, 168, 157, 69, 168, 80, 0, 58, 0, 69, 113)),
]
HALF = 3.5   # media letra de la fuente A (7 px)
STEP_B = 11  # avance de la fuente B

# Confirmación de la tienda (rutina 0x8002dd70 de ST.EXE): «BUY/REPAIR/TRADE   CANCEL» en y = 208, con un
# recuadro de selección de 50×16 en x = 105 (la opción) o 167 (CANCEL), y = 206. Las x no salen de una tabla
# sino de instrucciones «addiu reg,zero,X»: se cambia el inmediato. (dirección, valor original)
SHOP_OPTIONS = [('stat/00#0105', 0x8002de04, 120), ('stat/00#0106', 0x8002de70, 110),
                ('stat/00#0107', 0x8002de90, 113)]
SHOP_CANCEL = ('stat/00#0108', 0x8002dee4, 172)
SHOP_BOX_X = [(0x8002ddac, 105), (0x8002ddb0, 167)]  # recuadro: opción, CANCEL
SHOP_BOX_W = (0x8002ddd0, 50)
SHOP_MID = 161   # centro entre los dos recuadros (105 + (50 + 12 + 50) / 2)
SHOP_GAP = 12    # separación original entre los recuadros
STEP_A = 7       # avance de la fuente A; un texto de n letras mide 7n − 1 px


def shop_values(en, es):
    """{dirección: (valor original, valor nuevo)} de la confirmación de la tienda.

    El recuadro se ensancha para la palabra más larga (con 2 px de aire por lado, nunca menos de los 50 del
    original) y los dos quedan centrados en el mismo punto que en el original; cada texto, centrado en su
    recuadro. Con el inglés da exactamente los valores originales.
    """
    lens = {k: visible_len(es.get(k, en[k])) for k, _, _ in SHOP_OPTIONS + [SHOP_CANCEL]}
    w = max(SHOP_BOX_W[1], STEP_A * max(lens.values()) + 4)
    gap = max(4, SHOP_GAP - (w - SHOP_BOX_W[1]))
    left = round_half_up(SHOP_MID - (2 * w + gap) / 2)
    right = left + w + gap
    out = {SHOP_BOX_W[0]: (SHOP_BOX_W[1], w),
           SHOP_BOX_X[0][0]: (SHOP_BOX_X[0][1], left), SHOP_BOX_X[1][0]: (SHOP_BOX_X[1][1], right)}
    for (k, addr, v), box in [(o, left) for o in SHOP_OPTIONS] + [(SHOP_CANCEL, right)]:
        out[addr] = (v, round_half_up(box + w / 2 - (STEP_A * lens[k] - 1) / 2))
    return out


def exe_base(data):
    return struct.unpack_from('<I', data, 0x18)[0] - 0x800


def patch_imm(data, addr, old, new):
    """Cambia el inmediato de «addiu reg,zero,old» en addr; False si la instrucción no está ahí."""
    off = addr - exe_base(data)
    if not 0 <= off <= len(data) - 4:
        return False
    w = struct.unpack_from('<I', data, off)[0]
    if w >> 21 != 0x09 << 5 or w & 0xffff != old:  # addiu con rs = zero
        return False
    struct.pack_into('<I', data, off, (w & 0xffff0000) | (new & 0xffff))
    return True


def visible_len(text):
    return len(CODE.sub('x', text.split('\n')[0]).rstrip(' '))


def round_half_up(x):
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)


def new_values(table, en, es):
    _name, ks, mode, orig = table
    if all(es.get(k, en[k]) == en[k] for k in ks):
        return tuple(orig)  # sin traducir: la tabla queda como en el original
    out = []
    for k, v in zip(ks, orig):
        if v == 0 and mode == 'right':  # casillas sin uso (BUG DESU)
            out.append(0)
            continue
        le, ls = visible_len(en[k]), visible_len(es.get(k, en[k]))
        if mode == 'right':
            out.append(v + STEP_B * (ls - le))
        else:
            out.append(round_half_up(v + HALF * le - HALF * ls))
    if mode == 'left':
        out = [max(0, min(out))] * len(out)
    if mode == 'center':
        out = [max(0, x) for x in out]
    return tuple(out)


def patch(data, en, es, log=None):
    data = bytearray(data)
    for table in TABLES:
        name, _ks, _mode, orig = table
        old = struct.pack(f'<{len(orig)}h', *orig)
        new = struct.pack(f'<{len(orig)}h', *new_values(table, en, es))
        hits = [m.start() for m in re.finditer(re.escape(old), bytes(data))]
        for off in hits:
            data[off:off + len(old)] = new
        if log is not None:
            log.append((name, len(hits)))
    if data[:8] == b'PS-X EXE':
        vals = shop_values(en, es)
        ok = [patch_imm(data, a, *on) for a, on in vals.items()]
        if any(ok):
            assert all(ok), 'confirmación de la tienda: faltan instrucciones'
        if log is not None:
            log.append(('confirmación de la tienda', int(all(ok))))
    return bytes(data)


def import_(use_en=False):
    en = st_text.load_translation(True)
    es = en if use_en else st_text.load_translation(False)
    for exe in EXES:
        log = []
        data = patch(open(os.path.join(ORIG, exe), 'rb').read(), en, es, log)
        p = os.path.join(OUT, exe)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data)
        found = ', '.join(f'{n} ×{c}' for n, c in log if c)
        print(f'{exe}: {found or "ninguna tabla"}')


def check_found():
    """Cada tabla tiene que estar al menos una vez en ST.EXE."""
    data = open(os.path.join(ORIG, 'ST.EXE'), 'rb').read()
    for name, _ks, _mode, orig in TABLES:
        assert struct.pack(f'<{len(orig)}h', *orig) in data, f'{name}: no está en ST.EXE'
    probe = bytearray(data)
    for addr, old in [(a, v) for _, a, v in SHOP_OPTIONS + [SHOP_CANCEL]] + SHOP_BOX_X + [SHOP_BOX_W]:
        assert patch_imm(probe, addr, old, old), f'confirmación de la tienda: 0x{addr:08x} no está en ST.EXE'


def show():
    en = st_text.load_translation(True)
    es = st_text.load_translation(False)
    for table in TABLES:
        print(f'{table[0]} ({table[2]}):')
        print('  original', table[3])
        print('  español ', new_values(table, en, es))
    vals = shop_values(en, es)
    names = {a: k for k, a, _ in SHOP_OPTIONS + [SHOP_CANCEL]}
    names.update({SHOP_BOX_X[0][0]: 'recuadro, x opción', SHOP_BOX_X[1][0]: 'recuadro, x CANCEL',
                  SHOP_BOX_W[0]: 'recuadro, ancho'})
    print('confirmación de la tienda:')
    for a, (o, n) in vals.items():
        print(f'  {names[a]:20} {o:4} → {n}')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    check_found()
    if cmd == 'show':
        show()
    elif cmd == 'import':
        import_()
    elif cmd == 'roundtrip':
        import_(use_en=True)
        same = all(open(os.path.join(ORIG, e), 'rb').read() == open(os.path.join(OUT, e), 'rb').read() for e in EXES)
        print('ida y vuelta:', 'idéntica' if same else 'DISTINTA')
        sys.exit(0 if same else 1)
    else:
        print(__doc__)
