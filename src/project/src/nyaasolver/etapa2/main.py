import nyaasolver.etapa2.etapa2_week as etapa2_week
import nyaasolver.etapa2.etapa2_sat as etapa2_sat
import nyaasolver.import_file as import_file

def solve_optimization():
    demand_workers = import_file.import_file_etapa2()
    objective_function = 0
    for value in demand_workers:
        objective_function += etapa2_week.solve_week_optimization(demand_workers[value])
        objective_function += etapa2_sat.solve_saturday_optimization(demand_workers[value])
    print(">> only saturday opt:", objective_function)

def build_solve_csv():
    """Build and solve the optimization problem."""
