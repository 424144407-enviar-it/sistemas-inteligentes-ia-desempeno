from pathlib import Path
import unittest
import json
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]


class DashboardAppTest(unittest.TestCase):
    def test_cinco_vistas_sin_excepciones(self):
        at=AppTest.from_file(str(ROOT/'dashboard.py'),default_timeout=30).run()
        self.assertEqual(len(at.exception),0)
        for vista in ['Uso de IA','Entorno y bienestar','Modelos','Documentación','Panorama']:
            with self.subTest(vista=vista):
                at.radio(key='vista').set_value(vista).run()
                self.assertEqual(len(at.exception),0)

    def test_selecciones_vacias_muestran_mensaje(self):
        at=AppTest.from_file(str(ROOT/'dashboard.py'),default_timeout=30).run()
        at.radio(key='vista').set_value('Uso de IA').run()
        at.multiselect(key='filtro_herramientas').set_value([]).run()
        self.assertEqual(len(at.exception),0)
        self.assertTrue(any('Selecciona al menos' in x.value for x in at.info))
        at.radio(key='vista').set_value('Entorno y bienestar').run()
        at.multiselect(key='variables_correlacion').set_value([]).run()
        self.assertEqual(len(at.exception),0)
        self.assertTrue(any('Selecciona al menos' in x.value for x in at.info))

    def test_clusters_visibles_sin_clasificacion(self):
        import streamlit as st
        r=json.loads((ROOT/'resultados'/'resumen.json').read_text(encoding='utf-8'))
        r['supervisado']={'estado':'insuficiente','motivo':'Sin suficientes casos por clase'}
        st.cache_data.clear()
        try:
            with patch('dashboard_datos.leer_resumen',return_value=r):
                at=AppTest.from_file(str(ROOT/'dashboard.py'),default_timeout=30).run()
                at.radio(key='vista').set_value('Modelos').run()
                self.assertEqual(len(at.exception),0)
                self.assertEqual(len(at.tabs),2)
        finally:st.cache_data.clear()

    def test_correlacion_indeterminada_no_rompe_entorno(self):
        import streamlit as st
        r=json.loads((ROOT/'resultados'/'resumen.json').read_text(encoding='utf-8'))
        r['correlacion_traslado_ia'].update(rho=None,p=None)
        st.cache_data.clear()
        try:
            with patch('dashboard_datos.leer_resumen',return_value=r):
                at=AppTest.from_file(str(ROOT/'dashboard.py'),default_timeout=30).run()
                at.radio(key='vista').set_value('Entorno y bienestar').run()
                self.assertEqual(len(at.exception),0)
        finally:st.cache_data.clear()


if __name__=='__main__':unittest.main()
