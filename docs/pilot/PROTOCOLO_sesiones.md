# Protocolo de sesiones del piloto

Dos sesiones de 30 a 40 minutos por grupo, entre el 9 y el 18 de noviembre de 2026. Sólo participan quienes tengan el consentimiento firmado (y el acudiente, si es menor).

## Límite importante: un aprendiz a la vez

El tutor responde a un aprendiz por vez. Cada turno tarda unos 2–8 s en modo práctica y unos 6 s de mediana en modo corrector. La primera consulta tras arrancar tarda cerca de 1 minuto. Si todos escriben a la vez, se forma fila y los tiempos suben.

**Recomendación:** grupos de **3 a 4 aprendices por Chromebook**, rotando. Mientras uno conversa con el tutor, los demás miran la pantalla o su celular y preparan su siguiente frase en un papel. Cada aprendiz hace bloques de 5–8 minutos. Con grupos grandes, haga dos turnos de 30–40 min el mismo día o en días distintos.

## Preparación del instructor (15 min antes)

1. Encienda el Chromebook, conéctelo al cargador y a la red local (router o punto de acceso; no necesita internet).
2. Abra la terminal y ejecute: `bash ~/f2/biblioteca/demo/arranca_demo.sh`
3. Espere a que aparezca **"listo"**. No lance nada más hasta verlo.
4. Haga una consulta de prueba (la primera tarda ~1 min) para dejarlo caliente. Anote la hora.
5. Conecte los celulares a la misma red y abra la dirección del tutor. Verifique que cargue en uno.
6. Dé a cada aprendiz un **código de sesión** (el que muestra el tutor, tipo S-3F2A). Anótelo sólo junto a un número de lista que usted no guardará con el nombre. No escriba nombres en el tutor.
7. Tenga a mano consentimientos firmados, encuesta impresa o abierta, papel y lápiz.

## Sesión 1 (35 min): conocer el tutor

| Min | Aprendiz | Instructor |
|---|---|---|
| 0–5 | Escucha qué es el tutor, que puede equivocarse y que no es nota. Recibe su código. | Explica, resuelve dudas, recuerda que puede retirarse. |
| 5–9 | Modo **tienda**: pide dos cosas y pregunta el precio ("I want two bananas. How much is it?"). | Observa; no ayuda con el inglés. |
| 9–14 | Sigue en **tienda**: pregunta si hay algo más barato, se despide. Mínimo 5 turnos. | Anota fallos y esperas largas. |
| 14–20 | Modo **entrevista**: responde "Tell me about yourself" y por qué quiere el trabajo. Mínimo 5 turnos. | Anota si las pistas se entienden. |
| 20–27 | Modo **corrector**: escribe 5 frases suyas sobre su día (con las dudas reales que tenga). Lee la corrección. | Observa si copia o ignora las pistas. |
| 27–31 | Vuelve a decir una de las frases ya corregida, sin mirarla. | Observa; no corrige. |
| 31–35 | Resumen final del tutor. Comenta en voz alta qué entendió. | Toma nota de comentarios. |

## Sesión 2 (35 min): uso más libre

| Min | Aprendiz | Instructor |
|---|---|---|
| 0–3 | Recuerda su código. | Verifica el arranque; consulta de prueba. |
| 3–12 | Modo **proyecto**: presenta su proyecto como en una feria (qué es, para qué sirve, qué tecnología usa). Mínimo 6 turnos. | Observa y anota. |
| 12–20 | Elige la situación que quiera (tienda, entrevista o proyecto) y repite, intentando evitar el error que más le marcaron. | Anota qué elige. |
| 20–26 | Modo **corrector**: 5 frases nuevas con lo que quería decir y no sabía. | Observa. |
| 26–29 | Resumen final. | — |
| 29–35 | Responde la **encuesta final** (anónima, con su código). | Entrega la encuesta; no la mira mientras la llenan. |

## Qué observa el instructor

- Esperas largas (> 10 s), pantallas congeladas, mensajes de error.
- Si los aprendices entienden las pistas en español.
- Frases que el tutor corrigió mal o de forma rara (anótelas con hora; luego aparecerán en el CSV).
- Si alguien se frustra, se aburre o deja de participar.
- Cuántos usan el celular y cuántos el Chromebook.

Anote en papel, sin nombres. No intervenga en el inglés del aprendiz durante el uso.

## Si algo falla

| Problema | Qué hacer |
|---|---|
| El tutor tarda más de 1 min en un turno (salvo la primera consulta) | Espere 1 min más. Si no responde, reinicie el script de arranque y espere "listo". |
| No aparece "listo" | Reinicie el Chromebook y repita el arranque. Si falla dos veces, plan B. |
| Un celular no conecta | Verifique que esté en la misma red; si no, ese aprendiz usa el Chromebook por turnos. |
| Mensaje de error del tutor | Anote la hora y la frase; el turno queda en el CSV como error. Reintente una vez. |
| Se apaga o se cuelga | Guarde la hora, reinicie y continúe donde iba. No repita turnos para "compensar". |

## Plan B (si el Chromebook no funciona)

1. Suspenda la sesión y anótelo (hora y motivo). No se inventan turnos.
2. Si hay otro computador con el tutor, úselo; si no, haga la actividad en papel: los aprendices escriben las mismas frases de la tabla y el instructor las corrige oralmente. **Esa actividad no cuenta como dato del piloto**, sólo como clase.
3. Reprograme la sesión dentro del 9–18 de noviembre si es posible. Si no, se reporta la sesión perdida.
4. La encuesta se puede aplicar igual si ya usaron el tutor al menos una vez.

## Al final: descargar el CSV

1. Con el tutor aún encendido, en el Chromebook abra `/api/registro.csv` (ejemplo: `http://<dirección-del-tutor>/api/registro.csv`) y guarde el archivo, o descárguelo desde otro dispositivo en la red.
2. Nómbrelo con fecha, por ejemplo `registro_2026-11-12.csv`. Haga una copia en una memoria USB.
3. Revise que tenga las columnas: `sesion, turno, timestamp, tipo_entrada, ambito, texto_aprendiz, frase_corregida, n_errores, n_verificadas, errores, pregunta_tutor, segundos_primera_respuesta, segundos, estado, error_sistema`.
4. Revise rápido que no haya nombres ni teléfonos escritos por los aprendices; si los hay, tápelos antes de guardar o compartir el archivo.
5. Guarde los consentimientos firmados en un lugar separado del CSV.
