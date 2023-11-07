import nyaasolver.etapa2.etapa2_week as etapa2_week
import nyaasolver.etapa2.etapa2_sat as etapa2_sat
import nyaasolver.import_file as import_file

def solve_optimization():
    demand_workers = import_file.import_file_etapa2()
    objective_function = 0
    for sucursal in demand_workers:
        sucursal_week_solution = etapa2_week.solve_week_optimization(demand_workers[sucursal], sucursal)
        sucursal_saturday_solution = etapa2_sat.solve_saturday_optimization(demand_workers[sucursal], sucursal)
        objective_function += sucursal_week_solution["objective_function_result"] + sucursal_saturday_solution["objective_function_result"]
        objective_function += sucursal_saturday_solution["objective_function_result"]
    print(">> only saturday opt:", objective_function)


