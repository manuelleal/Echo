# Piloto F1b — VEREDICTO: HAY ALGO MODESTO (4-nov-2026)

Preregistro: `biblioteca/PREREGISTRO_F1b.md` (7fd0723), detectores congelados en 9d3ba7d (y el arreglo "and he", anotado antes de correr). Banco v3 ciego, sha c02a99fa…, construido por un agente aparte que no vio el tutor; 120 frases, 0,5B cabezaq4. Crudos en `banco_v3/`; tabla completa en `banco_v3/RESUMEN_F1b.md`.

| Brazo | Detección /90 | Falsas /30 | Corrección con la forma de la clave /114 |
|---|---|---|---|
| (a) v1 sólo LLM | 53 | 1 | 34 |
| (r) rival trivial, 2 reglas | 55 | 1 | 36 |
| **(e) detectores + LLM** | **58** | **1** | **45** |
| (s) sólo detectores | 19 | 1 | 14 |

**Predicciones:**
1. (e) > (a) con p < 0,05: **falla por poco**. Discordantes 5 contra 0, p = 0,0625.
2. (e) ≥ (r) + 3: **se cumple justo** (58 = 55 + 3).
3. Falsas (e) ≤ (a) + 1: **se cumple** (1 = 1).

Con 1 sin cumplirse, 2 y 3 cumplidas y (e) > (a), el veredicto preregistrado es HAY ALGO MODESTO.

**Lo que dice el dato:**
- **Las reglas suman sin estorbar.** En las 5 frases discordantes con (a) gana (e) y en ninguna pierde; las falsas no suben. La señal más clara es secundaria: la corrección exacta sube de 34 a 45 (+11), porque la regla escribe la forma correcta y el 0,5B no.
- **Las reglas solas cubren muy poco: 19/90.** En desarrollo daban 42/43 sobre la biblioteca y 18/20 en la sonda retenida, pero las frases del v3 son más largas (15,2 palabras de media) y más variadas.
  - Ejemplos: people_is 2/8 y concordancia 3/12, porque la regla exige que sujeto y verbo estén pegados.
  - **El desarrollo propio sobreestimó la cobertura**: las frases que escribe uno mismo se parecen a las reglas que uno escribe. Es la misma lección que la ERR-T1, ahora vista desde el constructor.
- El LLM sigue cargando casi todo: (e) detecta 39 frases que (s) no detecta.
- El cupo del banco v3 va en 4 de 6: (a) es la base y (r), (e), (s) los candidatos.

**Qué sigue (para decidir):** el camino que generaliza no son más expresiones regulares, sino un **analizador gramatical de verdad**, la ERG con mal-reglas de SINTESIS_v2. Encuentra el sujeto aunque haya palabras en medio ("the people in my village is"). Las fichas quedan como la pista y la explicación, y la ERG como el detector.
