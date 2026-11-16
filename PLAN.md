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

- [ ] Extraer los archivos del juego, a una carpeta fuera del repo.
- [ ] Adaptador: exportar el texto al formato común (`source` de `loc.json`) e importarlo de vuelta.
- [ ] Ida y vuelta idéntica: exportar e importar sin cambios da los mismos archivos.
- [ ] Caracteres: si la fuente tiene las letras españolas, o cómo se agregan (T-5).
- [ ] Límites: bytes, ancho y renglones de cada tipo de texto (T-3, T-4), y sus chequeos en `hooks`.
- [ ] Pseudolocalización: todo el texto más largo y con letras españolas, en el juego, para ver cortes y glifos que faltan.
- [ ] Completar TECH.md y `loc.json` (`codes`, `fixed_break`, `excluded`, `sections`).

### Fase 2. Inventario y presupuesto

- [ ] Volumen por sección (`loc.py progress`).
- [ ] Costo estimado por sección, antes de empezarla.

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
