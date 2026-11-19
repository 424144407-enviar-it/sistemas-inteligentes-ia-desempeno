# Metodología y alcance

El análisis reúne 24 respuestas sobre uso de IA y 19 sobre entorno universitario. Las claves se usan en memoria para validar y emparejar los registros de uno a uno. Los archivos públicos contienen solo resultados agregados.

## Preparación de los datos

Se validan las columnas y las claves únicas antes del cruce. Se normalizan horas, edades, traslados y variantes de nombres de herramientas. Las duraciones expresadas en rangos se aproximan y las unidades se convierten a horas o minutos según corresponda.

Las respuestas abiertas ausentes permanecen vacías. Las cinco personas sin encuesta de bienestar conservan esos datos como faltantes. Para describir entorno, calcular asociaciones y explorar grupos se usan las 19 observaciones reales.

## Análisis del lenguaje

TF-IDF resume términos destacados mediante unigramas y bigramas, con hasta 30 características. La polaridad se calcula por pregunta con un lexicón que contempla negaciones y expresiones de alivio. Después se promedian las preguntas respondidas.

Este indicador describe señales del lenguaje. No tiene validación como escala académica o clínica. Un cero puede aparecer porque no hubo palabras reconocidas, especialmente en respuestas de frecuencia, y no demuestra neutralidad emocional. La ironía, la ambigüedad y las negaciones lejanas siguen siendo límites del procedimiento.

## Clasificación de modalidad

La etiqueta distingue uso mixto de uso exclusivo como guía o atajo. Se excluyen las dos respuestas ambiguas o no clasificables, y la pregunta que define la etiqueta no entra en los predictores.

Los 22 casos etiquetables se dividen de forma estratificada en 16 para entrenamiento y seis para prueba, con semilla 42. La validación cruzada de cinco pliegues se realiza solo sobre entrenamiento. En cada pliegue se vuelven a ajustar escala, imputación KNN, TF-IDF y PCA, evitando aprender de los casos que se van a evaluar.

Se comparan regresión logística, SVM, Random Forest y KNN con una referencia que predice siempre la clase mayoritaria. El candidato entre los cuatro clasificadores se elige por F1 medio de validación, con desempate por accuracy y menor dispersión. La prueba se consulta después de esa elección.

Se reportan accuracy, precisión, recall, F1 y matriz de confusión. Con seis casos de prueba, un acierto cambia accuracy en 16.7 puntos porcentuales. La tarea evalúa categorías declaradas de uso, sin medir aprendizaje efectivo.

## Regresión de horas de uso

El objetivo numérico es `horas_ia_dia`. Los predictores son `semestre_inicio` y `total_herramientas`; el objetivo no se utiliza como entrada. Se conservan casos completos con valores finitos y horas no negativas. En esta ejecución se utilizaron los 24 casos y no hubo exclusiones.

Se fija una partición 75/25 con semilla 42: 18 casos de entrenamiento y seis de prueba. La regresión lineal con escalamiento se compara con `DummyRegressor(strategy='mean')`, que predice el promedio del conjunto con el que se entrena. No se buscan hiperparámetros ni se seleccionan modelos o particiones por su resultado de prueba.

Sobre los 18 casos de entrenamiento se aplica `KFold` de cinco pliegues, mezclados con semilla 42. Cada pliegue vuelve a ajustar el modelo y el escalamiento con su parte de entrenamiento. Luego ambos modelos se ajustan sobre los 18 casos y se evalúan en los mismos seis de prueba. Esta partición es propia de la regresión y no tiene por qué coincidir con la clasificación.

Se calculan R², MAE y RMSE en entrenamiento, por pliegue y en prueba. El resumen de CV contiene la media de los R² definidos, su desviación estándar, el número de pliegues válidos y las medias de MAE y RMSE. No es un R² obtenido al reunir todas las predicciones. Un pliegue con horas constantes conserva R² nulo; se mantienen sus errores en horas. Si no hay suficientes casos o variación para entrenar, el ejercicio se informa como insuficiente.

R² puede ser negativo y no se recorta. Su referencia matemática usa la media del conjunto evaluado, mientras que el modelo de referencia usa la media de entrenamiento. MAE y RMSE se expresan en horas. Las tablas públicas y las figuras muestran métricas, sin predicciones individuales. La regresión evalúa intensidad declarada de uso, no calificaciones ni efectos de la IA sobre el desempeño.

## Asociaciones y agrupación

Se exploran correlaciones de Spearman sin ajuste por comparaciones múltiples. Una asociación no prueba causalidad, y un valor p alto tampoco prueba que la relación no exista.

K-Means y clustering jerárquico usan variables estandarizadas de los 19 registros con entorno observado. El mejor silhouette se elige entre k = 2, 3, 4 y 5. La proyección PCA ayuda a resumir variación, pero no demuestra que los grupos sean estables. Se omiten perfiles si un grupo o su complemento tienen menos de tres personas.

## Reproducibilidad y lectura

La metodología corresponde a la versión 2.1.0. `resultados/resumen.json` registra semilla, versiones y hashes de las fuentes. El notebook, las figuras, el tablero y los PDF usan el mismo análisis. Las encuestas y los PDF originales se necesitan solo para recalcular o regenerar los informes.

La [guía de interpretación](INTERPRETACION.md) explica las métricas con los resultados de esta ejecución. Las definiciones técnicas pueden consultarse en la documentación de scikit-learn sobre [R²](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html), [referencia del promedio](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyRegressor.html) y [evaluación de modelos](https://scikit-learn.org/stable/modules/model_evaluation.html).
