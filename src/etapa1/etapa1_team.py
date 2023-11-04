from src.print_schedules import print_2d_schedule
from src.import_file import import_file
import pulp

path_to_glkp = "/usr/local/lib"

# Import demand Data
d = import_file()
d = d[0][0]

# Define the length of the schedule, for example, an 8-hour workday has 32 blocks
T = 46
E = 6

# Define the LP problem
prob = pulp.LpProblem("Minimize_Breaks", pulp.LpMinimize)

# Decision variables
x = pulp.LpVariable.dicts(
    "Block", [(x, y) for x in range(E) for y in range(T)], 0, 3, cat=pulp.LpInteger
)  # Value from 0 to 3

pd = pulp.LpVariable.dicts(
    "Positive Difference", range(T), lowBound=0, cat=pulp.LpInteger
) 

# Channels
n = pulp.LpVariable.dicts(
    "Nothing", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)  # 1 for not working, 0 otherwise
w = pulp.LpVariable.dicts(
    "Work", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)  # 1 for working, 0 otherwise
b = pulp.LpVariable.dicts(
    "Break", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)  # 1 for active pause, 0 otherwise
l = pulp.LpVariable.dicts(
    "Lunch", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)  # 1 for lunch, 0 otherwise

# Status
a = pulp.LpVariable.dicts(
    "Active", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)  # 1 for active, 0 otherwise
end_active = pulp.LpVariable.dicts(
    "end_active", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)  # 1 for end of active, 0 otherwise
end_almuerzo = pulp.LpVariable.dicts(
    "end_almuerzo", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)  # 1 for end of lunch, 0 otherwise

# Objective function: Maximize work blocks.
# prob += pulp.lpSum([w[(i, j)] for i in range(E) for j in range(T)])
prob += pulp.lpSum(pd[i] for i in range(T))

# Constraints

for i in range(T):
    prob += pd[i] >= d[i] - pulp.lpSum(w[(k, i)] for k in range(E))


for k in range(E):
    # 1. Los empleados deben trabajar mínimo 1 hora de forma continua para poder
    #    salir a una Pausa Activa o Almuerzo. Esto quiere decir que, si un empleado
    #    solo ha trabajado 3 franjas horarias, en la 4 franja horaria NO debe salir
    #    a Pausa Activa o Almuerzo.

    # (No breaks in the first 4 blocks.)
    prob += pulp.lpSum(b[(k, i)] for i in range(4)) == 0

    for i in range(4, T):
        # (Breaks can only occur after at least 4 consecutive work blocks.)
        prob += 4 * b[(k, i)] <= pulp.lpSum([w[(k, i - j)] for j in range(1, 5)])
        # (Lunch can only begin after at least 4 consecutive work blocks.)
        prob += 4 * l[(k, i)] <= pulp.lpSum(
            [w[(k, i - j)] + l[(k, i - j)] for j in range(1, 5)]
        )

        # (End can only happen with at least 4 consecutive work blocks.)
        prob += 4 * end_active[(k, i)] <= pulp.lpSum(
            [w[(k, i - j)] for j in range(0, 4)]
        )

    # 2. Los empleados deben trabajar máximo 2 horas de forma continua sin salir a
    #    una pausa activa. Esto quiere decir que, si un empleado ha trabajado 8
    #    franjas horarias, en la 9 franja horaria SÍ debe salir a Pausa Activa o
    #    Almuerzo.

    for i in range(T - 8):
        # (No more than 8 work blocks in a 9-long segment.)
        prob += pulp.lpSum([w[(k, i + j)] for j in range(9)]) <= 8

    # 3. El tiempo de almuerzo debe tomarse de forma CONTINUA y es de 1 hora y
    #    media. Se debe tomar almuerzo una única vez en el día.

    # (Ensure 6 blocks of lunch.)
    prob += pulp.lpSum([l[(k, i)] for i in range(T)]) == 6

    # (Ensure the lunch block is continuous.)
    for i in range(T - 1):
        prob += l[(k, i)] <= l[(k, i + 1)] + end_almuerzo[(k, i)]
    prob += pulp.lpSum(end_almuerzo[(k, i)] for i in range(T)) == 1

    # 4. La hora mínima de salida para tomar el almuerzo son las 11:30 am y la hora
    #    máxima para salir a tomar el almuerzo es a la 1:30 pm.
    #    Esto quiere decir que:
    #      i. Una persona NO puede salir a tomar almuerzo a las 11:15 am
    #      ii. Una persona NO puede salir a tomar almuerzo a la 1:45 pm
    #      iii. Es VÁLIDO que una persona tome almuerzo de la 1:30 pm a las 3:00

    # (Ensure no lunch outside of valid hours.)
    prob += pulp.lpSum([l[(k, i)] for i in range(16)]) == 0
    prob += pulp.lpSum([l[(k, i)] for i in range(30, T)]) == 0

    # 5. La jornada laboral de todos los empleados de es 8 horas diarias. Los
    #    estados de Trabaja y Pausa Activa hacen parte de la jornada laboral. El
    #    tiempo de almuerzo NO constituye tiempo de jornada laboral.
    # (Ensure 32 blocks of work or breaks.)
    prob += pulp.lpSum([w[(k, i)] + b[(k, i)] for i in range(T)]) == 32

    # 6. El horario de los empleados debe ser CONTINUO, desde que comienza la
    #    jornada laboral del empleado este solo puede estar en los estados de
    #    Trabaja, Pausa Activa y Almuerza. Es decir, que el estado Nada solo puede
    #    estar activo al comienzo del día si el empleado no ha comenzado su jornada
    #    laboral o al final del día si el empleado ya completó su jornada laboral.

    # (Define active periods.)
    for i in range(T):
        prob += a[(k, i)] >= w[(k, i)]
        prob += a[(k, i)] >= b[(k, i)]
        prob += a[(k, i)] >= l[(k, i)]
        prob += a[(k, i)] <= w[(k, i)] + b[(k, i)] + l[(k, i)]

    # (Ensure the active block is continuous.)
    for i in range(T - 1):
        prob += a[(k, i)] <= a[(k, i + 1)] + end_active[(k, i)]

    prob += end_active[(k, T - 1)] == a[(k, T - 1)]

    # (Ensure there is only one end block)
    prob += pulp.lpSum(end_active[(k, i)] for i in range(T)) == 1

    # 7. El último estado de la jornada laboral de los empleados debe ser Trabaja.

    # (Work should be 1 when end_active is 1.)
    for i in range(T):
        prob += w[(k, i)] >= end_active[(k, i)]

    # 9. Cualquier franja de trabajo debe durar entre 1 y 2 horas.
    # NOOP: Inferred from previous restrictions.

    # Misc

    # Channel Decomposition
    for i in range(T):
        prob += (
            x[(k, i)] == n[(k, i)] * 0 + w[(k, i)] * 1 + b[(k, i)] * 2 + l[(k, i)] * 3
        )
        prob += n[(k, i)] + w[(k, i)] + b[(k, i)] + l[(k, i)] == 1

# 8. Debe haber por lo menos 1 empleado en el estado Trabaja en cada franja
#    horaria.

# (There is at least 1 work block per column.)
for i in range(T):
    prob += pulp.lpSum(w[(k, i)] for k in range(E)) >= 1

# Test

# Set the end of the shift.
# prob += end_active[37] == 1

# Set a lunch block.
# prob += l[29] == 1

# Solve the problem
prob.solve(pulp.GLPK_CMD())  # Set a time limit of 60 seconds

# Check the solver status
if pulp.LpStatus[prob.status] == "Optimal":
    print("Found an optimal solution!")

    # Display results functions
    print_2d_schedule(x)
    print("\n")
    print("Objective =", pulp.value(prob.objective))
else:
    print("Could not find an optimal solution.")