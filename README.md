# IA en contexto · Sistemas Inteligentes

Dashboard sobre el uso de IA y el entorno universitario en MAC. Reúne 24 respuestas sobre IA y 19 sobre entorno y bienestar. Incluye los resultados agregados, el notebook y los dos informes corregidos.

El panel ya tiene los resultados necesarios para funcionar: **no necesita las encuestas privadas para desplegarse**.

## Abrir en tu computadora

Usa Python 3.12 y ejecuta desde esta carpeta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run dashboard.py --server.address 127.0.0.1
```

En Linux o macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run dashboard.py --server.address 127.0.0.1
```

Abre la dirección que imprime Streamlit, normalmente `http://127.0.0.1:8501`.

## Subir y desplegar

1. Sube **el contenido de esta carpeta** a la raíz de tu repositorio de GitHub. Incluye `.streamlit`, `assets`, `resultados` y `docs/actualizados`.
2. En [Streamlit Community Cloud](https://share.streamlit.io/), crea una app y elige ese repositorio y su rama.
3. En **Main file path**, escribe `dashboard.py`.
4. En **Advanced settings**, selecciona **Python 3.12** y despliega.

`requirements.txt` instala el dashboard. La configuración de esta entrega permite que el proveedor configure el servidor; no fija una dirección de red local.

Consulta [la guía de despliegue](docs/DESPLIEGUE.md) si necesitas más detalle. Esta carpeta está preparada para desplegar; no incluye una publicación ya realizada.

## Qué contiene

```text
dashboard.py                     Aplicación Streamlit
dashboard_datos.py               Lectura y validación de agregados
.streamlit/config.toml           Apariencia y configuración
assets/                         Estilos del panel
resultados/                     Resumen JSON, tablas y figuras
docs/actualizados/              Los dos PDF corregidos
Analisis_IA_Desempeno_MAC_Cuestionarios.ipynb
analisis.py                     Limpieza, NLP y evaluación
visualizaciones.py              Figuras del estudio
reportes.py                     Generación de los PDF
verificar_notebook.py           Ejecución y comprobación del notebook
tests/                          Pruebas del análisis y el panel
requirements.txt                Dependencias del dashboard
requirements-analysis.txt       Dependencias opcionales del análisis y PDF
requirements-dev.txt            Dependencias para todas las pruebas y el notebook
```

## Volver a calcular el análisis

Solo necesitas este paso si quieres cambiar las encuestas o recalcular los resultados. Primero instala las dependencias opcionales:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-analysis.txt
```

Coloca localmente los archivos `Desempeño académico por el uso de IA (Respuestas).xlsx` y `Cuestionario_ Entorno Universitario y Bienestar.csv` en `data/private/`. Después ejecuta:

```powershell
.\.venv\Scripts\python.exe analisis.py --data-dir data/private --out resultados
```

Para regenerar los PDF, coloca tus PDF originales en `docs/originales/`, con sus nombres originales, y ejecuta:

```powershell
.\.venv\Scripts\python.exe reportes.py --referencias docs/originales --out docs/actualizados
```

Las carpetas de datos privados y PDF originales se entregan vacías y están excluidas de Git. Los informes corregidos sí están incluidos y el dashboard permite descargarlos.

## Ejecutar las pruebas

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Para probar solo el dashboard con las dependencias mínimas:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_dashboard*.py" -v
```

`verificar_notebook.py` requiere las dependencias de desarrollo y tus encuestas locales. No se ejecuta durante el despliegue.

## Cómo leer los resultados

El estudio es exploratorio. Describe las respuestas de este grupo, no a toda la carrera. La clasificación distingue uso mixto de uso declarado solo como guía o atajo; no mide calificaciones, aprendizaje efectivo o dependencia.

Las ausencias de bienestar se mantienen como datos faltantes. Los porcentajes conservan su base aunque selecciones herramientas. Los modelos se comparan con una referencia mayoritaria, que en esta ejecución obtiene mejor F1 en validación. No se ofrecen predicciones individuales.

Más detalles en [la metodología](docs/METODOLOGIA.md) y en los [informes corregidos](docs/actualizados/).
