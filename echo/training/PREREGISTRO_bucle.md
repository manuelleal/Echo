# Bucle nocturno «la API entrena al modelo» (4-nov-2026, antes de correr)

**Qué es:** un ciclo automático que pidió Christiam.
1. Claude Opus 5.5 genera pares (frase con error → corrección mínima, con su tipo) y frases correctas para 14 tipos de error del hispanohablante.
2. Un filtro descarta lo malo:
   - la corrección y las correctas tienen que analizarse con la ERG sin reglas de error gramatical;
   - como máximo 3 palabras cambiadas;
   - sin duplicados;
   - Jaccard < 0,6 contra los bancos v1, v2, v3 y real. El filtro sólo calcula el puntaje y nunca imprime frases.
3. Con lo que queda se entrena un **etiquetador de errores chico**: regresión logística sobre rasgos de cada palabra. Corre en CPU, pesa kilobytes y cabe en el Chromebook.
4. Se evalúa sólo en desarrollo: 15 % de los datos generados, separado por vuelta; los pares y el inglés correcto de la biblioteca; las sondas propias.
5. Se repite.

**Topes:** 15 USD esta noche (`gasto.jsonl`); se detiene al 95 % del tope. Ninguna medición en bancos ciegos: eso se preregistra aparte, cuando el etiquetador entre como votante en la cadena.

**Qué se espera ver (puede fallar):** con más datos, el etiquetador sube su detección en desarrollo, frase con error marcada, y mantiene las falsas alarmas en las correctas de la biblioteca en ≤ 5 %. Si después de unos 5000 pares no pasa del 60 % en desarrollo con ≤ 5 % de falsas, el etiquetador lineal no sirve y hace falta otra arquitectura, como el etiquetador de 2–10 M de la nota Fable.

**Riesgo conocido:** los errores que genera Claude pueden no parecerse a los reales. Eso lo dirá el banco real, más adelante y con preregistro.
