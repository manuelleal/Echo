# F2 — la cadena reglas + ERG + LLM en el Chromebook · VEREDICTO: FUNCIONA (4-nov-2026)

Preregistro: `PREREGISTRO_F2_cadena.md` (3cf9566, antes de copiar nada a candy). 68 frases propias (sondas y humo), nunca bancos. Celeron N2840, 2 hilos. ACE 0.9.34 + `erg-2025-educ.dat` (sha 6682f3b6…, el mismo del PC). llama-server 7adf160 con `qwen05-q4_0-cabezaq4.gguf`, `-ctk q8_0 -ctv q8_0 -fa on`.

| Medida | Predicción | Resultado |
|---|---|---|
| ACE solo, por frase (cargando la gramática en cada llamada) | ≤ 3 s y ≤ 400 MB | **0,41 s** de mediana (p90 0,56) y **250 MB** |
| Parte simbólica (reglas + ERG) | — | 0,43 s de mediana |
| **Cadena completa** (reglas + ERG + LLM: corrección, tipos y pregunta) | ≤ 13 s de mediana | **6,3 s** de mediana; p90 13,0 s; mínimo 4,8 s; máximo 39 s (la primera, con la caché fría) |
| Identidad de reglas + ERG con el PC | ≥ 66/68 | **68/68** |
| Memoria máxima | ≤ 3 GB en conjunto | llama-server 504 MB + ACE 250 MB, **unos 0,75 GB** de 3,8 GB |

**Lectura:**
- La parte simbólica, la que sabe qué regla falló, tarda menos de medio segundo y da **exactamente lo mismo que en el PC**.
- La consulta entera tarda 6 s de mediana en un Chromebook escolar de 2014. Sobra memoria: cabría hasta un modelo de 1,5B.
- **Lo que no mide:** si 6 s es aceptable para un aprendiz (eso se ve con usuarios), ni la detección en el N2840 sobre un banco ciego. La detección no debería cambiar, porque la parte simbólica es idéntica y el LLM corre a temperatura 0, pero no se comprobó con el banco.
- La primera consulta (39 s) paga la caché fría. En el aula conviene "calentar" el tutor al arrancar.
