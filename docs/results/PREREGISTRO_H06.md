# Preregistro H06 — cabeza en Q4_0 y caché KV q8_0 en el N2840 (4-nov-2026, antes de medir)

**Pregunta:** ¿escribe más rápido el 0,5B en el Chromebook si la cabeza de salida deja de estar en Q8_0 (que va por el bucle escalar sin AVX) y si la caché KV va en q8_0 en vez de f16 (sin F16C)?

**Base de la hipótesis:**
- Nota 06: en el Q4_0 oficial, 1 tensor (la cabeza/embedding, 136M) está en q8_0 (lo verificó el coordinador con llama-bench -v).
- Nota 01 e INFORME de latencia: con KV q8 la escritura subió de unos 3,9 a unos 5,3 t/s en el servidor del N2840.

**Brazos (mismo binario 7adf160, 2 hilos, llama-bench -r 3, en el N2840 sin escritorio gráfico si ya se pudo quitar):**
- A — oficial `qwen2.5-0.5b-instruct-q4_0.gguf` (rival, sha 7671c0c3…)
- B — `qwen05-q4_0-cabezaq4.gguf` (todo Q4_0, requantizado desde el Q8_0 oficial con llama-quantize; sha 7cb9e930…, 361 MB)
- Cada uno con caché KV f16 (por defecto) y q8_0 (`-ctk q8_0 -ctv q8_0 -fa 1`), con pp 128 y tg 64, a profundidad 0 y 340 (`-d 0,340`, el tamaño del prompt real del tutor).

**Predicciones (pueden fallar):**
1. B escribe (tg) ≥ 1,3× que A, con la misma caché.
2. La caché q8_0 escribe ≥ 1,2× que f16 a profundidad 340, con el mismo modelo.
3. B pierde poco en calidad: en 12 frases inventadas (no de los bancos) con temperatura 0 y el prompt v1 del tutor, B devuelve la misma frase_corregida que A en ≥ 10/12.

**Veredicto:**
- FUNCIONA si se cumplen 1 y 3.
- HAY ALGO MODESTO si tg ≥ 1,1× y 3 se cumple.
- NO si tg < 1,1× o si B cambia la corrección en más de 2/12.

**Lo que no mide:** la detección en el banco ciego v2 (Fase 3), la perplejidad formal ni el parche SSSE3 de Q8_0 (fuera de este humo).
