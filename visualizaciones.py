"""Figuras agregadas para notebook y documentos. Sin identificadores personales."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud

AZUL='#2b5c8f'
VERDE='#1f9e89'
MORADO='#675583'


def generar_figuras(resultado, destino: Path) -> None:
    destino.mkdir(parents=True,exist_ok=True)
    r,df=resultado.resumen,resultado.datos
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
                         'axes.spines.top':False,'axes.spines.right':False,
                         'axes.titleweight':'bold','figure.facecolor':'white'})

    def guardar(fig,nombre):
        fig.tight_layout(pad=1.2)
        fig.savefig(destino/f'{nombre}.png',dpi=180,bbox_inches='tight',facecolor='white')
        plt.close(fig)

    herramientas=pd.Series(r['herramientas']).sort_values()
    herramientas=herramientas[herramientas>0]
    fig,ax=plt.subplots(figsize=(7,3.2))
    ax.barh(herramientas.index.str.upper(),herramientas.values,color=AZUL)
    for i,n in enumerate(herramientas):ax.text(n+.15,i,f'{n} ({100*n/len(df):.1f}%)',va='center',fontsize=8)
    ax.set_xlim(0,max(herramientas)+5)
    ax.set_xlabel(f'Respuestas que mencionan cada herramienta (n={len(df)})')
    ax.set_title('Adopción de herramientas de IA; menciones no excluyentes')
    guardar(fig,'herramientas')

    fig,axes=plt.subplots(1,2,figsize=(8,3.1))
    axes[0].hist(df['horas_ia_dia'].dropna(),bins=8,color=AZUL,edgecolor='white')
    axes[0].axvline(r['kpis']['mediana_ia_h'],color=MORADO,ls='--',label=f'Mediana {r["kpis"]["mediana_ia_h"]:.2f} h')
    axes[0].set(xlabel='Horas/día',ylabel='Respuestas',title=f'Intensidad de uso (n={len(df)})')
    axes[0].legend(fontsize=8)
    tipos=pd.Series(r['tipo_uso'])
    axes[1].barh(tipos.index,tipos,color=VERDE)
    for i,n in enumerate(tipos):axes[1].text(n+.15,i,str(n),va='center')
    axes[1].set_xlim(0,max(tipos)+2)
    axes[1].set(xlabel='Respuestas',title='Modalidad declarada')
    guardar(fig,'uso_modalidad')

    corr=pd.DataFrame(r['correlacion_spearman'])
    labels=['Horas IA','Inicio','Herramientas','Traslado','Polaridad IA','Polaridad entorno','Edad']
    fig,ax=plt.subplots(figsize=(7,4.4))
    im=ax.imshow(corr.to_numpy(),cmap='RdBu_r',vmin=-1,vmax=1)
    ax.set_xticks(range(len(labels)),labels,rotation=35,ha='right',fontsize=8)
    ax.set_yticks(range(len(labels)),labels,fontsize=8)
    for (i,j),x in np.ndenumerate(corr.to_numpy()):
        ax.text(j,i,f'{x:.2f}',ha='center',va='center',fontsize=8,color='white' if abs(x)>.65 else 'black')
    fig.colorbar(im,ax=ax,shrink=.8)
    ax.set_title(f'Correlación de Spearman: solo encuestas emparejadas (n={r["muestra"]["emparejados"]})')
    guardar(fig,'correlacion')

    fig,ax=plt.subplots(figsize=(7,2.6))
    wc=WordCloud(width=1100,height=380,background_color='white',colormap='viridis',random_state=42)
    if r['tfidf_top']:
        wc.generate_from_frequencies(r['tfidf_top'])
        ax.imshow(wc,interpolation='bilinear')
    else:
        ax.text(.5,.5,'Sin vocabulario descriptivo disponible',ha='center',va='center')
    ax.axis('off')
    ax.set_title('Términos destacados por TF-IDF; resumen descriptivo de respuestas')
    guardar(fig,'nlp')

    c=r['clusters']
    if c['estado']=='ok':
        fig,axes=plt.subplots(1,2,figsize=(8,3))
        ks=[int(k) for k in c['siluetas']]
        axes[0].plot(ks,list(c['siluetas'].values()),marker='o',color=AZUL)
        axes[0].set(xticks=ks,xlabel='Número de grupos ensayado',ylabel='Silhouette',title='Selección exploratoria de k')
        tamanos={f'Grupo {k}':n for k,n in c['tamanos'].items() if n>=3}
        menores=sum(n for n in c['tamanos'].values() if n<3)
        if menores:tamanos['Grupos pequeños\n(perfiles omitidos)']=menores
        axes[1].bar(list(tamanos),list(tamanos.values()),color=VERDE)
        axes[1].set(title=f'Participantes agrupados (n={c["n"]})',ylabel='Participantes')
        guardar(fig,'clusters')

    s=r['supervisado']
    if s['estado']=='ok':
        tabla=pd.DataFrame(s['cv']).sort_values('cv_f1')
        fig,ax=plt.subplots(figsize=(7,3.2))
        colores=[MORADO if 'Baseline' in m else AZUL for m in tabla['modelo']]
        ax.barh(tabla['modelo'],tabla['cv_f1'],color=colores)
        ax.errorbar(tabla['cv_f1'],range(len(tabla)),xerr=tabla['cv_f1_sd'],fmt='none',color='black',capsize=3)
        ax.set_xlim(-.03,1.08)
        ax.set(xlabel='F1 medio ± desviación entre folds',title=f'Validación solo en entrenamiento (n={s["n_train"]}, {s["n_folds"]} folds)')
        guardar(fig,'modelos_cv')
        fig,ax=plt.subplots(figsize=(5,3.1))
        cm=np.asarray(s['test']['confusion'])
        ax.imshow(cm,cmap='Blues',vmin=0)
        for (i,j),x in np.ndenumerate(cm):ax.text(j,i,str(x),ha='center',va='center',fontsize=15)
        ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['Exclusiva','Mixta'],yticklabels=['Exclusiva','Mixta'],
               xlabel='Predicción',ylabel='Modalidad declarada',title=f'{s["seleccionado"]}: prueba reservada (n={s["n_test"]})')
        guardar(fig,'confusion')

    g=r.get('regresion',{})
    if g.get('estado')=='ok':
        fig,axes=plt.subplots(1,2,figsize=(8,3.1))
        nombres=['Lineal','Promedio']
        valores=[m['prueba'] for m in g['modelos']]
        for ax,clave,titulo,unidad in [(axes[0],'r2','R² en prueba reservada','R² (mayor es mejor)'),
                                       (axes[1],'mae_h','Error absoluto medio','Horas (menor es mejor)')]:
            ys=[m[clave] for m in valores]
            if any(v is None for v in ys):
                ax.text(.5,.5,'R² no definido: horas constantes',ha='center',va='center',transform=ax.transAxes)
                continue
            ax.bar(nombres,ys,color=[AZUL,MORADO],width=.55)
            ax.axhline(0,color='#667788',linewidth=.8)
            for i,v in enumerate(ys):ax.annotate(f'{v:.3f}',(i,v),xytext=(0,6 if v>=0 else -13),textcoords='offset points',ha='center',fontsize=9)
            ax.margins(y=.3)
            ax.set(title=titulo,ylabel=unidad)
        fig.suptitle(f'Estimación de horas de IA: {g["n_train"]} casos de entrenamiento y {g["n_test"]} de prueba',fontsize=10)
        guardar(fig,'regresion')
