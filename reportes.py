"""Recrea los informes con cifras de resultados/resumen.json y portadas originales."""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                               Spacer, Table, TableStyle)

AZUL=colors.HexColor('#365F91')
ANCHO=520


def estado_meta(valor:float,meta:float)->str:
    return 'CUMPLE' if valor>=meta else 'REVISAR'


def estilos():
    reg=Path('C:/Windows/Fonts/GOTHIC.TTF')
    bold=Path('C:/Windows/Fonts/GOTHICB.TTF')
    if not reg.is_file():
        from matplotlib.font_manager import findfont
        reg=Path(findfont('DejaVu Sans'))
        bold=Path(findfont('DejaVu Sans:weight=bold'))
    pdfmetrics.registerFont(TTFont('Proyecto',str(reg)))
    pdfmetrics.registerFont(TTFont('Proyecto-Bold',str(bold)))
    pdfmetrics.registerFontFamily('Proyecto',normal='Proyecto',bold='Proyecto-Bold',
                                italic='Proyecto',boldItalic='Proyecto-Bold')
    return {
        'body':ParagraphStyle('body',fontName='Proyecto',fontSize=10.5,leading=14.5,
                              alignment=TA_JUSTIFY,spaceAfter=8),
        'title':ParagraphStyle('title',fontName='Proyecto',fontSize=19,leading=23,
                               textColor=AZUL,spaceAfter=15),
        'sub':ParagraphStyle('sub',fontName='Proyecto-Bold',fontSize=11,leading=14.5,
                             spaceBefore=9,spaceAfter=7),
        'note':ParagraphStyle('note',fontName='Proyecto',fontSize=9,leading=12,
                              textColor=colors.HexColor('#444444'),spaceAfter=7),
        'cell':ParagraphStyle('cell',fontName='Proyecto',fontSize=9.2,leading=12),
        'head':ParagraphStyle('head',fontName='Proyecto-Bold',fontSize=9.2,leading=12),
        'caption':ParagraphStyle('caption',fontName='Proyecto',fontSize=8.5,leading=11,
                                 alignment=TA_CENTER,spaceBefore=5,spaceAfter=8),
    }


class Informe:
    def __init__(self,r:dict,figuras:Path):
        self.r=r;self.figuras=figuras;self.s=estilos()

    def p(self,t,style='body'):
        return Paragraph(t,self.s[style])

    def h(self,t):return self.p(t,'title')
    def sub(self,t):return self.p(t,'sub')
    def nota(self,t):return self.p(t,'note')

    def tabla(self,filas,anchos):
        datos=[[self.p(escape(str(c)),'head' if i==0 else 'cell') for c in fila]
               for i,fila in enumerate(filas)]
        t=Table(datos,colWidths=anchos,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),.65,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#F1F4F8')),
        ]))
        return t

    def img(self,nombre,ancho=ANCHO,maxalto=260):
        i=Image(str(self.figuras/f'{nombre}.png'))
        escala=min(ancho/i.imageWidth,maxalto/i.imageHeight)
        i.drawWidth=i.imageWidth*escala;i.drawHeight=i.imageHeight*escala
        i.hAlign='CENTER'
        return i

    def tecnica(self):
        r=self.r;m=r['muestra'];k=r['kpis'];c=r['clusters'];s=r['supervisado']
        filas=r['descriptivos'];rho=r['correlacion_traslado_ia']
        paginas=[]
        paginas.append([
            self.h('CONTEXTO, PROBLEMA Y OBJETIVOS'),
            self.p('<b>Análisis exploratorio del uso de IA, modalidades declaradas y entorno universitario.</b> Se mantiene el tema académico del proyecto y se ajusta el alcance a lo que realmente permiten medir las dos encuestas.'),
            self.sub('CONTEXTO ACADÉMICO Y TECNOLÓGICO'),
            self.p('Las herramientas de inteligencia artificial forman parte de las actividades académicas de las personas encuestadas. Sus respuestas abiertas describen hábitos, verificación de información y percepciones sobre autonomía, tiempo y bienestar. La heterogeneidad del texto requiere limpieza y codificación explícitas.'),
            self.sub('PLANTEAMIENTO DEL PROBLEMA'),
            self.p('El estudio busca estructurar respuestas cualitativas y explorar su relación con el entorno. Las fuentes no incluyen calificaciones verificadas antes y después del uso de IA ni una escala validada de dependencia. Por ello, no permiten demostrar efectos causales sobre el rendimiento ni emitir diagnósticos individuales.'),
            self.sub('OBJETIVO GENERAL'),
            self.p('Implementar un análisis reproducible que integre los cuestionarios, describa sus respuestas y compare modelos para clasificar la modalidad declarada de uso mixto frente al uso exclusivo como guía o atajo.'),
            self.sub('OBJETIVOS ESPECÍFICOS'),
            self.p('1. Validar esquema y claves antes de unir las fuentes.<br/>2. Estandarizar variables numéricas y alias de herramientas.<br/>3. Resumir texto mediante TF-IDF y polaridad léxica contextual.<br/>4. Explorar asociaciones y agrupaciones sin fabricar bienestar ausente.<br/>5. Evaluar modelos con preprocesamiento dentro de cada fold y prueba reservada.'),
            self.nota('Versión corregida. Los resultados previos de “aprendizaje efectivo” se sustituyen por una tarea de clasificación de respuestas observadas. No son experimentos equivalentes.'),
        ])
        paginas.append([
            self.h('ARQUITECTURA E INTEGRACIÓN DE DATOS'),
            self.p('El módulo compartido analisis.py es la fuente de cálculos para el notebook, las figuras y ambos documentos. El dashboard futuro podrá consumir los mismos resultados agregados.'),
            self.tabla([
                ['Módulo','Responsabilidad'],
                ['1. Fuentes y validación','Verificar columnas, orden, identificadores de nueve dígitos, unicidad y presencia de archivos.'],
                ['2. Limpieza y unión','Expresiones regulares, alias documentados y left join uno a uno.'],
                ['3. Texto y codificación','Corpus sin valores nan ni respuestas inventadas. Polaridad por pregunta con negación.'],
                ['4. Descripción y agrupación','EDA de la muestra; asociaciones y clustering de registros con bienestar observado.'],
                ['5. Evaluación supervisada','Split estratificado; pipelines en CV; baseline; selección sin consultar la prueba.'],
                ['6. Salidas','JSON, tablas y figuras agregadas; reportes generados desde la misma ejecución.'],
            ],[135,385]),Spacer(1,14),
            self.tabla([
                ['Fuente / cruce','Registros','Atributos originales'],
                ['Uso de IA',m['ia'],18],['Entorno y bienestar',m['bienestar'],17],
                ['Emparejados',m['emparejados'],'Llave validada, unión uno a uno'],
                ['Solo en IA',m['solo_ia'],'Bienestar no observado'],
                ['Solo en bienestar',m['solo_bienestar'],'No se incorporan al universo principal'],
            ],[270,80,170]),
            self.nota('La clave se utiliza únicamente en memoria para el cruce. No se exportan cuentas, marcas temporales ni respuestas abiertas. Las encuestas originales permanecen locales, excluidas de Git.'),
        ])
        paginas.append([
            self.h('LIMPIEZA, REGEX Y DATOS AUSENTES'),
            self.tabla([
                ['Variable / caso','Regla aplicada'],
                ['Horas de IA','Minutos / 60; “hora y media” = 1.5; “entre 1 y 3” = 2. Los rangos se aproximan y no representan mediciones exactas.'],
                ['Semestre de inicio','Ordinales y dígitos. “Hace 3 semestres” se interpreta respecto al 7.º semestre de la cohorte descrita.'],
                ['Edad y traslado','Se extraen edades; horas y minutos se convierten a minutos. No se recortan los valores extremos observados.'],
                ['Herramientas','Chat GPT y Chargpt se unifican con ChatGPT; Deepsek con DeepSeek; no se cuenta dos veces un alias en la misma respuesta.'],
                ['Modalidad de uso','Guía, atajo, híbrido, contextual o no clasificable. “Depende” por sí solo no prueba modalidad híbrida.'],
                ['Reemplazo laboral','Se distinguen Sí, No, Parcial / Depende e Indeciso antes de calcular porcentajes.'],
            ],[125,395]),
            self.sub('TRATAMIENTO DE AUSENCIAS'),
            self.p(f'Los {m["solo_ia"]} participantes sin segunda encuesta conservan bienestar nulo. Las {r["calidad"]["textos_ia_ausentes"]} respuestas abiertas faltantes de IA no se sustituyen por textos de otros estudiantes. Para describir entorno se usan solo los {m["emparejados"]} registros observados.'),
            self.p('En clasificación, la escala y la imputación KNN (k=3) se aprenden únicamente con cada fold de entrenamiento. Se escala antes de calcular distancias y se añaden indicadores de ausencia. La imputación no se utiliza para simular respuestas textuales.'),
            self.nota('Control de calidad de esta ejecución: no quedaron horas, semestres, edades ni traslados sin convertir entre los registros que sí los respondieron. La recuperación sin nulos no valida por sí sola la exactitud de cada aproximación textual.'),
        ])
        paginas.append([
            self.h('PROCESAMIENTO DE LENGUAJE NATURAL'),
            self.sub('NORMALIZACIÓN Y VECTORIZACIÓN'),
            self.p('El texto se normaliza con Unicode, se retiran signos y números y se filtran palabras funcionales preservando negaciones. TF-IDF utiliza hasta 30 características con unigramas y bigramas. La vectorización descriptiva de toda la muestra es independiente de la que se ajusta dentro de cada fold del modelo.'),
            self.sub('POLARIDAD LÉXICA CONTEXTUAL'),
            self.p('Se cuentan raíces positivas y negativas por pregunta. La negación en las cuatro palabras anteriores y las expresiones de alivio modifican la polaridad. La puntuación por pregunta es (positivos - negativos) / (positivos + negativos + 1); el indicador final es la media de las preguntas respondidas.'),
            self.tabla([
                ['Comprobación','Comportamiento corregido'],
                ['ayuda / no ayuda','Polaridad positiva / negativa'],
                ['La práctica no afecta mi comprensión','No se penaliza como afectación afirmada'],
                ['Mi estrés ha bajado / no reduce mi estrés','Alivio positivo / alivio negado negativo'],
                ['El descanso no parece bueno','Polaridad negativa en el contexto de descanso'],
                ['Sin encuesta','Dato ausente; no se asigna bienestar neutral'],
            ],[245,275]),Spacer(1,10),self.img('nlp',maxalto=170),
            self.nota('Ejemplos sintéticos de regresión. Indicadores sin validación externa: negación de largo alcance, ironía y ambigüedad siguen siendo límites. Cero puede indicar falta de coincidencias léxicas; no demuestra neutralidad. El notebook desglosa n, media y ceros por pregunta. No se mide aprendizaje ni salud mental.'),
        ])
        nombres={'horas_ia_dia':'Horas IA / día','semestre_inicio':'Inicio (semestre)',
                 'total_herramientas':'Herramientas','edad':'Edad observada',
                 'traslado_min':'Traslado (min)','score_beneficio_ia':'Polaridad IA','score_bienestar':'Polaridad entorno'}
        tabla=[['Variable','n','Media','DE','Mediana','Mín.','Máx.']]
        for var in nombres:
            d=filas[var]
            tabla.append([nombres[var],d['n'],f'{d["media"]:.2f}',f'{d["sd"]:.2f}',f'{d["mediana"]:.2f}',f'{d["min"]:.2f}',f'{d["max"]:.2f}'])
        paginas.append([
            self.h('ANÁLISIS EXPLORATORIO UNIVARIADO'),self.tabla(tabla,[155,35,66,66,66,66,66]),
            Spacer(1,12),self.img('uso_modalidad',maxalto=245),
            self.p(f'La mediana de uso es {k["mediana_ia_h"]:.2f} h/día. La diversidad de herramientas, una vez normalizados los alias, tiene media {filas["total_herramientas"]["media"]:.2f}; {k["multiherramienta_n"]} de {m["ia"]} participantes mencionan al menos dos plataformas.'),
            self.p(f'El uso híbrido explícito representa {k["hibrido_pct"]:.1f}%. Guía e híbrido suman {k["guia_hibrido_pct"]:.1f}%. Las respuestas contextuales y no clasificables se conservan en el denominador total y no se fuerzan a una modalidad.'),
            self.nota('DE = desviación estándar muestral. Edad, traslado y polaridad del entorno se describen sobre observaciones reales; no sobre valores imputados. El valor extremo de traslado se conserva como respuesta, sin asumir que corresponde a un solo trayecto.'),
        ])
        paginas.append([
            self.h('ASOCIACIONES Y CRUCE DE ENCUESTAS'),
            self.p(f'El cruce directo utiliza {rho["n"]} participantes con respuesta en ambos cuestionarios. Para traslado y horas de IA se obtuvo rho de Spearman = {rho["rho"]:.3f}, con p = {rho["p"]:.3f}.'),
            self.p('Este resultado no aporta evidencia suficiente de asociación monotónica en la muestra. No demuestra ausencia de relación, causalidad ni un papel moderador del transporte. Las correlaciones adicionales son exploratorias y no están ajustadas por comparaciones múltiples.'),
            self.img('correlacion',maxalto=330),
            self.sub('ALCANCE DE LA INTERPRETACIÓN'),
            self.p('Las respuestas describen percepciones en un único momento. La selección de participantes, el tamaño reducido y el posible sesgo de autoinforme limitan la generalización a la carrera. La presencia de valores extremos puede alterar tanto correlaciones como agrupaciones.'),
        ])
        paginas.append([
            self.h('CLUSTERING Y PROYECCIÓN PCA'),
            self.p(f'Se agruparon {c["n"]} registros observados, sin imputar bienestar. Se estandarizaron horas de IA, semestre de inicio, diversidad de herramientas, traslado y los dos indicadores léxicos. Entre k=2..5, K-Means obtuvo su mejor silhouette con k={c["k"]}: {c["silhouette"]:.3f}.'),
            self.img('clusters',maxalto=225),
            self.p(f'El clustering jerárquico con el mismo k obtuvo {c["silhouette_jerarquico"]:.3f}. Los dos primeros componentes PCA explican {100*sum(c["pca_varianza"]):.2f}% de la varianza: PC1 {100*c["pca_varianza"][0]:.2f}% y PC2 {100*c["pca_varianza"][1]:.2f}%.'),
            self.sub('GRUPOS PEQUEÑOS Y ESTABILIDAD'),
            self.p('El máximo se eligió únicamente entre los valores de k ensayados. Un silhouette moderado y la presencia de grupos muy pequeños no acreditan arquetipos estables. Los grupos con menos de tres integrantes no se describen individualmente ni se vinculan con diagnósticos o intervenciones personales.'),
            self.p('Los cinco perfiles del informe anterior no se mantienen: procedían de otra preparación de variables y de bienestar imputado o neutralizado. Las agrupaciones actuales se presentan como exploración de estructura, no como perfiles institucionales confirmados.'),
        ])
        cv=[['Clasificador','Accuracy CV','DE','F1 CV','DE']]
        cv.extend([[x['modelo'],f'{x["cv_accuracy"]:.3f}',f'{x["cv_accuracy_sd"]:.3f}',f'{x["cv_f1"]:.3f}',f'{x["cv_f1_sd"]:.3f}'] for x in s['cv']])
        paginas.append([
            self.h('CLASIFICACIÓN SUPERVISADA Y VALIDACIÓN'),
            self.p(f'Objetivo: {s["objetivo"]} Se etiquetaron {s["n_etiquetados"]} respuestas ({s["clases"]["mixta"]} mixtas y {s["clases"]["exclusiva"]} exclusivas); {s["n_excluidos"]} ambiguas o no clasificables se excluyeron.'),
            self.p('La pregunta de modalidad no se incluye en los predictores. Se combinan siete variables estructuradas con TF-IDF de otras preguntas, reducido a un máximo de cuatro componentes PCA según disponibilidad. Un vocabulario vacío aporta ceros. Cada fold ajusta escala, imputación, vocabulario y PCA.'),
            self.p(f'Se reservan {s["n_test"]} casos para prueba. La validación cruzada estratificada de {s["n_folds"]} folds se aplica solo a los {s["n_train"]} casos de entrenamiento. Se compara contra la estrategia de predecir siempre la clase mayoritaria.'),
            self.tabla(cv,[180,85,85,85,85]),Spacer(1,10),
            self.img('modelos_cv',maxalto=205),
            self.nota('DE expresa dispersión entre folds, no un intervalo de confianza. La clase positiva es modalidad mixta. No se evaluaron diagnósticos ni notas académicas.'),
        ])
        t=s['test'];b=s['baseline_test']
        mensaje=('El candidato supera el F1 medio del baseline en esta CV, sin acreditar significación ni generalización.' if s['supera_baseline_cv'] else 'El candidato no supera el F1 medio del baseline en validación cruzada. No se acredita ventaja predictiva para uso operativo.')
        paginas.append([
            self.h('PRUEBA RESERVADA, LÍMITES Y CONCLUSIONES'),
            self.p(f'Entre los cuatro modelos entrenables, se seleccionó {s["seleccionado"]} por F1 medio de CV, sin consultar la prueba. {mensaje}'),
            self.tabla([
                ['Evaluación sobre prueba','Accuracy','Precisión','Recall','F1'],
                [s['seleccionado'],f'{t["accuracy"]:.3f}',f'{t["precision"]:.3f}',f'{t["recall"]:.3f}',f'{t["f1"]:.3f}'],
                ['Baseline (mayoría)',f'{b["accuracy"]:.3f}',f'{b["precision"]:.3f}',f'{b["recall"]:.3f}',f'{b["f1"]:.3f}'],
            ],[180,85,85,85,85]),Spacer(1,8),self.img('confusion',ancho=350,maxalto=190),
            self.p(f'Con n={s["n_test"]} en prueba, un acierto cambia accuracy en {s["test_sensible_pp"]:.1f} puntos porcentuales. El resultado puntual no corrige la inestabilidad observada entre folds.'),
            self.sub('CONCLUSIONES Y REPRODUCIBILIDAD'),
            self.p('La integración y el análisis descriptivo son reproducibles. Los indicadores textuales y los clusters siguen siendo exploratorios. Se necesita una muestra mayor y una medición independiente del resultado académico para estudiar rendimiento o dependencia; este experimento no permite afirmarlos.'),
            self.nota('Fuente de cifras: resultados/resumen.json, versión de metodología '+r['metodologia']['version']+'. Fecha de ejecución: '+r['proveniencia']['fecha'][:10]+'. Dependencias fijadas en requirements.txt; pruebas de regresión y ejecución del notebook documentadas en README. No se modificaron las encuestas originales.'),
        ])
        return paginas

    def negocio(self):
        r=self.r;m=r['muestra'];k=r['kpis'];c=r['clusters'];s=r['supervisado']
        n=m['ia'];nb=m['emparejados'];tipos=r['tipo_uso'];rep=r['reemplazo']
        cv={x['modelo']:x for x in s['cv']}
        p=[]
        p.append([
            self.h('CONTEXTO DE NEGOCIO Y KPIs'),
            self.p('<b>Diagnóstico exploratorio sobre adopción de IA y entorno estudiantil en MAC.</b><br/>Destinatarios: coordinación de la licenciatura y profesora de Sistemas Inteligentes.'),
            self.p(f'El estudio resume {n} respuestas sobre IA y {nb} respuestas emparejadas de entorno. Permite orientar conversaciones y pilotos de apoyo académico. No mide causalmente el rendimiento, ni diagnostica dependencia o salud emocional.'),
            self.sub('CUADRO DE MANDO: ADOPCIÓN Y MODALIDAD'),
            self.tabla([
                ['Indicador','Valor observado','Referencia propuesta','Lectura'],
                ['Adopción observada',f'{k["adopcion_observada_pct"]:.1f}% ({k["adopcion_observada_n"]}/{n})','Descriptiva','Menciones de herramientas reconocidas en las respuestas; no representa a toda la carrera ni acredita uso ético.'],
                ['Consumo mediano',f'{k["mediana_ia_h"]:.2f} h/día','Sin umbral validado','Intensidad declarada; no se etiqueta como saludable o excesiva solo por la mediana.'],
                ['Guía o modalidad mixta',f'{k["guia_hibrido_pct"]:.1f}% ({tipos.get("Guía",0)+tipos.get("Híbrido",0)}/{n})','>=90%: meta de piloto',f'Estado: {estado_meta(k["guia_hibrido_pct"],90)}. Referencia propuesta; no equivale a calidad pedagógica demostrada.'],
                ['Diversidad (>=2 herramientas)',f'{k["multiherramienta_pct"]:.1f}% ({k["multiherramienta_n"]}/{n})','>=60%: meta de piloto',f'Estado: {estado_meta(k["multiherramienta_pct"],60)}. Usar más plataformas no garantiza aprender mejor.'],
            ],[124,93,118,185]),Spacer(1,12),
            self.nota('Las metas son propuestas de seguimiento y no políticas institucionales aprobadas. Los denominadores siempre corresponden a respuestas disponibles. Se retira el antiguo indicador de vulnerabilidad por dependencia por falta de una medida validada.'),
        ])
        p.append([
            self.h('KPIs DE CONTEXTO Y VISIÓN PROFESIONAL'),
            self.tabla([
                ['Indicador','Valor observado','Interpretación y uso propuesto'],
                ['Modalidad mixta explícita',f'{k["hibrido_pct"]:.1f}% ({tipos.get("Híbrido",0)}/{n})','Describe combinación de guía y agilización. Las respuestas “depende” sin explicación no se fuerzan a esta categoría.'],
                ['Traslado mediano',f'{k["traslado_mediana_min"]:.0f} min (n={nb})',f'{k["traslado_mayor_90_n"]}/{nb} respuestas superan 90 min. Verificar necesidad de apoyo, sin inferir causalidad sobre aprovechamiento.'],
                ['Reemplazo laboral: Sí',f'{k["reemplazo_si_pct"]:.1f}% ({rep.get("Sí",0)}/{n})',f'Separado de respuestas parciales/depende ({rep.get("Parcial / Depende",0)}) e indecisas ({rep.get("Indeciso",0)}). No equivale a una predicción del mercado laboral.'],
                ['Cobertura de entorno',f'{100*nb/n:.1f}% ({nb}/{n})',f'{m["solo_ia"]} participantes sin segunda encuesta. No se les asigna bienestar neutral.'],
            ],[140,110,270]),Spacer(1,12),self.img('herramientas',maxalto=240),
            self.nota('Las menciones de herramientas no son excluyentes. Se normalizaron variantes ortográficas antes de contar. No se interpretan los porcentajes como estimaciones representativas de toda la generación.'),
        ])
        p.append([
            self.h('SEGMENTACIÓN EXPLORATORIA'),
            self.p(f'K-Means se aplicó a {c["n"]} participantes con entorno observado. Entre k=2..5, la mejor puntuación ensayada fue k={c["k"]}, con silhouette {c["silhouette"]:.3f}. Los grupos tienen tamaños '+', '.join(str(x) for x in c['tamanos'].values())+'.'),
            self.img('clusters',maxalto=240),
            self.sub('LO QUE PERMITE ESTA EXPLORACIÓN'),
            self.p('Las agrupaciones muestran que algunos casos extremos pueden dominar la separación. No respaldan cinco perfiles institucionales estables ni categorías como “escépticos con desgaste emocional”. Los subgrupos con menos de tres personas no se describen individualmente.'),
            self.tabla([
                ['Uso apropiado','Uso que requiere más evidencia'],
                ['Identificar preguntas para futuras encuestas y revisar sensibilidad a extremos.','Asignar tutorías, beneficios o restricciones a una persona según su cluster.'],
                ['Explorar variación de hábitos dentro de esta muestra.','Atribuir dependencia, burnout o bajo rendimiento a una agrupación.'],
                ['Volver a medir con una muestra mayor y criterios observables.','Generalizar tamaños y perfiles a toda la carrera.'],
            ],[260,260]),
            self.nota('La segmentación se ofrece como material descriptivo. No constituye un mecanismo de selección de estudiantes ni reemplaza una evaluación individual consentida.'),
        ])
        inicio=r['semestre_inicio'];inicio34=inicio.get('3',0)+inicio.get('4',0)
        p.append([
            self.h('PLAN DE ACCIÓN Y SEGUIMIENTO'),
            self.p('Las siguientes iniciativas se proponen como pilotos. Su justificación combina las percepciones recogidas y objetivos pedagógicos; no son intervenciones cuya eficacia haya sido demostrada por este estudio.'),
            self.tabla([
                ['Iniciativa propuesta','Fundamento en la muestra','Cómo verificar el piloto'],
                ['Formación en verificación de IA',f'{inicio34}/{n} respuestas sitúan el inicio entre 3.º y 4.º semestre.','Aplicar ejercicios equivalentes antes/después y evaluar explicación, fuentes y detección de errores.'],
                ['Evaluación del proceso','Guía y uso mixto predominan entre las modalidades declaradas.','Usar rúbricas de comprensión, pruebas de depuración y defensa del procedimiento, además del producto final.'],
                ['Recursos académicos flexibles',f'{k["traslado_mayor_90_n"]}/{nb} respuestas reportan más de 90 min de traslado.','Ofrecer materiales asíncronos y preguntar directamente por barreras y utilidad del apoyo.'],
                ['Orientación profesional','Existen percepciones de reemplazo total, parcial e incertidumbre.','Comparar comprensión de tareas automatizables y competencias de supervisión antes/después de un taller.'],
                ['Mejorar la recolección',f'La cohorte es pequeña y {m["solo_ia"]} personas carecen de encuesta complementaria.','Repetir el instrumento, registrar cobertura y reunir un resultado académico independiente con consentimiento.'],
            ],[128,180,212]),Spacer(1,14),
            self.sub('REGLAS PARA EL DASHBOARD FUTURO'),
            self.p('Mostrar tamaño de muestra y denominador en cada KPI; separar medición observada de imputación; usar las mismas fórmulas del análisis; omitir identificadores y perfiles pequeños; presentar las limitaciones junto a las métricas. Las metas deben etiquetarse como propuestas hasta su aprobación institucional.'),
        ])
        mejor=cv[s['seleccionado']];base=cv['Baseline (mayoría)']
        p.append([
            self.h('RESULTADO PREDICTIVO Y CONCLUSIONES'),
            self.p(f'La clasificación distingue uso mixto frente a uso exclusivo declarado, no aprendizaje efectivo. Se utilizaron {s["n_etiquetados"]} respuestas etiquetables; {s["n_excluidos"]} ambiguas se excluyeron. El conjunto de prueba tiene solo {s["n_test"]} casos.'),
            self.img('modelos_cv',maxalto=220),
            self.p(f'Entre los cuatro clasificadores, {s["seleccionado"]} obtuvo F1 medio de CV {mejor["cv_f1"]:.3f}, frente a {base["cv_f1"]:.3f} del baseline mayoritario. '+('Esta ventaja puntual necesita confirmación independiente.' if s['supera_baseline_cv'] else 'No se observó ventaja por F1 frente al baseline; el modelo no se recomienda para decisiones sobre estudiantes.')),
            self.p(f'El accuracy de prueba del candidato fue {100*s["test"]["accuracy"]:.1f}%, pero una sola predicción cambia ese porcentaje en {s["test_sensible_pp"]:.1f} puntos. No es una tasa demostrada de predicción del desempeño académico.'),
            self.sub('CONCLUSIÓN PARA LA TOMA DE DECISIONES'),
            self.p('El aporte actual es un diagnóstico descriptivo reproducible de las respuestas: adopción, modalidades y contexto. Conviene priorizar formación en verificación, mejorar la recolección y evaluar pilotos con criterios independientes. No se justifica diagnosticar dependencia, atribuir efectos causales al transporte ni mantener los cinco perfiles anteriores.'),
            self.nota('Cifras generadas desde resultados/resumen.json, metodología '+r['metodologia']['version']+', ejecución '+r['proveniencia']['fecha'][:10]+'. Los originales se conservan. El dashboard queda como siguiente etapa, después de estas correcciones.'),
        ])
        return p


def construir(paginas,portada:Path,destino:Path,r:dict,titulo:str):
    if not portada.is_file():
        raise FileNotFoundError('Falta el PDF de referencia para conservar su portada.')
    cuerpo=io.BytesIO()
    doc=SimpleDocTemplate(cuerpo,pagesize=(612,792),leftMargin=46,rightMargin=46,
                          topMargin=42,bottomMargin=53,title=titulo)
    fecha=r['proveniencia']['fecha'][:10]
    def pie(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(AZUL);canvas.setLineWidth(.6)
        canvas.line(46,43,566,43);canvas.setFont('Proyecto',8)
        canvas.setFillColor(colors.HexColor('#555555'))
        canvas.drawString(46,30,f'Versión corregida | {fecha} | Sistemas Inteligentes')
        canvas.drawRightString(566,30,str(doc.page+1));canvas.restoreState()
    story=[]
    for i,pagina in enumerate(paginas):
        if i:story.append(PageBreak())
        story.extend(pagina)
    doc.build(story,onFirstPage=pie,onLaterPages=pie)
    writer=PdfWriter()
    writer.append(PdfReader(portada),pages=(0,1))
    writer.append(PdfReader(cuerpo))
    writer.add_metadata({'/Title':titulo,'/Subject':'Versión corregida: resultados agregados reproducibles',
                         '/Author':'Proyecto Sistemas Inteligentes - MAC'})
    destino.parent.mkdir(parents=True,exist_ok=True)
    with destino.open('wb') as f:writer.write(f)


def main():
    root=Path(__file__).parent
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resultados',type=Path,default=root/'resultados')
    p.add_argument('--referencias',type=Path,default=root/'docs'/'originales')
    p.add_argument('--out',type=Path,default=root/'docs'/'actualizados')
    args=p.parse_args()
    r=json.loads((args.resultados/'resumen.json').read_text(encoding='utf-8'))
    if r['supervisado']['estado']!='ok' or r['clusters']['estado']!='ok':
        p.error('El informe requiere resultados completos; revise las limitaciones de muestra.')
    informe=Informe(r,args.resultados/'figuras')
    construir(informe.tecnica(),args.referencias/'DOCUMENTACION TECNICA SI_C.pdf',
              args.out/'DOCUMENTACION_TECNICA_SI_C_CORREGIDA.pdf',r,'Documentación técnica corregida')
    construir(informe.negocio(),args.referencias/'DOCUMENTACIÓN NEGOCIO SI_C.pdf',
              args.out/'DOCUMENTACION_NEGOCIO_SI_C_CORREGIDA.pdf',r,'Documentación de negocio corregida')
    print('Se generaron dos PDF nuevos con las portadas originales.')


if __name__=='__main__':main()
