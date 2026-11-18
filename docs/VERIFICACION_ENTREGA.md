# Verificación de la entrega

18 de noviembre de 2026.

## Ejecución

- Se creó un entorno Python 3.12 nuevo, sin reutilizar las bibliotecas del equipo.
- Con solo `requirements.txt`, pasaron las 11 pruebas del dashboard: cinco vistas, controles, descargas y estados de datos incompletos. scikit-learn no estaba instalado en ese entorno mínimo.
- Con `requirements-dev.txt`, pasaron las 23 pruebas del proyecto completo.
- El arranque del dashboard no requiere encuestas privadas, PDF originales o entrenamiento de modelos.
- Se mantuvieron las mismas rutas, datos agregados y PDF corregidos que usa la versión revisada.

## Organización y privacidad

- El repositorio incluye dashboard, notebook, análisis, figuras, tablas e informes corregidos.
- `requirements.txt` contiene las dependencias del dashboard; análisis y desarrollo tienen archivos separados.
- `.streamlit/config.toml` no fija la aplicación a una dirección local; CORS y XSRF se mantienen activados.
- Se comprobaron los archivos de texto y los dos PDF de la entrega contra los identificadores de las fuentes. No se encontraron números de cuenta reales.
- Las encuestas, PDF originales, secretos, entornos virtuales y notas internas no forman parte del commit de entrega.
- El historial previo del repositorio se conserva: esta organización no reescribe commits anteriores.

## Alcance

La estructura está preparada para Streamlit Community Cloud con entrada `dashboard.py` y Python 3.12. Se verificó la ejecución local desde esta carpeta; el despliegue real en el proveedor queda pendiente de configurar la app con el repositorio.
