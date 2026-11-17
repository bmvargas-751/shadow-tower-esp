# Pendientes

La cola del usuario: lo que ninguna regla cubre, las líneas delicadas con su solución provisional, los términos por decidir y los choques entre documentos. Nada de esto cambia el texto hasta que el usuario lo decide.

Formato: `- [ ] \`clave\` (rol, motivo): «fragmento» → «propuesta». Por qué.` `loc.py findings` agrega aquí, solo, los hallazgos sin regla de cada lote. Lo decidido pasa a DECISIONS.md y se borra de aquí.

## Para la prueba en el juego

Se deciden al ver la pantalla.

- [ ] `vs_etc/15#…` (terminólogo, duda): «DILUTE» → «DILUCIÓN». El juego no dice qué hace (habilidad de criatura del modo VS); cambiarla si en pantalla resulta otra cosa.
- [ ] `stat/08#…` (terminólogo, duda): «CAPTURED» → «CAPTURA». Dato de criatura del modo VS; ver a qué se refiere.
- [ ] `stat/02#0147` (terminólogo, duda): «Hallow Mage» → «Mago Sagrado». Si es errata de *hollow*, sería «Mago Hueco».
- [ ] `stat/00#0700`–`0741` (orquestador, ancho): los lugares van en forma corta hasta 21 caracteres (el más largo del original). Medir el ancho real en la pantalla donde aparecen; si cabe más, volver a las formas largas (GLOSSARY.md, notas «forma corta»).
- [ ] `crt#0267`, `fdat/480#0613` (terminólogo, inconsistencia del original): WATER WORLD aparece también como «MAGIC WORLD» y «WATER SPRIT WORLD». Se señala, no se corrige (E-61): ¿es el mismo lugar?
- [ ] `stat/00#0916`–`0933` y `stat/03#0512`–`0528` (terminólogo, duda): dos listas de magias que coinciden solo en parte. Se traducen igual las que coinciden; falta saber dónde se muestra la primera.
- [ ] `stat/03#0210` (corrector, sin regla): «ANILLO SAGRADO⏎⏎0211⏎ANILLO OSCURO» → «ANILLO SAGRADO». El corrector lo leyó como un resto de extracción. Nota del orquestador: el original es igual («HOLY RING⏎⏎0211⏎DARK RING», 5 renglones, en `stat/03` y `stat/04`), así que la traducción lo sigue tal cual; propuesta: dejarlo y ver en el juego si esa casilla se muestra.
- [ ] `stat/04#0273`, `#0302`, `#0673` (orquestador, para la prueba en el juego): el apóstrofo de KING'S, DORADO'S y GUARDIAN'S es el código {0035}, de una lámina que no se sabe cuál es (TECH.md); T-1 obliga a conservarlo y quedó al final: «LLAVE DEL REY{0035}». Ver qué dibuja; si es un apóstrofo, agregarlo al adaptador como en `stat/02` y quitarlo del español. Lo mismo para {0036}/{0037} de FRASCO DE ALMA (`stat/04#0310`–`0313`).
- [ ] `stat/00#0350`–`0371`, `fdat/480#0352` (orquestador, ancho): mensajes de la memory card bastante más largos que el original (`stat/00#0352`, 37 caracteres contra 24). Ver que entren en su cuadro.
- [ ] `stat/08#0027`, `#0028`, `#0030` y `stat/01#0134` (revisor, ancho): mensajes del modo VS (de 43 a 52 caracteres) y «TELETRANSPORTE» con sangría (24 columnas). Ver en pantalla.

## Alineación con el largo en inglés (prueba 0.9.1, 2026-11-17)

- [ ] (orquestador, técnico): el tipo de criatura de la ficha (alineado a la derecha) y las opciones del menú principal y de OPTIONS (centradas) se ubican con el largo del texto en inglés (TECH.md, «Prueba 0.9.0 en el juego»). No se arregla desde el texto: hay que parchear el código. El usuario pidió las opciones alineadas a la izquierda.

## Formas cortas de la prueba 0.9.0 (2026-11-17)

Soluciones provisionales, ya aplicadas, para lo que no entraba en pantalla (límites en TECH.md y en `tools/hooks.py`). Se apartan del glosario a propósito (avisos G-3). Falta tu «ok» o la alternativa.

- [ ] `stat/03`/`stat/04` (orquestador, ancho 25): nombres de objetos. Afijos: «DE RESIST.» (como el «OF RESIST» del original), «DE EQUIL.», «DE CURACIÓN» → CURATIVO/A, «DE PROTECCIÓN» → PROTECTORA. Anillos con oficio: adjetivos, ANILLO HECHICERO ÍGNEO, ANILLO INVOCADOR GÉLIDO, ANILLO CLERICAL ÍGNEO (PRIEST → CLERICAL), ANILLO CÁUSTICO CLERICAL, ANILLO HECHICERO VENENOSO, ANILLO GÉLIDO EQUILIBRADO, ANILLO SAGRADO CLERICAL. Sueltos: ANILLO IGNÍFUGO (RING OF FIRE RESIST), ANILLO DE ESPÍRITU MUERTO, COTA DE CABALLERO, ARMADURA COMPL. REFORZADA, PROT. DE MANO CÁUSTICO, BASTARDA APLASTANTE.
- [ ] `stat/03#0644`, `#0678` (orquestador, ancho 37): «TE LLEVA AL ÚLTIMO PUNTO DE GUARDADO» y «ALIMENTA LA VELA DEL MUNDO DE TIERRA» (la fuente B no tiene coma).
- [ ] `stat/00#0904`–`0915` (orquestador, ancho 8): etiquetas de EQUIP: MANO D./I., RES. D./I., BRAZ. D./I., ANIL. D./I., MAG. D./I.; la cabecera de peso, PESO.
- [ ] `stat/00#0211`–`0216` (orquestador, ancho 12 y 11): GIRAR IZQ./DER., MOVER IZQ./DER., SUBIR VISTA, BAJAR VISTA (también en `fdat/480`).

## Términos sin regla (set de oro, 2026-11-17)

- [ ] `equip#0003` (revisor, original): el original trae los signos de pie y pulgada invertidos (`2"11'`, visto en la imagen). Se lee como 2 pies 11 pulgadas → 89 CM.

## Para el kit (piloto, 2026-11-17)

- [ ] (orquestador, kit): un aviso de `loc.py check` (por ejemplo, caja T-3 después de una edición) no puede convertirse en hallazgo aprobado, así que `loc.py edits` rechaza la corrección del editor. En el piloto lo resolvió el usuario a mano (`equip#0117`). Propuesta: que `loc.py findings` acepte los avisos de `checks.jsonl` como hallazgos con su regla.
- [ ] (orquestador, kit): el control de glosario solo reconoce género y número si el término está en minúscula (el sufijo se quita con una regla en minúscula). Hoy se resuelve escribiendo los afijos en minúscula en GLOSSARY.md.
