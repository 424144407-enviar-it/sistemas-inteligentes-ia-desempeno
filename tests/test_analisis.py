import importlib.util
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


class CorreccionesTest(unittest.TestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('analisis'), 'Falta el módulo de análisis')
        import analisis
        return analisis

    def test_alias_no_pierde_herramientas(self):
        a = self.api()
        self.assertEqual(a.extraer_herramientas('Chat GPT, Chargpt, Deepsek y Gemini'),
                         {'chatgpt', 'deepseek', 'gemini'})

    def test_modalidad_ambigua_no_inventa_etiqueta(self):
        a = self.api()
        self.assertEqual(a.clasificar_proposito('Depende del ejercicio que preparemos mañana'), 'Contextual')
        self.assertEqual(a.clasificar_proposito('no'), 'No clasificable')
        self.assertEqual(a.clasificar_proposito('Guía para aprender y ahorrar tiempo'), 'Híbrido')
        self.assertEqual(a.clasificar_proposito('Aprender'), 'Guía')

    def test_reemplazo_respeta_incertidumbre_y_parcialidad(self):
        a = self.api()
        self.assertEqual(a.clasificar_reemplazo('No sé'), 'Indeciso')
        self.assertEqual(a.clasificar_reemplazo('No completamente. Automatiza tareas.'), 'Parcial / Depende')
        self.assertEqual(a.clasificar_reemplazo('Sí, pero no todas las actividades'), 'Parcial / Depende')
        self.assertEqual(a.clasificar_reemplazo('No, requiere supervisión'), 'No')
        self.assertEqual(a.clasificar_reemplazo('No, está limitada en algunas tareas'), 'No')

    def test_polaridad_conserva_negaciones_y_alivio(self):
        a = self.api()
        self.assertGreater(a.score_polaridad('ayuda', 'ia'), 0)
        self.assertLess(a.score_polaridad('no ayuda', 'ia'), 0)
        self.assertGreater(a.score_polaridad('La actividad no afecta mi comprensión del ejemplo', 'ia'), 0)
        self.assertGreater(a.score_polaridad('El ejercicio facilitó el repaso, siento menos estrés', 'ia'), 0)
        self.assertLess(a.score_polaridad('La calidad de ese descanso no parece buena', 'bienestar'), 0)
        self.assertLess(a.score_polaridad('Mala', 'bienestar'), 0)
        self.assertTrue(np.isnan(a.score_polaridad(None, 'bienestar')))

    def test_alivio_estres_antes_despues_y_negado(self):
        a=self.api()
        self.assertGreater(a.score_polaridad('La plataforma baja mis niveles de estrés académico','ia'),0)
        self.assertGreater(a.score_polaridad('Mi estrés ha bajado durante el ejercicio guiado','ia'),0)
        self.assertLess(a.score_polaridad('La plataforma no reduce mi estrés académico','ia'),0)
        self.assertLess(a.score_polaridad('Resuelvo el ejemplo bajo estrés académico','ia'),0)

    def test_validacion_rechaza_columnas_cambiadas_y_cuentas_duplicadas(self):
        a = self.api()
        with self.assertRaisesRegex(ValueError, 'esquema'):
            a.validar_esquema(pd.DataFrame(columns=['equivocada']), 'ia')
        df = pd.DataFrame({'cuenta': ['111111111', '111111111']})
        with self.assertRaisesRegex(ValueError, 'duplicad'):
            a.validar_cuentas(df, 'prueba')

    def test_bienestar_ausente_es_nulo_y_no_texto_inventado(self):
        a = self.api()
        ia = pd.DataFrame([{c: None for c in a.COLS_IA} for _ in range(2)])
        ia['cuenta'] = ['111111111', '222222222']
        ia['horas_ia_raw'] = ['1 hora', '2 horas']
        ia['semestre_inicio_raw'] = ['tercer semestre', 'tercer semestre']
        ia['herramientas_frecuencia'] = ['Chat GPT', 'Gemini']
        ia['guia_o_atajo_raw'] = ['Ambas', 'Guía']
        bie = pd.DataFrame([{c: None for c in a.COLS_BIE}])
        bie['cuenta'] = ['111111111']
        bie['edad_raw'] = ['22']
        bie['traslado_raw'] = ['30 min']
        bie['calidad_sueno'] = ['Buena']
        df = a.preparar_datos(ia, bie)
        self.assertFalse(df.loc[1, 'tiene_bienestar'])
        self.assertTrue(pd.isna(df.loc[1, 'score_bienestar']))
        self.assertEqual(df.loc[1, 'corpus_bie'], '')
        self.assertTrue(pd.isna(df.loc[1, 'pensamiento_critico']))
        self.assertNotIn('nan', df.loc[1, 'corpus_ia'])

    def test_objetivo_no_se_incluye_en_predictores(self):
        a = self.api()
        df = pd.DataFrame({'tipo_uso_ia':['Híbrido','Guía','Atajo','Contextual','No clasificable'],
                           **{c: [1] * 5 for c in a.FEATURES_NUM},
                           'corpus_ia': ['explicaciones verificadas'] * 5})
        X, y = a.datos_supervisados(df)
        self.assertEqual(len(y), 3)
        self.assertEqual(y.tolist(), [1, 0, 0])
        self.assertNotIn('tipo_uso_ia', X.columns)
        self.assertNotIn('guia_o_atajo_raw', X.columns)

    def test_pipeline_no_aprende_vocabulario_ni_escala_de_prueba(self):
        a = self.api()
        from sklearn.linear_model import LogisticRegression
        X = pd.DataFrame({c: np.arange(8,dtype=float) for c in a.FEATURES_NUM})
        X['corpus_ia'] = ['explicaciones codigo matematicas verificar conceptos',
                          'comprender teoria ejercicios contrastar fuentes',
                          'organizar estudio comprobar resultados ejemplos',
                          'programacion proyectos dudas investigacion problemas'] * 2
        pipe = a.crear_pipeline(LogisticRegression())
        pipe.fit(X, [0,1] * 4)
        prep = pipe.named_steps['preprocesar']
        text_pipe = prep.named_transformers_['texto']
        before = prep.named_transformers_['numeros'].named_steps['escalar'].mean_.copy()
        test = X.iloc[:1].copy()
        test['corpus_ia'] = 'palabraexclusivaprueba'
        test.loc[:, a.FEATURES_NUM] = 1000000.
        pipe.predict(test)
        self.assertNotIn('palabraexclusivaprueba', text_pipe.named_steps['tfidf'].vocabulary_)
        np.testing.assert_equal(before, prep.named_transformers_['numeros'].named_steps['escalar'].mean_)

    def test_pipeline_con_un_termino_o_sin_texto(self):
        a=self.api()
        from sklearn.linear_model import LogisticRegression
        for texto in ['concepto','']:
            with self.subTest(texto=texto):
                X=pd.DataFrame({c:np.arange(8,dtype=float) for c in a.FEATURES_NUM})
                X['corpus_ia']=[texto]*8
                try:
                    pipe=a.crear_pipeline(LogisticRegression()).fit(X,[0,1]*4)
                    self.assertEqual(len(pipe.predict(X.iloc[:1])),1)
                except ValueError as e:
                    self.fail(f'El corpus pequeño o vacío impide evaluar: {e}')

    def test_semaforos_respetan_meta_propuesta(self):
        import reportes
        self.assertTrue(callable(getattr(reportes,'estado_meta',None)), 'Falta calcular el estado a partir de la meta')
        self.assertEqual(reportes.estado_meta(94,90),'CUMPLE')
        self.assertEqual(reportes.estado_meta(54.2,60),'REVISAR')

    def test_no_publica_perfil_si_complemento_es_individual(self):
        a=self.api()
        rng=np.random.default_rng(7)
        df=pd.DataFrame(rng.normal(0,.01,(19,len(a.FEATURES_CLUSTER))),columns=a.FEATURES_CLUSTER)
        df.iloc[-1]=100
        df['tiene_bienestar']=True
        r=a.analizar_clusters(df)
        for grupo in r['perfiles_n_min_3']:
            n=r['tamanos'][grupo]
            self.assertGreaterEqual(r['n']-n,3,'Un perfil agregado permite reconstruir un complemento demasiado pequeño')


if __name__ == '__main__':
    unittest.main()
