import nyaasolver.etapa2.etapa2_week as etapa2_week
import nyaasolver.etapa2.etapa2_sat as etapa2_sat
import nyaasolver.import_file as import_file
import nyaasolver.merge_csv as merge_csv
import pulp

# Solver configuration
path_to_cplex = (r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\cplex\bin\x64_win64\cplex.exe")
solver = pulp.getSolver("CPLEX_CMD", path=path_to_cplex, threads=16, timeLimit=30)

def solve_optimization():
    demand_workers = import_file.import_file_etapa2()
    objective_function = 0
    for sucursal in demand_workers:
        sucursal_week_solution = etapa2_week.solve_week_optimization(demand_workers[sucursal], sucursal, solver)
        sucursal_saturday_solution = etapa2_sat.solve_saturday_optimization(demand_workers[sucursal], sucursal, solver)
        objective_function += sucursal_week_solution["objective_function_result"] + sucursal_saturday_solution["objective_function_result"]
        objective_function += sucursal_saturday_solution["objective_function_result"]
    merge_csv.merge_csv_files()
    print("FINAL SCORE:", objective_function)


