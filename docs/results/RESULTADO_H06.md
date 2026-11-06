# Resultado H06 (4-nov-2026) — cabeza en Q4_0 y caché KV q8_0 en el N2840

**Veredicto: FUNCIONA** según el preregistro (b463512): se cumplen las predicciones 1 y 3. La 2 queda confundida (ver ERR-C5).

| N2840, 2 hilos, -fa 1, -r 3 | pp@d0 | tg@d0 | pp@d340 | tg@d340 |
|---|---|---|---|---|
| A oficial Q4_0, KV f16 | 6,71 | 1,10 | 6,30 | 2,61 ± 1,52 |
| A oficial Q4_0, KV q8_0 | 13,60 | 5,71 | 11,18 | 5,18 |
| B cabeza Q4_0, KV f16 | 14,22 | 8,94 | 13,43 | 4,59 |
| **B cabeza Q4_0, KV q8_0** | **13,78** | **9,54** | **11,24** | **8,09** |

1. **B escribe más rápido que A con la misma caché:** ×1,67 (d0) y ×1,56 (d340) con q8_0. Predicción ≥ 1,3×: **se cumple**.
2. **q8_0 frente a f16:** ×1,98 (A) y ×1,76 (B) a d340. Predicción ≥ 1,2×: se cumple en la cifra, pero **queda confundida**, porque el brazo f16 corrió con `-fa 1` y sin F16C eso lo hunde (A f16 tg@d0 = 1,10, contra 5,41 de la Fase 2 con la configuración por defecto).
3. **Calidad:** con el tutor real (prompt v1, 12 frases inventadas, temperatura 0), B da la misma frase_corregida que A en **11/12**. La única diferencia es que B corrige además "cows needs" → "cows need" (mejor). Predicción ≥ 10/12: **se cumple**. Ambos siguen sin corregir "I have 17 years".
4. **Consulta de punta a punta** (lat.py, flags por defecto, sin KV q8): mediana **12,3 s → 10,1 s** (−18 %).

**Configuración recomendada hoy para el N2840:** `qwen05-q4_0-cabezaq4.gguf` (sha 7cb9e930…) + `-ctk q8_0 -ctv q8_0 -fa 1`: escribe unos 8–9,5 t/s, contra 5,4 de la Fase 2.
