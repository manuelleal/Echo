# Preregistro del piloto: tutor de inglés offline en el SENA

Fecha de escritura: 5 de noviembre de 2026. Escrito ANTES del piloto (9–18 de noviembre de 2026). Instructor responsable: Christiam Puentes. Lugar: SENA Málaga, Santander (ADSO o Animación Digital). Reporte: 19 de noviembre de 2026.

## Pregunta

Cuando aprendices reales del SENA usan, durante dos sesiones, un tutor de práctica de inglés que corre sin internet en un Chromebook Dell 11 de 2014: **¿el sistema funciona en la práctica (rápido, estable) y sus correcciones le parecen pertinentes al instructor, y los aprendices lo perciben útil?**

Es un piloto de factibilidad y uso. No mide aprendizaje.

## Qué se va a medir

| Métrica | Cómo |
|---|---|
| n de aprendices | Sesiones con código anónimo distinto en el CSV |
| Interacciones por aprendiz | Turnos por código de sesión (mediana y rango) |
| Tiempo de respuesta | Columnas `segundos` y `segundos_primera_respuesta`: mediana, rango (mín.–máx.) e IQR. No se reportan medias solas |
| Fallos del sistema | % de turnos con `estado` = error |
| Correcciones pertinentes | Juicio a ciegas del instructor (ver abajo), con intervalo de Wilson al 95 % |
| Percepción | Encuesta final de 5 ítems (escala 1–5): mediana por ítem |
| Conectividad | Encuesta anónima: ¿internet en casa?, ¿datos en el celular? (conteos) |

**Juicio a ciegas.** El instructor revisa una muestra de hasta 60 pares (frase del aprendiz, respuesta del tutor), barajada con semilla fija, sin ver la sesión ni la hora. Marca cada par como `pertinente`, `no pertinente` o `dañina` (corrección que enseña algo falso o confunde). La muestra incluye sólo turnos en que el tutor mostró alguna corrección. No se juzgan los errores que el tutor no detectó (limitación declarada).

## Criterios de éxito y de fracaso (fijados hoy)

| Medida | Éxito | Fracaso | Entre medio |
|---|---|---|---|
| Correcciones pertinentes | ≥ 70 % | < 50 % | 50–69 %: no concluyente |
| Correcciones dañinas | ≤ 5 % | > 10 % | 5–10 % |
| Turnos con fallo del sistema | ≤ 5 % | > 15 % | 5–15 % |
| Tiempo de respuesta (mediana de `segundos`) | ≤ 10 s | > 15 s | 10–15 s |
| Aprendices que participan (n) | ≥ 12 | < 6 | 6–11 |
| Turnos por aprendiz (mediana) | ≥ 8 | < 4 | 4–7 |
| Encuesta, utilidad (mediana, 1–5) | ≥ 4 | ≤ 2 | 3 |

**Veredicto global.** ÉXITO si se cumplen todos los criterios de éxito de pertinencia, fallos, tiempo y n. FRACASO si se cumple cualquier criterio de fracaso en pertinencia, dañinas, fallos o tiempo. En otro caso: RESULTADO MIXTO, y se reporta tal cual. Los umbrales no se cambian después de ver los datos; si se cambia alguno, se declara como desviación en el reporte.

## Qué NO se va a afirmar

- Que los aprendices **aprendieron** inglés o mejoraron (no hay prueba previa ni posterior).
- Que el tutor es **eficaz** como método de enseñanza.
- **Generalización** a otros grupos, centros, niveles, otros temas o a otras situaciones fuera de tienda, entrevista y proyecto.
- **Comparación** con otras aplicaciones, tutores humanos o con no usar nada.
- Que las cifras previas (bancos sintéticos: 59 de 90 frases con error detectadas, 1 de 30 correctas marcada) sean válidas con personas; fueron frases fabricadas, no aprendices.

## Qué sí se reportará

Todos los resultados, incluidos los malos; n real; turnos fallidos; las limitaciones (un solo juez, muestra pequeña, aprendices voluntarios, un Chromebook que atiende un turno a la vez).

## Datos

Sólo el registro anónimo (código de sesión, no nombres). Descarga en CSV desde `/api/registro.csv`. Análisis con `analiza_piloto.py` (semilla fija). El CSV y el informe se guardan sin datos identificables.
