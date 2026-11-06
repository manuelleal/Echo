# Qué copiar de otros para el tutor offline (4-nov-2026)

**Veredicto: HAY ALGO MODESTO, y es útil.** Ninguno de los proyectos parecidos corrige gramática de forma verificable ni mide a ciegas: todos son chats con un LLM y encuestas Likert o anécdotas, sobre equipos con 4–8 GB o más y CPU moderna. Por eso no hay un sistema entero para copiar. Lo que sí está hecho, abierto y listo para tomar son **piezas**. Las reglas y falsos amigos de LanguageTool cubren justo nuestros huecos léxicos. La voz se arma con whisper.cpp, Vosk y Piper. Para medir sin gastar banco están ERRANT, un treebank con 500 frases reales de hispanohablantes y los corpus EFCAMDAT y SLAM. En conjunto, ahorran unas dos semanas de construcción (estimación mía).

Alcance: leí los cuatro documentos internos que pidió el encargo. No abrí nada bajo `TUTOR-LOCAL-EVAL\banco*`. Abrí cada enlace que cito. Marco **[DUDOSO]** lo que no pude abrir y lo que es estimación sin medir.

---

## 1. Proyectos parecidos: cómo están hechos por dentro

### 1.1 Tabla comparativa

| Proyecto | Hardware | Modelo y cuantización | Interfaz | ¿Cómo corrige? | ¿Cómo evalúa? | Resultados | Código / licencia |
|---|---|---|---|---|---|---|---|
| **Intel + WWT, Guatemala** (escuela Esperanza Juvenil) | Portátiles Dell con Intel Core Ultra (CPU + GPU + NPU) | No lo nombran: «free open source models», «tuned and adapted» a Guatemala | Chat. **Los profes revisan los registros de chat** para ajustar sus clases | No corrige gramática; es un tutor general de español, inglés y matemáticas | No hay evaluación | Sólo frases cualitativas («is already making a difference») | No hay código. Dicen que priorizan código abierto |
| **Walusimbi et al. 2026** (Uganda) | Equipos sólo con CPU, de 4 a 16 GB de RAM, con Windows | Tres niveles en GGUF de 4 bits, elegidos según el hardware al arrancar: TinyLlama-1.1B (2–3 GB), Qwen2.5-3B (4–6 GB) y Mistral-7B (8–12 GB) | Ejecutable de Windows con interfaz web local. RAG ligero sobre documentos locales. **Cuatro niveles de explicación** (Simple English, Lower Secondary, Upper Secondary, Technical). El modelo queda en memoria toda la sesión | No corrige: explica contenidos | Piloto con **120 estudiantes y 9 docentes en 4 instituciones**: registros de tiempo y una encuesta Likert de 5 puntos. Ellos mismos dicen que no midieron aprendizaje | Latencia típica de 1–3 s y máxima de unos 43 s. «Mayoría positiva» en Likert, sin cifras | No publican código. El artículo es CC BY 4.0. La página de arXiv dice que **una versión más nueva fue retirada** |
| **SparshAI** (India) | Portátil usado de 8 GB sin GPU (unas 18 000 rupias) | **Gemma 4 E4B**; no dice la cuantización ni el motor. Descartó E2B por «superficial» | Chat por teclado o por WiFi local; hindi, inglés o mezcla. **Caché de respuestas** a preguntas repetidas (idea tomada de LENTERA) | No corrige | 5 niños una tarde, «not a formal study» | Tarda 15–20 s en preguntas complejas; las repetidas salen casi al instante | Sin repositorio ni licencia |
| **AI Learning Box** (Ruanda) | Raspberry Pi 5 de 8 GB, sin pantalla, con microSD de 256 GB | Gemma2:2b con Ollama; prueba también aya-expanse:8b para kinyarwanda | Open-WebUI en Docker más **Kolibri** con lecciones offline (Khan Academy, African Storybook) | No corrige | No hay | Sólo cualitativo: los modelos chicos manejan mal el kinyarwanda | Sin código; un video en YouTube |
| **Project LocalMind** (Sudáfrica) | Escritorio reacondicionado que emite su propia red WiFi | Un SLM «ajustado» con los textos escolares de matemáticas de grados 10–12; no lo nombra | Chat web en la red local | No corrige | Todavía no: piloto planeado en 1–2 escuelas de Johannesburgo | Ninguno | Sin código |
| **Rori** (Rising Academies, Ghana) | Celulares básicos por WhatsApp (poco ancho de banda, **no** offline) | No lo dice | Chat de WhatsApp para matemáticas | Ejercicios de matemáticas | Unos 1000 alumnos de grados 3–9 en 11 escuelas, tratamiento contra control. El artículo no dice explícitamente que fuera aleatorizado | **Efecto de 0,37** en crecimiento en matemáticas (p < 0,001), sólo el primer año y «preliminar» | Sin código |
| **Efekta / EF** (Brasil, México, Rep. Dominicana) | No lo dice | No lo dice. Según su CEO, rehicieron la plataforma para que lo esencial funcione **sin internet** | Asistente de enseñanza de inglés, decide el profe | Práctica y retroalimentación «turno a turno» | Afirmaciones de la empresa: Paraná con 750 000 alumnos y «más del 32 %» en la prueba estatal en menos de dos años | Sin evaluación independiente | Cerrado |
| **llm_voice_chatbot_rpi** | Raspberry Pi 4 de 4 GB, micrófono USB y un botón | whisper.cpp + TinyLlama-1.1B Q5_K_M (llamafile) + Piper en_US-amy-medium | **Hablar mientras se aprieta el botón** | No corrige | No mide latencia: dice que «tarda un rato» | — | **MIT** y el código está completo |
| **GradrAI** (África) | Portátil del profe; los alumnos se conectan por su punto de acceso WiFi | Gemma 4 con Ollama | App de escritorio para crear y calificar exámenes | Califica ensayos | No hay | 8B sin GPU: unos 14 min para generar un examen | Sin repositorio |
| **Kolibri** (Learning Equality) | Equipos baratos o viejos como servidor local; Android 6 o más | — | Plataforma offline de contenidos, sincronización entre equipos o por USB, reportes para el profe | Ejercicios cerrados | — | Instalado en más de 220 países | **MIT** |

Fuentes, todas abiertas hoy:
- Intel/WWT: [nota de Intel](https://www.intel.com/content/www/us/en/newsroom/news/artificial-intelligence/intel-brings-offline-ai-opportunity-to-students-in-guatemala.html). [Techfinitive](https://www.techfinitive.com/intel-and-world-wide-technology-deliver-offline-ai-learning-to-students-in-guatemala/) respondió 403 **[DUDOSO]**, y las páginas de WWT llegaron vacías **[DUDOSO]**.
- Walusimbi et al.: [arXiv 2603.03339v2](https://arxiv.org/abs/2603.03339v2). Leí el PDF completo y de ahí salen la tabla 1, la tabla 2 y §4.
- [SparshAI](https://dev.to/_prshant01/sparshai-i-built-an-offline-ai-tutor-for-students-using-gemma-4-heres-what-happened-glk), [AI Learning Box](https://online.coolestprojects.org/projects/24549), [LocalMind](https://contest.techbriefs.com/2026/entries/robotics-and-automation/14333).
- Rori: [arXiv 2402.09809](https://arxiv.org/abs/2402.09809).
- Efekta: [The PIE News](https://thepienews.com/edtechs-moment-has-finally-arrived-efekta-educations-ai-teaching-assistants-are-taking-off-across-businesses-and-schools/). La afirmación de que funciona offline viene de un buscador que cita a Computer Weekly, que respondió 403 **[DUDOSO]**.
- [llm_voice_chatbot_rpi](https://github.com/zhoupingjay/llm_voice_chatbot_rpi), [GradrAI](https://dev.to/fiewor/how-gemma-4-helped-us-cut-the-last-wire-keeping-ai-out-of-african-classrooms-315i), Kolibri ([sitio](https://learningequality.org/kolibri/), [repositorio MIT](https://github.com/learningequality/kolibri)).
- LENTERA sólo lo conozco de segunda mano, por SparshAI **[DUDOSO]**.

### 1.2 Qué nos dice el cuadro

1. **Nuestro hueco no lo ocupa nadie.** Ninguno detecta ni corrige errores de aprendices, ninguno trae diagnóstico explicable y ninguno mide con un banco ciego. El más serio, Walusimbi, reporta latencia y Likert y dice que no midió aprendizaje. Para la tesis es la diferencia que se puede defender: **hardware más débil (N2840 sin AVX, 4 GB), corrección verificable y medición ciega.**
2. **Todos corren en máquinas mejores.** El piso de los demás es una Pi 5 de 8 GB o un portátil de 8 GB. El único que baja a 4 GB (Walusimbi, nivel 1) usa TinyLlama-1.1B, y en Uganda un equipo de 4 GB tiene AVX casi seguro.
3. **Ideas de diseño que se copian gratis** (ninguna exige código ajeno):
   - **Caché de respuestas** (SparshAI/LENTERA): nuestra cadena corre a temperatura 0, así que la misma frase normalizada da siempre el mismo resultado. Un diccionario `sha(frase normalizada) → salida` convierte los 6,3 s en milisegundos para las frases repetidas, que en un aula son muchas («My name is…», «I have 20 years»).
   - **Modelo residente y precalentado** (Walusimbi §3.5): ya lo pide F2 por la primera consulta de 39 s.
   - **Niveles de explicación** (Walusimbi §3.4): en nuestro caso serían dos niveles de pista (sólo resaltar, o resaltar y dar la regla), que ya están en la política de la nota de exploración.
   - **Registro de chats para el profe** (Intel/WWT): es la señal «aceptó, editó, ignoró» de la biblioteca viva, más un reporte simple para Christiam.
   - **Botón para hablar** (llm_voice_chatbot_rpi): evita detectar silencios y bajar el consumo de CPU.
   - **Normalizar la salida del modelo** (GradrAI: Gemma 4 rompía el esquema JSON): nosotros ya tenemos la gramática GBNF de llama.cpp en la lista.

---

## 2. Componentes abiertos que sirven hoy para nuestros puntos débiles

### 2.1 LanguageTool para hispanohablantes: ¿se pueden usar sus reglas sin Java?

**Sí, en parte, y vale la pena.** Lo que encontré:

| Pieza | Qué es | Lo que trae para nosotros | Licencia | ¿Cabe sin Java? |
|---|---|---|---|---|
| [`false-friends.xml`](https://github.com/languagetool-org/languagetool/blob/master/languagetool-core/src/main/resources/org/languagetool/rules/false-friends.xml) | Unas 14 600 líneas (488 KB) de grupos `<rulegroup>`, cada uno con `<pattern lang>` y `<translation lang>` | Grupos es↔en de verdad. En el primer quinto del archivo están ACTUAL (*actualmente → currently*), ADEPT, ALTERNATIVELY y ACCOMMODATION. Faltan por leer los cuatro quintos restantes | LGPL 2.1+ | Sí: es XML, se lee con `xml.etree` |
| [`confusion_sets_l2_es.txt`](https://github.com/languagetool-org/languagetool/tree/master/languagetool-language-modules/en/src/main/resources/org/languagetool/resource/en) | Pares que confunde un hispanohablante al escribir inglés, **generados a partir de false-friends.xml y dejando sólo los de precisión ≥ 0,9** | **26 pares activos y 15 comentados**, por ejemplo *actually → currently*, *eventually → possibly*, *realize → produce*, *notice → news*, *fabric → factory*, *form → shape*, *regular → steady*, *rent → pension*, *prevent → alert*, *comprehensive → understandable* | LGPL (la del repositorio) | La lista sí. **El detector no**: LanguageTool decide con conteos de 3-gramas de Google, que pesan **8,3 GB comprimidos y unos 14 GB descomprimidos** ([Wikipedia](https://en.wikipedia.org/wiki/LanguageTool), [Cloudron](https://docs.cloudron.io/packages/languagetool)) |
| Reglas de colocaciones en inglés (`grammar.xml`) | Patrones en XML sobre palabras y etiquetas de categoría | Sirven estas, vistas en el [índice de reglas](https://community.languagetool.org/rule/list?lang=en&filter=depend&search=Search): **DEPEND_ON** (*He depends of you*), **DID_A_MISTAKE** (*I did a mistake*), **MARRY_WITH** (*married with*), **ARRIVE_NNP** (*arrive Dallas*), ARRIVE_AT_IN, APPLY_TO. **No hay** regla para *I have 20 years* ni para *make a question* | LGPL 2.1 | Las que sólo miran palabras se pasan a regex. Las que usan etiquetas necesitan el etiquetador |
| [**nlprule**](https://github.com/bminixhofer/nlprule) | LanguageTool reimplementado en **Rust, sin Java**, con módulo de Python | **3725 reglas de gramática en inglés, ~85 % de LT 5.2**, y el 100 % de las de desambiguación. Corre unas 1,7–2 veces más rápido que LT | Código MIT o Apache-2.0; los binarios de reglas son LGPL 2.1 | Sí, pero **los wheels sólo existen para Python 3.6–3.9**, 0.6.4 del 24-abr-2021, de unos 3,4 MB ([PyPI](https://pypi.org/pypi/nlprule/0.6.4/json)). En candy haría falta un Python 3.9 aparte o compilar el crate de Rust en el PC |

En la página oficial, [usage-of-false-friends-rule](https://dev.languagetool.org/usage-of-false-friends-rule) (marcada «outdated»), LanguageTool explica que `false-friends.xml` ya sólo arma el mensaje y que la detección la hacen los archivos `confusion_sets_l2_xx.txt`.

**Versión fuerte de esta copia: el método de LanguageTool con nuestro propio modelo de lenguaje.** LanguageTool decide entre *actually* y *currently* con 8 GB de 3-gramas. Nosotros ya tenemos en memoria un modelo de lenguaje: el Qwen 0,5B. La copia es esta:
1. Tomar los pares de `confusion_sets_l2_es.txt`, los grupos es→en de `false-friends.xml`, las colocaciones de LT y los léxicos G de la nota de exploración.
2. Cuando aparece la palabra del par, puntuar las dos variantes de la frase con la logprob del 0,5B, con el prefijo en caché y sin generar texto.
3. Calibrar el umbral **como LT**, con su propio evaluador (`AutomaticConfusionRuleEvaluator`): sólo entra un par si alcanza **precisión ≥ 0,9** en las 500 frases correctas y en los pares mínimos.

Así un solo mecanismo cubre falsos cognados, make/do y preposiciones, que juntos son 15 de las 34 instancias que hoy se nos escapan.

**Licencia.** Las reglas son LGPL. Si las pasamos a Python, conviene dejarlas en un archivo aparte (`detectores_lt.py`) con la atribución y la misma licencia, y el resto del tutor queda libre.

**Riesgo en una línea:** LT tiene pocas reglas pensadas para la L1 española (sólo los falsos amigos), así que en make/do aporta casi nada fuera de DID_A_MISTAKE. Ese tipo seguirá dependiendo de nuestro léxico G.

### 2.2 Corrección gramatical de otros: ERRANT, GECToR y T5 chico

| Componente | Qué es | Licencia | ¿Cabe en el N2840? | Uso que le veo |
|---|---|---|---|---|
| [**ERRANT**](https://github.com/chrisjbryant/errant) | Recibe la frase original y la corregida, extrae las ediciones y les pone tipo (`VERB:SVA`, `DET`, `PREP`…) en formato M2. Trae su script de evaluación | MIT; necesita spaCy + `en_core_web_sm` | No hace falta: corre en el PC | (1) **Evaluar por tipo y con F0.5** las correcciones del tutor, comparables con la literatura BEA. (2) **Etiquetar en automático el tramo y el tipo** de los datos sintéticos B. (3) Comprobar que la ficha que dice el tutor coincide con el tipo ERRANT |
| [**GECToR**](https://github.com/grammarly/gector) (Grammarly) | Etiquetador «tag, not rewrite» sobre BERT, RoBERTa o XLNet. F0.5 en la prueba BEA-2019: **71,8** con RoBERTa y 71,2 con XLNet. Hasta 10 veces más rápido que seq2seq | Apache-2.0, con pesos oficiales | No comprobado: RoBERTa-base tiene unos 125 M de parámetros y haría falta ONNX o torch sin AVX **[DUDOSO]** | Copiar **el vocabulario de etiquetas y el diccionario de formas verbales** (`verb-form-vocab.txt`) para nuestro etiquetador T y para los detectores de 3sg y pasado. Usarlo como **maestro en el PC** para preetiquetar datos |
| [gotutiyan/gector](https://github.com/gotutiyan/gector) | Reimplementación sin AllenNLP, con 8 checkpoints en HF. [roberta-base-5k](https://huggingface.co/gotutiyan/gector-roberta-base-5k) tiene 0,1 B; DeBERTa-large llega a 73,8 en BEA-2019 | Código MIT; **pesos «Only non-commercial»** | Igual que arriba | El atajo práctico para correr GECToR en el PC con Python 3.11 |
| [Unbabel/gec-t5_small](https://huggingface.co/Unbabel/gec-t5_small) | T5-small ajustado con cLang-8; la ficha dice **F0.5 = 60,7** | Apache-2.0 | Unos 60 M. llama.cpp tiene soporte de T5, pero no comprobé que funcione en `llama-server` **[DUDOSO]** | Un **tercer votante barato** que no es un LLM general |
| [CoEdIT-large](https://huggingface.co/grammarly/coedit-large) | Flan-T5-large (770 M) para editar texto | **CC BY-NC 4.0** | Pesado para 4 GB junto a lo demás | Sólo como juez en el PC; no vale el esfuerzo |

**Lectura.** Estos sistemas se entrenaron con FCE, W&I y Lang-8: ensayos B1–C1 con errores generales, muy pocos de transferencia español→inglés como *have 20 years*, *make a question* o *assist to*. Sirven para artículo, plural, preposición y forma verbal, no para falsos cognados. Por eso el mejor uso inmediato no es ponerlos en candy: es **ERRANT para medir y las etiquetas de GECToR como molde**.

### 2.3 Datos de errores de aprendices: cuáles sirven de verdad

**Corrección importante al encargo:** CEDEL2 y COWS-L2H son corpus de gente que **aprende español**, no inglés.
- [CEDEL2](http://cedel2.learnercorpora.com/) tiene 15 L1 aprendiendo español; licencia CC BY-NC-ND 3.0 ES.
- [COWS-L2H](https://github.com/ucdaviscl/cowsl2h) son ensayos de cursos de español de UC Davis; Apache-2.0.

Para errores es→en no sirven. Los que sí:

| Conjunto | Qué trae | Nivel | ¿Hay L1 español? | Licencia / acceso | Uso |
|---|---|---|---|---|---|
| [**TLE / UD_English-ESL**](https://github.com/UniversalDependencies/UD_English-ESL) | 5124 frases de FCE con árbol UD en su forma original y en la corregida | B2 (FCE) | **Sí: 500 frases de hispanohablantes**, cada una con al menos un error gramatical ([Berzak et al. 2016](https://aclanthology.org/P16-1070/)) | Anotaciones CC BY-SA 4.0; el texto se baja aparte de FCE, sólo para uso no comercial | Conjunto de **desarrollo real** inmediato, nunca banco ciego. Distribución de tipos del hispanohablante. Probar `detectores_lt.py` |
| [FCE v2.1 y W&I+LOCNESS v2.1](https://www.cl.cam.ac.uk/research/nl/bea2019st/) | W&I+LOCNESS: 3700 textos, 43 169 frases, niveles A, B y C. FCE: 1244 respuestas | A–C | El sitio no lo dice para W&I | **Sólo uso no comercial**, descarga directa | La parte A de W&I como más desarrollo |
| [Write & Improve 2024](https://researchdatasets.cambridge.org/datasets/write-and-improve-corpus-2024) | 5050 conjuntos de 766 aprendices, unas 762 000 palabras, con etiquetas CEFR | A–C | No lo dice | No comercial. **Prohíbe publicar modelos o estadísticas derivadas sin permiso** y usar LLM que no sean locales o sin retención | Sólo para mirar; no entrenar con esto lo que se publique |
| [**EFCAMDAT**](https://ef-lab.mmll.cam.ac.uk/EFCAMDAT.html) (EF y Cambridge) | 1 180 310 textos de 174 743 aprendices, con 16 niveles alineados al CEFR y una parte limpia, etiquetada por categoría y **con códigos de error** | **Desde A1** | Las 11 nacionalidades principales, que la página no nombra. Que estén Brasil y México es un recuerdo mío **[DUDOSO]** | Afiliación académica, formulario y acuerdo de uso | **La fuente más parecida a nuestros aprendices** (adultos, A1–A2, escritura libre corta). **Pedir el acceso ya**: es un trámite |
| [**SLAM 2018 (Duolingo)**](https://sharedtask.duolingo.com/2018.html), pista `en_es` | Respuestas de **hispanohablantes que aprenden inglés en sus primeros 30 días**, con 0 o 1 por palabra (error u OK). Más de 2 M de tokens y 6000 usuarios entre las tres pistas | A1 | Sí, por definición | Bajada de [Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/8SWHNO); la licencia no la pude leer **[DUDOSO]** | Ya está en la nota 04 para BKT. Sirve también para ver qué palabras falla un hispanohablante A1 |
| **CLEC** (Universidad del Norte y U. de Antioquia, [Pardo Rodríguez 2020](https://revistas.udea.edu.co/index.php/lyl/article/view/343874)) | **515 textos de universitarios colombianos**, 149 325 tokens, etiquetados con el manual de Lovaina (8 categorías y 56 etiquetas) | B1.1–B2.3 | Sí, colombianos | El artículo es CC BY-NC-SA 4.0; **el corpus no dice cómo se accede** | Escribir a la autora: es colombiano y sirve como antecedente de la tesis |
| WriCLE (U. Autónoma de Madrid) | Aprendices L1 español → L2 inglés | Universitario | Sí | No encontré cómo se accede **[DUDOSO]** | — |
| [C4_200M](https://github.com/google-research-datasets/C4_200M-synthetic-dataset-for-grammatical-error-correction) | 200 M de frases corrompidas de forma sintética; se reconstruyen desde C4 | — | No (errores generales) | Ediciones CC BY 4.0 | Baja prioridad: nuestro activo B, hecho a medida, es mejor |

### 2.4 Modelos chicos con sus números publicados en CPU

| Modelo | Tamaño en GGUF | Velocidad publicada | Licencia | ¿Cabe en el N2840 (3,8 GB útiles, sin AVX)? |
|---|---|---|---|---|
| [**Gemma 4 E2B**](https://huggingface.co/google/gemma-4-E2B-it) | 2,3 B efectivos y **5,1 B con las embeddings por capa**. [Q4_0 = 3,04 GB, Q3_K_S = 2,45 GB, IQ2_M = 2,29 GB](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF). Acepta **audio** (ASR de hasta 30 s) | Pi 5 de 8 GB: [8–12 tok/s](https://dev.to/alanwest/gemma-4-runs-on-a-raspberry-pi-i-tested-it-56c5). i5-6400 con Ollama: [6,9 tok/s y 6,3 GB de RAM promedio](https://dev.to/gramli/old-pc-vs-new-ai-can-a-2015-desktop-actually-run-gemma-4-2b-vs-4b-benchmark-2eg6) | Apache-2.0 | **Apenas.** Q4_0 llena casi toda la memoria con 0,25 GB de ACE al lado. Por cómputo, unas 4–5 veces el 0,5B: ≈ 2 tok/s en el N2840 **[DUDOSO, extrapolado de H06]**. Sólo Q3_K_S o IQ2 entran con margen |
| Gemma 4 E4B | — | Pi 5: 3–5 tok/s, con swap | Apache-2.0 | **No** |
| Qwen2.5-1.5B (ya probado por nosotros en el PC) | ≈ 1 GB en Q4_0 | — | Apache-2.0 | **Sí**: F2 dice que cabe. F1 mostró que el 1,5B **sí aprende de ejemplos** (52 contra 46, p = 0,031) |
| [LFM2-350M](https://huggingface.co/LiquidAI/LFM2-350M) (y 700M y 1.2B) | 354 M; hay GGUF oficial | El fabricante dice que decodifica y lee el prompt **2 veces más rápido que Qwen3 en CPU** | LFM Open License v1.0, cuyos términos no leí **[DUDOSO]** | Sí; candidato para la parte de conversar |
| [Gemma 3 270M](https://huggingface.co/google/gemma-3-270m) | 0,3 B, pensado para ajustarlo a una tarea | No publican velocidad | Licencia Gemma, que se acepta en HF | Sí; candidato para el **etiquetador o clasificador de ficha** ajustado (el T de la nota de exploración) |

**Lectura.** Gemma 4 es la estrella de los proyectos de este año (SparshAI, GradrAI, la Pi 5), pero en todos corre sobre 8 GB. En el N2840 lo sensato es **probar antes Qwen2.5-1.5B**: cabe, ya sabemos que aprende de ejemplos y es de la misma familia que el 0,5B. Gemma 4 E2B se prueba en IQ2 o Q3 sólo por su ASR integrado, para ver si un único modelo puede escuchar y corregir. Espero que no alcance la velocidad.

### 2.5 Voz en CPU vieja

| Componente | Tamaño y RAM | Licencia | ¿Cómo corre sin AVX? | Nota |
|---|---|---|---|---|
| [**whisper.cpp**](https://github.com/ggml-org/whisper.cpp) tiny.en / base.en | tiny: 75 MiB en disco y ~273 MB de RAM. base: 142 MiB y ~388 MB. Admite cuantización (q5_0) | MIT | **Usa la misma biblioteca ggml que nuestro llama.cpp**, que ya compila y corre en candy: es la vía con menos riesgo | Riesgo pedagógico **[DUDOSO, por medir]**: el modelo de lenguaje de Whisper tiende a «arreglar» lo que dice el aprendiz y así esconde el error que queremos ver |
| [**Vosk**](https://alphacephei.com/vosk/models) `small-en-us-0.15` | 40 MB; WER 9,85 en LibriSpeech test-clean | Apache-2.0 | Kaldi, pensado para Android y Raspberry Pi. No verifiqué el wheel x86 sin AVX **[DUDOSO]** | Los modelos chicos **dejan cambiar el vocabulario en ejecución**: en «lee conmigo», se le da la frase esperada y devuelve la confianza por palabra, que sirve como medida barata de pronunciación. También hay `small-es-0.42` (39 MB) para entender órdenes en español |
| [Moonshine](https://github.com/moonshine-ai/moonshine) tiny | [27 M](https://huggingface.co/UsefulSensors/moonshine-tiny); sólo inglés | MIT (los modelos viejos que no son de inglés usan otra licencia, no comercial) | Su biblioteca usa ONNX Runtime: mismo riesgo que abajo | El artículo dice **5 veces menos cómputo que Whisper tiny.en** en un fragmento de 10 s sin perder WER ([arXiv 2410.15608](https://arxiv.org/abs/2410.15608)) |
| [**Piper**](https://github.com/rhasspy/piper) | Voces en_US/en_GB, es_MX, es_ES y es_AR ([lista](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)) | El original es MIT, **archivado el 6-oct-2025**. Sigue como [piper1-gpl](https://github.com/OHF-Voice/piper1-gpl), con licencia **GPL-3.0** | Usa ONNX Runtime. Hay un reporte de que el **paquete de Python cae con SIGILL** en una Pi Zero 2W mientras el binario suelto sí funciona ([issue #773](https://github.com/rhasspy/piper/issues/773)) | **Generar en el PC el audio de las 10 fichas y de sus pistas** (0 s y 0 riesgo en candy). La voz es_MX sirve para leer las pistas en español |
| [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | Un solo motor para ASR (Zipformer, Whisper, Moonshine), TTS (Piper/VITS), detección de voz y palabras clave | Apache-2.0 | ONNX Runtime | Útil si ONNX Runtime pasa la prueba en candy |

**El riesgo que cruza toda la columna: ONNX Runtime sin AVX.** Una guía de terceros dice que el ONNX Runtime empaquetado se compila con AVX2 de base. La salida es compilarlo desde el código con `onnxruntime_DISABLE_AVX=ON`, `onnxruntime_DISABLE_AVX2=ON` y `onnxruntime_DISABLE_AVX512=ON` ([memtrace](https://cdn.jsdelivr.net/gh/syncable-dev/memtrace-public@main/docs/pre-avx2-cpus.md)). No es documentación oficial **[DUDOSO]**. Por eso la voz sigue el orden whisper.cpp (ggml) → Vosk → todo lo que depende de ONNX (Piper en vivo, Moonshine, ZIPA, sherpa), y antes se corre una prueba de una línea en candy.

### 2.6 Pronunciación

| Componente | Qué es | Licencia | ¿Cabe? |
|---|---|---|---|
| [**ZIPA**](https://github.com/lingjzhu/zipa) ([arXiv 2505.23170](https://arxiv.org/abs/2505.23170v1), ACL 2025) | Reconocedor de fonemas multilingüe. Las versiones small (64–65 M) superan a sistemas anteriores de 300 M. Hay ONNX en FP32, FP16 e **INT8** | Código MIT. Pesos CC BY 4.0, salvo las variantes «Ns», que son CC BY-NC-SA | 64 M en INT8 es chico. Depende de ONNX Runtime en candy **[DUDOSO]**. La nota 09 ya midió 59,6 % y 1/114 falsas en el PC |
| [**L2-ARCTIC**](https://psi.engr.tamu.edu/l2-arctic-corpus/) | 24 hablantes, **4 con L1 español** (EBVS, ERMS, MBMPS, NJS), con unos 150 enunciados por hablante anotados por fonema (sustitución, borrado, inserción) | CC BY-NC 4.0, se pide por formulario | Es para validar en el PC |
| [speechocean762](https://openslr.org/101/) | 5000 frases con puntaje por fonema, palabra y frase | CC BY 4.0 | Todos sus hablantes tienen L1 mandarín: sirve para calibrar el GOP, no las 13 reglas del hispanohablante |

No encontré un puntuador de pronunciación abierto, offline y listo para hispanohablantes. Lo más cercano a «copiar» sigue siendo **ZIPA-small INT8 + GOP + nuestras 13 reglas** (nota 09), validado con los 4 hablantes hispanos de L2-ARCTIC. En candy, la versión barata es Vosk con la frase esperada como gramática.

---

## 3. Qué copiar, por prioridad

Los «días ahorrados» son mi estimación de lo que costaría construirlo desde cero. Las mejoras esperadas son predicciones que hay que medir con preregistro.

| # | Componente | Qué nos ahorra | Mejora esperada (tipo o función) | Licencia | ¿Cabe en el N2840? | Esfuerzo | Prueba chica para validarlo |
|---|---|---|---|---|---|---|---|
| 1 | **Pares y falsos amigos de LT** (`confusion_sets_l2_es.txt`, grupos es↔en de `false-friends.xml`) **+ puntuación con la logprob del 0,5B** en lugar de los 3-gramas | 2–3 días de armar el léxico de falsos cognados y el método de calibración | falso_cognado (hueco 5) y, con el mismo mecanismo y el léxico G, make_do (7) y preposicion (3): **+4 a +8 instancias** | LGPL 2.1 (archivo aparte) | Sí: es una pasada de prompt con el prefijo en caché, sin generar | 1 día | 300 pares mínimos con vocabulario nuevo: ≥ 85 % prefiere la buena; 0 falsas en las 500 correctas; ningún par entra con precisión < 0,9, como en LT |
| 2 | **Reglas de colocación de LT** (DEPEND_ON, DID_A_MISTAKE, MARRY_WITH, ARRIVE_*, APPLY_TO…) medidas con **nlprule** en el PC y pasadas a regex las que den 0 falsas | 1–2 días de escribir reglas de preposición | preposicion, make_do: +2 a +4 | Código MIT/Apache; reglas LGPL | Las regex sí (ms); nlprule queda en el PC con Python 3.9 | 1 día | nlprule sobre las 500 correctas + las 500 frases de TLE: reglas que disparan por tipo y falsas |
| 3 | **ERRANT** en el arnés | 1–2 días de clasificar ediciones a mano; vuelve comparables nuestras cifras con BEA | Medición: F0.5 por tipo y acuerdo ficha↔tipo. Etiquetado automático del activo B | MIT | No hace falta (PC) | 0,5 día | Correr sobre 50 pares de desarrollo: % de acuerdo entre el tipo ERRANT y nuestra ficha |
| 4 | **TLE: 500 frases reales de hispanohablantes** (más EFCAMDAT y SLAM `en_es` en cuanto haya acceso) | Semanas de conseguir errores reales mientras llega el consentimiento de las 200 frases | Desarrollo con errores reales; corrige la sobreestimación de cobertura de las frases propias (F1b, ERR-T1) | CC BY-SA + FCE no comercial; EFCAMDAT con acuerdo | No aplica | 0,5 día (EFCAMDAT: trámite) | Correr la cadena actual sobre las 500 de TLE y comparar la distribución de tipos con la de nuestro sintético (sólo agregados) |
| 5 | **whisper.cpp tiny.en** + el bucle de **botón para hablar** de llm_voice_chatbot_rpi | 2–3 días de pelear con dependencias de ASR y de armar el bucle de audio | Función nueva: voz (PLAN #3) | MIT | **Casi seguro sí** (ggml, como llama.cpp). ~273 MB | 1 día | 20 frases leídas por Christiam en candy: tiempo por frase, RAM y WER; y **cuántos errores gramaticales sembrados «arregla» Whisper** |
| 6 | **Audio de Piper pregenerado en el PC** (en_US para ejemplos, es_MX para pistas) | 1 día | Función: escuchar el `ejemplo_bien` y la pista sin costo en candy | MIT (v1) o GPL-3.0 (piper1) | Sí: son archivos WAV u OGG | 0,5 día | 10 fichas × 2 audios; tamaño total y que suenen en candy |
| 7 | **Caché de respuestas** (SparshAI/LENTERA) + **calentado al arrancar** (Walusimbi) | 0,5 día de diseño | Latencia percibida: de 6,3 s a ms en las frases repetidas; quita los 39 s de la primera | Idea, sin código | Sí | 2 horas | Con 68 frases propias repetidas: aciertos de caché y salida idéntica bit a bit |
| 8 | **Vosk small-en-us** con la frase esperada como gramática, para «lee conmigo» | 2 días de un puntuador mínimo | Función: pronunciación por palabra (confianza) antes de que llegue ZIPA | Apache-2.0 | Probable; el wheel sin AVX está **[DUDOSO]** | 1 día | 20 lecturas buenas y 20 con un sonido cambiado a propósito: separación de la confianza por palabra |
| 9 | **Etiquetas de GECToR + `verb-form-vocab.txt`** como molde del etiquetador T; GECToR-RoBERTa como maestro en el PC | 1–2 días de diseñar el inventario de etiquetas y las formas verbales | articulo, plural, concordancia y pasado en T | Apache-2.0 (los pesos de gotutiyan son no comerciales) | El modelo completo no se probó en candy **[DUDOSO]**; el vocabulario sí | 1 día | GECToR en el PC sobre las 500 de TLE: F0.5 por tipo ERRANT, como techo de referencia |
| 10 | **Qwen2.5-1.5B Q4_0** antes que Gemma 4 E2B; LFM2-350M como LLM de conversación rápida | 1 día de descartar caminos | La parte del LLM; que los ejemplos en el prompt vuelvan a servir (F1) | Apache-2.0; LFM con licencia propia | 1,5B sí; Gemma 4 E2B sólo en IQ2 o Q3 | 1 sesión (PLAN #5) | Como en H06: tok/s, RAM y 12 frases. Gemma 4 E2B sólo si el 1,5B baja de 3 tok/s |
| 11 | **ZIPA-small INT8** + validación con los 4 hispanos de **L2-ARCTIC** | Semanas: el reconocedor de fonemas ya existe y está medido | Función: decir *qué* sonido falló (PLAN #4) | MIT + CC BY 4.0; L2-ARCTIC no comercial | Depende de ONNX Runtime sin AVX **[DUDOSO]** | 2–3 sesiones | Primero la prueba de una línea: `onnxruntime` carga y corre ZIPA INT8 en candy sin SIGILL; luego la latencia por frase (meta ≤ 3 s) |
| 12 | **Kolibri** para repartir fichas y audios y ver reportes del profe | Días de construir distribución y reportes | Despliegue en varias aulas (nota 10) | MIT | Corre en equipos viejos; no se probó en candy | Más de 2 días | No antes del piloto; anotarlo como opción |

**Lo que NO copiaría:**
- Las reglas de W&I 2024 aplicadas al entrenamiento: su licencia prohíbe publicar modelos derivados sin permiso.
- CoEdIT: es no comercial y pesado.
- Gemma 4 E4B: no cabe.
- La «evaluación» de los proyectos parecidos (Likert o anécdotas): la nuestra ya es mejor y es lo que nos diferencia.

---

## 4. Lista [DUDOSO]

1. El artículo de Techfinitive respondió 403 y las páginas de WWT llegaron vacías. Lo de Guatemala viene de la nota de Intel.
2. Que Efekta funcione sin internet viene de una cita de segunda mano; Computer Weekly respondió 403. Las cifras de Paraná (750 000 alumnos, +32 %) son de la empresa.
3. LENTERA: lo conozco sólo por SparshAI.
4. Licencia de SLAM 2018: Dataverse llegó vacío.
5. Que EFCAMDAT incluya a Brasil y México entre sus 11 nacionalidades principales.
6. Acceso a WriCLE y a CLEC.
7. Términos de la LFM Open License.
8. Que ONNX Runtime, el wheel de Vosk y el paquete de Python de Piper corran en el N2840 sin AVX. El dato del AVX2 viene de una guía de terceros.
9. Que `llama-server` corra modelos T5 (gec-t5_small). La F0.5 de 60,7 está tomada de la ficha del modelo.
10. Gemma 4 E2B a ≈ 2 tok/s en el N2840: es una extrapolación mía.
11. Que Whisper «arregle» la gramática del aprendiz: es un riesgo por medir, no un dato.
12. Leí sólo el primer quinto de `false-friends.xml`. El número total de grupos es↔en está por contar.
13. «Días ahorrados» y «mejora esperada» de la tabla 3: son estimaciones mías.

---

## Las 3 cosas que copiaría mañana

1. **El método de falsos amigos de LanguageTool con nuestro 0,5B como juez:** los 26 pares de `confusion_sets_l2_es.txt`, los grupos es↔en de `false-friends.xml` y las reglas DEPEND_ON, DID_A_MISTAKE y MARRY_WITH pasadas a `detectores_lt.py` (LGPL, archivo aparte). La logprob del 0,5B reemplaza los 8 GB de 3-gramas, con el mismo umbral de precisión ≥ 0,9 que usa LT. Ataca falsos cognados, make/do y preposiciones, donde está casi la mitad de lo que se nos escapa.
2. **La voz con piezas ya probadas:** compilar whisper.cpp tiny.en en candy (misma ggml que llama.cpp), copiar el bucle de botón para hablar de `llm_voice_chatbot_rpi` (MIT) y generar en el PC con Piper el audio de las 10 fichas y sus pistas. Primera medida: tiempo por turno, RAM, y cuántos errores sembrados «arregla» Whisper.
3. **Medir con lo de otros sin gastar banco:** ERRANT en el arnés (F0.5 por tipo y etiquetado automático de los datos sintéticos) y las **500 frases reales de hispanohablantes del TLE** como conjunto de desarrollo. Ese mismo día, **pedir el acceso a EFCAMDAT** (A1–A2, adultos, con códigos de error), porque es un trámite y tarda.

---

INCOMPLETA (cierre apurado porque se apagaba el PC). Faltó:
- leer los cuatro quintos restantes de `false-friends.xml` y contar los grupos es↔en;
- confirmar la licencia de SLAM y de LFM2;
- buscar un tutor de pronunciación offline ya hecho para hispanohablantes, aparte de los componentes sueltos.
