# Desplegar el dashboard

La opción prevista es Streamlit Community Cloud con un repositorio de GitHub.

## Archivos que deben estar en el repositorio

`dashboard.py` y `requirements.txt` deben quedar en la raíz. También son necesarios `dashboard_datos.py`, `.streamlit/config.toml`, `assets/dashboard.css`, `resultados/resumen.json` y los dos PDF de `docs/actualizados/` para habilitar sus descargas.

Sube el contenido de la entrega, no el ZIP. Si añades una carpeta exterior en GitHub, la ruta de entrada cambia; la estructura recomendada evita ese paso.

## Configuración en Community Cloud

- Repository: el repositorio al que subiste esta entrega.
- Branch: la rama que contiene los archivos; por ejemplo, `main`.
- Main file path: `dashboard.py`.
- Python version: `3.12`, en Advanced settings.
- Secrets: no se necesitan para esta versión.

Antes de publicar, revisa la audiencia elegida en el proveedor. El panel contiene solo resultados agregados, pero esa configuración determina quién puede verlo. No subas las encuestas, los PDF originales, `.venv`, `.git` o archivos de credenciales.

## Dependencias

Community Cloud usa `requirements.txt`, que instala Streamlit, Altair y pandas. Los archivos `requirements-analysis.txt` y `requirements-dev.txt` son opcionales y no se seleccionan automáticamente como dependencias del despliegue.

La aplicación lee los resultados ya calculados. No descarga corpus, reentrena modelos ni necesita abrir las encuestas al arrancar.

## Si no arranca

- Si falta una biblioteca, comprueba que `requirements.txt` está en la raíz y que seleccionaste Python 3.12.
- Si faltan datos, comprueba que `resultados/resumen.json` se subió completo.
- Si falta el estilo, comprueba `assets/dashboard.css` y `.streamlit/config.toml`.
- Si no aparecen las descargas, revisa los dos PDF de `docs/actualizados/` y respeta sus nombres.
- En Linux las mayúsculas importan: no cambies nombres de archivos o carpetas.

## Referencias oficiales

- [Organización de archivos](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)
- [Dependencias de la app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Pasos de despliegue](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
