# Preregistro F2 — la cadena reglas + ERG + LLM en el N2840 (4-nov-2026, antes de copiar nada a candy)

**Pregunta:** ¿cabe y corre en el Chromebook (Celeron N2840, 2 núcleos, 4 GB, eMMC) la cadena que ganó en F1c, (g) = reglas de texto → ERG educ → LLM v1, con un tiempo de aula?

**Montaje:**
- ACE 0.9.34 (binario sin AVX, verificado con objdump en SIMBOLICO) con `erg-2025-educ.dat`, el mismo del PC (se compara el sha256).
- llama-server 7adf160 con `qwen05-q4_0-cabezaq4.gguf` y la configuración de H06: `-t 2 -ctk q8_0 -ctv q8_0 -fa 1`, caché de prefijo.
- Código copiado del PC sin cambios de lógica; el único cambio es que ACE se llama directo en Linux y no por `wsl`.

**Frases:** sólo propias, nunca bancos. Son 68:
- sonda de estructura (12 con error y 12 correctas);
- sonda retenida (20 y 20);
- humo (4).

**Medidas:**
1. ACE solo: tiempo por frase (con la carga de la gramática en cada llamada, como en el PC) y RSS máximo.
2. Cadena completa por frase: reglas + ERG + LLM v1 (a1 + a2 + pregunta). Mediana y p90.
3. Identidad: la salida de reglas + ERG en candy es igual a la del PC (texto exacto) en las 68.
4. Memoria: RSS máximo de llama-server + ACE corriendo juntos.

**Predicciones (pueden fallar):**
- ACE ≤ 3 s por frase (mediana) y ≤ 400 MB.
- Cadena ≤ 13 s mediana (H06 dio 10,1 s sin ERG).
- Identidad ≥ 66/68.
- RSS conjunto ≤ 3 GB.

**Veredicto:**
- FUNCIONA si la cadena da ≤ 13 s, la identidad ≥ 66/68 y el RSS ≤ 3 GB.
- HAY ALGO MODESTO si la cadena da ≤ 20 s y lo demás se cumple.
- NO en cualquier otro caso.

Si ACE resulta lento por cargar la gramática en cada llamada, el arreglo (proceso persistente) se mide aparte y se informa como tal, sin reemplazar esta medida.
