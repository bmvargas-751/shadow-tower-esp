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
- [ ] Adaptador: exportar el texto al formato común (`source` de `loc.json`) e importarlo de vuelta. (Texto codificado listo: `tools/st_text.py`, 1654 líneas. Texto en imágenes: `tools/st_image.py` exporta 584 textos y `tools/st_render.py` los vuelve a dibujar; introducción con `tools/st_intro.py`; faltan los paneles de 16 bpp.)
- [x] Ida y vuelta idéntica: exportar e importar sin cambios da los mismos archivos. (Texto codificado e imágenes: idéntica.)
- [x] Caracteres: si la fuente tiene las letras españolas, o cómo se agregan (T-5). (Imágenes: dibujadas. Texto codificado: en celdas libres de las láminas A y B, probado en el juego; diseño de B por confirmar en la prueba 8.)
- [ ] Límites: bytes, ancho y renglones de cada tipo de texto (T-3, T-4), y sus chequeos en `hooks`.
- [ ] Pseudolocalización: todo el texto más largo y con letras españolas, en el juego, para ver cortes y glifos que faltan.
- [ ] Completar TECH.md y `loc.json` (`codes`, `fixed_break`, `excluded`, `sections`).

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

- [ ] Glosario: el terminólogo propone las filas.
- [ ] Fichas de personajes: el perfilador, antes de cada sección.
- [ ] DECISIONS.md y PENDING.md al día.

### Fase 4. Set de oro

Obligatorio: sin él, `loc.py prepare` no arma lotes.

- [ ] Elegir con el usuario los casos reales (al menos uno de cada tipo; mejor dos o tres).
- [ ] Aprobarlo (`loc.py golden approve`).
- [ ] Probar a los agentes (`loc.py golden prepare`, traductor, revisor y corrector, `loc.py golden score`) hasta que pase.

### Fase 5. Piloto

- [ ] Un primer lote de cada tipo de texto con el equipo completo.
- [ ] Ajustar documentos y roles con lo que salga (y volver a pasar el set de oro si cambia un prompt).

### Fase 6. Traducción

- [ ] (una casilla por sección de `loc.json`)

### Fase 7. Prueba en el juego

- [ ] Jugar con la traducción completa y anotar cortes, cajas que se pasan, glifos que faltan y texto que quedó sin traducir.

### Fase 8. Entrega

- [ ] Instalador, registro de cambios y publicación.
