from nyaasolver.print_schedules import print_2d_schedule
from nyaasolver.import_file import import_file
import pulp

Solver_name = "PULP_CBC_CMD"
solver = pulp.getSolver(Solver_name, threads=4)

# Import demand Data
d = import_file()
d = d[0][0]

# Define the length of the schedule and number of employees
T = 46
E = 8

# Define the LP problem
prob = pulp.LpProblem("Minimize_Undercapacity", pulp.LpMinimize)

# Decision variables
x = pulp.LpVariable.dicts(
    "Block", [(x, y) for x in range(E) for y in range(T)], 0, 3, cat=pulp.LpInteger
)
pd = pulp.LpVariable.dicts(
    "Positive Difference", range(T), lowBound=0, cat=pulp.LpContinuous
)

# channels

# 1 for not working, 0 otherwise
n = pulp.LpVariable.dicts(
    "Nothing", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)
# 1 for working, 0 otherwise
w = pulp.LpVariable.dicts(
    "Work", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)
# 1 for active pause, 0 otherwise
b = pulp.LpVariable.dicts(
    "Break", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)
# 1 for lunch, 0 otherwise
l = pulp.LpVariable.dicts(
    "Lunch", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)

# Status
# 1 for active, 0 otherwise
a = pulp.LpVariable.dicts(
    "Active", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)
# 1 for end of active, 0 otherwise
end_active = pulp.LpVariable.dicts(
    "end_active", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)
# 1 for end of lunch, 0 otherwise
end_almuerzo = pulp.LpVariable.dicts(
    "end_almuerzo", [(x, y) for x in range(E) for y in range(T)], cat=pulp.LpBinary
)

# Objective function: Minimize_Undercapacity
prob += pulp.lpSum(pd[i] for i in range(T))

# Constraints

for i in range(T):
    # pd is a number only when demand is higher than capacity
    prob += pd[i] >= d[i] - pulp.lpSum(w[(k, i)] for k in range(E))
    # Debe haber por lo menos 1 empleado en el estado Trabaja en cada franja horaria.
    prob += pulp.lpSum(w[(k, i)] for k in range(E)) >= 1

for k in range(E):
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

    for i in range(T - 8):
        # (No more than 8 work blocks in a 9-long segment.)
        prob += pulp.lpSum([w[(k, i + j)] for j in range(9)]) <= 8

    # (Ensure 6 blocks of lunch.)
    prob += pulp.lpSum([l[(k, i)] for i in range(T)]) == 6

    for i in range(T - 1):
        # (Ensure the lunch block is continuous.)
        prob += l[(k, i)] <= l[(k, i + 1)] + end_almuerzo[(k, i)]
        # (Ensure the active block is continuous.)
        prob += a[(k, i)] <= a[(k, i + 1)] + end_active[(k, i)]

    prob += end_active[(k, T - 1)] == a[(k, T - 1)]
    prob += pulp.lpSum(end_almuerzo[(k, i)] for i in range(T)) == 1

    # (Ensure no lunch outside of valid hours.)
    prob += pulp.lpSum([l[(k, i)] for i in range(16)]) == 0
    prob += pulp.lpSum([l[(k, i)] for i in range(30, T)]) == 0

    # (Ensure 32 blocks of work or breaks.)
    prob += pulp.lpSum([w[(k, i)] + b[(k, i)] for i in range(T)]) == 32

    # (Define active periods.)
    for i in range(T):
        prob += a[(k, i)] >= w[(k, i)]
        prob += a[(k, i)] >= b[(k, i)]
        prob += a[(k, i)] >= l[(k, i)]
        prob += a[(k, i)] <= w[(k, i)] + b[(k, i)] + l[(k, i)]
        # (Work should be 1 when end_active is 1.)
        prob += w[(k, i)] >= end_active[(k, i)]

        prob += n[(k, i)] + w[(k, i)] + b[(k, i)] + l[(k, i)] == 1

        prob += (
            x[(k, i)] == n[(k, i)] * 0 + w[(k, i)] * 1 + b[(k, i)] * 2 + l[(k, i)] * 3
        )

    # (Ensure there is only one end block)
    prob += pulp.lpSum(end_active[(k, i)] for i in range(T)) == 1

prob.solve(solver)  # Set a time limit of 60 seconds

# Check the solver status
if pulp.LpStatus[prob.status] == "Optimal":
    print("Found an optimal solution!")
    # Display results functions
    print_2d_schedule(x)
    print("\n")
    print("Objective =", pulp.value(prob.objective))
else:
    print("Could not find an optimal solution.")
