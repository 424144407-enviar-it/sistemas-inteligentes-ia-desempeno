import json
import unittest

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split

import analisis


class RegresionTest(unittest.TestCase):
    def datos(self):
        rng = np.random.default_rng(42)
        x = rng.normal(size=(24, 2))
        return pd.DataFrame({'semestre_inicio': x[:, 0], 'total_herramientas': x[:, 1],
                             'horas_ia_dia': 10 + 2 * x[:, 0] + 3 * x[:, 1],
                             'cuenta': ['111111111'] * 24, 'corpus_ia': ['texto privado'] * 24})

    def test_objetivo_excluido_y_solo_predictores_aprobados(self):
        X, y = analisis.datos_regresion(self.datos())
        self.assertEqual(list(X.columns), ['semestre_inicio', 'total_herramientas'])
        self.assertEqual(y.name, 'horas_ia_dia')
        self.assertEqual(len(y), 24)

    def test_referencia_usa_media_de_entrenamiento_y_misma_prueba(self):
        df = self.datos()
        r = analisis.evaluar_regresion(df)
        X, y = analisis.datos_regresion(df)
        _, _, ytr, yte = train_test_split(X, y, test_size=.25, random_state=42)
        pred = np.repeat(ytr.mean(), len(yte))
        base = next(m for m in r['modelos'] if m['modelo'] == 'Referencia (media)')
        self.assertEqual((r['n_train'], r['n_test'], r['n_folds']), (18, 6, 5))
        self.assertAlmostEqual(base['prueba']['r2'], r2_score(yte, pred))
        self.assertAlmostEqual(base['prueba']['mae_h'], mean_absolute_error(yte, pred))
        self.assertAlmostEqual(base['prueba']['rmse_h'], root_mean_squared_error(yte, pred))
        self.assertEqual(r, analisis.evaluar_regresion(df))

    def test_pipeline_no_reajusta_escala_al_predecir(self):
        X, y = analisis.datos_regresion(self.datos())
        pipe = analisis.crear_pipeline_regresion().fit(X.iloc[:18], y.iloc[:18])
        antes = pipe.named_steps['escalar'].mean_.copy()
        pipe.predict(X.iloc[18:] * 1000000)
        np.testing.assert_allclose(antes, X.iloc[:18].mean())
        np.testing.assert_equal(antes, pipe.named_steps['escalar'].mean_)

    def test_r2_negativo_y_objetivo_constante_no_se_ocultan(self):
        self.assertLess(analisis.metricas_regresion([1, 2, 3], [8, 8, 8])['r2'], 0)
        self.assertIsNone(analisis.metricas_regresion([2, 2, 2], [1, 1, 1])['r2'])
        df = self.datos()
        df['horas_ia_dia'] = 2
        self.assertEqual(analisis.evaluar_regresion(df)['estado'], 'insuficiente')

    def test_faltantes_excluidos_y_exportacion_solo_agregada(self):
        df = self.datos()
        df.loc[0, 'horas_ia_dia'] = np.nan
        df.loc[1, 'total_herramientas'] = np.inf
        r = analisis.evaluar_regresion(df)
        self.assertEqual((r['n'], r['n_excluidos']), (22, 2))
        texto = json.dumps(r, allow_nan=False)
        for privado in ['111111111', 'texto privado', 'predicciones', 'cuenta']:
            self.assertNotIn(privado, texto)
        self.assertEqual(analisis.evaluar_regresion(df.head(8))['estado'], 'insuficiente')

    def test_informe_interpreta_los_resultados_y_la_particion_recalculados(self):
        from pathlib import Path
        from reportes import Informe
        root=Path(__file__).resolve().parents[1]
        r=json.loads((root/'resultados/resumen.json').read_text(encoding='utf-8'))
        r['regresion']=analisis.evaluar_regresion(self.datos().head(20))
        informe=Informe(r,root/'resultados/figuras')
        texto=lambda paginas:' '.join(f.getPlainText() for pagina in paginas for f in pagina if hasattr(f,'getPlainText'))
        tecnica=texto(informe.tecnica())
        negocio=texto(informe.negocio())
        self.assertIn('con los 15 casos de entrenamiento',tecnica)
        self.assertIn('en los 5 casos reservados',tecnica)
        self.assertIn('la regresión redujo el error medio',negocio)

    def test_r2_cv_informa_cuantos_pliegues_tienen_variacion(self):
        df=self.datos()
        _, _, ytr, _=train_test_split(df,df['horas_ia_dia'],test_size=.25,random_state=42)
        df['horas_ia_dia']=1.
        df.loc[ytr.index[0],'horas_ia_dia']=2.
        r=analisis.evaluar_regresion(df)
        self.assertEqual(r['estado'],'ok')
        for modelo in r['modelos']:
            self.assertEqual(modelo['cv']['folds_r2_validos'],1)
            self.assertEqual(sum(f['r2'] is None for f in modelo['folds']),4)


if __name__ == '__main__':
    unittest.main()
