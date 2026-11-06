# Piloto real del tutor de inglés offline (SENA Málaga, 9–18 nov 2026)

Instructor: Christiam Puentes. Reporte: 19 de noviembre de 2026. Nunca antes usado con estudiantes reales.

## Documentos y orden de uso

1. `PREREGISTRO_piloto.md`: pregunta, métricas y criterios de éxito/fracaso. Fechado 5-nov-2026. No se cambia después de ver datos. Guárdelo (ideal: copia con fecha en un lugar público o sellado) antes del 9 de nov.
2. `CONSENTIMIENTO_adultos.md` y `CONSENTIMIENTO_menores_acudiente.md`: imprimir y firmar ANTES de la primera sesión. Se guardan aparte del CSV.
3. `PROTOCOLO_sesiones.md`: guía de las dos sesiones (minuto a minuto, preparación, fallos, plan B, descarga del CSV).
4. `ENCUESTA_final.md`: se aplica al final de la sesión 2, anónima, con el código de sesión.
5. `analiza_piloto.py`: después del piloto.
   - `python analiza_piloto.py registro.csv` crea `muestra_ciega.csv` e `informe_piloto.md`.
   - El instructor llena `juicio_instructor` (pertinente / no pertinente / dañina) sin ver sesión ni hora.
   - `python analiza_piloto.py registro.csv --juicios muestra_ciega.csv` agrega % de pertinentes con intervalo de Wilson 95 %.
6. Reporte del 19 de nov: contrastar el informe con los criterios del preregistro y reportar todo, también lo malo.

No se afirman aprendizaje, eficacia, generalización ni comparación con otras apps.
