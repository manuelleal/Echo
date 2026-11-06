# Plan de implementación — la Biblioteca de Comportamiento (4-nov-2026)

**Idea del director:** no depender de entrenar el modelo. El comportamiento con cada usuario lo definen **datos que vamos guardando y curando**. El modelo base no cambia; lo que crece y viaja es la biblioteca.

**Evidencia propia de partida:** sin tocar los pesos, 16 ejemplos en el prompt subieron la detección de 46 a 52 de 60 en el banco ciego v2, con 0/20 falsas (McNemar p = 0,031; TUTOR-LOCAL-EVAL/medicion_banco_v2).
**Respaldo en la literatura:**
- El estilo se copia fácil y la exactitud no: Gudibande 2023, arXiv 2305.15717.
- La pedagogía con evidencia (pista y reintento, repaso espaciado, trazado del conocimiento) no depende del tamaño del modelo: nota 04.

## 1. Los cajones (todo texto plano / JSON, versionado en git)
```
biblioteca/
  fichas/          una ficha por regla: id, regla_es, ejemplo_mal, ejemplo_bien, pista_es, nivel, fuente, aprobada_por
  ejemplos/        conversaciones cortas de buen comportamiento: situación, rol, turnos, por_que, ficha_id, origen, aprobado
  estudiantes/     un JSON por alias (sin nombres reales): dominio por regla, errores recientes, próximo repaso
  profe/           bitácora de lo que el docente aceptó, editó o rechazó (alimenta fichas y ejemplos)
  MANIFIESTO.json  versión, sha256 de cada archivo y del modelo base con el que se probó
```

## 2. Cómo se usa en cada consulta (camino rápido en el N2840)
1. **Diagnóstico** (sin LLM, < 0,1 s): la gramática ERG y las reglas propias → `ficha_id` o "no sé".
2. **Recuperar** (BM25 en Python puro, < 0,1 s): 1–2 ejemplos de esa ficha y del rol actual.
3. **Prompt:** prefijo FIJO en caché, luego los ejemplos y la frase.
   - **Truco medido:** guardar en disco un estado KV por cada ficha (sistema + sus ejemplos) y restaurarlo en 8–10 ms (`--slot-save-path`, INFORME de latencia). Así los ejemplos no cuestan tiempo de lectura.
4. **Respuesta:** el LLM conversa y redacta. La regla y la pista salen de la ficha, nunca inventadas.
5. **Consecuencia:** lo que haga el aprendiz (corrige o no) actualiza su memoria; lo que haga el profe va a `profe/`.

## 3. Fases
| Fase | Qué | Criterio de "listo" | Costo |
|---|---|---|---|
| F0 | Formatos JSON, validador y 10 fichas escritas por Christiam (los errores de su aula) | El validador pasa y el profe aprueba las 10 | 0 |
| F1 | **Piloto:** 50 ejemplos generados por Claude (sin ver los bancos) y curados; recuperación BM25; prompt armado | Preregistro abajo | < 3 USD de API |
| F2 | Estados KV por ficha guardados y restaurados en el N2840 | Latencia por consulta medida contra el tutor actual | 0 |
| F3 | Memoria del estudiante y bitácora del profe (el ciclo de alefast) | Una semana de uso simulado sin romper nada | 0 |
| F4 | **Paquete portable:** carpeta con modelo + binario + biblioteca + `arrancar.sh`, con sha256; sincronizar sólo la biblioteca por USB | Se copia a otro equipo y corre igual (mismas salidas con temperatura 0) | 0 |
| F5 | Skill "biblioteca" que genera y cura con la API, con un tope de gasto que no se pueda pasar | Corre con el tope y deja el gasto registrado | según el tope |

## 4. Preregistro del piloto F1 (antes de construir)
- **Pregunta:** ¿una biblioteca de 10 fichas + 50 ejemplos, con recuperación, iguala o supera al prompt v2 fijo, usando menos tokens por consulta?
- **Brazos** (mismo modelo 0,5B Q4_0, temperatura 0):
  - (a) prompt v1 sin ejemplos;
  - (b) prompt v2 fijo, el rival fuerte (52/60);
  - (c) biblioteca con recuperación;
  - (d) control: biblioteca con ejemplos al azar de otra ficha.
- **Medida:** banco ciego v2 (detección /60, falsas /20) en el PC, más la latencia y los tokens por consulta en el N2840.
- **Predicción:** (c) ≥ (b) − 2 en detección, ≤ 1/20 falsas, y ≤ 60 % de los tokens de (b); (c) > (d) por ≥ 3.
- **Veredicto:**
  - FUNCIONA si se cumple todo.
  - HAY ALGO MODESTO si (c) ≥ (b) − 4.
  - NO si (c) < (a) o si (c) ≤ (d).
- **Reglas:** quien genere ejemplos no ve los bancos (ERR-T1); hay cruce de solape antes de medir; auditor de sólo lectura.

### Enmienda 1 (4-nov-2026, escrita y commiteada ANTES de correr ningún brazo)
Al leer el arnés (`TUTOR-LOCAL-EVAL/medicion_banco_v2`) aparecieron tres cosas que el preregistro no fijaba:
1. **Modelo:** el 52/60 de v2 se midió con el 1,5B Q4_K_M del PC, no con el 0,5B. Para respetar "mismo modelo 0,5B Q4_0", **los cuatro brazos se corren de nuevo** con `qwen05-q4_0-cabezaq4.gguf` (sha 7cb9e930…), el modelo que va en el Chromebook (H06). Mismo binario llama-server del PC y mismos parámetros del tutor (temperatura 0, semilla 42, contexto 2048). El rival (b) es v2 **medido con ese modelo**, no el 52/60 histórico.
2. **Qué cambia en (c) y (d):** sólo el paso a1 (los ejemplos de corrección), igual que v2.
   - (c) = sistema v1 + los 4 ejemplos base de v1 + **K = 4 pares** recuperados con BM25 sobre la frase del aprendiz.
   - Los pares salen de la biblioteca aprobada: el `ejemplo_mal → ejemplo_bien` de cada ficha y, de cada conversación, la frase del aprendiz con error emparejada con su reintento corregido. El emparejamiento es automático: similitud ≥ 0,5, largo entre 0,7 y 1,3 y sin español; si un par no cumple, se descarta.
   - Sin líneas de regla en el sistema.
   - (d) = igual, pero los 4 pares son al azar (semilla = crc32 de la frase), de fichas distintas a la del primer par que habría recuperado (c).
3. **Tokens:** se usa el total de tokens de prompt por consulta (a1 + a2 + pregunta), como dice el texto, que es la lectura más exigente. También se reporta el de a1.
4. **Latencia en el N2840:** no entra en esta corrida; se mide en F2. Aquí se reporta la del PC sólo como dato.
5. **Cupo del banco v2:** "máximo 6 candidatos". B1–B5 usaron 5, (c) es el 6.º, (d) es un control y (a), (b) son repeticiones. **Después de esta corrida el banco v2 queda agotado** y lo siguiente necesita un banco v3.
- **Ajuste 1a (aún sin correr ningún brazo):** al revisar los pares de la biblioteca (no los del banco), uno enseñaba a borrar palabras ("…an report about pigs for the class" → "…a report about pigs."). Por eso se exige además un máximo de 3 palabras cambiadas por par.
  - También se descarta el par que borra palabras; moverlas sí vale, por el orden del adjetivo.
  - Se usa el último reintento del aprendiz, porque el anterior puede seguir con error ("watchs").
  - La puntuación final la pone la frase mala.
  - Las palabras incluyen los números, para emparejar bien "She have 6 years".
  - Resultado: **43 pares** (10 de fichas y 33 de conversaciones), al menos 2 por ficha. Código: `biblioteca/recuperar.py`.
- **Puntaje:** `banco_v2/puntua_v2.py` sin modificar; McNemar exacto para (c) vs (b) y (c) vs (d) con `compara`, al estilo del RESUMEN v2.
