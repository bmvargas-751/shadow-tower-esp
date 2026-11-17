# shadow-tower-esp

Traducción al español neutro de *Shadow Tower* (PlayStation, versión USA, SLUS-00863), hecha con el kit de traducción de juegos. El repo tiene solo la traducción, los documentos y las herramientas propias: ningún archivo del juego.

- Método y decisiones: [PLAN.md](PLAN.md), [DECISIONS.md](DECISIONS.md)
- Estilo y términos: [STYLE.md](STYLE.md), [GLOSSARY.md](GLOSSARY.md), [characters/](characters)
- Técnica (formatos, fuentes, pruebas en el juego): [TECH.md](TECH.md)
- Pendientes del usuario: [PENDING.md](PENDING.md)

## Armar la imagen y el parche

Hace falta la imagen USA en `../shadow-tower-esp-local/original.bin` (SHA-1 `df441bf08b7079f8b3d36f1188f7eedd8cb73c50`).

- `python3 tools/st_build.py` → imagen traducida para probar, en `../shadow-tower-esp-local/test/`.
- `python3 tools/st_patch.py [VERSIÓN]` → parche `.xdelta` comprobado y paquete `.zip` para publicar, en `../shadow-tower-esp-local/dist/`. Necesita `xdelta3` (`sudo apt install xdelta3`, o la variable `XDELTA3`).

Cómo se aplica el parche: [tools/release/LEEME.txt](tools/release/LEEME.txt). Cambios: [CHANGELOG.md](CHANGELOG.md).

## Avance

Actualizado: 2026-11-17.

### Fases

| Fase | Estado |
|---|---|
| 0. Decisiones | ✅ |
| 1. Prueba técnica | ✅ (falta ver una conversación redibujada en el juego) |
| 2. Inventario y costo | ✅ 2244 líneas, ~950k tokens estimados |
| 3. Glosario y fichas | ✅ 287 términos, 7 personajes y 3 voces |
| 4. Set de oro | ✅ 14 de 14 (oro-001) |
| 5. Piloto | ✅ 4 lotes de 40 líneas (menús, objetos, equipo, diálogos) |
| 6. Traducción | ✅ 100 % (2217 líneas; dudas en PENDING.md) |
| 7. Prueba en el juego | ⏳ primera ronda corregida (anchos de menús, objetos y EQUIP; PENDING.md) |
| 8. Entrega (parche xdelta) | ⏳ 0.9.0 publicada como versión de prueba ([releases](https://github.com/bmvargas-751/shadow-tower-esp/releases)); la 1.0, después de la fase 7 |

### Secciones

<!-- loc:progress -->
**Etapa actual:** Fase 7. Prueba en el juego

| Sección | Líneas | Traducidas | Avance |
|---|---:|---:|---:|
| Introducción | 6 | 6 | 100,0 % |
| Interfaz y menús | 448 | 448 | 100,0 % |
| Estadísticas | 106 | 106 | 100,0 % |
| Nombres de criaturas | 153 | 153 | 100,0 % |
| Objetos y equipo | 760 | 760 | 100,0 % |
| Modo VS | 160 | 160 | 100,0 % |
| Diálogos | 112 | 112 | 100,0 % |
| Descripciones de equipo | 321 | 321 | 100,0 % |
| Descripciones de criaturas | 151 | 151 | 100,0 % |
| **Total** | **2.217** | **2.217** | **100,0 %** |
<!-- /loc:progress -->
