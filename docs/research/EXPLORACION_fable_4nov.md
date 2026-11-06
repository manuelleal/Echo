# Exploración 4-nov-2026 — cómo hacer que el tutor aprenda rápido y de verdad

Explorador: Fable 5.1, sólo lectura. Leí SINTESIS_v2, SIMBOLICO, las notas 02/03/04/07/09/10, PLAN_BIBLIOTECA, F1/F1b/F1c/F2/H06, las 10 fichas, `detectores.py`, `erg/reparar.py`, `erg/erg.py`, la tabla por tipo del RESUMEN_F1c (sólo agregados, ningún texto de frase) y el documento de Christiam sobre corpus sintéticos. No abrí nada bajo `TUTOR-LOCAL-EVAL\banco*`. Las citas de las notas del 19-oct ya las verificó el coordinador; las nuevas las abrí hoy y marco [DUDOSO] lo que no pude confirmar en la fuente primaria.

**Veredicto: HAY ALGO MODESTO, con una pieza que ya FUNCIONA y una que falta entera.** Lo que funciona: una cadena reglas + ERG «educ» + LLM que corre en un Chromebook de 2014 a 6,3 s con 0,75 GB, supera con significancia al LLM solo en un banco ciego (59/90, 1/30 falsas) y da el mismo diagnóstico simbólico que el PC en 68/68. Lo que falta: **el sistema todavía no aprende.** Cada mejora la escribe una persona a mano, cuesta un banco ciego entero (v2 y v3 agotados) y el LLM de 0,5B, que carga el 60 % de la detección, demostró en F1 que no aprende de ejemplos en el prompt. Está a un ciclo de aprendizaje (que no exige reentrenar en el aparato) y a un humo con 10 personas de ser algo real en un aula. Ninguna de las dos piezas depende del tamaño del modelo.

---

## 0. De dónde partimos (medido)

| Pieza | Dato | Fuente |
|---|---|---|
| Ejemplos en el prompt con el 0,5B | NO: (c) 40 = (d) 40 al azar; v2 fijo 42 contra v1 39, p = 0,45. En el 1,5B sí servían (52 contra 46, p = 0,031) | RESULTADO_F1 |
| Reglas de texto + LLM | 58/90, 1 falsa; sólo reglas 19/90 | RESULTADO_F1b |
| Reglas + ERG + LLM | **59/90**, 1 falsa; corrección exacta 46/114. Sin LLM: 29/90 | RESULTADO_F1c |
| En el N2840 | 6,3 s mediana (p90 13 s); simbólico 0,43 s; 0,75 GB; identidad 68/68 | RESULTADO_F2 |
| Modelo recomendado | `qwen05-q4_0-cabezaq4.gguf` + KV q8_0: 8–9,5 t/s | RESULTADO_H06 |
| Lo que ya aprende solo | Nada en el aparato. La biblioteca (10 fichas, 48 ejemplos) la curó Christiam; los detectores los escribió una persona | PLAN_BIBLIOTECA |

**Detección por tipo, instancias de error (n = 114 en las 90 frases; columna g = cadena completa, gs = sin LLM)**, del RESUMEN_F1c:

| Tipo | n | g | gs | Hueco de g |
|---|---|---|---|---|
| make_do | 12 | 5 | 1 | 7 |
| falso_cognado | 9 | 4 | 2 | 5 |
| orden_adjetivo | 9 | 4 | 4 | 5 |
| articulo | 11 | 7 | 4 | 4 |
| sujeto_omitido | 12 | 8 | 3 | 4 |
| plural | 9 | 6 | 3 | 3 |
| preposicion | 12 | 9 | 2 | 3 |
| edad_have | 8 | 7 | 5 | 1 |
| pasado | 12 | 11 | 4 | 1 |
| concordancia | 12 | 11 | 8 | 1 |
| people_is | 8 | 8 | 7 | 0 |

Lectura: 31 de las 34 instancias que se escapan están en siete tipos, y cuatro de ellos (make/do, falsos cognados, preposiciones, orden del adjetivo) son **léxicos o de transferencia del español**, justo donde la ERG «educ» no tiene reglas porque se hizo para aprendices chinos (SIMBOLICO §0). Eso define qué tiene que aprender el sistema primero.

---

## 1. Lo principal: cómo aprende el sistema, rápido y de verdad

### 1.0 La tesis en tres líneas

1. El sistema tiene tres órganos que aprenden a ritmos distintos: **la biblioteca** (fichas, reglas, casos; aprende en minutos y se audita), **un modelo chico reentrenable** (etiquetador o sonda; aprende en minutos en el PC, viaja en KB) y **el LLM de 0,5B** (aprende sólo tocando pesos, fuera del aparato, y es el que menos garantías da).
2. «Aprender de verdad» tiene una definición operativa: el sistema **nombra la regla** que falló (ficha = clave), **su juicio no cambia con paráfrasis ni con palabras nuevas**, y **se voltea con el contrafactual mínimo** (la frase corregida da «sin error»). La ERG cumple las tres por construcción dentro de su cobertura; los LLM fallan la segunda y la tercera de forma documentada (ParaRel, [arXiv 2102.01017](https://arxiv.org/abs/2102.01017); contrafactuales, [arXiv 2307.02477](https://arxiv.org/abs/2307.02477)).
3. Por eso «aprender rápido» no es «mover la aguja del LLM»: es **mover instancias de error de la columna del LLM a la columna simbólica o del modelo chico**, donde las tres propiedades se cumplen y donde una mejora cuesta minutos y no un banco.

**El indicador que propongo para medir la velocidad de aprendizaje del sistema:** *horas desde el primer ejemplo de un tipo de error nuevo hasta un detector verificado y desplegado, sin consumir banco ciego.* Hoy: una persona escribe el regex (1–2 h), se prueba a mano y hay que gastar un banco. Meta: menos de 30 minutos y cero banco (el banco se gasta sólo en la versión mensual).

### 1.1 Ciclo de aprendizaje continuo sin reentrenar en 4 GB: la biblioteca viva

**Mecanismo.** Cada consulta deja un evento: frase, diagnóstico (regla o ficha), corrección propuesta, qué hizo el aprendiz (corrigió o no) y, si hay profe, qué hizo él (aceptó, editó, ignoró). Los eventos alimentan tres sumideros, ninguno toca los pesos del LLM:

| Sumidero | Qué aprende | Cuándo | Dónde corre |
|---|---|---|---|
| **Memoria de casos deslexicalizada** | Un patrón `DET N_sg ADJ .` con su corrección y ficha. La frase se abstrae con los tipos léxicos del árbol de la ERG (cuando analiza) o con un etiquetador POS puro Python (NLTK perceptron) cuando no. Un caso nuevo que calce con un patrón guardado recibe la corrección guardada | En el momento (ms) | N2840 |
| **Inducción de reglas con verificador** (§1.2) | De 3–5 casos del mismo tipo, un regex o patrón sobre tokens + tipos, con pruebas | Semanal, o cuando se junten 3 casos | PC o Claude |
| **Reentrenar el modelo chico** (§1.4) | Etiquetador o sonda lineal con los casos nuevos | Cada noche (segundos–minutos) | PC |

**Evidencia.** Editar pesos del LLM falla en secuencia («Mirage of Model Editing», [arXiv 2502.11177](https://arxiv.org/abs/2502.11177): 38,5 % real con una edición; «fail drastically» con 1000); una memoria externa clave→valor aguanta miles de arreglos (GRACE, [arXiv 2211.11031](https://arxiv.org/abs/2211.11031)). Recuperar casos parecidos mejora un LM congelado sin tocarlo (kNN-LM, [arXiv 1911.00172](https://arxiv.org/abs/1911.00172)). Aprender de las ediciones del usuario sin ajuste fino: PRELUDE/CIPHER, [arXiv 2404.15269](https://arxiv.org/abs/2404.15269). El humo propio de la nota 10 ya mostró que viajar **ejemplos** entre aulas recupera 68–91 % de lo centralizado sin dañar lo propio, y que promediar pesos daña 7–14 puntos. Que el cuello de botella de los detectores aprendidos son las **características estructurales**, no el aprendiz, lo mostró la nota 02 (todos aprenden «la palabra antes del verbo»; con el núcleo del sujeto se resuelve): por eso la deslexicalización usa los tipos de la ERG.

**Cómo se monta aquí.** `biblioteca/casos/` (JSONL: patrón, ejemplo, corrección, ficha_id, origen, aprobado, sha del modelo con el que se verificó) y `biblioteca/profe/` ya previstos en PLAN_BIBLIOTECA §1. La abstracción sale gratis del árbol que `reparar.py` ya pide a ACE (los nodos léxicos `*_le` traen la categoría). Regla de entrada a la memoria: la corrección guardada **debe analizar sin reglas `rbst`** en la ERG (`erg.analizar`), si no, va a cuarentena para el profe. El Manifiesto con sha256 ya existe en el plan.

**Humo chico (1 día, sin banco).** Un agente aparte genera 60 frases de 2 tipos que hoy no tienen ficha (p. ej. *since/for* y *more + -er*) con vocabulario fijado por semilla, y 100 correctas del mismo tema. Se guardan en la memoria 5 casos de cada tipo (escritos por Claude, no de esas 60). Medir en las 60 + 100: detección por memoria deslexicalizada, falsas, y el tiempo desde «primer caso» hasta «cubre la frase nueva».
**Predicción que puede fallar:** ≥ 50 % de detección con 5 casos y 0/100 falsas. Si da < 30 %, la deslexicalización por tipos léxicos no generaliza y hay que ir directo a §1.2.
**Costo:** 0 USD (las frases las genera un agente con el saldo; < 0,5 USD).

### 1.2 Reglas que se escriben solas y se verifican con la ERG

**Mecanismo.** Síntesis de programas con verificador, al estilo de la «biblioteca de habilidades» de Voyager ([arXiv 2305.16291](https://arxiv.org/abs/2305.16291)) y de la búsqueda evolutiva de código con evaluador (OpenEvolve, [github.com/codelion/openevolve](https://github.com/codelion/openevolve); AlphaEvolve, [deepmind.google](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)), que Christiam ya usó en JUACO. Aquí el «programa» es un detector (regex o patrón sobre tokens y tipos léxicos) y el **evaluador no necesita banco**:

1. Entrada: 3–5 frases con el error y su corrección (del profe, de la memoria de casos o escritas por Claude).
2. Claude (en el PC, con la API) escribe el detector + 10 frases positivas + 30 negativas trampa (como `retenidas_detectores.py`).
3. Se acepta sólo si: dispara en los positivos; **0 falsas** en un conjunto fijo de 500 frases correctas A1–A2 (generado una vez, nunca el banco); cada corrección que produce **analiza en la ERG sin `rbst`** y conserva la MRS de la frase (la firma M de la nota 07, con tiempo y número); y la edición es ≤ 3 palabras sin borrar contenido (la Enmienda 1a del F1 ya exige esto).
4. Entra a `biblioteca/detectores_auto/<tipo>.py` con procedencia y pruebas, y la ficha nueva pasa por Christiam.

**Evidencia.** Un modelo de lenguaje que escribe código y lo corrige con la salida de las pruebas mejora de forma consistente (Self-Debugging, [arXiv 2304.05128](https://arxiv.org/abs/2304.05128)). La ERG como juez exacto de gramaticalidad ya se midió: 100 % buena > mala en 30 tripletas, 0/30 veces prefiere la frase genérica (nota 07). El patrón «generar, verificar, quedarse con lo verificado» es el de STaR ([arXiv 2203.14465](https://arxiv.org/abs/2203.14465)) y ReST-EM ([arXiv 2312.06585](https://arxiv.org/abs/2312.06585)), aplicado a reglas en vez de a pesos. **Riesgo en una línea (cambia la decisión):** la ERG no ve los errores de transferencia (*have 15 years*, *make a question*), así que para esos tipos el verificador semántico es la MRS más el léxico de transferencia de §2, no la gramaticalidad.

**Cómo se monta aquí.** Es una skill de la API con tope de gasto (F5 del plan) más `dev_detectores.py` y `retenidas_detectores.py` como formato de pruebas. El conjunto de 500 correctas y el de trampas se congelan con sha256 antes de la primera inducción.

**Humo chico (medio día).** Los mismos 2 tipos nuevos de §1.1. Medir: ¿cuántos intentos de Claude hasta pasar el verificador? ¿tiempo de pared? ¿detección en las 60 retenidas y falsas en las 100?
**Predicción que puede fallar:** detector aceptado en ≤ 3 intentos y ≤ 30 min; ≥ 60 % en las retenidas; 0/100 falsas. Falla si pasa el verificador y aun así da < 40 % en las retenidas: eso diría que el verificador deja pasar reglas que memorizan los 5 casos (sobreajuste al ejemplo, el mismo riesgo que la nota 02 vio en la TM).
**Costo:** < 2 USD por tipo (Opus 5.5, pocas llamadas).

### 1.3 Destilar desde Claude con los ~99 USD antes del 20-nov

**Qué dice F1 y qué implica.** El 0,5B no aprende del prompt; el aprendizaje en contexto crece con el tamaño del modelo ([Brown et al. 2020, arXiv 2005.14165](https://arxiv.org/abs/2005.14165)) y la mejora que daban los ejemplos en el 1,5B no bajó al 0,5B. Luego, si el 0,5B tiene que aprender, hay que **tocar pesos fuera del aparato** (LoRA en Colab o en el PC) o cambiar de arquitectura (§1.4). Dos advertencias con evidencia: imitar a un modelo grande copia el **estilo**, no la exactitud (Gudibande 2023, [arXiv 2305.15717](https://arxiv.org/abs/2305.15717)), y en modelos chicos **destilar rinde más que RL directo** (DeepSeek-R1 §4.1, [arXiv 2501.12948](https://arxiv.org/abs/2501.12948)). Por eso la destilación aquí es de **tarea cerrada** (frase → corrección mínima + id de ficha), no de explicaciones, y el filtro de calidad es simbólico.

**Qué datos generar (todos quedan como activos aunque venza el crédito):**

| Activo | Cómo | Cuánto | Para qué | Costo estimado |
|---|---|---|---|---|
| A. Frases correctas A1–A2 de finca, tienda y SENA, con **listas de vocabulario disjuntas** por partición (entrenamiento / desarrollo / retenidas), fijadas con semilla y hash | Claude escribe; un script separa | 3000 | Base de todo lo demás y pantalla de falsas alarmas | ≈ 1 USD |
| B. Corrupción **etiquetada** con tramo exacto: 70 % programática (el inverso de cada detector y de las mal-reglas: 3sg, pasado, a/an, people, edad…), 30 % escrita por Claude para lo léxico (make/do, falsos cognados, preposiciones, orden) con la consigna de imitar a un hispanohablante | Como los modelos de corrupción etiquetados de Stahlberg & Kumar 2021, [arXiv 2105.13318](https://arxiv.org/abs/2105.13318), que igualan la distribución de tipos a la del conjunto de desarrollo | 30 000 (20 000 programáticas gratis + 10 000 de Claude) | Entrenar el etiquetador y la sonda (§1.4); SFT del 0,5B | ≈ 6 USD con Sonnet 5.5 en lote (−50 %) |
| C. **Pares mínimos** por tipo con vocabulario nuevo (estilo BLiMP, [arXiv 1912.00582](https://arxiv.org/abs/1912.00582)) | Plantillas + Claude | 2000 pares | Prueba de entendimiento (§1.5) sin gastar banco | ≈ 1 USD |
| D. Tripletas para SFT: frase con error → corrección mínima + `ficha_id` + pista, **filtradas por la ERG** (la corrección analiza sin `rbst`, conserva la MRS, ≤ 3 palabras cambiadas) | Muestreo por rechazo | 5000 que pasen el filtro | LoRA del 0,5B | ≈ 5 USD |
| E. Pares de preferencia: corrección buena contra sobrecorrección, contra copia de la frase y contra frase genérica (las dos trampas medidas en la nota 07) | Programático desde D + Claude | 3000 | DPO/KTO | ≈ 2 USD |
| F. Tres bancos ciegos v4–v6 (120 frases cada uno) construidos por un agente que no ve el tutor, con sello sha256 | Igual que v3 | 3 × 120 | Medir | ≈ 3 USD (Opus 5.5) |
| G. Léxicos de transferencia (§2): colocaciones make/do, preposiciones tras verbo y de tiempo, falsos cognados con su marco sintáctico | Claude propone, Christiam aprueba | ≈ 300 entradas | Detectores léxicos | ≈ 2 USD |
| H. Jueces: Opus 5.5 califica 300 salidas del tutor (corrección aceptable, sobrecorrección, ficha correcta) para calibrar el arnés | 1 llamada por ítem | 300 | Auditoría | ≈ 4 USD |

Total ≈ 25 USD. Quedan ≈ 70 para una segunda ronda tras la semana 1 (más corrupción de los tipos que fallen, un banco v7, GRPO si entra) y reserva. Precios de la tabla cacheada del skill `claude-api` (6-oct-2026): Haiku 5.5 0,10 / 0,50 USD por millón de tokens, Sonnet 5.5 2 / 10, Opus 5.5 4 / 20; el lote cuesta la mitad. Confirmar en [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing). Regla: **comprar activos (datos, bancos, léxicos), no cómputo**; el cómputo lo da Colab gratis.

**La recompensa combinada como filtro, no como RL.** Para SFT/DPO la recompensa de la nota 07 se usa para *elegir* datos: R = 2·G (analiza sin `rbst`) + M (Dice de la MRS con tiempo y número) + E (la edición toca el tramo del error inyectado) + F (ficha = tipo inyectado) + 0,5·L (logprob del propio 0,5B como desempate de fluidez) − castigo por longitud. Sólo entran tripletas con G = 1, E = 1, F = 1. Esto cierra las dos trampas medidas: la perplejidad sola prefiere la frase genérica 13/30 veces; la ERG sola premia la copia 9/30 (nota 07). Si después hay GRPO, el control de **recompensa al azar** es obligatorio (Shao et al., [arXiv 2506.10947](https://arxiv.org/abs/2506.10947): con Qwen la recompensa basura también «mejora»).

**Cómo se monta.** Colab gratis (T4, 16 GB) con TRL `SFTTrainer` y PEFT LoRA r = 16 sobre Qwen2.5-0.5B-Instruct, 5000 tripletas, 2–3 épocas: menos de 1 h [DUDOSO, sin medir]. Luego dos caminos a medir: (a) fusionar y recuantizar a Q4_0 con la cabeza en Q4_0 (receta H06); (b) **adaptador LoRA en tiempo de ejecución** sobre el GGUF base (`convert_lora_to_gguf.py` + `--lora` en llama-server), que evita que la cuantización borre lo aprendido; costo de velocidad en el N2840 [DUDOSO, sin medir].

**Humo chico (1 día con Colab).** Brazos sobre el **banco de desarrollo** (no ciego) y los pares mínimos: base; SFT con tripletas filtradas; SFT con tripletas **sin filtrar** (control: ¿el filtro simbólico importa?). Luego un solo candidato al banco v4.
**Predicción que puede fallar:** SFT filtrado sube la corrección exacta ≥ 8 puntos sobre la base en desarrollo y ≥ 10 puntos en pares mínimos; falsas ≤ 2/30; tras Q4_0 conserva ≥ 70 % de la ganancia. SFT sin filtrar queda ≥ 3 puntos por debajo del filtrado. **NO** si el filtrado ≤ base + 3 en v4, o si Q4_0 borra la ganancia y el LoRA en ejecución cuesta > 2 s más por consulta.

### 1.4 ¿Aprende más rápido un modelo minúsculo especializado que el 0,5B general?

**La apuesta fuerte:** sí, porque la tarea es cerrada (11–20 tipos, vocabulario A1–A2) y el modelo chico sólo tiene que aprender **lo que los símbolos no saben**. Tres candidatos, de más barato a más ambicioso:

| Candidato | Qué es | Evidencia de eficiencia de muestra | Costo de entrenar | Costo en el N2840 |
|---|---|---|---|---|
| **S. Sonda lineal sobre el 0,5B congelado** | Un pase del prompt (sin generar) → estado oculto del último token (`--embeddings`, pooling último) → regresión logística multietiqueta por tipo de error. Nada se genera | Las representaciones de un LM codifican sintaxis recuperable con una sonda lineal (Hewitt & Manning 2019, [aclanthology N19-1419](https://aclanthology.org/N19-1419/)); destilar a modelos chicos con menos datos cuando el grande da señal (Hsieh et al. 2023, [arXiv 2305.02301](https://arxiv.org/abs/2305.02301)) | Minutos en el PC con los 30 000 de B | ≈ lectura del prompt: 2–3 s con prefijo en caché [DUDOSO] |
| **T. Etiquetador de tramos, 2–10 M de parámetros** | Encoder de 4 capas, d = 128–192, sobre tokens + tipo léxico de la ERG (o POS), que etiqueta `KEEP / tipo_de_error` por token, al estilo GECToR («tag, not rewrite», [arXiv 2005.12592](https://arxiv.org/abs/2005.12592), 10× más rápido que seq2seq) | 1,4 M de parámetros bastan para generalizar a palabras nuevas con episodios bien hechos (MLC, [Nature 2023](https://doi.org/10.1038/s41586-023-06668-3)); < 10 M escriben inglés gramatical en un mundo estrecho (TinyStories, [arXiv 2305.07759](https://arxiv.org/abs/2305.07759)); el clasificador de n-gramas de la nota 10 llegó a 0,92 en sintético. **Lo que no hay:** evidencia de un etiquetador de ese tamaño con errores reales de aprendices [DUDOSO] | 10–30 min en el PC o Colab | ms (2–40 MB) |
| **C. CANDY-LM, ≈ 30 M, entrenado para el aula** (nota 08) | Modelo propio con corpus sintético denso: la receta de los documentos de Christiam (TinyStories, Cosmopedia, reescritura pedagógica, Muon) | «Rephrasing the web» reduce tokens necesarios (WRAP, [arXiv 2401.16380](https://arxiv.org/abs/2401.16380)); BabyLM: ganan objetivo y arquitectura, no el currículo (nota 03) | Días de GPU; no cabe antes del 20-nov | ≈ 1 s [sin medir] |

Recomendación: **S y T esta quincena, C después**. S porque reutiliza lo que ya está cargado en el aparato y aprovecha lo que el 0,5B «sabe» de inglés sin pedirle que escriba; T porque es el que de verdad reentrena en minutos y viaja en KB entre aulas (nota 10). Lección de la nota 02 que gobierna el diseño de T: darle **estructura** (tipos léxicos del árbol de la ERG, núcleo del sujeto) o aprenderá el vecino inmediato.

**Humo chico (1 día).** Entrenar S y T con la partición de entrenamiento de B; medir en (i) desarrollo con el **mismo** vocabulario, (ii) retenidas con vocabulario **nuevo**, (iii) estructura nueva (el error dentro de una pregunta o subordinada), (iv) pares mínimos C, (v) 300 correctas. Rival estándar: regresión logística sobre n-gramas hasheados (nota 10) y HistGradientBoosting (nota 02).
**Predicción que puede fallar:** T ≥ 0,85 de F1 en (ii) y ≤ 0,60 en (iii), como manda MLC; S ≥ 0,80 en (ii). Falsas ≤ 2 %. Si T gana al rival de n-gramas por < 5 puntos en (ii), la gracia no es el modelo sino las plantillas y se descarta T. En v4, como voto adicional de la cadena: **≥ 65/90 con ≤ 2 falsas** es FUNCIONA; 62–64 MODESTO; ≤ 60 NO.

### 1.5 Cómo saber que aprendió de verdad y no memorizó

Una **suite de entendimiento** que corre sin gastar banco y, por ser sólo puntuación, corre en el Chromebook:

| Prueba | Qué mide | Cómo | Criterio |
|---|---|---|---|
| Pares mínimos con vocabulario nuevo (C) | Si prefiere la forma correcta por la regla y no por las palabras | Para LLM: logprob de cada frase del par; para T: etiqueta; para la ERG: análisis | ≥ 85 % por tipo; la ERG 100 % en lo que cubre (por construcción) |
| Contrafactual | Que la frase corregida dé «sin error» y la variante mínima con error dé «error» | Pares de B | ≥ 90 % |
| Paráfrasis | Misma etiqueta en 4 paráfrasis de la misma frase | 100 grupos (nota 03) | ≥ 85 % |
| Explicación correcta | ficha_id = tipo de la clave, no sólo «hay error» | Ya está en el arnés del v3 | Reportarla siempre al lado de la detección |
| Cruce de solape | Que nada del entrenamiento esté en el banco | `cruce_solape.py` | 0 frases, n-gramas de 5 ≤ 1 % |
| Frases reales | La única que vale al final | 200 frases anonimizadas de aprendices de Christiam (ver decisión 2) | Se mide una vez por versión |

Los dos riesgos documentados que esta suite detecta: un modelo chico que «razona» pero aprendió las tareas de evaluación (análisis de ARC Prize sobre HRM, nota 03) y el desarrollo propio que sobreestima la cobertura porque «las frases que escribe uno se parecen a las reglas que uno escribe» (F1b, ERR-T1 vista desde el constructor). Por eso las particiones las fija un script con semilla y el constructor nunca ve las retenidas.

### 1.6 Métodos de autoentrenamiento: cuáles caben

| Método | Mecanismo | Evidencia y tamaño | ¿Cabe aquí? | Costo |
|---|---|---|---|---|
| **Rechazo con verificador (STaR / ReST-EM / RFT)** | Generar varias correcciones, quedarse con las que aprueba la ERG + E + F, ajustar sobre ellas, repetir | STaR con GPT-J 6B ([arXiv 2203.14465](https://arxiv.org/abs/2203.14465)); ReST-EM con PaLM 2 ([arXiv 2312.06585](https://arxiv.org/abs/2312.06585)); RFT ([arXiv 2308.01825](https://arxiv.org/abs/2308.01825)), donde la ganancia es mayor en los modelos más débiles [DUDOSO para 0,5B: sin evidencia] | **Sí, es la primera opción.** El verificador exacto ya existe y cuesta 0,06 s por frase | Colab gratis; datos de §1.3 |
| **KTO con la señal del profe** | Ajuste con señal binaria «deseable / no deseable», sin necesidad de pares | Iguala o supera a DPO de 1B a 30B ([arXiv 2402.01306](https://arxiv.org/abs/2402.01306)) | **Sí**: «aceptó / ignoró / editó» es exactamente una señal sin pares. Requiere ≥ 500 eventos; mientras tanto se simula con Claude como profe sobre B | Colab |
| **DPO con pares E** | Buena contra sobrecorrección / copia / genérica | [arXiv 2305.18290](https://arxiv.org/abs/2305.18290) | Sí, después del SFT | Colab |
| **SPIN** | El modelo juega contra su versión anterior usando el SFT como «real» | Zephyr-7B ([arXiv 2401.01335](https://arxiv.org/abs/2401.01335)); documento de Christiam §3 | Cabe en Colab, pero sin verificador externo puede reforzar trampas de estilo; **segunda prioridad** | Colab, varias iteraciones |
| **GRPO con recompensa compuesta** | RL con grupo de 8 salidas y juez simbólico | Nota 07; GEC en chino con recompensa por reglas ([arXiv 2508.18780](https://arxiv.org/abs/2508.18780)) | Sí, **sólo después** del SFT y con el control de recompensa al azar | 1,5–2 h de Colab [DUDOSO] |
| **Quiet-STaR** | Tokens de pensamiento en cada posición, REINFORCE | [arXiv 2403.09629](https://arxiv.org/abs/2403.09629); documento de Christiam §3 | **No**: pide cómputo de preentrenamiento y alarga la salida, lo contrario de lo que el N2840 necesita | — |
| **Interacción maestro → alumno** (BabyLM 2025) | Un modelo grande da retroalimentación al chico durante el entrenamiento | Findings BabyLM 3 ([ACL 2025.babylm-main.28](https://aclanthology.org/2025.babylm-main.28)) | Sí, en la forma barata: Claude genera pares mínimos y correcciones a partir de los errores reales anonimizados; se entrena T con eso | Dentro de §1.3 |

**Principio de eficiencia de muestra que atraviesa todo:** entrenar al modelo chico **sólo en lo que la ERG y las reglas no cubren** (los cuatro tipos léxicos de §0 y lo que no analiza). Así el presupuesto de ejemplos no se gasta en concordancia, que ya está resuelta con 8/12 sin LLM.

### 1.7 Red de aulas (una línea)

Lo que viaja son ejemplos, reglas y el etiquetador T en KB, por USB o celular; la ciudad destila y firma la versión del mes; una frase de vereda puede identificar a un niño, así que sale sólo con consentimiento y revisión del profe (nota 10, Ley 1581 arts. 7 y 26).

---

## 2. Detección y corrección: de 59/90 hacia 75/90 sin perder falsas

Las cinco apuestas, ordenadas por ganancia esperada sobre el hueco de §0. Todas se desarrollan sobre A + B + C y la pantalla de 500 correctas; el banco v4 se toca una sola vez con 6 candidatos.

| # | Apuesta | Mecanismo | Tipos que ataca (hueco) | Predicción (instancias) | Riesgo en falsas |
|---|---|---|---|---|---|
| 1 | **Léxicos de transferencia como detectores deterministas** | Tres tablas: colocaciones *make/do/ask/take* + sustantivo (*make a question → ask*, *do a mistake → make*); preposición tras verbo y de tiempo (*depend of*, *married with*, *arrive to*, *in the night*, *in Monday*, *think in*, *listen the*); falsos cognados **con marco sintáctico** (*assist to* + lugar, *actually* inicial sin contraste, *sensible to*, *carpet* con *in my*…). Es la idea de las paráfrasis inducidas por la L1 de Dahlmeier & Ng 2011 ([ACL D11-1010](https://aclanthology.org/D11-1010/)): el error viene de traducir *hacer*, *asistir*, *de*. LanguageTool trae un archivo de falsos amigos por lengua materna que sirve de semilla ([documentación de `motherTongue`](https://language-tool-python.readthedocs.io/en/latest/references/examples.html); la ruta del archivo [DUDOSO]) | make_do (7), preposicion (3), falso_cognado (5) | +9 a +11 | Medio: las entradas ambiguas (*make exercise*) se mandan como **pregunta cerrada** al LLM: «¿*do exercise* o *make exercise*?», con el prefijo en caché cuesta ≈ 2 s y 1 token |
| 2 | **Ampliar la lista blanca de reglas `rbst` de la ERG** | `reparar.py` sólo escucha concordancia, tiempo y negación; la ERG «educ» trae 373 códigos, entre ellos la omisión del determinante obligatorio con sustantivo contable singular (Flickinger & Yu 2013, [ACL W13-3609](https://aclanthology.org/W13-3609/)) y la frase «Is raining today» **sí la analiza**, con una construcción de registro informal (SIMBOLICO §0): esa regla, en un aprendiz, es un error. Procedimiento: correr la ERG sobre B, listar qué reglas disparan por tipo, y admitir las que den 0 falsas en las 500 correctas | articulo (4), plural (3), sujeto_omitido (4) | +5 a +7 | Bajo si la pantalla de 500 se respeta; cada regla admitida con su tasa |
| 3 | **Orden del adjetivo por estructura, no por lista** | Dos vías: (a) cuando la ERG analiza, el predicado `_X_a_1` cuyo ARG1 es la variable del sustantivo y cuyo tramo `<a:b>` cae **después** del sustantivo sin cópula en medio; (b) cuando no analiza, patrón `DET N ADJ` con etiquetas POS del perceptron de NLTK (puro Python) y la lista de adjetivos ampliada a los ≈ 300 de A1–A2 | orden_adjetivo (5) | +3 a +4 | Bajo: excluir resultativos y cópulas como ya hace `_r_orden` |
| 4 | **Verificador por regeneración: el LLM propone, la ERG dispone** | Toda corrección del LLM se acepta sólo si analiza sin `rbst`, conserva la MRS (firma con tiempo y número) y cambia ≤ 3 palabras sin borrar; si no, se usa la corrección simbólica o se responde «no estoy seguro». Es LM-Critic al revés ([arXiv 2109.06822](https://arxiv.org/abs/2109.06822)) con un juez exacto. **Esto es lo que permite subir la detección sin subir las falsas** | Transversal; sube corrección exacta | Corrección exacta +8 a +12 /114; detección ±0 | Lo baja |
| 5 | **Tercer votante: la sonda S o el etiquetador T, con veto simbólico** | Decisión: si una regla o la ERG dispara → error (precisión alta); si no, error sólo si el LLM **y** S/T coinciden; una regresión logística apilada sobre los tres votos se calibra en desarrollo | Lo que quede (sobre todo lo léxico que el léxico no listó) | +3 a +5 | Medio; el apilado se calibra con tope de falsas ≤ 1/30 |

Suma esperada: +20 a +27 instancias, que en frases es llegar a **70–76/90**. La predicción honesta para v4 es **≥ 68/90 con ≤ 2/30 falsas** para la cadena con 1–4, y ≥ 72 si el votante 5 suma.

**Fuera de lo obvio, para probar después de las cinco:**
- **Decodificación restringida por gramática (GBNF de llama.cpp, [README de gramáticas](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md))** en dos niveles: (i) la salida sólo puede ser `{"correccion": …, "ficha": <uno de los 20 ids>}`, lo que convierte al 0,5B en un **clasificador de ficha** medible; (ii) una gramática **por frase** en la que cada palabra de la corrección es la original o una alternativa de su conjunto de confusión (3sg, pasado, a/an, be, don't/doesn't, to/for, make/do, currently/actually, in/on/at): el modelo no puede inventar ni borrar contenido y escribe menos tokens. Elimina las salidas mal formadas, no las mal entendidas (Geng et al., [arXiv 2305.13971](https://arxiv.org/abs/2305.13971)).
- **Votación por muestreo** ([self-consistency, arXiv 2203.11171](https://arxiv.org/abs/2203.11171)): no recomendable en el N2840 porque multiplica la generación; la versión barata es la pregunta cerrada de 1 token con prefijo en caché.
- **CG-3 (gramática de restricciones)** como formalismo de las reglas léxicas en vez de regex: aporta contexto, desambiguación y un motor maduro (GramDivvun, [visl.dk](https://edu.visl.dk/pdf/CG-workshop2019_paper_1.pdf)), pero exige un etiquetador previo y una dependencia GPL nueva. Mi lectura: sólo si los detectores en Python dejan de ser mantenibles; la inducción automática de §1.2 funciona igual con cualquiera de los dos.
- **Puntuar con el LLM en vez de generar**: para una frase con ≤ 3 correcciones candidatas (las que proponen los detectores), pedir la logprob de cada una con el prefijo en caché y quedarse con la mejor que apruebe la ERG. La perplejidad ordenó 80 % en la nota 07; con el veto de la ERG cierra el hueco de la frase genérica.

---

## 3. Acelerar el ciclo de mejora del sistema y el uso de la plata

**Lo que frena hoy:** cada variante consume un cupo del banco (6 por banco) y cada banco se agota en un día de trabajo bueno; v2 y v3 ya no sirven; el desarrollo se hace con frases propias que sobreestiman la cobertura.

1. **Tres niveles de datos, con reglas distintas.** (a) *Desarrollo* (A + B, no ciego, consultas ilimitadas): ahí se itera a minutos. (b) *Retenidas* (partición con vocabulario nuevo y la suite de §1.5, consultas contadas, p. ej. 1 por día): ahí se decide qué va al banco. (c) *Banco ciego* (v4–v6, cupo de 6, una corrida por versión). El cupo tiene fundamento formal: reusar un conjunto de prueba de forma adaptativa sobreajusta, y existe un mecanismo (Thresholdout) que permite muchas más consultas a cambio de ruido calibrado (Dwork et al. 2015, *Science*, [doi 10.1126/science.aaa9375](https://doi.org/10.1126/science.aaa9375)); vale la pena montarlo sobre un banco grande (300 frases) si el ritmo de candidatos sube.
2. **Bancos baratos y en serie.** Un banco de 120 frases cuesta ≈ 1 USD con Opus 5.5 más 30 min de curaduría de Christiam. Generar v4, v5 y v6 **ahora**, sellados, y no mirar ninguno hasta su corrida. El agente que los construye recibe sólo la lista de tipos y el nivel, nunca el tutor ni los detectores (ERR-T1).
3. **Una corrida, todos los brazos, una tabla.** `compara_f1b.py` ya hace McNemar; falta un solo comando que corra los 6 candidatos, la suite de entendimiento, la latencia en el PC y escriba el RESUMEN con la tabla por tipo. Preregistro commiteado antes, como hasta ahora.
4. **El activo que falta: frases reales.** 200 frases anonimizadas de aprendices de las fichas de Christiam, con consentimiento recogido por un tercero (nota 04 §7), son el único banco que nadie escribió y el que la tesis necesita. Son adultos, así que la Ley 1581 pide autorización, no el régimen de menores.
5. **Auditoría de sólo lectura** sobre cada preregistro y cada RESUMEN (ya es práctica): aquí sirve para dos cosas nuevas, vigilar el solape entre B y los bancos, y revisar las reglas inducidas automáticamente antes de que entren.
6. **La plata:** la tabla de §1.3 (≈ 25 USD) en la primera semana, ≈ 30 en la segunda según lo que falle, ≈ 40 de reserva que si no se usan al 18-nov se gastan en más corrupción etiquetada y un banco v7. Todo con la API en lote donde no haya prisa.

---

## 4. La pedagogía para el aprendiz (corta; nada de esto depende del modelo)

Los cuatro componentes con mejor evidencia ya estaban en la nota 04. Lo que agrego son las cifras de los mecanismos de *rapidez* de aprendizaje humano y cómo caben en las fichas:

| Mecanismo | Evidencia | Cómo se monta en las fichas | Humo |
|---|---|---|---|
| **Práctica de recuperación** (producir, no releer) | Testing > reestudio: g = 0,50, y 0,69 con un día o más de demora (Rowland 2014, *Psych. Bull.*, [doi 10.1037/a0037559](https://doi.org/10.1037/a0037559)); g = 0,61–0,70 en 272 efectos (Adesope et al. 2017, [doi 10.3102/0034654316689306](https://doi.org/10.3102/0034654316689306)); 80 % contra 36 % una semana después (Karpicke & Roediger 2008, *Science*, [doi 10.1126/science.1152408](https://doi.org/10.1126/science.1152408)) | Cada ficha genera 3 ítems de producción (corregir, completar, traducir del español) con el vocabulario del aprendiz; el primer turno siempre es suyo | Dentro del piloto |
| **Repaso espaciado** | Meta-análisis en L2, efecto medio-grande (Kim & Webb 2022, [doi 10.1111/lang.12479](https://doi.org/10.1111/lang.12479)); FSRS-6 log-loss 0,346 contra 0,469 de HLR ([srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark)) | BKT por ficha ([pyBKT, arXiv 2105.00385](https://arxiv.org/abs/2105.00385)) para «qué practicar»; [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) por ítem para «cuándo»; microsegundos | BKT sobre SLAM es→en, ≤ 0,03 de AUC del rival (nota 04 §6) |
| **Retroalimentación correctiva: pista antes que frase corregida, con explicación** | Prompts > recasts (Lyster & Saito 2010, [doi 10.1017/S0272263109990520](https://doi.org/10.1017/S0272263109990520)); en computador, la retroalimentación elaborada g = 0,49 contra 0,32 por dar la respuesta y 0,05 por decir «mal» (Van der Kleij et al. 2015, [doi 10.3102/0034654314564881](https://doi.org/10.3102/0034654314564881)); metalingüística + resaltado produce más autocorrección (Heift 2004, [doi 10.1017/S0958344004001120](https://doi.org/10.1017/S0958344004001120)); inmediata mejor que diferida en computador (Van der Kleij); enfocada y no enfocada rinden igual con artículos (Ellis et al. 2008, [doi 10.1016/j.system.2008.02.001](https://doi.org/10.1016/j.system.2008.02.001)) | Política de dos pasos: resaltar el tramo + `pista_es`; al segundo fallo, `ejemplo_bien` + `regla_es`. **Un tipo por turno**, elegido por BKT; los demás se registran en silencio. El LLM sólo conversa, ≤ 2 frases | Tasa de autocorrección sin ver la respuesta (Lyster & Ranta) |
| **Explícito para adultos A1–A2** | Explícito > implícito, también en rasgos complejos y en prueba diferida (Spada & Tomita 2010, [doi 10.1111/j.1467-9922.2010.00562.x](https://doi.org/10.1111/j.1467-9922.2010.00562.x); Norris & Ortega 2000, [doi 10.1111/0023-8333.00136](https://doi.org/10.1111/0023-8333.00136)) | Las fichas ya son explícitas y contrastivas (español ↔ inglés) | — |
| **Intercalar fichas entre sesiones** | Intercalar gramática mejora la retención a largo plazo (Nakata & Suzuki 2019, *MLJ* 103(3)); en conjugación, la ventaja aparece **entre sesiones**, no dentro de una (Pan et al. 2019, [preprint](https://sc-pan.github.io/pdf/PTLOR_2019W.pdf)) | El planificador mezcla 2–3 fichas con p(dominio) entre 0,3 y 0,8 por sesión | Diseño del piloto, no factor |
| **Carga cognitiva** | Ejemplo resuelto primero para el novato y retirarlo al ganar pericia (Sweller, van Merriënboer & Paas 2019, [doi 10.1007/s10648-019-09465-5](https://doi.org/10.1007/s10648-019-09465-5)) | Con p(dominio) < 0,3 se muestra `ejemplo_mal → ejemplo_bien` antes de pedir producción; después, sólo recuperación. Texto del LLM capado a 60 tokens | Medir largo de salida actual |
| **Uso, metas cortas, gamificación con cuidado** | El límite es el uso: 17 % de las sesiones con error escribieron al tutor (Oreopoulos & Low 2026, nota 04); metas específicas > «hazlo lo mejor que puedas» (Locke & Latham 2002, [doi 10.1037/0003-066X.57.9.705](https://doi.org/10.1037/0003-066X.57.9.705)); gamificación g = 0,49 en lo cognitivo, estable sólo en estudios rigurosos, menor en motivación y conducta (Sailer & Homner 2020, [doi 10.1007/s10648-019-09498-w](https://doi.org/10.1007/s10648-019-09498-w)) | Sesiones de 15 min **dentro** de la clase del SENA; «meta de hoy: 3 fichas»; barra de dominio por ficha; sin tablas de posiciones | Minutos y abandono desde el día 1 |
| **Voz offline** | Enseñar pronunciación d = 0,80–0,89 (Lee, Jang & Plonsky 2015, [doi 10.1093/applin/amu040](https://doi.org/10.1093/applin/amu040)); con ASR g = 0,69 y la explícita por fonema 0,86 (Ngo, Chen & Lai 2024, [doi 10.1017/S0958344023000113](https://doi.org/10.1017/S0958344023000113)); humo propio: GOP-L1 con ZIPA 59,6 % y 1/114 falsas (nota 09) | Primero lo gratis: audio Piper pregenerado del `ejemplo_bien` y la pista de cada ficha (0 s en el aparato). Después «lee conmigo» con ZIPA int8 | Latencia de ZIPA en el N2840 (≤ 3 s por frase) y L2-ARCTIC hispanos |

**Humo de pasillo con personas (semana 2, si Christiam quiere):** 8–10 aprendices adultos, 2 sesiones, intra-sujeto contrabalanceado: pista en la mitad de las fichas, frase corregida en la otra mitad. Medidas: autocorrección sin ver la respuesta, retención a 7 días con ítems nuevos, minutos de uso. No busca significancia (para eso son N ≈ 30–34, nota 04 §7): busca que la mecánica no se rompa y un prior del tamaño de efecto. Voluntario, sin nota, consentimiento recogido por un tercero.

---

## 5. Plan priorizado de dos semanas (5 → 19 de noviembre), centrado en que el sistema aprenda

| Día | Qué | Por qué | Costo | Predicción que puede fallar | Listo cuando |
|---|---|---|---|---|---|
| 1–2 | **Activos A, B, C, F, G, pantalla de 500 correctas**, con particiones por semilla y sha256 | Todo lo demás los usa; el crédito vence | ≈ 15 USD | B tiene ≥ 95 % de tramos bien ubicados en una muestra de 100 que audita Opus (H) | Carpeta `datos/` versionada, cruce de solape 0 con v3 |
| 2–3 | **Apuestas 1, 2 y 3 de §2** (léxicos, lista blanca ERG, orden por estructura) sobre desarrollo y retenidas | Mayor ganancia por hora; es lo que la ERG no sabe | 0 | Retenidas: +15 instancias sobre la cadena actual; 0/500 falsas | Detectores congelados en un commit con sus pruebas |
| 3 | **Apuesta 4** (verificador por regeneración) | Permite subir detección sin subir falsas | 0 | Corrección exacta +8 en retenidas | Función `verificar()` con 3 condiciones y sus pruebas |
| 3–5 | **Sonda S y etiquetador T** (§1.4), entrenados en el PC con B | Es el órgano que de verdad reentrena en minutos | 0 | T ≥ 0,85 en retenidas con vocabulario nuevo y ≤ 0,60 en estructura nueva; S ≥ 0,80 | Pesos < 40 MB, script de reentrenamiento de un comando, tiempo medido |
| 5–6 | **Biblioteca viva: memoria de casos + inducción de reglas con verificador** (§1.1–1.2), humo de los 2 tipos nuevos | Define el indicador «horas por tipo nuevo» | ≈ 4 USD | Detector verificado en ≤ 30 min y ≥ 60 % en retenidas, 0/100 falsas | Skill con tope de gasto; primer detector automático con procedencia |
| 6–8 | **SFT-LoRA del 0,5B en Colab** con D filtrado por la ERG; control sin filtrar; cuantizar y probar LoRA en ejecución | Única vía para que el 0,5B aprenda | 0 (Colab) | +8 corrección exacta en desarrollo; conserva ≥ 70 % tras Q4_0 | GGUF nuevo con sha; latencia en el PC medida |
| 8–9 | **Banco v4: una corrida, 6 candidatos** (cadena actual; +1–4; +S; +T; +LoRA; todo junto con apilado) y suite de entendimiento | Es la única medida que cuenta | 0 | Todo junto ≥ 68/90 con ≤ 2/30 falsas; T solo ≥ 35/90 | RESUMEN_v4 con tabla por tipo, McNemar y veredicto preregistrado |
| 10–11 | Según v4: **KTO/DPO con E** si el SFT dio algo; si no, segunda ronda de B sobre los tipos que fallaron; GRPO sólo si sobra tiempo y con control al azar | No gastar en lo que no dio señal | ≈ 10–30 USD | KTO ≥ SFT + 3 en retenidas | Decisión escrita de qué entra a la versión |
| 11–12 | **Paquete portable F4** al Chromebook con lo que ganó: biblioteca, T/S, LoRA si entra; calentar al arrancar; medir latencia | Que lo que aprendió corra donde importa | 0 | Mediana ≤ 7 s con todo; identidad simbólica 68/68 | `arrancar.sh` + Manifiesto con sha; misma salida que el PC |
| 12–13 | **Humo de pasillo** con 8–10 aprendices (§4) **o** recolección de las 200 frases reales, según la decisión 2–3 | Sin personas no hay tesis | 0 | Autocorrección sin respuesta ≥ 40 % con pista contra ≤ 20 % con recast [DUDOSO: prior mío] | Datos anónimos en el aparato; bitácora de uso |
| 14 | **Banco v5 para la versión del 19-nov**, auditoría de sólo lectura, escritura, gasto restante a activos | Cerrar con un número ciego y los activos comprados | resto | — | RESUMEN_v5, memoria y decisiones al día |

En paralelo, Christiam: aprobar las ≈ 10 fichas nuevas (make/do, preposiciones, plural con cantidad, artículo faltante, since/for, more + -er, pregunta sin do, doble negación, say/tell, go to home), los léxicos G, y decidir las tres cosas de abajo.

---

## 6. Las tres decisiones de Christiam

1. **¿El LLM sigue en el camino crítico del turno?** Propuesta: **símbolo primero, LLM después y capado.** La pista simbólica sale en < 0,5 s cuando una regla o la ERG disparan; el LLM llega a los 5–6 s sólo para conversar y para lo que nadie analizó, con salida de ≤ 60 tokens y bajo el verificador de la apuesta 4. Cambia la latencia percibida, el diseño del piloto y qué se mide.
2. **¿Autoriza recoger 200 frases reales anonimizadas de sus aprendices, con consentimiento tomado por un tercero?** Es el activo más valioso de la quincena y el único banco que nadie escribió. Sin él, todo lo de arriba sigue siendo sintético.
3. **¿Humo de pasillo con 8–10 personas en la semana 2, antes del aval de ética, o esperar?** Antes: da un prior del efecto y rompe lo que se tenga que romper; después: más limpio para la tesis pero sin señal humana hasta diciembre. La plata no exige decisión: la recomendación es activos de datos (≈ 25 + 30 USD) y nada de cómputo pago; sólo hay que decir si se objeta.

---

## 7. Lista [DUDOSO]

1. Tiempos de entrenamiento en Colab (SFT < 1 h; GRPO 1,5–2 h) y el costo de velocidad del LoRA en tiempo de ejecución en el N2840: sin medir.
2. Que RFT beneficie más a los modelos débiles y que algo de §1.6 funcione a 0,5B: no hay evidencia a ese tamaño; lo decide el humo.
3. Latencia de la sonda S (2–3 s con prefijo en caché) y del etiquetador T (ms) en el N2840: extrapolación.
4. Evidencia de un etiquetador de 2–10 M con errores **reales** de aprendices: no la encontré.
5. Nombre exacto de la construcción de la ERG que acepta «Is raining today» y de la mal-regla de determinante omitido en la versión 2025 «educ»: Flickinger & Yu 2013 la describen; hay que verla en `ParserErrorCodes.xlsx`.
6. Ruta del archivo de falsos amigos de LanguageTool y si trae el par es→en completo.
7. Los efectos de Adesope (0,61 fijo / 0,70 aleatorio) y el d ≈ 0,99 de la retroalimentación «de alta información» en Wisniewski et al. 2020 ([doi 10.3389/fpsyg.2019.03087](https://doi.org/10.3389/fpsyg.2019.03087)) vienen de resúmenes secundarios.
8. Nakata & Suzuki 2019: confirmé cita y hallazgo por fuentes que lo citan, no el resumen original.
9. El prior del humo de pasillo (40 % contra 20 % de autocorrección) es mío.
10. Precios de la API: tabla cacheada del 6-oct-2026; confirmar en la página oficial antes de gastar.
11. Que el PC pueda entrenar el LoRA sin GPU en horas razonables: no lo medí; por eso Colab.
