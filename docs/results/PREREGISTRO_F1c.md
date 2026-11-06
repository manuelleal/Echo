# Preregistro F1c — la ERG como detector con ubicación (4-nov-2026, antes de correr en el banco v3)

**Motivo:** en F1b, las reglas de texto solas cubrieron 19/90 en el banco v3 porque exigen que sujeto y verbo estén pegados. La ERG 2025 «educ» (ACE 0.9.34) analiza la estructura: dice qué regla de aprendiz se violó (`*_rbst`) y, por la MRS, dónde está y cuál es el número y la persona del sujeto. La reparación es pequeña y por tipo: concordancia, pasado con marcador de tiempo y negación con "not". Código: `biblioteca/erg/reparar.py`.

**Desarrollo (nunca bancos):**
- Biblioteca más sonda retenida: 61/63 corregidas y 0/136 correctas tocadas.
- Sonda de estructura escrita por el coordinador (`erg/sonda_estructura.py`): las reglas de texto dan 4/12 y **reglas + ERG 12/12**, con 0/12 correctas tocadas.

**Brazos nuevos** (banco v3 ciego, 0,5B cabezaq4, mismo arnés sin modificar, mismos (a), (r), (e), (s) de F1b como referencia):
- (g) reglas de texto → ERG → LLM v1.
- (gs) reglas de texto → ERG, sin LLM en la corrección.

Con esto se usan los candidatos 5 y 6: **el banco v3 queda agotado**.

**Predicciones (pueden fallar):**
1. (g) ≥ (e) + 4 en detección /90 (e = 58).
2. (g) > (a) con McNemar exacto p < 0,05 (a = 53).
3. Falsas de (g) ≤ 2/30.
4. (gs) ≥ 30/90 (s = 19).

**Veredicto:**
- FUNCIONA si se cumplen 1, 2 y 3.
- HAY ALGO MODESTO si (g) > (e) y se cumple 3, pero falla 1 o 2.
- NO si (g) ≤ (e) o si las falsas de (g) son más de 3.

La predicción 4 se informa aparte.

**Lo que no mide:** la latencia de ACE en el N2840 (en el PC son unos 0,3 s por análisis), la memoria en 4 GB ni la conversación.
