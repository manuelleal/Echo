# Versión congelada para el piloto (9–18 nov 2026)

Escrito el 7 de noviembre de 2026, antes de la primera sesión con aprendices.

| Qué | Valor |
|---|---|
| Preregistro | `PREREGISTRO_piloto.md`, publicado aquí el 6-nov-2026 (commit `6cdbc34`). SHA-256: `1974599e7b0ee0963689544b94776b693f2ecc7265e32e7d924164613d0395c6` |
| Versión del tutor | etiqueta `piloto-v1` del repositorio de trabajo (commit `8452ab8`, 7-nov-2026) |
| Modelo | echo-tutor-0.5B (Qwen2.5-0.5B con LoRA propio, Q4_0) |
| Modo | práctica por situaciones; sin enlaces a Profe/Estudiar durante el piloto |
| Registro | CSV anónimo vacío al empezar (0 filas); las pruebas previas quedaron archivadas aparte |

Antes de congelar se hizo una prueba con estudiantes simulados (ver `PRUEBA_ESTUDIANTES_SIMULADOS.md`). Su veredicto fue "sí, con arreglos", y los cinco arreglos esenciales entraron en `piloto-v1`:

1. "no sé" / "ayuda" ya no avanzan.
2. Avanzar exige responder lo que se preguntó.
3. Se felicita sólo cuando se usa la forma corregida.
4. Respuesta honesta y fija sobre qué es el tutor.
5. El corrector no inventa sujetos.

Durante el piloto no se cambia el tutor. Cualquier cambio forzoso (por ejemplo, una caída) se declara como desviación en el reporte del 19-nov.
