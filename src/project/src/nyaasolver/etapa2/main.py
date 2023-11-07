import nyaasolver.etapa2.etapa2_week as etapa2_week
import nyaasolver.etapa2.etapa2_sat as etapa2_sat
import nyaasolver.import_file as import_file

def solve_optimization():
    demand_workers = import_file.import_file_etapa2()
    objective_function = 0
    week_solution = []
    saturday_solution = []
    matrix = []
    for sucursal in demand_workers:
        # sucursal_week_solution = etapa2_week.solve_week_optimization(demand_workers[834])
        sucursal_saturday_solution = etapa2_week.solve_week_optimization(demand_workers[834])
        # objective_function += sucursal_week_solution["objective_function_result"] + sucursal_saturday_solution["objective_function_result"]
        objective_function += sucursal_saturday_solution["objective_function_result"]
        # week_solution.append(sucursal_week_solution["solution"])
        saturday_solution.append(sucursal_saturday_solution["solution"])
        # objective_function += etapa2_sat.solve_saturday_optimization(demand_workers[sucursal])
    print(">> only saturday opt:", objective_function)
    build_solve_csv(demand_workers, week_solution, saturday_solution)

def build_solve_csv(demand_workers, week_solution, saturday_solution):
    """Build and solve the optimization problem."""
    print(">> Building and solving the optimization problem...")
    print(">> demand_workers:", demand_workers)
    print(">> week_solution:", week_solution)
    print(">> saturday_solution:", saturday_solution)