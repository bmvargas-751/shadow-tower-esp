# Decisiones

Lo que el usuario decidió, con fecha, para no volver a discutirlo. Una regla de STYLE.md, TECH.md o GLOSSARY.md que sale de aquí lo cita: [DECISIONS fecha].

- **2026-11-16** Proyecto creado con el kit de traducción de juegos. Repo en GitHub: `bmvargas-751/shadow-tower-esp`.
- **2026-11-16** Original: versión USA en inglés (SLUS-00863), imagen `Shadow Tower.bin` (MODE2/2352, una pista).
- **2026-11-16** Sin versión de apoyo: solo el inglés. Las dudas de género, sujeto omitido y trato se resuelven con el contexto o van a PENDING.md.
- **2026-11-16** Terminología oficial: no hay traducción oficial al español del juego ni de la serie; el glosario sale del propio juego.
- **2026-11-16** Variante: español neutro (*tú*/*ustedes*).
- **2026-11-16** Pruebas en DuckStation, cargando la imagen parcheada.
- **2026-11-16** Entrega: parche xdelta sobre la imagen USA.
- **2026-11-16** STYLE.md: se deja la base completa.
- **2026-11-16** Siglas de sistema: HP → **PV**, MP → **PM**, SP → **PA** (puntos de vida, de magia y de alma), también dentro de frases. [glosario]
- **2026-11-16** Nombres de personajes y criaturas: los inventados quedan igual (Auriel, Necron, Balron…); los descriptivos se traducen (Sand Leech → Sanguijuela de arena). [glosario]
- **2026-11-16** El glosario se revisa por secciones en el chat; lo aprobado pasa a GLOSSARY.md con fecha.
- **2026-11-16** La tabla de menús de `FDAT.T` (entrada 480) se traduce: el juego la carga con el menú abierto (estados 9 y 10).
- **2026-11-16** Glosario aprobado por secciones (≈ 290 filas en GLOSSARY.md): estadísticas, habilidades y tipos de criatura, estados y elementos, interfaz, datos de descripciones, tipos y afijos de equipo, mundos y lugares, personajes, criaturas y magias.
- **2026-11-16** Largo de etiquetas: las estadísticas no pasan de 20 caracteres (SHIELD MAGIC DEFENSE, la más larga del original); los lugares, de 21. Lo que pasa va en forma corta (abreviatura reconocible o sin la cabeza: LLUVIA BLANCA).
- **2026-11-16** DRAIN → ABSORCIÓN en toda la familia (ABSORCIÓN DE PV/PM, CAMPO DE ABSORCIÓN); COLD/FREEZE/FROST/ICE → HIELO; SOUL POD → FRASCO DE ALMA.
- **2026-11-16** SHADOW TOWER se traduce como lugar y en los datos guardados: TORRE DE LAS SOMBRAS. El logo del título no se toca.
- **2026-11-16** Títulos delante de un nombre en minúscula a media frase («el rey Kells», «el capitán Apollos»); usados como nombre, con mayúscula («el Rey», «el Amo»).
- **2026-11-16** GLOSSARY.md: se quita G-1 (no hay traducción oficial, PLAN).
- **2026-11-17** Fichas de personajes (characters/): 7 personajes, el narrador, una voz compartida para las 96 cajas sin hablante identificado y la ficha del jugador. El juego no dice quién habla: lo dedujo el perfilador (`characters/hablantes.json`, que la exportación agrega como `speaker`).
- **2026-11-17** Trato al jugador: *tú* por defecto; *usted* en Auriel, Apollos, el Caballero de Ébano y las voces G7 y G27 (registro formal).
- **2026-11-17** El protagonista es masculino («un joven guerrero»). Apollos, el Caballero de Ébano, Disfraz y Necron, masculinos (el juego no los marca). Auriel y Akryal, femeninas; Abraxus, masculino (los marca el juego).
- **2026-11-17** «demoness» → «diablesa» (Auriel). «MEMORY CARD» queda en inglés. La traducción de referencia del caso O-6 del set de oro dice «demonia» porque es anterior a esta decisión; el caso solo controla el trato, así que no se cambia (cambiarlo obliga a aprobar y probar el set otra vez).
- **2026-11-17** Piloto: END GAME → SALIR; TRADE → INTERCAMBIAR; DARK como elemento → OSCURIDAD (como estado sigue CEGUERA); `equip#0117` sin punto final para que entre en 5 renglones.
- **2026-11-17** Glosario: los afijos que concuerdan van en minúscula (el control del kit solo reconoce género y número en minúscula); las filas con paréntesis en «Inglés» (DARK (estado), R (ranura), ON (opción)…) quedan fuera del control automático; los nombres sin artículo (rey Edward, Caos…).
- **2026-11-17** Medidas en pies y pulgadas: la exportación las da con ′ y ″ (no comillas).
- **2026-11-17** Las casillas vacías del original (`stat/01#0116`, `stat/08#0504`, `vs_etc/15#0504`) van en `excluded` de `loc.json`: no hay texto que traducir.
