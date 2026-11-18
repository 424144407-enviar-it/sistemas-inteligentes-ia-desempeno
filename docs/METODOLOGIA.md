# Metodología y alcance

Las fuentes son dos encuestas: 24 respuestas sobre IA y 19 sobre entorno universitario. Las cuentas se usan únicamente en memoria para validar y cruzar los registros. No están incluidas en los archivos de esta entrega.

## Preparación

Se validan columnas y claves únicas. Se normalizan horas, edades, traslados y alias de herramientas. No se reemplazan respuestas abiertas faltantes por textos de otras personas.

Quienes no contestaron la segunda encuesta mantienen el bienestar como dato ausente. Las asociaciones y el clustering de entorno usan las 19 observaciones reales.

## Texto

TF-IDF resume términos destacados. La polaridad léxica conserva negaciones y contempla expresiones de alivio, pero sigue siendo un indicador descriptivo sin validación externa. Un cero puede reflejar falta de coincidencias con el vocabulario, especialmente en respuestas de frecuencia; no demuestra neutralidad emocional.

## Modelos

La etiqueta supervisada distingue modalidad mixta frente a uso declarado solo como guía o atajo. Las respuestas ambiguas se excluyen y la pregunta que define la etiqueta no se incluye en los predictores.

La escala, imputación KNN, TF-IDF y PCA se ajustan dentro de cada fold de entrenamiento. La selección usa F1 de validación; el conjunto de prueba permanece reservado. Se compara con la referencia de predecir siempre la categoría mayoritaria.

Con seis casos de prueba, una sola predicción cambia accuracy en 16.7 puntos porcentuales. Los resultados no justifican predicciones de calificaciones ni decisiones individuales. Las agrupaciones son exploratorias y no se describen perfiles de grupos o complementos de menos de tres personas.

## Reproducibilidad

`resultados/resumen.json` registra la semilla, las versiones y los hashes de las fuentes. El notebook, las figuras, el dashboard y los PDF usan el mismo análisis. Las encuestas y los PDF originales son necesarios solo para recalcular o regenerar los informes, no para consultar o desplegar el panel.
