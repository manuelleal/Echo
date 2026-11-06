Voy a investigar en lotes, empezando por los productos, los trabajos académicos y la pedagogía.**Veredicto:** las piezas existen por separado (role-play con LLM en la nube, tutores locales de un solo usuario, voz sin internet). No encontré a nadie que junte tutor con rol y tareas, corrector verificado por reglas y gramática, memoria del aprendiz y voz, todo offline en un Celeron N2840 de 4 GB con un modelo de 0,5B para hispanohablantes A1–A2. El concepto ya está validado por otros, pero la evidencia con modelos pequeños y offline casi no existe, y eso es lo novedoso de ustedes. [DUDOSO: la cobertura es parcial, porque la herramienta de búsqueda se agotó a mitad de la investigación. Dejé marcado lo que no pude abrir.]

---

## 1. Referentes (14)

| # | Referente | Qué hace | Evidencia publicada | Licencia / ¿reutilizable? |
|---|---|---|---|---|
| 1 | [Duolingo Max: Roleplay y Video Call](https://duolingo-papers.s3.amazonaws.com/reports/Duolingo_whitepaper_language_video_call_improves_speaking_2025.pdf) | Escenario con personaje generado por GPT. En Video Call, la conversación con «Lily» corre con GPT-4o. | Informe del propio Duolingo con aprendices japoneses. Habla mejor que el control y hablar más palabras se correlaciona con mejor puntaje. Lily no da retroalimentación en tiempo real y la confianza reportada quedó «neutral». (Solo vi el resumen del buscador; el PDF no abrió.) | Propietario. Se copian las ideas, no el código. |
| 2 | [Praktika](https://openai.com/index/praktika/) | Avatares con sistema multiagente y memoria de largo plazo, sobre GPT-4.1. | Datos del proveedor: +24 % de retención el día 1 tras la memoria larga. | Propietario. Sirve para justificar la memoria. |
| 3 | [Speak](https://siliconangle.com/2024/12/10/openai-backs-78m-round-ai-language-learning-startup-speak/) | Práctica hablada con IA, respaldada por OpenAI según la nota. | No encontré estudio revisado por pares, solo reseñas de blogs. | Propietario. |
| 4 | [ELSA Speak](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0317378) | Pronunciación con IA. | El estudio de PLOS ONE mide satisfacción de estudiantes de inglés, no aprendizaje. Los estudios pequeños que vi en ResearchGate son cuasi-experimentales y no los abrí. | Propietario. |
| 5 | Gliglish / [Talkpal](https://talkpal.ai/gliglish-learn-languages-effortlessly-by-speaking-with-an-ai-teacher/) | Conversación con «profesor» de IA. | Solo encontré páginas comerciales, ninguna evidencia. | Propietario. |
| 6 | [Ensayo aleatorio de Nigeria (Banco Mundial)](https://reproducibility.worldbank.org/catalog/419) | Seis semanas de tutoría con Copilot (GPT-4) guiada por profesores. | Efecto de 0,31 DE en la evaluación global y 0,23 DE en inglés. [Resumen secundario](https://research.askpoppy.ai/papers/de-simone-2025-chalkboards-to-chatbots-nigeria/): el control no tenía programa alterno y solo ~57 % presentó la prueba final. | Paquete de reproducibilidad abierto. Sirve de modelo de protocolo, no de código. |
| 7 | [ChatFriend, CHI'26 (Delhi)](https://arxiv.org/abs/2601.19304) | Chatbot de voz con Whisper-1, GPT-4o-mini y TTS de Google. Estudio de campo de 6 días con 23 estudiantes en 4 escuelas pobres. | Cualitativa: más confianza para hablar. Hubo latencia o fallos de red en casi la mitad de las sesiones, problemas con el botón de hablar y TTS poco inteligible para no nativos. Los estudiantes querían conversación libre y los directivos querían evaluación alineada al currículo. | CC BY 4.0. Es una lista de lecciones aprendidas muy reutilizable. |
| 8 | [LLMersion-1](https://github.com/QM378/LLMersion) y [su artículo](https://arxiv.org/abs/2609.29672) | Offline en un portátil de ~200 USD. Hablar con pulsador, subtítulos sincronizados, tarjeta de gramática y feedback de pronunciación en paralelo. | Es una propuesta; no vi evaluación con personas. Cita tasas de 5–15 tok/s para un 3B en CPU de gama de entrada. Eso es un N100, mucho más moderno que su N2840. | MIT. Es la mejor referencia de código; se puede reutilizar. |
| 9 | [TACT (HKUST)](https://arxiv.org/abs/2608.03952) | Taxonomía de 13 estrategias de tutor y modelo Qwen3.5-4B entrenado con ellas. | Mejora de 20,3 puntos sobre su base. Estudio ciego con 50 aprendices. El corpus de partida (TSCC) es B1–C2, no A1–A2. | Dicen que liberan datos y pesos. [DUDOSO: no vi la licencia.] La taxonomía sí se puede copiar. |
| 10 | [Control de gramática en diálogo (NAACL 2025)](https://aclanthology.org/2025.naacl-long.495.pdf) | Control de la gramática CEFR (EGP) de la respuesta del chatbot, con ajuste fino y reordenamiento. | Admiten que sus estrategias no garantizan cumplir todo el control. (Solo vi fragmentos.) | [DUDOSO: licencia no verificada.] La idea de reordenar y filtrar por nivel se puede copiar. |
| 11 | [BetterSpeak + Gemma 4 E2B](https://deepmind.google/models/gemma/gemmaverse/betterspeak/) | Tutor de voz en el dispositivo, con guía en la lengua nativa y «estados de lección consistentes». | Caso de Google, sin datos de aprendizaje. | Propietario. Confirma la dirección, pero un 2B no corre en su Celeron. |
| 12 | [LinguaPal](https://dev.to/suraj_srivastav/linguapal-a-tiny-offline-language-tutor-i-built-for-one-friend-2p69) | Tutor local para una persona que teme equivocarse. Usa Gemma 3n E2B (2,79 GB) con FastAPI. | Ninguna. | MIT. Se puede mirar el diseño; el modelo es demasiado pesado. |
| 13 | [offline-tutor](https://github.com/kalashbaisoya/offline-tutor) | Asistente local por voz, con respuestas habladas oración por oración con Kokoro. | Su hallazgo: el modelo chico alucina y sirve como asistente, no como tutor confiable. Es en ingeniería, no inglés. | [DUDOSO: licencia no vista.] Respalda su diseño de «verificado por debajo». |
| 14 | [Ivy AI (ESP32)](https://www.electronicsforu.com/news/this-esp32-board-runs-an-offline-ai-tutor-for-kids) | Tutor de voz offline en un microcontrolador, con un modelo de ~19,7M de parámetros. | Ninguna. | Código abierto. Muestra el piso del hardware, no un tutor de idiomas. |

Dos notas sobre los datos:
- **Meta-análisis de chatbots en EFL:** existen, por ejemplo [este](https://www.researchgate.net/publication/380298384_Unraveling_Effects_of_AI_Chatbots_on_EFL_Learners'_Language_Skill_Development_A_Meta-analysis). No abrí ninguno, así que [DUDOSO] los tamaños de efecto.
- **Lo que funcionó y lo que no:** los efectos medidos vienen de modelos grandes en la nube con estructura humana alrededor (Nigeria con profesor guiando; Duolingo con tarea fija). Lo que falló en campo fue la infraestructura: red, botones y voz poco clara. En un modelo pequeño, lo que falló fue la fiabilidad, como alucinar (offline-tutor).

---

## 2. Pedagogía que lo hace tutor y no corrector

- **Tareas (TBLT).** El [meta-análisis de Bryfonski y McKay](https://www.semanticscholar.org/paper/TBLT-implementation-and-evaluation:-A-meta-analysis-Bryfonski-McKay/da6bfdd9d04dad73b25a513a8a5c9249f0825c13) (52 estudios) reporta d = 0,93. Un [comentario técnico](https://journals.sagepub.com/doi/abs/10.1177/13621688221131127) cuestiona su metodología, así que úsenlo como respaldo moderado. Estructura: antes de la tarea (vocabulario), tarea con meta verificable y después de la tarea (resumen).
- **Cuánto corregir.**
  - [Lyster y Saito 2010](https://www.researchgate.net/publication/234580927_Oral_Feedback_in_Classroom_SLA_A_Meta-Analysis): 15 estudios de aula, 827 participantes. Las pistas que obligan a reformular (prompts) dan d = 0,83 y los recasts d = 0,53; el efecto global es d ≈ 0,74 ([resumen](https://wiki.learningdesignalliance.org/claims/corrective-feedback-effect-on-l2-development-is-significant-and-durable/)).
  - [Li 2010](https://www.academia.edu/2911659/Li_S_2010_The_effectiveness_of_corrective_feedback_in_SLA_A_meta_analysis_Language_Learning_60_309_365): d ≈ 0,61. El feedback implícito se sostiene mejor con el tiempo y los tratamientos más cortos rinden más.
  - La misma página resumen dice que los de bajo nivel se benefician más de las pistas que de los recasts. [DUDOSO: no lo verifiqué en la fuente.]
  - Ambos son estudios de aula humana, no de IA.
- **Output de Swain y andamiaje.** No lo verifiqué en esta sesión; es conocimiento previo [DUDOSO como cita]. El principio: hacer producir al aprendiz, no explicarle.
- **Memoria y compromiso.** El único dato son los +24 % de retención de Praktika (del proveedor). En Delhi, el engagement era frágil en estudiantes nerviosos, y la confianza en Duolingo quedó neutral. Hay que diseñar el progreso de forma explícita.

---

## 3. Propuesta: «Tutor de práctica» para su hardware

**Idea central:** el LLM de 0,5B no conduce la conversación. La conduce una máquina de estados escrita por el profe, y el LLM solo pone una reacción corta de 1–2 frases. El corrector verificado (fichas + ERG) corre en segundo plano y decide cuándo hablar. Esto parte de que los ejemplos en el prompt no ayudan al 0,5B y de que [TACT](https://arxiv.org/abs/2608.03952) necesitó 4B para elegir la estrategia pedagógica; aquí esa decisión la toma el código.

**Escenarios iniciales (5, de 8–10 min):**
1. Tienda de la vereda: el aprendiz es el tendero.
2. Finca o agroturismo: el aprendiz es el anfitrión.
3. Turismo: indicaciones y recomendaciones.
4. Entrevista de trabajo (A2).
5. Taller: herramientas y problemas.

En casi todos el aprendiz hace el papel real que conoce, así que produce más. Cada escenario define esto:

```yaml
scenario: tienda
role_tutor: cliente
goal: "vender 2 kg de tomate y dar el vuelto"
pretask_words: [kilo, price, change, "how much"]
beats:
  - tutor: ["Hi! Do you have tomatoes?"]
    expect: {slot: product, pattern: "(yes|have).*"}
    ladder: [open, choice, frame, model_repeat, es_hint]
    target: [there_is/are, how_much]
    twist: "no hay tomate → ofrece alternativa"
fatal_errors: [meaning_blocking]   # solo estos interrumpen
```

**Flujo de un turno (los tiempos son objetivos, no mediciones):**
1. El aprendiz suelta el pulsador. Se reproduce un «Mm-hm» pregrabado para tapar la latencia.
2. ASR con whisper.cpp tiny o Vosk [DUDOSO: no pude verificar el rendimiento en un N2840; midan el día 1].
3. En paralelo, y fuera de la ruta crítica, corren las fichas y la ERG con ACE. El resultado va a una cola.
4. El gestor de diálogo (código) cruza los datos del aprendiz con el beat: ¿respondió?, ¿qué nivel de ayuda toca?, ¿se corrige ahora, después o nunca?
5. La pregunta del siguiente beat sale de audio pregrabado (cero cómputo). El LLM genera solo una reacción de ≤ 14 palabras con máximo ~30 tokens y control por gramática GBNF [de memoria, no verificado].
6. Se valida la reacción: vocabulario A1–A2, una sola pregunta y, **idea nuestra**, que la propia ERG la analice. Si falla, se usa una plantilla.
7. Si la reacción no está lista en ~1,5 s, se omite. Nunca se hace esperar al aprendiz por adornos.

**Cuándo corrige** (la regla se apoya en que la detección tiene 1/30 falsas alarmas, así que un fallo sin aviso es mejor que una alarma falsa):
- **En el momento (máx. 1 cada ~4 turnos):** solo si la ERG o una ficha dispara con alta confianza y el error bloquea la tarea o es el objetivo del escenario. Se hace recast dentro de la respuesta («Two kilos of tomatoes, OK!») más una petición de repetir («Can you say: *two kilos*?»). Eso mezcla lo implícito con una pista de producción.
- **Después, en el resumen:** máx. 3 ítems, cada uno con la frase del aprendiz, la versión correcta, la regla de la ficha en español y «dilo otra vez».
- **Nunca:** lo que el detector no sabe bien. En falsos cognados, make/do, orden de adjetivos y preposiciones usen listas por escenario, porque un diálogo cerrado reduce el espacio de errores y permite reglas específicas.
- **Frustración y aburrimiento:** la escalera de ayuda baja de pregunta abierta a opciones, luego a marco de frase, luego a modelo para repetir y por último a pista en español. Tras 2 beats fallidos seguidos se baja la dificultad y se termina siempre en logro. Si responde con ≤ 3 palabras tres veces, se pasa a una pregunta personal. Si acierta rápido, se sube con una complicación («no hay tomate»).

**Qué recuerda (SQLite local, el aprendiz puede borrarlo):**
- Hechos personales dichos («tengo finca de café»), extraídos por plantillas, no por el LLM, para no cargar el contexto del 0,5B.
- Conteo de errores por categoría (ids de fichas y mal-reglas), palabras usadas y minutos hablados.
- Uso: retoma lo dicho («¿Cómo va la cosecha?»), mete al siguiente escenario un beat sobre sus dos debilidades principales y celebra con datos reales («hoy pediste el precio sin ayuda»). La métrica principal que se muestra y premia: **palabras habladas**.

**Voz:**
- **Salida:** pregrabar todas las líneas fijas con TTS en un PC (Kokoro es [Apache-2.0](https://arxiv.org/abs/2609.29672); Piper tiene voces con licencias distintas [DUDOSO: sé de memoria que cambió a GPL, no lo verifiqué]). Solo las reacciones del LLM usan TTS en vivo, por frase, o aparecen solo como texto si no hay tiempo.
- **Entrada:** pulsar para hablar (como [LLMersion](https://arxiv.org/abs/2609.29672), por robustez con micrófonos baratos) y mostrar siempre la transcripción en pantalla, como en [Delhi](https://arxiv.org/abs/2601.19304). Un ASR general puede «arreglar» la gramática del aprendiz y ocultar el error. [DUDOSO: es mi hipótesis; encaja con su 40,4 % de whisper frente a 59,6 % de ZIPA+GOP]. Por eso la corrección gramatical por voz se deja para el resumen, o se ofrece también un canal escrito.
- **Memoria de la CPU:** ASR + LLM + ACE + TTS no caben en paralelo en 2 núcleos. Hay que serializarlos y medir.

---

## 4. Plan de 10 días (el modelo supuso que hoy era 31 oct; en realidad es 5 nov; el piloto es 9–18 nov)

| Día | Qué |
|---|---|
| 1 (31 oct) | Congelar el alcance a **3 escenarios** (tienda, finca, taller). Medir en el Chromebook ASR tiny/Vosk, TTS y la ruta crítica completa. |
| 2 | Máquina de estados mínima (un YAML y un gestor de turnos ≈ 200 líneas) con el escenario «tienda». |
| 3 | Pregenerar el audio de las líneas fijas. Integrar la reacción acotada del LLM con filtros (longitud, vocabulario, ERG) y la plantilla de respaldo. |
| 4 | Integrar la cola de correcciones fichas/ERG y la política «cuándo corrige». Pantalla de resumen con 3 ítems. |
| 5 | Escenarios 2 y 3. Listas de errores típicos por escenario; el bucle nocturno puede generar errores sintéticos por escenario. |
| 6 | Memoria SQLite, retomar hechos y pantalla de progreso. Registros de uso. |
| 7 | Ensayo con 3–5 personas (colegas del SENA): latencias, falsas correcciones, ajustes. |
| 8 | Instrumentos: rúbrica de habla, encuesta en español, consentimiento. Imagen del sistema, copia y reinicio. |
| 9 (8 nov) | Congelar versión. Prueba de punta a punta en 2 equipos. Plan B: modo solo texto. |
| 10 (9 nov) | Arranca el piloto: pre-prueba y primera sesión. |

**Piloto mínimo con evidencia creíble (no prueba eficacia):**
- **Muestra y diseño:** unos 24 adultos (mi cálculo: con n=24 pareados se detecta un efecto mediano-grande, d≈0,6, con 80 % de potencia), con pre y post sobre un mismo role-play de 3 minutos.
- **Evaluación ciega:** dos instructores que no saben si la grabación es pre o post, con una rúbrica de cumplimiento de la tarea, palabras por minuto, errores por 100 palabras e inteligibilidad.
- **Prueba de su tesis:** cada aprendiz hace 2 sesiones en modo tutor y 2 en modo corrector (mismo motor, sin conversación), con el orden contrabalanceado. Se compara palabras habladas, rondas voluntarias extra y sensación de ser «corregido vs acompañado».
- **Registros:** latencias p50/p95, falsas correcciones (revisión humana de una muestra), uso de ayuda y abandonos.
- **Para los tres financiadores:** repositorio reproducible, video offline en el Chromebook, costo por aprendiz, resultados negativos y que todo corre local. [DUDOSO: no pude verificar los criterios de Mozilla Human-Scale AI, SENA CATA ni Anthropic Fellows; revisen las convocatorias.]

---

## Las 5 cosas que copiaría mañana

1. **Línea fija pregrabada + reacción corta del LLM con respaldo** (lo que hace [BetterSpeak](https://deepmind.google/models/gemma/gemmaverse/betterspeak/) con estados de lección, a su escala). Es lo que hace viable el tutor con un 0,5B.
2. **La arquitectura de turno de [LLMersion-1](https://github.com/QM378/LLMersion)** (MIT): pulsador para hablar, tarea paralela y transcripción visible. Lean su código antes de escribir el propio.
3. **Los 13 movimientos de tutor de [TACT](https://arxiv.org/abs/2608.03952)** como menú de acciones que el gestor elige por reglas, no el modelo.
4. **El diseño de Duolingo con Lily:** la conversación sin interrupciones, con la retroalimentación después ([informe](https://duolingo-papers.s3.amazonaws.com/reports/Duolingo_whitepaper_language_video_call_improves_speaking_2025.pdf)), y la métrica de palabras habladas.
5. **Las recomendaciones de [Delhi](https://arxiv.org/abs/2601.19304):** interacción de un toque, TTS inteligible para no nativos, ayuda en la lengua materna y analíticas útiles para el instructor.

**Pendientes sin verificar:** rendimiento de ASR/TTS en el N2840, licencias de Piper, Moonshine, Vosk y de los corpus abiertos (DailyDialog, Tatoeba, TSCC), y la evidencia de Speak, Gliglish y Talkpal. Conviene revisarlos antes de comprometerse con cualquiera.

---
Generado por claude-sonnet-5-5 (el pie decía opus por un error del script) con búsqueda web en el servidor, 2026-11-05 19:40. Gasto: 6.20 USD. Citas sin verificar por el coordinador.
