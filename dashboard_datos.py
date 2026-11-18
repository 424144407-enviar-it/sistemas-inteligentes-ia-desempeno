"""Adaptador de agregados públicos. No importa el análisis ni abre las encuestas."""
import json
import math
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

NOMBRES_HERRAMIENTAS={'gemini':'Gemini','chatgpt':'ChatGPT','claude':'Claude',
                     'deepseek':'DeepSeek','copilot':'Copilot','notebooklm':'NotebookLM',
                     'qwen':'Qwen','perplexity':'Perplexity'}
NOMBRES_VARIABLES={'horas_ia_dia':'Horas de IA','semestre_inicio':'Inicio de uso',
                   'total_herramientas':'Herramientas','traslado_min':'Traslado',
                   'score_beneficio_ia':'Polaridad IA','score_bienestar':'Polaridad entorno','edad':'Edad'}
INDIVIDUALES={'cuenta','cuentas','timestamp_ia','timestamp_bie','corpus_ia','corpus_bie',
              'datos_individuales','respuestas_individuales','guia_o_atajo_raw',
              'reemplazo_laboral_raw','herramientas_frecuencia'}
ESTADISTICOS=('n','media','mediana','sd','min','max','q1','q3')
MODALIDADES=('Híbrido','Guía','Atajo','Contextual','No clasificable')
REEMPLAZO=('Sí','No','Parcial / Depende','Indeciso')
MODELOS=('Regresión logística','Random Forest','SVM','KNN','Baseline (mayoría)')
PREGUNTAS=('fase_estudio','cambio_estudio','proceso_verificacion','impacto_tiempo',
           'diferencia_calificaciones','independencia_resolucion','impacto_estres',
           'reglas_personales','pensamiento_critico','motivo_principal','ambiente_hogar',
           'calidad_sueno','frecuencia_desanimo','irritabilidad','dificultad_concentracion')


def _validar_privacidad(obj):
    if isinstance(obj,dict):
        if INDIVIDUALES.intersection(obj):
            raise ValueError('Se detectaron campos individuales. Use únicamente el resumen público.')
        for value in obj.values():_validar_privacidad(value)
    elif isinstance(obj,list):
        for value in obj:_validar_privacidad(value)


def _numeros(obj,claves,enteros=(),nulos=False):
    salida={}
    for k in claves:
        v=obj[k]
        if v is None and nulos and k not in enteros:
            salida[k]=None
            continue
        if type(v) not in (int,float) or not math.isfinite(v):raise ValueError
        if k in enteros and (type(v) is not int or v<0):raise ValueError
        salida[k]=v
    return salida


def _metricas(obj):
    r=_numeros(obj,('accuracy','precision','recall','f1'))
    if any(not 0<=v<=1 for v in r.values()):raise ValueError
    cm=obj['confusion']
    if (not isinstance(cm,list) or len(cm)!=2 or
            any(not isinstance(fila,list) or len(fila)!=2 or
                any(type(x) is not int or x<0 for x in fila) for fila in cm)):raise ValueError
    r['confusion']=cm
    return r


def _supervisado(obj):
    if obj['estado']=='insuficiente':
        return {'estado':'insuficiente','motivo':'No hay suficientes respuestas por clase para evaluar esta parte del estudio.'}
    if obj['estado']!='ok':raise ValueError
    keys=('n_etiquetados','n_excluidos','n_train','n_test','n_folds')
    r=_numeros(obj,keys,enteros=keys)
    if r['n_train']+r['n_test']!=r['n_etiquetados'] or r['n_test']<1 or r['n_folds']<2:raise ValueError
    if obj['seleccionado'] not in MODELOS[:-1] or type(obj['supera_baseline_cv']) is not bool:raise ValueError
    r.update(estado='ok',seleccionado=obj['seleccionado'],supera_baseline_cv=obj['supera_baseline_cv'])
    cv=[]
    for fila in obj['cv']:
        if fila['modelo'] not in MODELOS:raise ValueError
        item=_numeros(fila,('cv_accuracy','cv_accuracy_sd','cv_f1','cv_f1_sd'))
        if not all(0<=item[k]<=1 for k in ('cv_accuracy','cv_f1')) or min(item.values())<0:raise ValueError
        folds=fila['fold_f1']
        if not isinstance(folds,list) or len(folds)!=r['n_folds'] or any(type(x) not in (int,float) or not 0<=x<=1 for x in folds):raise ValueError
        item.update(modelo=fila['modelo'],fold_f1=folds);cv.append(item)
    if 'Baseline (mayoría)' not in [x['modelo'] for x in cv] or r['seleccionado'] not in [x['modelo'] for x in cv]:raise ValueError
    r.update(cv=cv,test=_metricas(obj['test']),baseline_test=_metricas(obj['baseline_test']),test_sensible_pp=100/r['n_test'])
    return r


def _clusters(obj):
    if obj['estado']=='insuficiente':return {'estado':'insuficiente'}
    if obj['estado']!='ok':raise ValueError
    r=_numeros(obj,('n','k','silhouette'),enteros=('n','k'))
    if not 2<=r['k']<=5 or not -1<=r['silhouette']<=1:raise ValueError
    siluetas={k:v for k,v in obj['siluetas'].items() if k in ('2','3','4','5')}
    tamanos={k:v for k,v in obj['tamanos'].items() if re.fullmatch(r'\d+',k)}
    var=obj['pca_varianza']
    if (not siluetas or any(type(v) not in (int,float) or not -1<=v<=1 for v in siluetas.values()) or
        any(type(v) is not int or v<1 for v in tamanos.values()) or sum(tamanos.values())!=r['n'] or
        not isinstance(var,list) or len(var)!=2 or any(type(x) not in (int,float) or not 0<=x<=1 for x in var)):raise ValueError
    r.update(estado='ok',siluetas=siluetas,tamanos=tamanos,pca_varianza=var)
    return r


def leer_resumen(ruta:Path) -> dict:
    try:
        r=json.loads(Path(ruta).read_text(encoding='utf-8'))
    except FileNotFoundError:
        raise ValueError('No se encontró el resumen verificado. Ejecute el análisis antes de abrir el dashboard.') from None
    except (json.JSONDecodeError,UnicodeDecodeError):
        raise ValueError('El archivo de resultados no es un JSON válido.') from None
    _validar_privacidad(r)
    necesarias={'muestra','kpis','descriptivos','herramientas','tipo_uso','reemplazo',
                'supervisado','clusters','proveniencia','metodologia','calidad',
                'correlacion_traslado_ia','correlacion_spearman','tfidf_top','semestre_inicio'}
    if not isinstance(r,dict) or not necesarias.issubset(r):
        raise ValueError('El resumen está incompleto. Regénere los resultados con la versión corregida.')
    m=r['muestra']
    try:
        if (not isinstance(m['ia'],int) or m['ia']<=0 or m['emparejados']<0 or
                m['emparejados']>m['ia'] or m['emparejados']>m['bienestar'] or
                m['solo_ia']!=m['ia']-m['emparejados']):
            raise ValueError
        if sum(r['tipo_uso'].values())!=m['ia']:
            raise ValueError
        if any(not isinstance(v,int) or v<0 or v>m['ia'] for v in r['herramientas'].values()):
            raise ValueError
    except (KeyError,TypeError,AttributeError,ValueError):
        raise ValueError('Los totales de la muestra son inconsistentes. Revise el análisis.') from None
    # Proyectar listas permitidas: ningún comentario o columna añadida llega a la UI o CSV.
    try:
        limpio={'muestra':_numeros(m,('ia','bienestar','emparejados','solo_ia','solo_bienestar'),enteros=tuple(m))}
        campos_kpi=('adopcion_observada_n','adopcion_observada_pct','mediana_ia_h',
                     'guia_hibrido_pct','hibrido_pct','multiherramienta_pct','multiherramienta_n',
                     'traslado_mediana_min','traslado_mayor_90_n','reemplazo_si_pct')
        limpio['kpis']=_numeros(r['kpis'],campos_kpi,enteros=('adopcion_observada_n','multiherramienta_n','traslado_mayor_90_n'))
        limpio['descriptivos']={v:_numeros(r['descriptivos'][v],ESTADISTICOS,enteros=('n',),nulos=True) for v in NOMBRES_VARIABLES}
        # Las tarjetas de contexto necesitan duración observada para poder interpretarse.
        if limpio['descriptivos']['traslado_min']['n']<1 or any(limpio['descriptivos']['traslado_min'][k] is None for k in ESTADISTICOS):raise ValueError
        for campo,permitidos in [('herramientas',NOMBRES_HERRAMIENTAS),('tipo_uso',MODALIDADES),('reemplazo',REEMPLAZO)]:
            limpio[campo]=_numeros({k:r[campo].get(k,0) for k in permitidos},tuple(permitidos),enteros=tuple(permitidos))
        if sum(limpio['tipo_uso'].values())!=m['ia'] or sum(limpio['reemplazo'].values())!=m['ia']:raise ValueError
        limpio['supervisado']=_supervisado(r['supervisado']);limpio['clusters']=_clusters(r['clusters'])
        limpio['correlacion_traslado_ia']=_numeros(r['correlacion_traslado_ia'],('n','rho','p'),enteros=('n',),nulos=True)
        limpio['correlacion_spearman']={x:_numeros(r['correlacion_spearman'][x],tuple(NOMBRES_VARIABLES),nulos=True) for x in NOMBRES_VARIABLES}
        limpio['tfidf_top']={k:v for k,v in r['tfidf_top'].items() if re.fullmatch(r'[a-z ]{1,64}',k) and type(v) in (int,float) and math.isfinite(v) and 0<=v<=1}
        limpio['semestre_inicio']={k:v for k,v in r['semestre_inicio'].items() if re.fullmatch(r'[1-9]',k) and type(v) is int and 0<=v<=m['ia']}
        limpio['calidad']=_numeros(r['calidad'],('textos_ia_ausentes',),enteros=('textos_ia_ausentes',))
        limpio['polaridad_por_pregunta']={k:_numeros(v,('n','media','n_score_cero'),enteros=('n','n_score_cero'),nulos=True) for k,v in r.get('polaridad_por_pregunta',{}).items() if k in PREGUNTAS}
        fecha=r['proveniencia']['fecha'];datetime.fromisoformat(fecha)
        versiones={k:v for k,v in r['proveniencia']['versiones'].items() if k in ('pandas','numpy','scikit-learn','scipy','matplotlib') and isinstance(v,str) and re.fullmatch(r'[0-9a-zA-Z.+_-]{1,30}',v)}
        limpio['proveniencia']={'fecha':fecha,'versiones':versiones}
        version=r['metodologia']['version']
        if not isinstance(version,str) or not re.fullmatch(r'\d+\.\d+\.\d+',version):raise ValueError
        limpio['metodologia']={'version':version,**_numeros(r['metodologia'],('semilla',),enteros=('semilla',))}
    except (KeyError,TypeError,AttributeError,ValueError):
        raise ValueError('El resumen está incompleto o no cumple el esquema público. Vuelve a generar los resultados.') from None
    return limpio


def tabla_herramientas(r:dict,seleccion:list[str]|None=None)->pd.DataFrame:
    claves=list(r['herramientas']) if seleccion is None else seleccion
    filas=[{'Clave':k,'Herramienta':NOMBRES_HERRAMIENTAS.get(k,k),
            'Respuestas':r['herramientas'][k],
            'Porcentaje':100*r['herramientas'][k]/r['muestra']['ia']}
           for k in claves if k in r['herramientas']]
    return pd.DataFrame(filas,columns=['Clave','Herramienta','Respuestas','Porcentaje']).sort_values('Respuestas',ascending=False)


def tabla_modalidades(r:dict)->pd.DataFrame:
    return pd.DataFrame([{'Modalidad':k,'Respuestas':v,'Porcentaje':100*v/r['muestra']['ia']}
                         for k,v in r['tipo_uso'].items()])


def documentos_publicos(root:Path)->dict[str,Path]:
    base=Path(root)/'docs'/'actualizados'
    return {'tecnica':base/'DOCUMENTACION_TECNICA_SI_C_CORREGIDA.pdf',
            'negocio':base/'DOCUMENTACION_NEGOCIO_SI_C_CORREGIDA.pdf'}
