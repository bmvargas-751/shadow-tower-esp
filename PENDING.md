# Pendientes

La cola del usuario: lo que ninguna regla cubre, las líneas delicadas con su solución provisional, los términos por decidir y los choques entre documentos. Nada de esto cambia el texto hasta que el usuario lo decide.

Formato: `- [ ] \`clave\` (rol, motivo): «fragmento» → «propuesta». Por qué.` `loc.py findings` agrega aquí, solo, los hallazgos sin regla de cada lote. Lo decidido pasa a DECISIONS.md y se borra de aquí.

## Para la prueba en el juego

Se deciden al ver la pantalla.

- [ ] `vs_etc/15#…` (terminólogo, duda): «DILUTE» → «DILUCIÓN». El juego no dice qué hace (habilidad de criatura del modo VS); cambiarla si en pantalla resulta otra cosa.
- [ ] `stat/08#…` (terminólogo, duda): «CAPTURED» → «CAPTURA». Dato de criatura del modo VS; ver a qué se refiere.
- [ ] `stat/02#0147` (terminólogo, duda): «Hallow Mage» → «Mago Sagrado». Si es errata de *hollow*, sería «Mago Hueco».
- [ ] `stat/00#0700`–`0741` (orquestador, ancho): los lugares van en forma corta hasta 21 caracteres (el más largo del original). Medir el ancho real en la pantalla donde aparecen; si cabe más, volver a las formas largas (GLOSSARY.md, notas «forma corta»).
- [ ] `stat/01`, `stat/00#0904`–`0914` (orquestador, ancho): etiquetas de estadísticas hasta 20 caracteres (SHIELD MAGIC DEFENSE); confirmar en el panel de equipo.
- [ ] `crt#0267`, `fdat/480#0613` (terminólogo, inconsistencia del original): WATER WORLD aparece también como «MAGIC WORLD» y «WATER SPRIT WORLD». Se señala, no se corrige (E-61): ¿es el mismo lugar?
- [ ] `stat/00#0916`–`0933` y `stat/03#0512`–`0528` (terminólogo, duda): dos listas de magias que coinciden solo en parte. Se traducen igual las que coinciden; falta saber dónde se muestra la primera.
- [ ] `stat/03#0210` (corrector, sin regla): «ANILLO SAGRADO⏎⏎0211⏎ANILLO OSCURO» → «ANILLO SAGRADO». El corrector lo leyó como un resto de extracción. Nota del orquestador: el original es igual («HOLY RING⏎⏎0211⏎DARK RING», 5 renglones, en `stat/03` y `stat/04`), así que la traducción lo sigue tal cual; propuesta: dejarlo y ver en el juego si esa casilla se muestra.
- [ ] `stat/04#0273`, `#0302`, `#0673` (orquestador, para la prueba en el juego): el apóstrofo de KING'S, DORADO'S y GUARDIAN'S es el código {0035}, de una lámina que no se sabe cuál es (TECH.md); T-1 obliga a conservarlo y quedó al final: «LLAVE DEL REY{0035}». Ver qué dibuja; si es un apóstrofo, agregarlo al adaptador como en `stat/02` y quitarlo del español. Lo mismo para {0036}/{0037} de FRASCO DE ALMA (`stat/04#0310`–`0313`).
- [ ] `stat/00#0350`–`0371`, `fdat/480#0352` (orquestador, ancho): mensajes de la memory card bastante más largos que el original (`stat/00#0352`, 37 caracteres contra 24). Ver que entren en su cuadro.
- [ ] `stat/08#0027`, `#0028`, `#0030` y `stat/01#0134` (revisor, ancho): mensajes del modo VS (de 43 a 52 caracteres) y «TELETRANSPORTE» con sangría (24 columnas). Ver en pantalla.

## Términos sin regla (set de oro, 2026-11-17)

- [ ] `equip#0003` (revisor, original): el original trae los signos de pie y pulgada invertidos (`2"11'`, visto en la imagen). Se lee como 2 pies 11 pulgadas → 89 CM.

## Para el kit (piloto, 2026-11-17)

- [ ] (orquestador, kit): un aviso de `loc.py check` (por ejemplo, caja T-3 después de una edición) no puede convertirse en hallazgo aprobado, así que `loc.py edits` rechaza la corrección del editor. En el piloto lo resolvió el usuario a mano (`equip#0117`). Propuesta: que `loc.py findings` acepte los avisos de `checks.jsonl` como hallazgos con su regla.
- [ ] (orquestador, kit): el control de glosario solo reconoce género y número si el término está en minúscula (el sufijo se quita con una regla en minúscula). Hoy se resuelve escribiendo los afijos en minúscula en GLOSSARY.md.
