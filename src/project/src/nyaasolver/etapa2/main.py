# import nyaasolver.etapa2.etapa2_week as etapa2_week
import nyaasolver.etapa2.etapa2_sat as etapa2_sat
import nyaasolver.import_file as import_file

def solve_optimization():
    demand_workers = import_file.import_file_etapa2()
    objective_function = 0
    for key in demand_workers.keys():
        value = demand_workers.get(key)
        objective_function += etapa2_sat.solve_saturday_optimization(value).objective.value()
    print(objective_function)
    # etapa2_week.solve(demand_workers)
    # etapa2_sat.solve(demand_workers)
