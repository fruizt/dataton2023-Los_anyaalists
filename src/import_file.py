import pandas as pd

def import_file():
    route="/mnt/d/Repos/dataton/dataton2023-Los_anyaalists/src/files/Dataton 2023 Etapa 1.xlsx"
    demandData=pd.read_excel(route,sheet_name="demand")
    workerData=pd.read_excel(route,sheet_name="workers")
    Sucursales=pd.unique(demandData['suc_cod'])
    demandSeparated=demandData.groupby(demandData.suc_cod)
    #Vector de demanda. 1 coordenada es la sucursal, 2 coordenada el  dia, 3 coordenada la franja
    demand=[]
    for i in Sucursales:
        demandS1=demandSeparated.get_group(i)
        demandS1Separated=demandS1.groupby(demandS1['fecha_hora'].dt.dayofweek)
        demandS1=[demandS1Separated.get_group(j)['demanda'] for j in range(1)]
        demand.append(demandS1)
    return demand



