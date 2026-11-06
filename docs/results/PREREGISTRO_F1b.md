# Preregistro F1b — las fichas como detectores sin LLM (4-nov-2026, antes de construir y de ver el banco v3)

**Motivo:** F1 dio NO (biblioteca 40/60 = azar 40/60; en el 0,5B los ejemplos en el prompt casi no mueven nada). Hipótesis: en el 0,5B la corrección debe salir de reglas deterministas escritas desde las fichas aprobadas; el LLM sólo corrige lo que las reglas no cubren y conversa.

**Banco:** v3 ciego, construido por un agente aparte que no ve `CHROMEBOOK-CANDY` (ERR-T1).
- 120 frases: 90 con error y 30 correctas, con palabras trampa bien usadas.
- Se puntúa con `banco_v2/puntua_v2.py` sin modificarlo.
- El constructor de los detectores (el coordinador) no lo abre. Cupo: 6 candidatos.

**Desarrollo (lo único que se puede mirar al construir):**
- Positivos: los 43 pares de la biblioteca (`recuperar.pares()`).
- Negativos: las frases en inglés correcto de la biblioteca (lado "bien" y turnos del tutor) y 20 frases trampa escritas por el coordinador antes de abrir nada.
- Meta en desarrollo, antes de correr el banco: los detectores corrigen bien ≥ 80 % de los positivos y tocan ≤ 2 % de los negativos.

**Brazos** (0,5B cabezaq4, temperatura 0, mismo arnés que F1 con `corre_eval.py` sin modificar):
- (a) v1 sólo LLM: línea base.
- (r) rival trivial: v1 + las dos reglas a mano del 15-oct (edad con "have", "Actually" inicial), con sus dos excepciones (`medicion_banco_v2/rival_trivial.py`). Es el rival a vencer.
- (e) **detectores + LLM**: las 10 fichas como reglas se aplican primero y el v1 corrige después la frase ya corregida. Los errores se cuentan contra la frase original del aprendiz, como siempre.
- (s) **sólo detectores**: sin LLM en la corrección. Mide cuánto cubren las reglas solas.

**Predicciones (pueden fallar):**
1. (e) detecta más que (a) con McNemar exacto p < 0,05.
2. (e) ≥ (r) + 3 en detección (/90).
3. Falsas de (e) ≤ falsas de (a) + 1 (/30).

**Veredicto:**
- FUNCIONA si se cumplen 1, 2 y 3.
- HAY ALGO MODESTO si (e) > (a) y se cumple 3, pero falla 1 o 2.
- NO si (e) ≤ (r) o si las falsas de (e) > falsas de (a) + 2.

**Lo que no mide:** la calidad de la conversación ni de la pista, la latencia en el N2840 ni errores fuera de las 10 fichas (como make/do), que quedan para el LLM.
