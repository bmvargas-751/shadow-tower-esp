# Plan

## Decisiones

Se cierran en la fase 0, porque son caras de cambiar después.

- **Variante:** español neutro (*tú*/*ustedes*, sin regionalismos de ningún país).
- **Original:** versión USA en inglés (SLUS-00863). [DECISIONS 2026-11-16]
- **Otra versión de apoyo:** ninguna; solo el inglés. [DECISIONS 2026-11-16]
- **Terminología oficial:** no hay traducción oficial al español. [DECISIONS 2026-11-16]
- **Pruebas:** DuckStation; la traducción se instala con un parche xdelta sobre la imagen USA. [DECISIONS 2026-11-16]
- **Sin spoilers:** los documentos, los commits y el chat nombran zonas o archivos, nunca hechos de la historia.
- **Contenido del repo:** solo la traducción y las herramientas propias; nunca archivos del juego.

## Fases

### Fase 0. Antes de empezar

- [x] Cerrar las decisiones de arriba con el usuario.
- [x] Revisar con el usuario la base de STYLE.md: lo que no aplique se borra. (Se dejan todas, 2026-11-16.)

### Fase 1. Prueba técnica

Antes de esto no se decide nada más.

- [x] Extraer los archivos del juego, a una carpeta fuera del repo.
- [x] Adaptador: exportar el texto al formato común (`source` de `loc.json`) e importarlo de vuelta. (Texto codificado listo: `tools/st_text.py`, 1654 líneas. Texto en imágenes: `tools/st_image.py` exporta 584 textos y `tools/st_render.py` los vuelve a dibujar; introducción con `tools/st_intro.py`; faltan los paneles de 16 bpp.)
- [x] Ida y vuelta idéntica: exportar e importar sin cambios da los mismos archivos. (Texto codificado e imágenes: idéntica.)
- [x] Caracteres: si la fuente tiene las letras españolas, o cómo se agregan (T-5). (Imágenes y texto codificado: probados en el juego, pruebas 6 a 8.)
- [x] Límites: bytes, ancho y renglones de cada tipo de texto (T-3, T-4), y sus chequeos en `hooks`. (Cajas de imágenes en `hooks.check`; espacio del texto codificado con deduplicación, probada en el juego.)
- [x] Pseudolocalización: todo el texto más largo y con letras españolas, en el juego, para ver cortes y glifos que faltan. (Pruebas 2 a 8: letras, cajas de equipo, criaturas e introducción vistas en el juego; falta una conversación.) (Una conversación redibujada queda para la fase 7.)
- [x] Completar TECH.md y `loc.json` (`codes`, `fixed_break`, `excluded`, `sections`).

### Fase 2. Inventario y presupuesto

- [x] Volumen por sección (`loc.py progress`).
- [x] Costo estimado por sección, antes de empezarla.

Estimación (2026-11-16): referencia del kit de ~43 000 tokens por agente cada 250 líneas de ~60 caracteres, más ~15 000 fijos por lote y agente (documentos); tres agentes por lote (traductor, revisor, corrector). Se cuentan los textos únicos, porque el kit copia los repetidos.

| Sección | Líneas | Únicas | Caracteres | Tokens estimados |
|---|---:|---:|---:|---:|
| Introducción | 6 | 6 | 232 | ~47k |
| Interfaz y menús | 472 | 337 | 5014 | ~127k |
| Estadísticas | 107 | 81 | 989 | ~52k |
| Nombres de criaturas | 153 | 149 | 1442 | ~57k |
| Objetos y equipo | 760 | 324 | 10956 | ~134k |
| Modo VS | 162 | 72 | 1666 | ~53k |
| Diálogos | 112 | 111 | 7557 | ~110k |
| Descripciones de equipo | 321 | 265 | 15328 | ~206k |
| Descripciones de criaturas | 151 | 151 | 14432 | ~169k |
| **Total** | **2244** | **1496** | **57616** | **~950k** |

Más el editor, las líneas delicadas y el set de oro (fase 4). Las secciones chicas (introducción, VS, estadísticas) conviene juntarlas en un mismo lote para no pagar el costo fijo varias veces.

### Fase 3. Documentos

- [x] Glosario: el terminólogo propone las filas. (2026-11-16: 285 filas aprobadas por el usuario, por secciones.)
- [x] Fichas de personajes: el perfilador, antes de cada sección. (2026-11-17: todos los diálogos de una vez; género y trato aprobados.)
- [x] DECISIONS.md y PENDING.md al día.

### Fase 4. Set de oro

Obligatorio: sin él, `loc.py prepare` no arma lotes.

- [x] Elegir con el usuario los casos reales (al menos uno de cada tipo; mejor dos o tres). (2026-11-17: 14 casos, dos por tipo.)
- [x] Aprobarlo (`loc.py golden approve`).
- [x] Probar a los agentes (`loc.py golden prepare`, traductor, revisor y corrector, `loc.py golden score`) hasta que pase. (2026-11-17: oro-001, 14 de 14.)

### Fase 5. Piloto

- [x] Un primer lote de cada tipo de texto con el equipo completo. (2026-11-17: piloto-menus, piloto-objetos, piloto-equipo, piloto-dialogos; 160 líneas, 281 con copias.)
- [x] Ajustar documentos y roles con lo que salga (y volver a pasar el set de oro si cambia un prompt). (Glosario y exportación ajustados; ningún prompt cambió.)

### Fase 6. Traducción

- [x] Introducción (2026-11-17: chicas-001).
- [x] Interfaz y menús (2026-11-17: piloto-menus, menus-001 y criaturas-001).
- [x] Estadísticas (2026-11-17: chicas-001).
- [x] Nombres de criaturas (2026-11-17: criaturas-001).
- [x] Objetos y equipo (2026-11-17: piloto-objetos, objetos-001 y equipo-001).
- [x] Modo VS (2026-11-17: chicas-001).
- [x] Diálogos (2026-11-17: piloto-dialogos y diálogos-001).
- [x] Descripciones de equipo (2026-11-17: piloto-equipo, equipo-001 y equipo-002).
- [x] Descripciones de criaturas (2026-11-17: criaturas-desc-001).

### Fase 7. Prueba en el juego

- [x] Imagen completa con la traducción: `tools/st_build.py` → `../shadow-tower-esp-local/test/shadow-tower-esp.{bin,cue}` (2026-11-17).
- [ ] Jugar con la traducción completa y anotar cortes, cajas que se pasan, glifos que faltan y texto que quedó sin traducir. Mirar también los puntos de «Para la prueba en el juego» de PENDING.md y una conversación redibujada (fase 1).

### Fase 8. Entrega

- [x] Parche y paquete: `tools/st_patch.py` arma la imagen, crea el `.xdelta` (sin compresión secundaria, para que sirva en cualquier parcheador), lo comprueba aplicándolo sobre el original y deja `../shadow-tower-esp-local/dist/shadow-tower-esp-VERSIÓN.zip` con el parche, `LEEME.txt` (de `tools/release/`) y CHANGELOG.md. (2026-11-17: 1.0, parche de ~1 MB; la imagen sale idéntica en cada armado.)
- [x] Registro de cambios: CHANGELOG.md.
- [ ] Confirmar en la prueba del juego lo que afirma LEEME.txt: que las partidas de la versión en inglés sirven, y que el título, los créditos y los logos quedan en inglés.
- [x] Versión de prueba 0.9.0: release de GitHub `v0.9.0` (marcado como *Latest*, con «versión de prueba» en el título y las notas) con el `.zip` (2026-11-17), para probar la descarga y el parcheo como cualquier jugador.
- [x] Versión de prueba 0.9.1: correcciones de la primera ronda en el juego (2026-11-17).
- [x] Versión de prueba 0.9.2: alineación de menús (`ST.EXE`) y grebas en plural (2026-11-17).
- [ ] Publicación de la 1.0: cuando cierre la fase 7, CHANGELOG.md con la fecha y un *release* de GitHub con el `.zip` (lo confirma el usuario antes).
