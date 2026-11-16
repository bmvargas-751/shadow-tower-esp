#!/usr/bin/env python3
"""Reemplaza archivos dentro de una imagen de PS1 MODE2/2352 y recalcula EDC/ECC.

Uso:
  psxpatch.py verify IMAGEN.bin [N]               recalcula EDC/ECC de N sectores Form 1 (o hasta el final) y compara
  psxpatch.py put IMAGEN.bin RUTA_EN_ISO ARCHIVO  escribe ARCHIVO en el lugar de RUTA_EN_ISO

`put` modifica IMAGEN.bin en el lugar: se usa sobre una copia, nunca sobre el original.
El archivo nuevo tiene que tener el mismo tamaño que el original (no se toca el directorio).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psxiso  # noqa: E402

SECTOR = 2352

# --- EDC (CRC-32 de CD-ROM, polinomio 0xD8018001 reflejado) ---
EDC_TABLE = []
for i in range(256):
    e = i
    for _ in range(8):
        e = (e >> 1) ^ (0xD8018001 if e & 1 else 0)
    EDC_TABLE.append(e)


def edc(data):
    e = 0
    for b in data:
        e = (e >> 8) ^ EDC_TABLE[(e ^ b) & 0xFF]
    return e


# --- ECC (Reed-Solomon P y Q en GF(2^8)) ---
ECC_F = [0] * 256
ECC_B = [0] * 256
for i in range(256):
    j = (i << 1) ^ (0x11D if i & 0x80 else 0)
    ECC_F[i] = j
    ECC_B[i ^ j] = i


def ecc_block(sec, major_count, minor_count, major_mult, minor_inc, dest):
    size = major_count * minor_count
    for major in range(major_count):
        index = (major >> 1) * major_mult + (major & 1)
        a = b = 0
        for _ in range(minor_count):
            t = sec[0xC + index]
            index += minor_inc
            if index >= size:
                index -= size
            a ^= t
            b ^= t
            a = ECC_F[a]
        a = ECC_B[ECC_F[a] ^ b]
        sec[dest + major] = a
        sec[dest + major + major_count] = a ^ b


def fix_form1(sec):
    """sec: bytearray de 2352 bytes de un sector Mode 2 Form 1. Recalcula EDC y ECC."""
    e = edc(sec[0x10:0x818])
    sec[0x818:0x81C] = e.to_bytes(4, 'little')
    hdr = bytes(sec[0xC:0x10])
    sec[0xC:0x10] = b'\0\0\0\0'  # en Mode 2 el ECC se calcula con la cabecera en cero
    ecc_block(sec, 86, 24, 2, 86, 0x81C)   # P
    ecc_block(sec, 52, 43, 86, 88, 0x8C8)  # Q
    sec[0xC:0x10] = hdr


def is_form1(sec):
    return sec[0xF] == 2 and not (sec[0x12] & 0x20)


def verify(img, n):
    ok = bad = 0
    with open(img, 'rb') as f:
        for lba in range(16, 16 + n):
            f.seek(lba * SECTOR)
            orig = f.read(SECTOR)
            if len(orig) < SECTOR:
                break
            if not is_form1(orig):
                continue
            s = bytearray(orig)
            fix_form1(s)
            if bytes(s) == orig:
                ok += 1
            else:
                bad += 1
    print(f'Form 1 idénticos: {ok}, distintos: {bad}')
    return bad == 0


def put(img, iso_path, src):
    data = open(src, 'rb').read()
    with open(img, 'r+b') as f:
        files = {p: (lba, sz) for p, lba, sz in psxiso.walk(f)}
        if iso_path not in files:
            sys.exit(f'No está en la imagen: {iso_path}')
        lba, sz = files[iso_path]
        if len(data) != sz:
            sys.exit(f'Tamaño distinto: {len(data)} != {sz}')
        changed = 0
        for i in range((sz + 2047) // 2048):
            f.seek((lba + i) * SECTOR)
            s = bytearray(f.read(SECTOR))
            assert is_form1(s), f'sector {lba + i} no es Form 1'
            chunk = data[i * 2048:(i + 1) * 2048].ljust(2048, b'\0')
            if bytes(s[0x18:0x818]) == chunk:
                continue
            s[0x18:0x818] = chunk
            fix_form1(s)
            f.seek((lba + i) * SECTOR)
            f.write(s)
            changed += 1
    print(f'{iso_path}: {changed} sectores reescritos')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'verify':
        sys.exit(0 if verify(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2000) else 1)
    elif cmd == 'put':
        put(sys.argv[2], sys.argv[3], sys.argv[4])
