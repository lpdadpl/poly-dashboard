# Dashboard Mesa POLY (Polymarket EN PAPEL)

Oficina pixel art 16 bits con los 7 bots (SCOUT, RISK, WHALE, NEWS, QUANT, TRADER, EXIT) y JEFE POLY (figura original), embudo de operaciones (escaneado → aprobado → confirmado → valorado → ejecutado → resuelto), saldo/PnL, actividad y visor de archivos de solo lectura. Se sincroniza cada 30 s. Sin dinero real ni carteras.

Solo Python 3 estándar: `python3 server.py`

## Variables de entorno
| Variable | Obligatoria | Descripción |
|---|---|---|
| `POLY_PASS_ALBERTO` | sí | Contraseña del usuario `alberto` (HTTP Basic) |
| `POLY_PASS_NACHO` | sí | Contraseña del usuario `nacho` |
| `POLY_DIR` | no | Carpeta de datos (por defecto `/workspace/poly`) |
| `PORT` | no | Puerto (por defecto `8080`) |

Si falta alguna contraseña el servidor no arranca. Las contraseñas nunca van en el código: en Render se ponen como variables secretas (`sync: false` en `render.yaml`). La carpeta `data/` trae archivos de ejemplo para el despliegue.

Endpoints: `/` (panel), `/api/data` (JSON), `/api/file?path=...` (solo archivos dentro de `POLY_DIR`).
