# Piloto F1 — VEREDICTO: NO (4-nov-2026)

Preregistro: PLAN_BIBLIOTECA.md §4 + Enmienda 1 (commits 5d74af5 y 6359d9d, antes de correr). Banco ciego v2, 80 frases, 0,5B cabezaq4, temperatura 0. Crudos en `banco_v2/`; tabla completa en `banco_v2/RESUMEN_F1.md`.

| Brazo | Detección /60 | Falsas /20 | Tokens/consulta |
|---|---|---|---|
| (a) v1 sin ejemplos | 39 | 1 | 497 |
| (b) v2, 20 ejemplos fijos | 42 | 1 | 1254 |
| (c) biblioteca, 4 pares por BM25 | 40 | 2 | 663 (53 % de b) |
| (d) control, 4 pares al azar | 40 | 1 | 655 |

**Por qué NO:** (c) empata con el control al azar (40 = 40; McNemar 3 contra 3, p = 1), y la regla preregistrada dice NO si (c) ≤ (d). Además, (c) tuvo 2 falsas y el tope era 1.

**Lo que sí dice el dato:**
1. **Con el 0,5B, los ejemplos en el prompt casi no mueven nada.** Ni siquiera el v2 fijo supera a v1 de forma significativa (42 contra 39, p = 0,45). En el 1,5B sí lo hacía (52 contra 46, p = 0,031). La mejora con ejemplos no pasó del 1,5B al 0,5B.
2. **Qué ejemplos se le den da igual:** recuperados o al azar, 40 = 40. El 0,5B no lee el contenido de los pares; a lo sumo copia la forma.
3. **Única señal local:** con la biblioteca entraron 3 frases de edad (V21, V22, V24) que el azar no detectó. Pero perdió falsos cognados y "make/do", que no tiene ficha. Es demasiado poco para sostener algo.
4. **El banco v2 queda agotado** (6 candidatos). Cualquier variante nueva necesita un banco v3.

**Qué cambia en el plan:** en el 0,5B, la biblioteca no debe entrar como ejemplos para el LLM, sino como **reglas que se aplican sin LLM**. Cada ficha ganaría un detector (patrón o mal-regla de la ERG) que diagnostica y corrige de forma determinista; el LLM sólo conversa con la pista de la ficha. Es lo que ya apuntaban SINTESIS_v2 y el rival trivial del 15-oct, que con dos reglas igualó a la célula. Las fichas, los 48 ejemplos aprobados y la personalidad siguen sirviendo para la conversación; lo que cambia es de dónde sale la corrección.
