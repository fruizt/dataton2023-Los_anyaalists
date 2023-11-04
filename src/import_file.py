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

def import_file_etapa2():
    file_path = r"C:\Repos\dataton2023-Los_anyaalists\src\files\Dataton 2023 Etapa 2.xlsx"
    xl = pd.ExcelFile(file_path)
    demand_data = xl.parse(sheet_name='demand')
    workers_data = xl.parse(sheet_name='workers')
    branch_info = {}
    for _, worker in workers_data.iterrows():
        branch_code = worker['suc_cod']
        document = worker['documento']
        contract_type = worker['contrato']
        if branch_code not in branch_info:
            branch_info[branch_code] = {'TC': [], 'MT': [], 'days': {}, 'demands': []}
        branch_info[branch_code][contract_type].append(document)

    for _, demand in demand_data.iterrows():
        branch_code = demand['suc_cod']
        demand_entry = demand['demanda']
        date = str(demand['fecha_hora']).split()[0]
        if branch_code in branch_info:
            branch_info[branch_code]['demands'].append(demand_entry)
            if  branch_info[branch_code]['days'].get(date) == None:
                branch_info[branch_code]['days'][date] = [demand['demanda']]
            else:
                branch_info[branch_code]['days'][date].append(demand['demanda'])
    return branch_info

print(import_file_etapa2())
