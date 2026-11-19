import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[1]


class DashboardDatosTest(unittest.TestCase):
    def test_regresion_acepta_r2_negativo_y_descarta_campos_extra(self):
        a=self.api()
        metricas={'r2':-.245,'mae_h':.81,'rmse_h':1.04,'nota_privada':'no publicar'}
        obj={'estado':'ok','n':24,'n_excluidos':0,'n_train':18,'n_test':6,'n_folds':5,
             'modelos':[{'modelo':nombre,'prueba':metricas,'entrenamiento':metricas,
                         'cv':{'r2_media':-3.1,'r2_sd':3.6,'mae_media_h':.8,'rmse_media_h':1.,'folds_r2_validos':5},
                         'folds':[{'n':n,**metricas} for n in [4,4,4,3,3]]}
                        for nombre in ['Regresión lineal','Referencia (media)']]}
        limpio=a._regresion(obj)
        self.assertEqual(limpio['modelos'][0]['prueba']['r2'],-.245)
        self.assertNotIn('nota_privada',limpio['modelos'][0]['prueba'])
        obj['modelos'][0]['prueba']={**metricas,'r2':None}
        self.assertIsNone(a._regresion(obj)['modelos'][0]['prueba']['r2'])
        obj['modelos'][0]['prueba']={**metricas,'r2':1.5}
        with self.assertRaises(ValueError):a._regresion(obj)

    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('dashboard_datos'),'Falta el adaptador de agregados')
        import dashboard_datos
        return dashboard_datos

    def test_porcentaje_de_herramientas_conserva_denominador(self):
        a=self.api()
        r=json.loads((ROOT/'resultados'/'resumen.json').read_text(encoding='utf-8'))
        df=a.tabla_herramientas(r,['gemini'])
        self.assertEqual(len(df),1)
        self.assertAlmostEqual(df.iloc[0]['Porcentaje'],100*r['herramientas']['gemini']/r['muestra']['ia'])
        self.assertEqual(len(a.tabla_herramientas(r,[])),0)

    def test_cargador_rechaza_datos_individuales(self):
        a=self.api()
        r=json.loads((ROOT/'resultados'/'resumen.json').read_text(encoding='utf-8'))
        r['extra']={'cuenta':'111111111'}
        with TemporaryDirectory() as d:
            p=Path(d)/'resumen.json'
            p.write_text(json.dumps(r),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'individual'):
                a.leer_resumen(p)

    def test_cargador_valida_cobertura_y_totales(self):
        a=self.api()
        r=json.loads((ROOT/'resultados'/'resumen.json').read_text(encoding='utf-8'))
        r['muestra']['emparejados']=r['muestra']['ia']+1
        with TemporaryDirectory() as d:
            p=Path(d)/'resumen.json'
            p.write_text(json.dumps(r),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'muestra'):
                a.leer_resumen(p)

    def test_documentos_devuelve_informes_definitivos(self):
        a=self.api()
        docs=a.documentos_publicos(ROOT)
        self.assertEqual(set(docs),{'tecnica','negocio'})
        self.assertEqual({p.name for p in docs.values()},{'DOCUMENTACION_TECNICA.pdf','DOCUMENTACION_NEGOCIO.pdf'})
        for p in docs.values():
            self.assertEqual(p.parent,ROOT/'docs')
            self.assertNotIn('CORREGIDA',p.name)
            self.assertTrue(p.read_bytes().startswith(b'%PDF'))

    def test_resumen_incompleto_falla_con_mensaje(self):
        a=self.api()
        r=json.loads((ROOT/'resultados'/'resumen.json').read_text(encoding='utf-8'))
        del r['kpis']['mediana_ia_h']
        with TemporaryDirectory() as d:
            p=Path(d)/'resumen.json';p.write_text(json.dumps(r),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'incompleto|esquema'):
                a.leer_resumen(p)

    def test_exportacion_excluye_campos_ajenos_a_descriptivos(self):
        a=self.api()
        r=json.loads((ROOT/'resultados'/'resumen.json').read_text(encoding='utf-8'))
        r['descriptivos']['traslado_min']['comentario_privado']='Contenido que no debe salir'
        r['descriptivos']['otro_registro']={'media':3,'comentario':'No es parte del resumen'}
        with TemporaryDirectory() as d:
            p=Path(d)/'resumen.json';p.write_text(json.dumps(r),encoding='utf-8')
            limpio=a.leer_resumen(p)
            self.assertNotIn('comentario_privado',limpio['descriptivos']['traslado_min'])
            self.assertNotIn('otro_registro',limpio['descriptivos'])

    def test_campo_de_conteos_mal_formado_no_expone_excepcion_interna(self):
        a=self.api()
        r=json.loads((ROOT/'resultados'/'resumen.json').read_text(encoding='utf-8'))
        r['herramientas']=None
        with TemporaryDirectory() as d:
            p=Path(d)/'resumen.json';p.write_text(json.dumps(r),encoding='utf-8')
            try:a.leer_resumen(p)
            except ValueError:pass
            except Exception as e:self.fail(f'La estructura inválida deja escapar {type(e).__name__}')
            else:self.fail('La estructura inválida fue aceptada')


if __name__=='__main__':unittest.main()
