# F1c — la ERG como detector · VEREDICTO: HAY ALGO MODESTO (4-nov-2026)

Preregistro: `biblioteca/PREREGISTRO_F1c.md` (5ca42cb, antes de correr). Banco v3 ciego (sha c02a99fa…), 0,5B cabezaq4. Tabla completa en `banco_v3/RESUMEN_F1c.md`.

| Brazo | Detección /90 | Falsas /30 | Corrección exacta /114 |
|---|---|---|---|
| (a) v1 sólo LLM | 53 | 1 | 34 |
| (e) reglas de texto + LLM | 58 | 1 | 45 |
| **(g) reglas + ERG + LLM** | **59** | **1** | **46** |
| (s) reglas de texto, sin LLM | 19 | 1 | 14 |
| **(gs) reglas + ERG, sin LLM** | **29** | **1** | 23 |

**Predicciones:**
1. (g) ≥ (e) + 4: **NO** (59 contra 58).
2. (g) > (a) con p < 0,05: **sí** (6 contra 0, p = 0,031).
3. Falsas ≤ 2: **sí** (1).
4. (gs) ≥ 30: **NO por uno** (29), aunque pasa de 19 a 29 frente a (s), con 10 contra 0 y p = 0,002.

**Lo que dice el dato:**
- **(g) es el primer brazo que supera con significancia al LLM solo** en un banco ciego: gana 6 frases y no pierde ninguna, sin falsas nuevas, y la corrección exacta sube de 34 a 46.
- **Pero casi todo ese avance ya lo traían las reglas de texto (e).** La ERG suma sólo 1 frase cuando hay LLM detrás, porque lo que arregla (concordancia, people_is) el LLM ya lo detectaba.
- **Donde la ERG sí cambia el cuadro es sin LLM.** La parte simbólica, que es exacta y explicable, pasa de 19 a 29: people_is de 2/8 a 7/8 y concordancia de 3/12 a 8/12, con 1 falsa en 30.
  - El pasado sigue en 4/12 sin LLM. La ERG sólo dispara su regla de tiempo con algunos marcadores ("yesterday", "last"); con otros, el pasado queda en manos del LLM.
- **El banco v3 queda agotado** (6 de 6). Para iterar hace falta un banco v4.

**Para la tesis:** en un 0,5B, los ejemplos en el prompt no sirven (F1: NO). Lo que sí sirve es diagnosticar con símbolos y dejar al LLM para lo demás: es el único arreglo significativo frente al LLM solo, y la parte simbólica cubre un tercio de los errores con una sola falsa alarma.
