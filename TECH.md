# Reglas técnicas

Lo que el juego necesita para que el texto no se rompa. Cada regla tiene un número para citarla, y la mayoría la controla `loc.py check` (el chequeo va entre paréntesis). Salen de cómo está hecho el juego, del adaptador y de la sección 8 del encargo: una traducción nunca puede romper el archivo.

Plantilla del kit: los números quedan; lo de cada regla se completa con lo que muestre la prueba técnica de este juego (PLAN, fase 1). Lo que no aplique se borra.

## Códigos y saltos

- **T-1** Los códigos (variables, etiquetas, colores, nombres insertados) quedan intactos y en el mismo orden que en el original. Los reconoce la lista `codes` de `loc.json`. (`codigos`)
  - Completar: qué hace cada código de este juego.
- **T-2** Saltos de línea: los fijos (`fixed_break` en `loc.json`) van exactamente donde están en el original, ni más ni menos. Los demás, si el adaptador parte los renglones, los pone el adaptador. (`saltos`)

## Espacio

- **T-3** La caja: ningún renglón puede pasar del ancho que permite el juego. Si el límite medido es el del original y no el de la pantalla, el aviso no obliga a recortar: se permiten abreviaturas reconocibles, pero nunca se quitan palabras ni se acorta de forma que se pierda el sentido. Si la forma completa no cabe, va completa y con su aviso, y se revisa en el juego. [IVA] (chequeo del proyecto, en `hooks`)
- **T-4** Los textos con largo máximo en bytes (`max` en el lote) no pueden pasarlo: es un límite duro. Completar: cuántos bytes ocupa cada letra en este juego. (`bytes`)

## Caracteres

- **T-5** Solo se usan caracteres que tiene la fuente del juego. Completar: si la fuente tiene las letras españolas (á é í ó ú ü ñ, sus mayúsculas, ¿ ¡) o hay que agregarlas, y qué comillas y apóstrofo tiene. (`caracteres`)

## Qué se traduce

- **T-6** Lo que no se traduce ni cuenta (restos sin localizar, textos de prueba) va en `excluded` de `loc.json`. Completar: qué es en este juego.
- **T-7** Solo se traducen los textos que ve el jugador. Los nombres internos (archivos, etiquetas) no se exportan y no se tocan.
- **T-8** Toda línea del lote se traduce completa: ninguna queda vacía, igual al original ni con frases del original mezcladas. (`vacia`, `sin_traducir`, `ingles_mezclado`)

## Notas de la fase 1 (2026-11-16)

### Imagen y extracción

- Imagen: `Shadow Tower.bin`, MODE2/2352, una pista (el .cue original apunta a «Shadow Tower (USA).bin»). SHA-1 `df441bf08b7079f8b3d36f1188f7eedd8cb73c50`.
- Extracción con `tools/psxiso.py` (lector ISO9660 propio): 126 archivos, en `../shadow-tower-esp-local/files/`.
- Ningún archivo tiene texto ASCII.

### Contenedor `.T` (`tools/tfile.py`)

- u16 `n`, luego `n+1` u16 = sector de inicio (2048 bytes) de cada entrada; entrada i = sectores `[s[i], s[i+1])`. Entradas de tamaño 0 = vacías.
- Las entradas son TIM estándar (`tools/tim.py`) u otros datos (modelos, tablas).

### Dónde está el texto

| Qué | Dónde | Forma |
|---|---|---|
| Diálogos | `ST/COM/TALKMSG.T`, 600 entradas, 124 con TIM | **Imagen**: TIM 4 bpp 256×256, paleta de 16 colores, fuente de ancho fijo |
| Descripciones de equipo | `ST/COM/EQUIP.T`, 331 TIM 4 bpp 256×50 (321) y 240×50 (10) | **Imagen**, fuente en mayúsculas de ancho fijo |
| Nombres (objetos, equipo, estados, magias…) | `ST/COM/STAT.T` entradas 0 y 3 (≈580 cadenas); `ST/VS/STAT.T` es copia idéntica | **Texto codificado** 16 bits |
| Menús y opciones | `ST/COM/FDAT.T` entrada 480 (≈200 cadenas) y algunas más en `FDAT.T` | **Texto codificado** 16 bits |
| Menús dibujados (PAUSE, Menu, ITEM BAG, botones) | `ST/COM/STAT.T` (TIM 4 bpp 256×128 y 256×64) | **Imagen** con fuentes decorativas: se editan a mano |
| Texto de la introducción | `ST/OPTXT/OPTXT.MIC`, 7 TIM 4 bpp 256×240 | **Imagen**, fuente tipo máquina de escribir |
| Título, créditos, logos | `TITLE.MIC`, `STAFF.MIC`, `*.TIM`, videos `.STR` | Imagen 16 bpp / video; créditos y logos probablemente sin traducir |
| Descripciones de criaturas | `ST/COM/CRT.T`, 151 entradas con retrato (16 bpp 230×115) + **TIM 4 bpp 256×50** (misma letra que `EQUIP.T`). Cada entrada empieza con un u32 de tamaño y luego el TIM | **Imagen** |
| Paneles con texto grande («NO EQUIP») | `ST/COM/EQUIP.T`, TIM 16 bpp 292×124 (la mayoría son dibujos de objetos; falta separar los que tienen texto) | **Imagen** 16 bpp |
| Menús del modo VS | `ST/VS/VS_ETC.T` entrada 15 (40 cadenas) | **Texto codificado**, otra tabla: código = ASCII − 0x2A (A = 0x17) |

Descartado (2026-11-16): las pocas cadenas que el escaneo encontró en `EQUIP.T`, `ICON.T`, `MO.T`, `CHR*/M*.T`, `VS_CRT.T`, `ST.EXE` y `VS.EXE` son coincidencias en datos binarios, no texto. `ST/FN.` es un archivo de configuración de depuración en ASCII (piso, posición del jugador), no una fuente.

### Codificación de 16 bits

- Tabla de mayúsculas (lo que se ve): código = ASCII − 0x20 (A = 0x21 … Z = 0x3A), espacio = 0x20. Fin de cadena: `0000 0001 FFFF` (por confirmar qué hace cada código).
- Tabla de minúsculas (a = 0x17 …, espacio = 0x31): en `STAT.T` entradas 1, 2, 4, 8 y 10; parecen identificadores internos (por confirmar si se ven en pantalla).
- **Fuente de esta tabla (encontrada 2026-11-16):** TIM incrustado en `ST/COM/STAT.T`, entrada 0, desplazamiento `0x4608` de la entrada (`0x4E08` del archivo), 4 bpp, 256×256, paleta de 16 colores, sin comprimir. `ST/VS/STAT.T` tiene la misma copia. Se ubicó con la VRAM de un save state (`tools/dsstate.py`); en el juego se carga hacia x ≈ 944–1023, y = 256.
  - Trae dos juegos de letras: uno compacto (mayúsculas, números, `+-*/.,?!#%'() |:;<>"[]=`) y otro ancho y espaciado (mayúsculas, números, `/~+-.%`), más el glifo «lb».
  - **Sin minúsculas ni letras con tilde.** Solo se usan las primeras ~48 filas: el resto (≈200 filas) está libre para glifos nuevos (Á É Í Ó Ú Ñ Ü ¿ ¡).
  - Pendiente: dónde está la tabla código → posición del glifo (probablemente en `ST.EXE` o en la misma entrada 0) y si acepta códigos nuevos.
- La letra de las imágenes: ancho fijo, celda de 6 px, unos 10 px de alto, antialias con 14 tonos (índice 0xF = fondo).
