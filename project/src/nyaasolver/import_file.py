import pandas as pd
from importlib.resources import files

def import_file():
    file_path = files('nyaasolver.files').joinpath('Dataton 2023 Etapa 1.xlsx')
    demand_data = pd.read_excel(file_path, sheet_name="demand")
    worker_data = pd.read_excel(file_path, sheet_name="workers")
    sucursales = pd.unique(demand_data["suc_cod"])
    demand_separated = demand_data.groupby(demand_data.suc_cod)
    demand = []
    for i in sucursales:
        demandS1 = demand_separated.get_group(i)
        demandS1Separated = demandS1.groupby(demandS1["fecha_hora"].dt.dayofweek)
        demandS1 = [demandS1Separated.get_group(j)["demanda"] for j in range(1)]
        demand.append(demandS1)
    return demand


def import_file_etapa2():
    file_path = files('nyaasolver.files').joinpath('Dataton 2023 Etapa 2.xlsx')
    xl = pd.ExcelFile(file_path)
    demand_data = xl.parse(sheet_name="demand")
    worker_data = xl.parse(sheet_name="workers")
    branch_info = {}
    for _, worker in worker_data.iterrows():
        branch_code = worker["suc_cod"]
        document = worker["documento"]
        contract_type = worker["contrato"]
        if branch_code not in branch_info:
            branch_info[branch_code] = {"TC": [], "MT": [], "days": {}, "demands": []}
        branch_info[branch_code][contract_type].append(document)

    for _, demand in demand_data.iterrows():
        branch_code = demand["suc_cod"]
        demand_entry = demand["demanda"]
        date = str(demand["fecha_hora"]).split()[0]
        if branch_code in branch_info:
            branch_info[branch_code]["demands"].append(demand_entry)
            if branch_info[branch_code]["days"].get(date) == None:
                branch_info[branch_code]["days"][date] = [demand["demanda"]]
            else:
                branch_info[branch_code]["days"][date].append(demand["demanda"])
    return branch_info
