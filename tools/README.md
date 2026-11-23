# Herramientas

Las herramientas propias de Shadow Tower. Las del kit (lotes, validador, avance) están en `~/.claude/loc-kit/tools/loc.py`.

## Armar la imagen y el parche

Hace falta la imagen USA en `../shadow-tower-esp-local/original.bin` (SHA-1 `df441bf08b7079f8b3d36f1188f7eedd8cb73c50`).

- `python3 tools/st_build.py` → imagen traducida para probar, en `../shadow-tower-esp-local/test/`.
- `python3 tools/st_patch.py [VERSIÓN]` → parche `.xdelta` comprobado y paquete `.zip` para publicar, en `../shadow-tower-esp-local/dist/`. Necesita `xdelta3` (`sudo apt install xdelta3`, o la variable `XDELTA3`).

Cómo se aplica el parche: [release/LEEME.txt](release/LEEME.txt) (va dentro del paquete).

## Los scripts

| Script | Qué hace |
|---|---|
| `st_text.py` | Adaptador: texto codificado (nombres, estados, menús) de STAT.T, FDAT.T y VS_ETC.T |
| `st_image.py` | Adaptador: texto dibujado en imágenes (diálogos y descripciones de equipo y criaturas) |
| `st_intro.py` | Las 6 pantallas de texto de la introducción (OPTXT.MIC) |
| `st_render.py` | Vuelve a dibujar el texto traducido en las imágenes (TALKMSG, EQUIP, CRT) |
| `st_exe.py` | Posiciones de los menús en los ejecutables (precalculadas con el largo del inglés) |
| `st_build.py` | Imagen completa con la traducción, para probar en DuckStation |
| `st_testbuild.py` | Imagen de prueba combinada (no toca `translation/`) |
| `st_patch.py` | Parche xdelta y paquete de entrega |
| `hooks.py` | Hooks del kit (ver `loc.json`) |
| `psxiso.py`, `psxpatch.py` | Leer una imagen de PS1 (MODE2/2352) y reemplazar archivos dentro, con EDC/ECC |
| `tfile.py`, `tim.py` | Contenedores `.T` e imágenes TIM |
| `dsstate.py`, `mips.py` | Análisis: VRAM de un save state de DuckStation y desensamblador MIPS |
