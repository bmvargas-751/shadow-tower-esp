#!/usr/bin/env python3
"""Desensamblador MIPS R3000 mínimo para ejecutables PS-X EXE (solo para análisis)."""
import struct, sys

R = ['zero','at','v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7',
     's0','s1','s2','s3','s4','s5','s6','s7','t8','t9','k0','k1','gp','sp','fp','ra']
I_OPS = {0x08:'addi',0x09:'addiu',0x0a:'slti',0x0b:'sltiu',0x0c:'andi',0x0d:'ori',0x0e:'xori',
         0x20:'lb',0x21:'lh',0x23:'lw',0x24:'lbu',0x25:'lhu',0x28:'sb',0x29:'sh',0x2b:'sw',
         0x04:'beq',0x05:'bne',0x06:'blez',0x07:'bgtz',0x0f:'lui'}
R_OPS = {0x00:'sll',0x02:'srl',0x03:'sra',0x04:'sllv',0x06:'srlv',0x07:'srav',0x08:'jr',0x09:'jalr',
         0x10:'mfhi',0x12:'mflo',0x18:'mult',0x19:'multu',0x1a:'div',0x1b:'divu',
         0x20:'add',0x21:'addu',0x22:'sub',0x23:'subu',0x24:'and',0x25:'or',0x26:'xor',0x27:'nor',
         0x2a:'slt',0x2b:'sltu'}

def load(fn):
    d = open(fn, 'rb').read()
    assert d[:8] == b'PS-X EXE'
    base = struct.unpack_from('<I', d, 0x18)[0]
    return base, d[0x800:]

def dis(w, pc):
    op = w >> 26; rs = (w >> 21) & 31; rt = (w >> 16) & 31; rd = (w >> 11) & 31
    sh = (w >> 6) & 31; fn = w & 63; imm = w & 0xffff; simm = imm - 0x10000 if imm & 0x8000 else imm
    if w == 0: return 'nop'
    if op == 0:
        n = R_OPS.get(fn, f'r?{fn:x}')
        if n in ('sll','srl','sra'): return f'{n} {R[rd]},{R[rt]},{sh}'
        if n in ('jr',): return f'jr {R[rs]}'
        if n in ('jalr',): return f'jalr {R[rd]},{R[rs]}'
        if n in ('mfhi','mflo'): return f'{n} {R[rd]}'
        if n in ('mult','multu','div','divu'): return f'{n} {R[rs]},{R[rt]}'
        return f'{n} {R[rd]},{R[rs]},{R[rt]}'
    if op in (2, 3):
        return f"{'j' if op == 2 else 'jal'} 0x{(pc & 0xf0000000) | ((w & 0x3ffffff) << 2):08x}"
    if op == 1:
        return f"{'bltz' if rt == 0 else 'bgez' if rt == 1 else 'b?'} {R[rs]},0x{pc + 4 + simm * 4:08x}"
    n = I_OPS.get(op)
    if not n: return f'.word 0x{w:08x}'
    if n == 'lui': return f'lui {R[rt]},0x{imm:x}'
    if n in ('beq','bne'): return f'{n} {R[rs]},{R[rt]},0x{pc + 4 + simm * 4:08x}'
    if n in ('blez','bgtz'): return f'{n} {R[rs]},0x{pc + 4 + simm * 4:08x}'
    if n[0] in 'ls' and n not in ('slti','sltiu'): return f'{n} {R[rt]},{simm}({R[rs]})'
    if n in ('andi','ori','xori'): return f'{n} {R[rt]},{R[rs]},0x{imm:x}'
    return f'{n} {R[rt]},{R[rs]},{simm}'

def words(fn):
    base, code = load(fn)
    for i in range(0, len(code) - 3, 4):
        yield base + i, struct.unpack_from('<I', code, i)[0]

if __name__ == '__main__':
    fn, a, b = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
    for pc, w in words(fn):
        if a <= pc < b: print(f'{pc:08x}: {w:08x}  {dis(w, pc)}')
