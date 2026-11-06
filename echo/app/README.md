# Echo: app (modo desarrollo)

Servidor HTTP del tutor conversacional (`demo.py`) y quiosco.

## Correr en desarrollo

Requisitos: Python 3, un servidor `llama-server` (llama.cpp) con el modelo Qwen2.5-0.5B Q4_0 en el puerto 8097, y ACE + ERG 2025 «educ» (ver README raíz).

```bash
export ERG_DIR=/ruta/a/simbolico_ace      # carpeta con ace-0.9.34/ y los .dat de la ERG
export ERG_ACE=$ERG_DIR/ace-0.9.34/ace
# desde la raíz del repositorio:
cd echo/app
python3 -B demo.py --tutor ../vendor --puerto 8080
# abrir http://localhost:8080
```

- `--tutor` apunta a la carpeta que CONTIENE el paquete `tutor/` (aquí `echo/vendor`).
- El audio pregrabado va en `echo/app/audio/` (no está en el repositorio; ver `voz/`).
- Sin audio la app funciona, pero sin voz.
- El registro anónimo de uso se escribe en CSV; está excluido por `.gitignore`.

## Rutas absolutas a ajustar

Los scripts de `quiosco/`, `arranca_demo.sh` y `voz/revisa_e_instala.py` conservan rutas del Chromebook original (`/home/christiam/f2/...`, `/home/christiam/llama/...`) y marcadores `IP_DEL_CHROMEBOOK` / `IP_DEL_SERVIDOR`. Ajústalos a tu equipo. `core/erg/erg.py` usa `ERG_DIR` (por defecto `/home/ddiddimmo/simbolico_ace`).
