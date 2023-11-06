from src.print_schedules import print_3d_schedule
from src.import_file import import_file_etapa2
import pulp

# Solver configuration
solver = pulp.getSolver('PULP_CBC_CMD', threads=16, timeLimit=400 ,gapRel=0.01)

# Import demand and workers data
demand_workers = import_file_etapa2()

# Define the length of the schedule, for example, an 8-hour workday has 32 blocks
WORKERS =demand_workers[834]["TC"] + demand_workers[834]["MT"]

DEMAND_DICTIONARY = demand_workers[834]["days"]
DEMAND_ARRAY = demand_workers[834]["demands"]

def is_full_time_worker(worker):
    try:
        demand_workers[834]["TC"].index(worker)
        return True
    except:
        return False

EMPLOYEES = len(demand_workers[834]["TC"]) + len(demand_workers[834]["MT"])
DAYS = 5 #len(demand_workers[834]["days"])
SCHEDULE = 49

# Define the LP problem
prob = pulp.LpProblem("Minimize_PD", pulp.LpMinimize)

# Decision variables
x = pulp.LpVariable.dicts("Block", [(x, y, z) for x in range(DAYS) for y in range(EMPLOYEES) for z in range(SCHEDULE)], 0, 3, cat=pulp.LpInteger)
pd = pulp.LpVariable.dicts("Positive Difference", [(x, z) for x in range(DAYS) for z in range(SCHEDULE)], lowBound=0, cat=pulp.LpInteger)

# Channels
n = pulp.LpVariable.dicts("Nothing", [(x, y, z) for x in range(DAYS) for y in range(EMPLOYEES) for z in range(SCHEDULE)], cat=pulp.LpBinary)  # 1 for not working, 0 otherwise
w = pulp.LpVariable.dicts("Work", [(x, y, z) for x in range(DAYS) for y in range(EMPLOYEES) for z in range(SCHEDULE)], cat=pulp.LpBinary)  # 1 for working, 0 otherwise
b = pulp.LpVariable.dicts("Break", [(x, y, z) for x in range(DAYS) for y in range(EMPLOYEES) for z in range(SCHEDULE)], cat=pulp.LpBinary)  # 1 for active pause, 0 otherwise
l = pulp.LpVariable.dicts("Lunch", [(x, y, z) for x in range(DAYS) for y in range(EMPLOYEES) for z in range(SCHEDULE)], cat=pulp.LpBinary)  # 1 for lunch, 0 otherwise

# Status
a = pulp.LpVariable.dicts("Active", [(y, z) for y in range(EMPLOYEES) for z in range(SCHEDULE)], cat=pulp.LpBinary)  # 1 for active, 0 otherwise
end_active = pulp.LpVariable.dicts("end_active", [(y, z) for y in range(EMPLOYEES) for z in range(SCHEDULE)], cat=pulp.LpBinary)  # 1 for end of active, 0 otherwise
end_almuerzo = pulp.LpVariable.dicts("end_almuerzo", [(y, z) for y in range(EMPLOYEES) for z in range(SCHEDULE)], cat=pulp.LpBinary)  # 1 for end of lunch, 0 otherwise

# Objective function: Minimize pd.
prob += pulp.lpSum(pd[(x, i)] for x in range(DAYS) for i in range(SCHEDULE))

# Constraints

for d in range(DAYS):

    for i in range(SCHEDULE):
        prob += pd[(d, i)] >= DEMAND_ARRAY[(d * 49) + i] - pulp.lpSum(w[(d, k, i)] for k in range(EMPLOYEES))

    for worker in WORKERS:

        k = WORKERS.index(worker)

        # 1. Los empleados deben trabajar mínimo 1 hora de forma continua para poder
        #    salir a una Pausa Activa o Almuerzo. Esto quiere decir que, si un empleado
        #    solo ha trabajado 3 franjas horarias, en la 4 franja horaria NO debe salir
        #    a Pausa Activa o Almuerzo.

        # (No breaks in the first 4 blocks.)
        prob += pulp.lpSum(b[(d, k, i)] for i in range(4)) == 0

        for i in range(4, SCHEDULE):
            # (Breaks can only occur after at least 4 consecutive work blocks.)
            prob += 4 * b[(d, k, i)] <= pulp.lpSum([w[(d, k, i - j)] for j in range(1, 5)])
            # (Lunch can only begin after at least 4 consecutive work blocks.)
            if is_full_time_worker(worker):
                prob += 4 * l[(d, k, i)] <= pulp.lpSum([w[(d, k, i - j)] + l[(d, k, i - j)] for j in range(1, 5)])

            # (End can only happe+n with at least 4 consecutive work blocks.)
            prob += 4 * end_active[(k, i)] <= pulp.lpSum([w[(d, k, i - j)] for j in range(0, 4)])

            # 2. Los empleados deben trabajar máximo 2 horas de forma continua sin salir a
            #    una pausa activa. Esto quiere decir que, si un empleado ha trabajado 8
            #    franjas horarias, en la 9 franja horaria SÍ debe salir a Pausa Activa o

        for i in range(SCHEDULE - 8):
            # (No more than 8 work blocks in a 9-long segment.)
            prob += pulp.lpSum([w[(d, k, i + j)] for j in range(9)]) <= 8
        

        if is_full_time_worker(worker):
            #    Almuerzo.
            # 3. El tiempo de almuerzo debe tomarse de forma CONTINUA y es de 1 hora y
            #    media. Se debe tomar almuerzo una única vez en el día.

            # (Ensure 6 blocks of lunch.)
            prob += pulp.lpSum([l[(d, k, i)] for i in range(SCHEDULE)]) == 6

            # (Ensure the lunch block is continuous.)
            for i in range(SCHEDULE - 1):
                prob += l[(d, k, i)] <= l[(d, k, i + 1)] + end_almuerzo[(k, i)]
            prob += pulp.lpSum(end_almuerzo[(k, i)] for i in range(SCHEDULE)) == 1

            # 4. La hora mínima de salida para tomar el almuerzo son las 11:30 am y la hora
            #    máxima para salir a tomar el almuerzo es a la 1:30 pm.
            #    Esto quiere decir que:
            #      i. Una persona NO puede salir a tomar almuerzo a las 11:15 am
            #      ii. Una persona NO puede salir a tomar almuerzo a la 1:45 pm
            #      iii. Es VÁLIDO que una persona tome almuerzo de la 1:30 pm a las 3:00

            # (Ensure no lunch outside of valid hours.)
            prob += pulp.lpSum([l[(d, k, i)] for i in range(16)]) == 0
            prob += pulp.lpSum([l[(d, k, i)] for i in range(30, SCHEDULE)]) == 0

            # 5. La jornada laboral de todos los empleados de es 8 horas diarias si es de TC, en otro caso es de 4 horas. Los
            #    estados de Trabaja y Pausa Activa hacen parte de la jornada laboral. El
            #    tiempo de almuerzo NO constituye tiempo de jornada laboral.
            # (Ensure 32 blocks of work or breaks.)
            prob += pulp.lpSum([w[(d, k, i)] + b[(d, k, i)] for i in range(SCHEDULE)]) == 32
        else:
            prob += pulp.lpSum([w[(d, k, i)] + b[(d, k, i)] for i in range(SCHEDULE)]) == 16

            prob += pulp.lpSum([l[(d, k, i)] for i in range(SCHEDULE)]) == 0


        # 6. El horario de los empleados debe ser CONTINUO, desde que comienza la
        #    jornada laboral del empleado este solo puede estar en los estados de
        #    Trabaja, Pausa Activa y Almuerza. Es decir, que el estado Nada solo puede
        #    estar activo al comienzo del día si el empleado no ha comenzado su jornada
        #    laboral o al final del día si el empleado ya completó su jornada laboral.

        # (Define active periods.)
        for i in range(SCHEDULE):
            prob += a[(k, i)] >= w[(d, k, i)]
            prob += a[(k, i)] >= b[(d, k, i)]
            prob += a[(k, i)] >= l[(d, k, i)]
            prob += a[(k, i)] <= w[(d, k, i)] + b[(d, k, i)] + l[(d, k, i)]

        # (Ensure the active block is continuous.)
        for i in range(SCHEDULE - 1):
            prob += a[(k, i)] <= a[(k, i + 1)] + end_active[(k, i)]

        prob += end_active[(k, SCHEDULE - 1)] == a[(k, SCHEDULE - 1)]

        # (Ensure there is only one end block)
        prob += pulp.lpSum(end_active[(k, i)] for i in range(SCHEDULE)) == 1

        # 7. El último estado de la jornada laboral de los empleados debe ser Trabaja.

        # (Work should be 1 when end_active is 1.)
        for i in range(SCHEDULE):
            prob += w[(d, k, i)] >= end_active[(k, i)]

        # 9. Cualquier franja de trabajo debe durar entre 1 y 2 horas.
        # NOOP: Inferred from previous restrictions.

        # Misc

        # Channel Decomposition
        for i in range(SCHEDULE):
            prob += (
                x[(d, k, i)] == n[(d, k, i)] * 0 + w[(d, k, i)] * 1 + b[(d, k, i)] * 2 + l[(d, k, i)] * 3
            )
            prob += n[(d, k, i)] + w[(d, k, i)] + b[(d, k, i)] + l[(d, k, i)] == 1

# 8. Debe haber por lo menos 1 empleado en el estado Trabaja en cada franja
#    horaria.

# (There is at least 1 work block per column.)
    for i in range(SCHEDULE):
        prob += DEMAND_ARRAY[(d * 49) + i] *  pulp.lpSum(w[(d, k, i)] for k in range(EMPLOYEES)) >= DEMAND_ARRAY[(d * 49) + i] 

# Test

# Set the end of the shift.
# prob += end_active[37] == 1

# Set a lunch block.
# prob += l[29] == 1

# Solve the problem

prob.solve(solver)

# Check the solver status
if pulp.LpStatus[prob.status] == "Optimal":
    print("Found an optimal solution!")

    # Display results functions
    print_3d_schedule(x)
    print("\n")
    print("Objective =", pulp.value(prob.objective))
else:
    print_3d_schedule(x)
    print("Could not find an optimal solution.")