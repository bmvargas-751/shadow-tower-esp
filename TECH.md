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

- **T-5** Solo se usan caracteres que tiene la fuente del juego. Texto codificado (nombres, menús): solo mayúsculas; fuente A con Á É Í Ó Ú Ñ Ü ¿ ¡ y fuente B con Á É Í Ó Ú Ñ Ü (agregadas en las láminas, ver la prueba 7). Texto en imágenes: los diálogos tienen mayúsculas, minúsculas y las letras españolas (dibujadas para el proyecto); equipo y criaturas, solo mayúsculas con Á É Í Ó Ú Ñ Ü. Apóstrofo `'`; comillas `"` (dibujadas para el proyecto en los diálogos). `tools/hooks.py` avisa de cada letra que falte. (`caracteres`)

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
  - **No hay tabla código → glifo: el código es el número de celda.** Fuente compacta en celdas de 6×12 px, 42 por fila: celda = código; x = (código % 42) × 6, y = (código // 42) × 12. Verificado con las 782 cadenas de `STAT.T` 0 y 3 y `FDAT.T` 480: todos los códigos tienen glifo salvo `0x01`.
  - Mapa: `02`–`0B` = 0–9; `0C`–`18` = `+ - * / . , ? ! # % ' ( )`; `1A`–`1F` = `| : ; < > "`; `20` = espacio; `21`–`3A` = A–Z; `3B` `[`, `3C` `]`, `3E` `=`, `3F` `"`; `40`–`52` (pares) = dígitos anchos. Filas 2 y 3 (códigos 84–167): fuente ancha, celdas de 12 px.
  - Control: `0000` fin de cadena; `0001` aparece 22 veces dentro de las cadenas (probablemente salto de línea, por confirmar); `FFFF` separa.
  - Letras nuevas: irían en las filas libres (códigos desde 168 = fila 4). **Por confirmar en el juego** que la rutina de dibujo acepte códigos ≥ 168 (que calcule y con la fórmula y no los recorte a 8 bits ni a 84). Es la primera prueba de la pseudolocalización.
- La letra de las imágenes: ancho fijo, celda de 6 px, unos 10 px de alto, antialias con 14 tonos (índice 0xF = fondo).

### Adaptador del texto codificado (`tools/st_text.py`, 2026-11-16)

- Bloques de texto (búsqueda en todos los `.T`; no hay otros):

| Prefijo de clave | Archivo, entrada, desplazamiento | Fuente | Cadenas | Libre |
|---|---|---|---:|---:|
| `stat/00` | `STAT.T` 0, 0 | A | 236 | 7602 B |
| `stat/01` | `STAT.T` 1, 0 | B | 107 | 12266 B |
| `stat/02` | `STAT.T` 2, 0 (la 10 es copia) | B | 153 | 11052 B |
| `stat/03` | `STAT.T` 3, 0 | A | 380 | **162 B** |
| `stat/04` | `STAT.T` 4, 0 | B | 380 | **200 B** |
| `stat/08` | `STAT.T` 8, 0 | B | 81 | 12440 B |
| `fdat/480` | `FDAT.T` 480, `0x7488` | A | 236 | 8482 B |
| `vs_etc/15` | `VS_ETC.T` 15, 0 | B | 81 | 12484 B |

- Formato del bloque: u32 `0x4600`; u16[1536] desplazamientos (relativos a `+0xC04`; casilla i = [off[i], off[i+1]), vacía si son iguales; la cola repite el final); cadenas; ceros hasta `+0x4600`. Cada cadena: renglones terminados en `0000 0001`, cierre `FFFF`. Una cadena (`stat/00#0312`) trae un `0001` suelto antes del `FFFF`: el adaptador lo conserva.
- Clave: `prefijo#casilla` (la casilla es el número que usa el juego). Texto: renglones unidos con `\n` (sin los vacíos del final); al importar se rellenan hasta la cantidad del original (más renglones = error). Códigos sin letra: `{XXXX}`.
- Fuente B (entradas 1, 2, 4, 8, 10 de `STAT.T` y `VS_ETC.T`): celdas 12×10, 18 por fila, celda = código − 2; A = `0x17`, espacio = `0x31`. Cada entrada tiene su propia lámina con algunos signos extra (flechas, «lb», `: ? ( ) "`), que por ahora salen como `{XXXX}`. Se leen como letra (2026-11-17, `FONT_B_ENTRY`): el guion `0x11` (igual en todas las láminas) y el apóstrofo, que cambia de celda según la lámina (`0x32` en la entrada 2, `0x33` en la 8 y en `VS_ETC.T` 15). `stat/04` usa códigos que no coinciden con su propia lámina ({0035} en KING'S, {0036}/{0037} en SOUL POD): el juego la dibuja con otra, que falta identificar en pantalla.
- **Ida y vuelta idéntica** de los cuatro archivos (`STAT.T` ×2, `FDAT.T`, `VS_ETC.T`), también recodificando todo desde el texto: `python3 -I tools/st_text.py roundtrip`.
- **Solo mayúsculas:** ninguna de las dos fuentes tiene minúsculas ni tildes. `tools/hooks.py` (`missing_chars`) avisa de cada letra que falte.
- **Espacio:** `stat/03` y `stat/04` (nombres de objetos y equipo) casi no tienen lugar libre. Opciones por probar: achicar la lámina de la fuente de esa entrada (usa ~48 de 256 filas) y correr el bloque, si el juego respeta el puntero `0x4600`.
- `stat/03` y `stat/04` coinciden en 353 de 380 casillas, y `stat/08` y `vs_etc/15` en 73 de 81; no se copian automáticamente (las diferencias pueden ser a propósito).

### Texto en imágenes: reconocedor (`tools/st_image.py`, 2026-11-16)

- Exporta a `../shadow-tower-esp-local/image_source.jsonl` (segunda fuente en `loc.json`).

| Prefijo | Origen | Imagen | Celda | Textos |
|---|---|---|---|---:|
| `talk` | `TALKMSG.T` | TIM 4 bpp 256×256 | 6×12, mayúsculas y minúsculas | 112 |
| `equip` | `EQUIP.T` | TIM 4 bpp 256×50 y 240×50 | 10×10, solo mayúsculas | 321 |
| `crt` | `CRT.T` (TIM incrustado tras el retrato) | TIM 4 bpp 256×50 | 10×10, misma letra que `equip` | 151 |

- Método: brillo por píxel desde la paleta de cada imagen, umbral elegido por imagen (12/16/20/24: hay diálogos con trazo más grueso); paso vertical por imagen (117 diálogos con 12 px, 3 con 11, 1 con 10); origen x por renglón; la columna 0 de cada celda se ignora (restos del signo anterior). Huella sha1 de cada celda → letra en `tools/glyph_labels/` (solo huellas, sin píxeles del juego). Sin etiqueta: plantilla más parecida (Hamming ≤ 6, ±2 filas); pedazos marcados `{?}` para que nunca se asignen a una letra.
- Resultado: `equip` 100 % por etiqueta; `crt` 12 039 por etiqueta y 3 por parecido; `talk` 6172 por etiqueta y 26 por parecido (revisados a ojo en láminas). Sin `{?}` en la salida.
- Formato del texto: `talk` en un párrafo (el dibujador corta de nuevo); `equip`/`crt` con la prosa en un párrafo y cada línea de datos («LENGTH…», «CRITICAL 5») en su renglón.
- Riesgo: errores de reconocimiento sueltos en letras poco frecuentes. Si el revisor ve una palabra rara en el inglés, comprobar contra la imagen.
- Falta: los paneles de 16 bpp con texto de `EQUIP.T`.

### Texto en imágenes: dibujador (`tools/st_render.py`, 2026-11-16)

- `glyphs` arma las plantillas de color (brillo relativo por píxel, la variante más votada de cada letra, alineada por la línea de base) en `../shadow-tower-esp-local/glyphs/` (salen del juego: no van al repo).
- **Letras propias** (dibujadas para el proyecto, en el código): en la letra de los diálogos, las que el inglés nunca usa (z, J, Q, R, X, Z, dígitos menos el 7, `: ; - " ( ) /`) y las españolas (á é í ó ú ñ ü, Á É Í Ó Ú Ñ Ü, ¿ ¡). En la letra de equipo/criaturas (solo mayúsculas): Á É Í Ó Ú Ñ Ü; la letra se baja un píxel (se quita su fila más redundante) y la marca va en una sola fila arriba, con una fila de aire. **Por ver en el juego.**
- Caja: diálogos hasta 33 caracteres y 5 renglones; el bloque se alinea a la izquierda y se centra en la caja (x = 5 + 6·k, k = redondeo de (123 − 3n)/6, n = renglón más largo), como el original. Equipo/criaturas: celdas desde x = −1 (como el original), hasta 25 caracteres (24 en las de 240 px) y 5 renglones. Corte por palabras; `\n` fuerza un renglón.
- Color: cada píxel toma el índice de la paleta de la imagen con el brillo más parecido; el fondo es el índice más común.
- Prueba de geometría (`test`): redibujar el inglés con los cortes del original da las mismas celdas en el 100 % de los diálogos, 98,3 % de criaturas y 89,8 % de equipo (los renglones que el original corrió un píxel).
- **Ida y vuelta idéntica** de `TALKMSG.T`, `EQUIP.T` y `CRT.T`: un texto que no cambió conserva su imagen original (`roundtrip`).
- `tools/hooks.py`: `missing_chars` y `check` (caja, T-3) también para `talk`, `equip` y `crt`.

### Introducción (`tools/st_intro.py`, 2026-11-16)

- `ST/OPTXT/OPTXT.MIC`: bloques `[u32 tamaño][TIM]` desde el byte 0. Seis pantallas de texto (TIM 4 bpp 256×240, 1 o 2 renglones centrados, paleta de 16 tonos) y un fondo (16 bpp 320×240, sin texto).
- El inglés (6 pantallas, 11 renglones) se transcribió a mano en `../shadow-tower-esp-local/optxt_transcript.json`; `st_image.py export` lo suma a `image_source.jsonl` con las claves `intro#0`…`intro#5`. El original trae la errata «challange» (pantalla 6).
- **Letra:** la del original es de máquina de escribir y solo trae las letras de esas 11 líneas. El español se dibuja completo con **Special Elite** (`tools/fonts/`, Apache 2.0, Astigmatic), tamaño 14, centrada en celdas fijas de 9 px como el original, con la paleta de la pantalla. El parche lleva solo las imágenes, no la fuente. Si no convence, la alternativa es reusar las letras del juego y dibujar las que faltan (unas 40).
- Caja: hasta 3 renglones de 28 caracteres, centrados a la altura de los del original.
- **Ida y vuelta idéntica** (`roundtrip`); `hooks.py` controla letras y caja de `intro#`.

### Imagen de prueba 2 (`tools/st_testbuild.py`, 2026-11-16) — pendiente de revisar en DuckStation

`../shadow-tower-esp-local/test/shadow-tower-prueba-2.cue`. Qué mirar y qué significa:

| Prueba | Dónde se ve | Bien | Mal |
|---|---|---|---|
| Á (código 168) y É (300) en la fuente del texto codificado | menú: «STÁTUS», «MAGIC LÉFT» | el juego acepta códigos altos: las letras españolas se agregan en la lámina | qué letra o basura sale en su lugar |
| Fuente de `STAT.T` 3 movida a `0xA600` (64 filas) y nombres de objetos 171+ más allá de `0x4600` | nombres de objetos y equipo | todos bien: hay lugar de sobra para los nombres | todos mal: no respeta el puntero/altura; solo los altos mal: no lee más allá de `0x4600` |
| Diálogos redibujados | cualquier conversación («Prueba talk N: …») | se lee, sin cortes | letras cortadas, caja que se pasa |
| Descripciones de equipo y criaturas redibujadas | menú de equipo y libro de criaturas («PRUEBA EQUIP N - …») | tildes visibles en las mayúsculas | marcas que no se ven |
| Introducción redibujada | al empezar partida nueva («Pantalla N: …») | Special Elite se lee y combina | — |

**Resultado de la prueba 2 (2026-11-16, usuario en DuckStation):** la introducción se ve bien (Special Elite, tildes, ñ, ¿¡). **Al abrir el menú el emulador se cierra.** El código de `ST.EXE` no usa `0x4600` como constante (no aparece en ninguna instrucción). Para aislar la causa, tres imágenes con un solo cambio cada una (`st_testbuild.py glyphs|move|shrink`):

| Imagen | Cambio | Si el menú se cae |
|---|---|---|
| `prueba-3a` | Á (168) y É (300) en la entrada 0 («STÁTUS», «MAGIC LÉFT») | los códigos altos no sirven: buscar otra forma de agregar letras |
| `prueba-3b` | fuente de la entrada 3 corrida a `0x4780` (256 filas); casillas 686, 687 y 999 más allá de `0x4600` | el juego no respeta el puntero de la cabecera |
| `prueba-3c` | fuente de la entrada 3 recortada a 64 filas, en su lugar | el juego no respeta la altura del TIM |

### Gráficos con texto (inventario, 2026-11-16)

Palabras dibujadas con letras decorativas; no pasan por el reconocedor. Cada palabra ocupa un rectángulo que el código usa por coordenadas: el reemplazo tiene que caber en el mismo rectángulo (o hay que cambiar las coordenadas en `ST.EXE`).

| Gráfico | Archivo | Formato | Traducir |
|---|---|---|---|
| PAUSE, Menu, BUTTON, HP/MP, DATA LOAD, OPTIONS, SAVE, ITEM, USE, EQUIP, TRADE, FOR, HP POTION, BUY, REPAIR, CONFIGURATION, SOUL POD | `ST/COM/STAT.T` entrada 6 (copia en `ST/VS/STAT.T`) | TIM 4 bpp 256×128 | sí (prioridad) |
| ITEM BAG, CREATURE VS | `ST/COM/STAT.T` entrada 7 | TIM 4 bpp 256×64 | sí |
| NO EQUIP | `ST/COM/EQUIP.T` entrada 1 | TIM 16 bpp 292×124 | sí |
| PUSH START (92×15); NEW / LOAD / VS (44×46) | `ST/TITLE/TITLE.MIC` | TIM 16 bpp | sí |
| Now Loading (sobre una ilustración) | `LOAD02.TIM` | TIM 16 bpp 320×120 | sí |
| PLAYER 1, PLAYER 2, VS, LOADING... | `ST/VS/VS_ETC.T` entradas 31–35 | TIM 16 bpp 64×240 (tiras) | sí (modo VS) |
| Logo SHADOW TOWER, FROM SOFTWARE, avisos de copyright | `TITLE.MIC`, `FLOGO320.TIM`, `COPYRIGT.TIM`, `STR/*.STR` | 16 bpp / video | no (marcas y avisos legales) |

Plan: medir el rectángulo de cada palabra (componentes conexas de la lámina), elegir con el usuario la traducción corta de cada una (con el glosario) y dibujarla con una letra parecida, en la misma paleta y sin pasarse del rectángulo.

**Resultado de la prueba 3 (2026-11-16):** 3a (Á/É) y la prueba de la fuente: el menú se cae. 3b (fuente movida) y 3c (fuente achicada): el menú abre, pero se cae la pantalla de equipo (que usa la entrada 3).

**Causa: suma de verificación por entrada.** Cada entrada de todos los `.T` termina en una palabra de 32 bits = `0x12345678` + suma de todas las palabras de la entrada salvo la última (rutina en `ST.EXE` `0x80015B80`; compara con `xor` y devuelve error). Se cumple en 4909 de 4961 entradas, y en el 100 % de las que tocamos (`STAT.T`, `TALKMSG.T`, `EQUIP.T`, `CRT.T`, `VS_ETC.T`, `FDAT.T` 480). Las tres pruebas cambiaban entradas sin recalcularla. `tfile.fix_checksums` la recalcula; `st_text`, `st_render` y `st_testbuild` la usan. `OPTXT.MIC` no es un `.T` y no la tiene (la introducción funcionó).

Prueba 4 (pendiente): `prueba-4` (todo junto, con sumas corregidas) y `4a/4b/4c` (los mismos cambios que 3a/3b/3c), por si hay que aislar de nuevo.

**Resultado de la prueba 4 (2026-11-16):** con las sumas corregidas, el menú abre sin caerse. «STÁTUS» y «MAGIC LÉFT» salen con un hueco en lugar de la Á (168) y la É (300): el juego acepta códigos altos, pero dibuja la letra desde una lámina que no la tenía. Hipótesis: el menú dibuja con la lámina de otra entrada de fuente A (la 3, que en la prueba 4 estaba achicada a 64 filas y sin las letras nuevas).

Prueba 5 (pendiente): Á (168) y É (169) en las láminas de las entradas 0 **y** 3, ambas en la fila 4 (dentro de las 64 filas); lo demás como en la 4. Si siguen en blanco: save state con el menú abierto para ver qué lámina está en la VRAM.

**Resultado de la prueba 5 (2026-11-16, estados 9 y 10 del usuario):**
- «STÁTUS»/«MAGIC LÉFT» siguen con hueco. La VRAM del estado 9 tiene la lámina de la entrada 0 **entera** (256 filas, con la Á en la fila 4) en (960, 256): la letra está cargada, pero **la rutina de dibujo no dibuja códigos ≥ 168** (4 filas × 42 celdas). Las letras nuevas van en celdas libres por debajo de 168 que ninguna cadena usa: **25, 61, 150, 151, 154–167** (18 celdas, en las láminas de las entradas 0 y 3). Las celdas 93–95 están vacías pero las usan cadenas de `stat/00` (casillas 800–801): son códigos especiales, no se tocan.
- Los nombres de objetos de las casillas 292–302 y la descripción 676 se ven bien aunque estaban más allá de `0x4600`: **el juego lee el texto movido**. En la RAM del estado 10 está la entrada 3 completa (texto incluido); el juego reemplaza la palabra de cabecera por otro valor al cargar.
- Al pasar a «Soul Pod» (casilla 310, descripción 684, sin códigos especiales) la pantalla sale con basura. Causa no aislada (fuente movida/achicada). **Se descarta mover o achicar la fuente.**
- **Espacio sin mover la fuente:** deduplicar (las casillas con el mismo texto apuntan a una copia). En `stat/03` y `stat/04` deja ~2500 B libres (21–23 % del texto). `st_text.rebuild_entry` deduplica solo si un bloque no entra (la ida y vuelta sigue idéntica). Por probar en el juego.

Prueba 6 (pendiente): Á en la celda 154 y É en la 25 (entradas 0 y 3), fuente sin mover, **deduplicación forzada en las entradas 3 y 4** (mismo texto visible) y el texto en imágenes redibujado.

**Resultado de la prueba 6 (2026-11-16, estados 8, 9 y 10):**
- «MAGIC LÉFT» con la É en la celda **25** (fila 0): **se ve**. «ST TUS» con la Á en la celda **154** (fila 3): hueco. El juego dibuja como letras normales solo los códigos de las filas 0–1 (2–83); las filas 2–3 son de la fuente ancha.
- USE ITEM (Soul Pod incluido) y la pantalla de equipo, con las entradas 3 y 4 **deduplicadas**: correctos. **La deduplicación funciona.**
- Libro de criaturas y descripción de equipo redibujados: se ven, con tildes en mayúsculas (chicas pero legibles).
- Conversaciones: sin probar (no había un personaje cerca).

**Letras españolas de la fuente A (definitivo, `st_text.SPANISH_A`):** É 25, Á 61 (celdas vacías) e Í 26 (`|`), Ó 28 (`;`), Ú 59 (`[`), Ñ 60 (`]`), Ü 62 (`=`), ¿ 20 (`#`), ¡ 14 (`*`): signos que ninguna cadena usa. No se usan `< > + %` ni los dígitos anchos, porque el juego podría dibujarlos por su cuenta. `st_text.import_` las dibuja (letra base + marca en la fila 0; ¿ y ¡ invirtiendo ? y !) en las láminas de las entradas 0 y 3 cuando alguna traducción de fuente A las usa.

**Fuente B:** sus 3 filas (18 celdas de 12 px) no tienen celdas libres salvo la celda 0 (código 2). Prueba 7: Á en la fila 3 (código 56) y É en el código 2.

Prueba 7 (pendiente): menú de pausa con «STÁTUS», «ÉÍÓÚ» (en lugar de SLASH), «ÑÜ¿¡» (SMASH) y «PIÉRCE»; panel derecho de la pantalla de equipo con «WEAPON ÁTTACK» y «MAGIC SPÉED» (fuente B); texto en imágenes redibujado (conversaciones).

**Resultado de la prueba 7 (2026-11-16):** las 9 letras de la fuente A se ven en el menú («STÁTUS», «ÉÍÓÚ», «ÑÜ¿¡», «PIÉRCE»): **resuelto**. En la fuente B, la Á en el código 56 (fila 3) se ve («WEAPON ÁTTACK»): el juego dibuja la fila 3 de la lámina B. El código 2 (celda 0) no sirve.

**Letras españolas de la fuente B (`st_text.SPANISH_B`):** Á 56, É 57, Í 58, Ó 59, Ú 60, Ñ 61, Ü 62 (fila 3, libre en todas las láminas B). Se dibujan en las entradas 1, 2, 4, 8 y 10 de `STAT.T` (las dos copias) y en la 15 de `VS_ETC.T`, cuando alguna traducción de fuente B las usa. La letra se baja un píxel (se quita su fila más redundante) y la marca va en la fila 0, con la fila 1 vacía. Sin ¿ ni ¡ (la fuente B no trae ? ni !; `hooks.py` avisa si se usan).

Prueba 8 (pendiente): las 9 letras de A en el menú y las 7 de B en el panel de equipo («WEAPON ÁTTACK», «MAGIC SPÉED», «ÍÓÚ DEFENSE», «MAGIC DEFÑÜ»), con el adaptador real; y el texto en imágenes (conversaciones sin probar todavía).

**Resultado de la prueba 8 (2026-11-16):** con el adaptador real, la fuente A muestra Á É Í Ó Ú Ñ Ü ¿ ¡ en el menú y la fuente B muestra Á É Í Ó Ú Ñ Ü en el panel de equipo, con la marca separada de la letra. **Letras españolas del texto codificado: resuelto.** Falta ver en el juego una conversación redibujada (`TALKMSG.T`).

**Reconocedor corregido (2026-11-16):** en los renglones con origen 9 (831 de equipo y 696 de criaturas) se perdía la primera letra: la primera celda empieza en x = −1 y no se leía. `st_image.lines` ahora arranca las celdas antes del origen y el dibujador escribe desde esa misma celda (`EQUIP_X = −1`, 25 caracteres por renglón; 24 en las de 240 px): el texto redibujado empieza en la misma x que el original. Se resolvieron «HP/MP DRAIN» y «HP/MP RECOVERY». Una «i» degradada de `talk#0150` se leía como «!»: etiqueta explícita.

**Imagen completa (fase 7, `tools/st_build.py`, 2026-11-17):** reconstruye los 8 archivos con `translation/` (4 de texto codificado con `st_text`, 3 de imágenes con `st_render` y `OPTXT.MIC` con `st_intro`), los escribe en una copia de `original.bin` y comprueba lo escrito. Resultado: `../shadow-tower-esp-local/test/shadow-tower-esp.{bin,cue}`, 584 imágenes y 6 pantallas redibujadas, sin errores. Pendiente de probar en DuckStation.

**Parche (fase 8, `tools/st_patch.py`, 2026-11-17):** comprueba el SHA-1 del original, arma la imagen con `st_build.build`, crea el parche con `xdelta3 -e -9 -S none` (sin compresión secundaria: Rom Patcher JS y otros parcheadores no la soportan) y lo aplica de vuelta para comparar. El armado es determinista: dos corridas dan la misma imagen (SHA-1 `6fe34831…` con la traducción del 2026-11-17). El `.cue` del paquete va con fin de línea CRLF. `LEEME.txt` sale de `tools/release/LEEME.txt` con los hashes de las dos imágenes.
