"""Ejecuta el notebook con el Python activo en un kernel temporal y valida salidas."""
import json
import os
from pathlib import Path
import sys
import asyncio
from tempfile import TemporaryDirectory

import nbformat
from nbclient import NotebookClient


def main():
    if os.name=='nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    root=Path(__file__).parent
    path=root/'Analisis_IA_Desempeno_MAC_Cuestionarios.ipynb'
    nb=nbformat.read(path,as_version=4)
    anterior=os.environ.get('JUPYTER_PATH')
    with TemporaryDirectory(prefix='ia-kernel-') as tmp:
        kernel=Path(tmp)/'kernels'/'ia-proyecto'
        kernel.mkdir(parents=True)
        (kernel/'kernel.json').write_text(json.dumps({
            'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
            'display_name':'Python del proyecto','language':'python',
        }),encoding='utf-8')
        os.environ['JUPYTER_PATH']=tmp+(os.pathsep+anterior if anterior else '')
        try:
            NotebookClient(nb,timeout=180,kernel_name='ia-proyecto',
                           resources={'metadata':{'path':str(root)}}).execute()
        finally:
            if anterior is None:os.environ.pop('JUPYTER_PATH',None)
            else:os.environ['JUPYTER_PATH']=anterior
    nb.metadata['kernelspec']={'display_name':'Python 3 (proyecto)','language':'python','name':'python3'}
    if any(o.output_type=='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs):
        raise RuntimeError('El notebook contiene errores de ejecución.')
    # Comprobar los identificadores reales sin mostrarlos ni guardarlos en otro archivo.
    from analisis import cargar_fuentes
    data_dir=Path(os.environ.get('IA_DATA_DIR',str(root/'data'/'private')))
    ia,bie=cargar_fuentes(data_dir)
    serialized=nbformat.writes(nb)
    if any(cuenta in serialized for cuenta in set(ia['cuenta'])|set(bie['cuenta'])):
        raise RuntimeError('Una salida contiene identificadores; no se guardó el notebook.')
    path.write_text(serialized,encoding='utf-8')
    print('Notebook ejecutado sin errores y sin identificadores de participantes.')


if __name__=='__main__':main()
