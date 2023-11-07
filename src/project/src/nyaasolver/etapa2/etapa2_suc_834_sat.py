from nyaasolver.print_schedules import print_2d_schedule
from nyaasolver.import_file import import_file_etapa2
import pulp

# Import demand Data
demand_workers = import_file_etapa2()

# Solver configuration
solver = pulp.getSolver("PULP_CBC_CMD", threads=16, timeLimit=30, gapRel=0.01)

# Define the length of the schedule, for example, an 8-hour workday has 32 blocks
DEMAND_ARRAY = demand_workers[834]["demands"]


def is_full_time_worker(worker):
    try:
        demand_workers[834]["TC"].index(worker)
        return True
    except:
        return False


SCHEDULE = 29
EMPLOYEES = len(demand_workers[834]["TC"]) + len(demand_workers[834]["MT"])

WORKERS = demand_workers[834]["TC"] + demand_workers[834]["MT"]

MAX_WORK_BLOCKS_TC = 20
MAX_WORK_BLOCKS_MT = 16

# Define the LP problem
prob = pulp.LpProblem("Minimize_PD", pulp.LpMinimize)

# Decision variables
x = pulp.LpVariable.dicts(
    "Block",
    [(x, y) for x in range(EMPLOYEES) for y in range(SCHEDULE)],
    0,
    3,
    cat=pulp.LpInteger,
)  # Value from 0 to 3

pd = pulp.LpVariable.dicts(
    "Positive Difference", range(SCHEDULE), lowBound=0, cat=pulp.LpInteger
)

# Channels
n = pulp.LpVariable.dicts(
    "Nothing",
    [(x, y) for x in range(EMPLOYEES) for y in range(SCHEDULE)],
    cat=pulp.LpBinary,
)  # 1 for not working, 0 otherwise
w = pulp.LpVariable.dicts(
    "Work",
    [(x, y) for x in range(EMPLOYEES) for y in range(SCHEDULE)],
    cat=pulp.LpBinary,
)  # 1 for working, 0 otherwise
b = pulp.LpVariable.dicts(
    "Break",
    [(x, y) for x in range(EMPLOYEES) for y in range(SCHEDULE)],
    cat=pulp.LpBinary,
)  # 1 for active pause, 0 otherwise

# Status
a = pulp.LpVariable.dicts(
    "Active",
    [(x, y) for x in range(EMPLOYEES) for y in range(SCHEDULE)],
    cat=pulp.LpBinary,
)  # 1 for active, 0 otherwise
end_active = pulp.LpVariable.dicts(
    "end_active",
    [(x, y) for x in range(EMPLOYEES) for y in range(SCHEDULE)],
    cat=pulp.LpBinary,
)  # 1 for end of active, 0 otherwise
end_almuerzo = pulp.LpVariable.dicts(
    "end_almuerzo",
    [(x, y) for x in range(EMPLOYEES) for y in range(SCHEDULE)],
    cat=pulp.LpBinary,
)  # 1 for end of lunch, 0 otherwise

# Objective function: Minimize pd.
prob += pulp.lpSum(pd[i] for i in range(SCHEDULE))

# Constraints

for i in range(SCHEDULE):
    prob += pd[i] >= DEMAND_ARRAY[(5 * 49) + i] - pulp.lpSum(
        w[(k, i)] for k in range(EMPLOYEES)
    )

for worker in WORKERS:
    k = WORKERS.index(worker)

    # 1. Los empleados deben trabajar mínimo 1 hora de forma continua para poder
    #    salir a una Pausa Activa o Almuerzo. Esto quiere decir que, si un empleado
    #    solo ha trabajado 3 franjas horarias, en la 4 franja horaria NO debe salir
    #    a Pausa Activa o Almuerzo.

    # (No breaks in the first 4 blocks.)
    prob += pulp.lpSum(b[(k, i)] for i in range(4)) == 0

    for i in range(4, SCHEDULE):
        # (Breaks can only occur after at least 4 consecutive work blocks.)
        prob += 4 * b[(k, i)] <= pulp.lpSum([w[(k, i - j)] for j in range(1, 5)])

        # (End can only happen with at least 4 consecutive work blocks.)
        prob += 4 * end_active[(k, i)] <= pulp.lpSum(
            [w[(k, i - j)] for j in range(0, 4)]
        )

    # 2. Los empleados deben trabajar máximo 2 horas de forma continua sin salir a
    #    una pausa activa. Esto quiere decir que, si un empleado ha trabajado 8
    #    franjas horarias, en la 9 franja horaria SÍ debe salir a Pausa Activa o
    #    Almuerzo.

    for i in range(SCHEDULE - 8):
        # (No more than 8 work blocks in a 9-long segment.)
        prob += pulp.lpSum([w[(k, i + j)] for j in range(9)]) <= 8

    # 5. La jornada laboral de todos los empleados de es 8 horas diarias. Los
    #    estados de Trabaja y Pausa Activa hacen parte de la jornada laboral. El
    #    tiempo de almuerzo NO constituye tiempo de jornada laboral.
    # (Ensure 32 blocks of work or breaks.)

    if is_full_time_worker(worker):
        prob += (
            pulp.lpSum([w[(k, i)] + b[(k, i)] for i in range(SCHEDULE)])
            == MAX_WORK_BLOCKS_TC
        )
    else:
        prob += (
            pulp.lpSum([w[(k, i)] + b[(k, i)] for i in range(SCHEDULE)])
            == MAX_WORK_BLOCKS_MT
        )

    # 6. El horario de los empleados debe ser CONTINUO, desde que comienza la
    #    jornada laboral del empleado este solo puede estar en los estados de
    #    Trabaja, Pausa Activa y Almuerza. Es decir, que el estado Nada solo puede
    #    estar activo al comienzo del día si el empleado no ha comenzado su jornada
    #    laboral o al final del día si el empleado ya completó su jornada laboral.

    # (Define active periods.)
    for i in range(SCHEDULE):
        prob += a[(k, i)] >= w[(k, i)]
        prob += a[(k, i)] >= b[(k, i)]
        prob += a[(k, i)] <= w[(k, i)] + b[(k, i)]

    # (Ensure the active block is continuous.)
    for i in range(SCHEDULE - 1):
        prob += a[(k, i)] <= a[(k, i + 1)] + end_active[(k, i)]

    prob += end_active[(k, SCHEDULE - 1)] == a[(k, SCHEDULE - 1)]

    # (Ensure there is only one end block)
    prob += pulp.lpSum(end_active[(k, i)] for i in range(SCHEDULE)) == 1

    # 7. El último estado de la jornada laboral de los empleados debe ser Trabaja.

    # (Work should be 1 when end_active is 1.)
    for i in range(SCHEDULE):
        prob += w[(k, i)] >= end_active[(k, i)]

    # 9. Cualquier franja de trabajo debe durar entre 1 y 2 horas.
    # NOOP: Inferred from previous restrictions.

    # Misc

    # Channel Decomposition
    for i in range(SCHEDULE):
        prob += x[(k, i)] == n[(k, i)] * 0 + w[(k, i)] * 1 + b[(k, i)] * 2
        prob += n[(k, i)] + w[(k, i)] + b[(k, i)] == 1

# 8. Debe haber por lo menos 1 empleado en el estado Trabaja en cada franja
#    horaria.

# (There is at least 1 work block per column.)
for i in range(SCHEDULE):
    prob += (
        DEMAND_ARRAY[(5 * 49) + i] * pulp.lpSum(w[(k, i)] for k in range(EMPLOYEES))
        >= DEMAND_ARRAY[(5 * 49) + i]
    )
    # prob += DEMAND_ARRAY[(5 * 49) + i] - pulp.lpSum(w[(k, i)] for k in range(EMPLOYEES)) >= 1*DEMAND_ARRAY[(5 * 49) + i]

# Solve the problem
prob.solve(solver)  # Set a time limit of 60 seconds

# Check the solver status
if pulp.LpStatus[prob.status] == "Optimal":
    print("Found an optimal solution!")

    # Display results functions
    print_2d_schedule(x)
    print("\n")
    print("Objective =", pulp.value(prob.objective))
else:
    print_2d_schedule(x)
    print("Could not find an optimal solution.")