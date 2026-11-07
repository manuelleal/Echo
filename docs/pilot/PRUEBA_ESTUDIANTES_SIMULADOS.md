# Prueba de estudiantes simulados: Echo en el Chromebook (7-nov-2026)

Servidor: la vista previa del Chromebook (puerto 8081). Sesiones `SIMUL-ANA`, `SIMUL-LUIS`, `SIMUL-VALE`, `SIMUL-EDGE`. Una petición a la vez. Sin navegador: se juzga el texto y los tiempos, no la voz ni la cara. Transcripciones crudas en el scratchpad (`ana1.txt`, `ana2.txt`, `ana3.txt`, `luis1.txt`, `luis2.txt`, `vale1.txt` a `vale4.txt`, `edge.txt`).

**Veredicto de una línea: SÍ CON ARREGLOS.** Es rápido y la FAQ es honesta, pero hay tres fallos que un aprendiz real notaría el primer día (avance falso, felicitación falsa, tutor que dice que necesita internet).

## Veredicto

**SÍ CON ARREGLOS.** Imprescindibles antes del 9-nov:

1. Que "no sé / no entiendo / ayuda / ok bye" no avancen el paso ni reciban "OK, I understand" (B1, B2).
2. Quitar o arreglar el "logro" que felicita por una regla que el aprendiz acaba de fallar o ni usó (B3).
3. Quitar del guion LLM las afirmaciones sobre sí mismo ("I need internet", "I am a computer program that makes animations", "I love anime"). Contradicen la FAQ, que sí es honesta (B4).
4. En modo corrector, no reescribir el significado: "he work in a farm" quedó como "my sister works on a farm" (B5).

## Mediana y rango de tiempos

57 turnos de `/api/practica`, medidos con el campo `segundos`.

| Medida | Valor |
|---|---|
| Mediana (todos) | 3,4 s |
| Mediana (turnos con LLM, más de 1 s; n=46) | 3,8 s |
| Rango | 0,2 s a 10,4 s |
| Percentil 90 | 8,5 s |
| Turnos de 0,2 a 0,3 s | camino de plantilla: pista fija, "hello" inicial, despedida |
| Primer turno de cada escenario | 9 a 10 s casi siempre (carga en frío del modelo) |
| `/api/turno` (modo corrector) | 4,6 a 17,6 s (mediana cerca de 6,5 s) |
| `/api/pregunta`, `/api/estudio/*`, `/api/actividad`, páginas | menos de 0,4 s |

Lectura: 3 a 5 s por turno es tolerable. Los 9 a 10 s del primer turno, sin indicador de espera, hacen que el aprendiz piense que se colgó. El modo corrector (12 a 17 s en frases con 2 errores) se siente lento.

## Opinión de cada "estudiante"

### Ana, 19 años, ADSO, A2

"Me gustó la Entrevista: las preguntas siguen el orden de una entrevista de verdad y la ayuda en español con el ejemplo me salvó una vez. Cuando escribí *I have 19 years* me dijo *I am 19 years old* y me dio la regla, y eso sí lo voy a recordar. Pero me molestó que me corrigiera solo algunos errores. Escribí *yesterday I go... I make the homework* y solo me marcó *go*; *he work* y *for buy* no me los dijo en el momento, solo al final en el resumen. En Soporte técnico me felicitó ('¡Qué berraquera!, usaste bien la -s') justo después de que yo había escrito *It take* mal y en una frase donde no había ningún verbo con -s. Ahí dejé de creerle los elogios. Al final me corrigió *he work good now* a *he worked good now* y eso está peor que lo mío. En Estudiar, *She is 13* me la dio por mala, y *in order to wash* también, aunque están bien. Aun así, rápido y sin internet: lo usaría."

### Don Luis, 45 años, finquero, A1

"Yo contesto con una palabra y a veces en español. A veces me ayuda bien: me pone el ejemplo y me lo repite en español. Pero lo raro: en la Finca me preguntó qué tiene el cuarto, le puse *breakfast* y me repitió el ejemplo, y luego le puse *yes tomorrow*, que no tiene nada que ver, y me dejó pasar. Le dije *no se* y *no entiendo* y me contestó 'OK, I understand what you mean' y me pasó de pregunta, como si hubiera dicho algo bien. Escribí *ayuda* y no lo tomó como pedir ayuda, me soltó la misma frase de ejemplo (la que ya sabía). En la Tienda dije *change 500 pesos* y me contestó 'fifty hundred pesos', no se entiende. Al terminar, el resumen me salió vacío: 21 turnos, 39 palabras y ni una felicitación. Yo me esforcé y nadie me dijo 'muy bien'. Si fuera con un instructor al lado, bien; solo, me desanimo."

### Valentina, 17 años, Animación Digital, curiosa

"Me divertí probando. Le pregunté *Do you like anime?* y me contestó que ama el anime y las películas de robots, y luego le pregunté si era un robot y dijo que era un programa que hace animaciones, y eso es mentira, no hace nada de eso. Luego le pregunté si necesita internet y me dijo 'Yes, I need an internet connection to watch the show'. Pero en la sección Pregúntale al tutor dice que NO necesita internet. Se contradice, y justo en lo que el profe nos presumió. Lo bueno: cuando me salgo del tema, vuelve a la pregunta ('So, what did you learn?'), no se pierde. Lo malo: le dije *Hi! I am Valentina* y respondió 'Valentina is an interesting idea'. Y con *Do you like anime?* en Pregúntale al tutor solo dice que no entiende y me sugiere otras. Con el Profe armé una actividad en 0,3 s y quedó bien, aunque mi instructor querría escoger el escenario de García Rovira y no deja."

## Tabla de hallazgos priorizados

Escala: **Bloqueante** = hay que arreglar antes del 9-nov. **Molesto** = lo notarán, arreglar si hay tiempo. **Detalle** = pulir.

| # | Gravedad | Hallazgo | Ejemplo exacto (lo que escribí, lo que respondió) | Dónde | Sugerencia |
|---|---|---|---|---|---|
| B1 | Bloqueante | Respuestas sin contenido avanzan el paso y reciben reacción de aprobación. Paso a veces avanza con cualquier cosa y otras veces se queda con una respuesta relevante (inconsistente). | Finca p3 ("What does the room have?"): `breakfast` -> repite ejemplo; `yes tomorrow` -> "Great, I can come back tomorrow." y avanza. Tienda p2: `tomatoes yes` avanza. gr4 p2 ("for you or a friend?"): `how much` avanza con "I can help with the price"; `red` -> ayuda. | finca p3, tienda p2, gr4 p2 | Compuerta de avance: exigir verbo/estructura mínima del paso o al menos relación con el tema. Si no, repetir el paso con la pista. No avanzar por una pregunta del aprendiz. |
| B2 | Bloqueante | "No sé", "no entiendo" y "ayuda" no se reconocen como petición de ayuda. Reciben "OK, I understand", incluso avanzan. | Finca p1: `no se` -> "OK, I understand you don't have it." / "Nice! Tell me about one animal." (avanza). Tienda p4: `no entiendo` -> "OK, I understand what you mean." y avanza. Finca p3: `ayuda` -> solo repite el ejemplo. | finca p1, tienda p4, finca p3 | Detectar por lista (no sé, no entiendo, ayuda, help, how do I say) y responder con la ayuda en español y el ejemplo sin avanzar. Es el perfil de Don Luis; ocurrirá cada clase. |
| B3 | Bloqueante | "Logro" (felicitación) falso: celebra una regla que el aprendiz acaba de fallar o no usó en esa frase. | Taller p5: tras `It take two hours` (error), escribí `The price is 50 thousand pesos` -> "¡Qué berraquera! ... Esta vez usaste bien: Con he/she/it el verbo en presente lleva -s". Animación p5: `Next year I want to make a video game` -> "usaste bien: Para expresar propósito se usa 'to' + verbo" (es 'want to', no propósito). | taller p5, animación p5 | Dar el logro solo si la frase del turno contiene la construcción correcta verificada por el detector. Si no, no celebrar. |
| B4 | Bloqueante | El tutor, en la conversación, afirma cosas falsas sobre sí mismo y contradice la FAQ. | Animación: `do you need internet?` -> "Yes, I need an internet connection to watch the show." `are you a robot?` -> "Yes, I am a computer program that makes animations." `Do you like anime?` -> "Yes, I love anime and movies about robots and space." (la FAQ dice: "Corro sin internet"). | animación p2, p5 | Preguntas sobre el tutor (internet, qué eres, gustos) en un escenario: responder con una línea fija honesta en inglés simple ("I do not need internet. I am a program.") y volver a la pregunta del paso. |
| B5 | Bloqueante | Modo corrector cambia el significado de lo que dijo el aprendiz (corrección falsa). | `/api/turno`: `I have 19 years and he work in a farm` -> `frase_corregida`: "I am 19 years old and my sister works on a farm." (inventó "my sister"; "he" -> "my sister"). | `/api/turno` | Prohibir en el prompt cambiar sujetos y palabras de contenido; solo morfología. Validar que `frase_corregida` conserve los tokens de contenido. |
| M1 | Molesto | Corrección falsa en el resumen final: "mejor" también está mal. | Taller final: `I install the program yesterday and he work good now` -> `mejor`: "I installed the program yesterday and he worked good now" (presente "now" con pasado; "he" por el portátil; "good" por "well"). Animación: `people is happy when see it` -> `mejor`: "people are happy when see it" (queda mal: falta "they"). | resumen de taller y animación | Mostrar solo la parte verificada (`I install` -> `I installed`) y no reescribir la frase completa. Si no puede arreglarse todo, mejor mostrar solo el error marcado. |
| M2 | Molesto | Correcciones faltantes en el turno (se dicen solo al final o nunca). | Entrevista p4: `yesterday I go ... I make the homework`: `errores` solo marcó `I go` (y `I make` en marcas, sin corregir). `He work with me in the team last year`, `for buy` no se corrigieron en el turno. `She dont like coffee` (turno): `errores: []`. Animación `I dont have a good computer`: nada. | entrevista p4-p6, turno, animación p4 | Subir cobertura de `he work`, `dont`, `for + verbo`; corregir máximo un error por turno pero en el turno en que ocurre, no solo al resumen. |
| M3 | Molesto | La reacción no tiene sentido o parece de otro contexto. | Animación p0: `Hi! I am Valentina` -> "Valentina is an interesting idea." Tienda p8: `change 500 pesos` -> "fifty hundred pesos is fine for me." Entrevista p2: dije dónde estudio y preguntó "What do you study at SENA?". Mercado: `no hablo ingles...` -> "Meow, I speak Spanish..." | varios | Filtro de reacciones (palabras raras como "Meow"), reacciones genéricas más seguras para frases cortas o saludos. En entrevista, no preguntar lo que ya dijo (usar slots). |
| M4 | Molesto | Falsos negativos en Estudiar: respuestas correctas rechazadas, y la pista no aplica. | edad_have: `She is 13.` -> "Casi. Revisa la frase completa" con la pista "¿Qué verbo usas?" (ya usó "is"). para_infinitivo: `I go to the river in order to wash the clothes.` rechazada. | /estudiar | Aceptar variantes con el mismo cambio de regla (sin "years old", "in order to"). Cuando el verbo ya está bien, la pista debe decir otra cosa ("falta 'years old'"). |
| M5 | Molesto | Resumen final vacío para el aprendiz que más lo necesita, y contradictorio en otros. | Luis (tienda): `{"turnos":21,"palabras":39,"a_practicar":[],"logros":[],"dilo_otra_vez":[]}`. Animación: la misma regla (for/to) sale en `a_practicar` y en `logros`. Taller: el resumen arrastra cosas de la Entrevista (misma sesión, 16 turnos). | `resumen` | Si no hay errores ni logros, dar un cierre positivo con lo que sí dijo ("Hoy dijiste: ... "). Resumen por escenario, no por sesión; no repetir la misma regla en ambas listas. |
| M6 | Molesto | `fin` sin cierre del tutor: último turno sin respuesta ni correcciones. | Taller p6 (7 pasos): `fin: true` sin `tutor` ni `errores`; Entrevista p7: reacción "I see." a "Thank you very much". Animación p7 `bye`: sin respuesta. | último paso | Mensaje final fijo en inglés y la `meta_final_es` del escenario. Hoy no aparece en la respuesta de práctica. |
| M7 | Molesto | Rol invertido en Soporte técnico: el cliente hace la pregunta de diagnóstico. | Taller p1: yo (técnico) pregunté `What is the problem with your laptop` -> "It is five years old. Why is it so slow?" | taller p1-p2 | Revisar guion: que la clienta responda con síntomas y el técnico explique. |
| M8 | Molesto | Primer turno de 9 a 10 s sin indicador. | Entrevista p0 10,4 s, taller p0 9,6 s, animación p0 8,9 s, gr4 p1 9,1 s. | primer turno | Precalentar el modelo al abrir el escenario (turno ficticio) o mostrar "pensando...". |
| M9 | Molesto | García Rovira no está disponible para el Profe, y la FAQ no entiende preguntas en inglés. | `/api/actividad` con `modulo: "e:gr3"` -> 400 "Elige al menos una regla o un módulo/escenario". `/api/pregunta` con `Do you like anime?` y `what are you` -> "No estoy seguro de entender tu pregunta". | Profe, FAQ | Aceptar escenarios `gr*` en el Profe (o decir por qué no), y mapear preguntas básicas en inglés a la FAQ. |
| D1 | Detalle | El recast termina con una pregunta sin signos: "Can you say it like that?" pegada a la frase sin punto. | `Oh, it takes two hours Can you say it like that?` | recast | Añadir punto/coma o poner "Dilo así:" antes. |
| D2 | Detalle | Hace falta repetir la frase dos veces: la pista es la misma ya dicha en `ayuda_es`. | Finca p1: `si` -> ejemplo; `farm` -> "Let me help you. You can say: ..." (igual al ejemplo de `ayuda_es`). | pista del paso | Variar: al segundo intento, dar una versión incompleta para completar ("We have ___ and ___"). |
| D3 | Detalle | Entradas inválidas: texto vacío da HTTP 400 sin mensaje amable. | `texto: ""` -> HTTP 400. | /api/practica | Mostrar "Escribe algo" en la interfaz (verificar en el cliente). |
| D4 | Detalle | `/api/turno` devuelve siempre la misma pregunta de seguimiento. | 4 de 5 frases -> "What tools do you use at work?" | modo corrector | Variar o relacionar con la frase. |
| D5 | Detalle | Etiqueta del error del modelo no verificado es errónea. | `actually` -> `and` marcado como `negacion`; `have` -> `am` marcado como `articulo`. Falso amigo no explicado. | `/api/turno` | No mostrar `tipo` cuando `verificada=false`; para `actually`, usar la ficha de falsos cognados. |
| D6 | Detalle | Actividad del Profe: huecos ambiguos. | "My father ________ the car." (clave: washes), "I'm 30 ________ old." | Profe | Dar el infinitivo entre paréntesis en cada hueco. |

## Correcciones falsas o equivocadas encontradas (lo más grave)

| # | Dónde | Lo que escribí | Lo que corrigió Echo | Por qué es falso |
|---|---|---|---|---|
| F1 | `/api/turno` | `I have 19 years and he work in a farm` | `I am 19 years old and my sister works on a farm.` | Cambió "he" por "my sister" y "in" por "on": inventa información. |
| F2 | Resumen del taller | `I install the program yesterday and he work good now` | `I installed the program yesterday and he worked good now` | "now" pide presente; "he worked" es incorrecto, debería ser "it works well now". |
| F3 | Resumen de animación | `people is happy when see it` | `people are happy when see it` | Sigue mal: "when they see it". Presentado como "mejor". |
| F4 | Taller p5 (logro) | `The price is 50 thousand pesos` | "Esta vez usaste bien: Con he/she/it el verbo en presente lleva -s" | Elogio falso: no hay verbo con -s en la frase; viene tras un error. |
| F5 | Animación p5 (logro) | `Next year I want to make a video game` | "usaste bien: ... 'to' + verbo (propósito)" | "want to make" no es propósito. Elogio sin base. |
| F6 | Estudiar (rechazo) | `She is 13.` (en la ficha edad_have) | "Casi. Revisa la frase completa" | La frase es correcta en inglés. Rechazar una respuesta correcta frustra al aprendiz. |
| F7 | Estudiar (rechazo) | `I go to the river in order to wash the clothes.` | "Casi..." | Correcta. |
| F8 | Reacción (finca p1) | `no se` | "OK, I understand you don't have it." | Interpreta "no sé" como "no tengo". Tomó una duda como respuesta. |
| F9 | Tienda p4 | `no entiendo` | "OK, I understand what you mean." | Contrario a lo que dijo el aprendiz. |
| F10 | `/api/turno` (modelo) | `I am agree with you, actually I have 20 years` | `I am` -> `I`, `actually` -> `and` (sin verificar) | La primera es válida pero el motivo no se explica; la segunda borra una palabra sin explicar el falso amigo. |

Sin falsos positivos con las reglas de ficha (edad, -s, pasado, a/an, for/to, people): todas las correcciones `verificada: true` de práctica fueron correctas. El riesgo está en el modelo generador (`fuente: "modelo"`, resumen, reacciones, logros).

## Qué funcionó bien

- Camino de plantilla muy rápido (0,2 s) y estable. Páginas `/estudiar`, `/profe`, `/practica` abren en menos de 0,2 s.
- `ayuda_es` en cada paso, con ejemplo: Don Luis pudo seguir sin saber qué decir.
- Correcciones por ficha, con regla y pista en español, correctas (edad, -s, pasado, a/an, for/to).
- Si el aprendiz se sale del tema (Valentina), el tutor vuelve a la pregunta ("So, what did you learn?").
- FAQ `/api/pregunta` honesta y breve: qué es, sin internet, quién lo hizo, datos anónimos.
- Profe: actividades A/B con clave de respuestas, correctas, en 0,3 s. Validación de cantidad y nivel sin error.
- Estudiar: reintento con pista, luego revela con la regla (flujo pedagógico sano).

## Notas de método y límites

- Sin voz ni cara: no se evaluó audio, ni lectura en pantalla, ni la interfaz de móvil. El juicio de lo que "siente" cada perfil es una simulación a partir del texto.
- La sesión `SIMUL-ANA` se reutilizó entre Entrevista, Taller y Estudiar; ahí salió que el resumen es por sesión (M5).
- Una conversación por escenario y perfil (14 escenarios, 8 ejercitados); no se midió la variación entre repeticiones. Las reacciones del LLM no son deterministas: los ejemplos exactos pueden no repetirse idénticos.
- No se editó código. No se usaron sesiones sin prefijo `SIMUL-`.
