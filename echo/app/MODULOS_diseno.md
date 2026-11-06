# Módulos de clase del tutor: diseño pedagógico

Archivo de contenido: `modulos.json` (8 módulos, 6 a 8 pasos cada uno). El motor no cambia; esto es solo contenido. Fuente de la lógica: `investigacion/TUTOR_CONVERSACIONAL_5nov.md`.

## Lógica pedagógica

1. **Antes, durante y después de la tarea.** La nota respalda el aprendizaje basado en tareas (meta-análisis de Bryfonski y McKay, d = 0,93, con la salvedad de que un comentario técnico cuestiona su metodología: "úsenlo como respaldo moderado") y propone esta estructura: "antes de la tarea (vocabulario), tarea con meta verificable y después de la tarea (resumen)". Por eso cada módulo trae `vocabulario` (6-8 palabras para el antes), `pasos` con una meta clara (el durante) y `meta_final_es` (el después, que cierra en logro).
2. **El aprendiz hace el papel que conoce.** La nota dice: "En casi todos el aprendiz hace el papel real que conoce, así que produce más." Por eso en la tienda y en la finca el aprendiz es el tendero y el anfitrión, en el taller es el técnico y en indicaciones es el vecino que guía. El tutor es quien pregunta, así que el aprendiz es quien habla.
3. **Escalera de ayuda.** La nota la define como "pregunta abierta, luego a opciones, luego a marco de frase, luego a modelo para repetir y por último a pista en español". En el JSON: la línea `tutor` es la pregunta abierta; `opciones` (2-3 respuestas cortas) son el escalón de opciones y de modelo para repetir; el comienzo de `ayuda_es` es el marco de frase y la pista en español; y el "Ej.:" final de `ayuda_es` es el modelo. El "Ej.:" siempre es la primera opción, así lo que el motor muestra y lo que acepta `espera` coinciden.
4. **Una regla por módulo, a propósito.** La nota dice que un diálogo cerrado "reduce el espacio de errores y permite reglas específicas", y que solo se corrige en el momento lo que "es el objetivo del escenario". Cada módulo hace aparecer una de las reglas del profe en un paso donde la respuesta natural la necesita (por ejemplo, "Sorry, I don't have lemons" en la tienda, o "I am 24 years old" en la entrevista).
5. **Terminar en logro.** La nota pide "se termina siempre en logro". Cada módulo cierra con una despedida fácil y con una `meta_final_es` que dice lo que el aprendiz hizo hoy.
6. **Tolerancia a errores en `espera`.** Cada expresión regular acepta palabras clave sueltas, no frases perfectas. La nota advierte que "un fallo sin aviso es mejor que una alarma falsa". Es mejor que el motor avance con una respuesta imperfecta y la corrección salga después, que bloquear a un aprendiz que respondió bien con errores.
7. **Una pregunta clara por turno.** Cada línea del tutor termina con una sola pregunta, inglés A1-A2, para que el modelo de 0,5 B no tenga que ser el que conduzca la conversación (la conduce el guion).
8. **Contexto local.** Pesos, la plaza de mercado de Málaga, Concepción, el páramo del Almorzadero, el SENA, mute y cabrito, arepa y chocolate en el desayuno. Es un lugar que el aprendiz conoce, así que no necesita inventar nada.

## Tabla de módulos

| # | id | Módulo | Qué hace el aprendiz | Regla objetivo | Pasos |
|---|---|---|---|---|---|
| 1 | `tienda` | En la tienda de la vereda (mejorado) | Es el tendero: atiende, dice precio, dice lo que no tiene, da el vuelto | `do_negacion` | 7 |
| 2 | `entrevista` | Entrevista de trabajo (mejorado) | Se presenta, dice su edad, estudios, habilidades y un proyecto pasado | `edad_have` | 8 |
| 3 | `proyecto` | Presenta tu proyecto (mejorado) | Explica para qué sirve, por qué y cómo lo hizo y qué sigue | `para_infinitivo` | 7 |
| 4 | `mercado` | En la plaza de mercado de Málaga (mejorado) | Compra papas, cebolla y moras, pregunta el total y paga | `articulo_a_an` | 7 |
| 5 | `finca` | Tu finca: eres el anfitrión (nuevo) | Recibe a una turista y le muestra animales, cuarto, comida y actividades | `concordancia_3sg` | 8 |
| 6 | `taller` | Soporte técnico de computadores (nuevo, ADSO) | Diagnostica un portátil lento, explica el arreglo, el tiempo y el precio | `sujeto_omitido` | 7 |
| 7 | `indicaciones` | Indicaciones a un turista en Málaga (nuevo) | Guía a la plaza, describe lugares, recomienda dónde comer y qué visitar | `orden_adjetivo` | 7 |
| 8 | `animacion` | Presenta tu animación o videojuego (nuevo, Animación Digital) | Cuenta qué hizo, cómo, cuánto tardó, qué fue difícil y qué aprendió | `pasado_irregular` | 8 |

Reglas sin módulo propio: `people_plural` y `falso_cognado` quedan para la corrección general; con 8 módulos no había un guion donde salieran de forma natural sin forzarlos. Pueden entrar en una segunda tanda (por ejemplo "people are" en una charla sobre la feria de San Jerónimo).

## Notas de uso

- `espera` está en minúsculas; el motor debe pasar la respuesta del aprendiz a minúsculas antes de buscarla con `re.search`. Se probó que cada expresión compila y acepta todas sus opciones y su "Ej.:".
- Los nombres propios del contexto local (Almorzadero, Concepción) están escritos con y sin tilde en las expresiones donde importa.
- Los datos de lugares y comidas salen de `garcia_rovira.json`; algunas expresiones de allí están marcadas [DUDOSO] y por eso no se usaron en estos módulos.
- Limitación: las `opciones` y el vocabulario son propuestas del diseñador y no pasaron por una revisión del instructor; Christiam debe leerlas antes del piloto.
