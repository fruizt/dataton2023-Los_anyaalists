from nyaasolver.print_schedules import (
    print_3d_schedule_channels,
    generate_week_schedule_csv,
)
from nyaasolver.etapa2.helper import is_full_time_worker
import pulp


def solve_week_optimization(demand_workers, sucursal_id):
    """Solve the optimization problem from monday to friday."""

    MAX_WORK_BLOCKS_TC = 28
    MAX_WORK_BLOCKS_MT = 16
    SCHEDULE = 49
    DAYS = 5

    WORK_BLOCKS_BEFORE_BREAK = 4
    WORK_BLOCKS_BEFORE_LUNCH = 4
    WORK_BLOCKS_BEFORE_END = 4

    MAX_WORK_BLOCKS_BEFORE_BREAK = 8

    START_LUNCH = 16
    END_LUNCH = 30
    LUNCH_BLOCKS = 6

    DEMAND_ARRAY = demand_workers["demands"]
    EMPLOYEES = len(demand_workers["TC"]) + len(demand_workers["MT"])
    WORKERS = demand_workers["TC"] + demand_workers["MT"]

    # Solver configuration
    # solver = pulp.getSolver("PULP_CBC_CMD", threads=16, timeLimit=400)
    path_to_cplex = (
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\cplex\bin\x64_win64\cplex.exe"
    )
    solver = pulp.getSolver("CPLEX_CMD", path=path_to_cplex, threads=12, timeLimit=30)

    # Define the LP problem
    prob = pulp.LpProblem("Minimize_PD", pulp.LpMinimize)

    # Decision variables
    pd = pulp.LpVariable.dicts(
        "Positive Difference",
        [(x, z) for x in range(DAYS) for z in range(SCHEDULE)],
        lowBound=0,
        cat=pulp.LpInteger,
    )

    # Channels
    w = pulp.LpVariable.dicts(
        "Work",
        [
            (x, y, z)
            for x in range(DAYS)
            for y in range(EMPLOYEES)
            for z in range(SCHEDULE)
        ],
        cat=pulp.LpBinary,
    )  # 1 for working, 0 otherwise
    b = pulp.LpVariable.dicts(
        "Break",
        [
            (x, y, z)
            for x in range(DAYS)
            for y in range(EMPLOYEES)
            for z in range(SCHEDULE)
        ],
        cat=pulp.LpBinary,
    )  # 1 for active pause, 0 otherwise
    l = pulp.LpVariable.dicts(
        "Lunch",
        [(y, z) for y in range(EMPLOYEES) for z in range(SCHEDULE)],
        cat=pulp.LpBinary,
    )  # 1 for lunch, 0 otherwise

    # Status
    a = pulp.LpVariable.dicts(
        "Active",
        [(y, z) for y in range(EMPLOYEES) for z in range(SCHEDULE)],
        cat=pulp.LpBinary,
    )  # 1 for active, 0 otherwise
    active_end = pulp.LpVariable.dicts(
        "Actrive End",
        [(y, z) for y in range(EMPLOYEES) for z in range(SCHEDULE)],
        cat=pulp.LpBinary,
    )  # 1 for end of active, 0 otherwise
    lunch_end = pulp.LpVariable.dicts(
        "Lunch End",
        [(y, z) for y in range(EMPLOYEES) for z in range(SCHEDULE)],
        cat=pulp.LpBinary,
    )  # 1 for end of lunch, 0 otherwise

    # Objective function: Minimize pd.
    prob += pulp.lpSum(pd[(x, i)] for x in range(DAYS) for i in range(SCHEDULE))

    # Constraints

    for d in range(DAYS):
        # (Define the positive difference. Negative values are disallowed by the lower bound.)
        for i in range(SCHEDULE):
            prob += pd[(d, i)] >= DEMAND_ARRAY[(d * SCHEDULE) + i] - pulp.lpSum(
                w[(d, k, i)] for k in range(EMPLOYEES)
            )

        for k, worker in enumerate(WORKERS):
            # 1. Los empleados deben trabajar mínimo 1 hora de forma continua para poder
            #    salir a una Pausa Activa o Almuerzo. Esto quiere decir que, si un empleado
            #    solo ha trabajado 3 franjas horarias, en la 4 franja horaria NO debe salir
            #    a Pausa Activa o Almuerzo.

            # (No breaks in the first WORK_BLOCKS_BEFORE_BREAK blocks.)
            prob += (
                pulp.lpSum(b[(d, k, i)] for i in range(WORK_BLOCKS_BEFORE_BREAK)) == 0
            )

            # (Breaks can only occur after at least WORK_BLOCKS_BEFORE_BREAK consecutive work
            #  blocks.)
            for i in range(WORK_BLOCKS_BEFORE_BREAK, SCHEDULE):
                prob += WORK_BLOCKS_BEFORE_BREAK * b[(d, k, i)] <= pulp.lpSum(
                    [w[(d, k, i - j)] for j in range(1, WORK_BLOCKS_BEFORE_BREAK + 1)]
                )

            # (Lunch can only begin after at least WORK_BLOCKS_BEFORE_LUNCH consecutive work blocks.
            #  (Only for full time workers.))
            for i in range(WORK_BLOCKS_BEFORE_LUNCH, SCHEDULE):
                if is_full_time_worker(worker, demand_workers):
                    prob += WORK_BLOCKS_BEFORE_LUNCH * l[(k, i)] <= pulp.lpSum(
                        [
                            w[(d, k, i - j)] + l[(k, i - j)]
                            for j in range(1, WORK_BLOCKS_BEFORE_LUNCH + 1)
                        ]
                    )

            # (End can only happen with at least WORK_BLOCKS_BEFORE_END - 1 consecutive work blocks
            #  preceding and 1 concurrent work block.)
            for i in range(WORK_BLOCKS_BEFORE_END, SCHEDULE):
                prob += WORK_BLOCKS_BEFORE_END * active_end[(k, i)] <= pulp.lpSum(
                    [w[(d, k, i - j)] for j in range(WORK_BLOCKS_BEFORE_END)]
                )

            # 2. Los empleados deben trabajar máximo 2 horas de forma continua sin salir a una pausa
            #    activa. Esto quiere decir que, si un empleado ha trabajado
            #    MAX_WORK_BLOCKS_BEFORE_BREAK franjas horarias, en la
            #    (MAX_WORK_BLOCKS_BEFORE_BREAK + 1) franja horaria SÍ debe salir a Pausa Activa o
            #    Almuerzo.

            for i in range(SCHEDULE - MAX_WORK_BLOCKS_BEFORE_BREAK):
                # (No more than MAX_WORK_BLOCKS_BEFORE_BREAK work blocks in a
                #  (MAX_WORK_BLOCKS_BEFORE_BREAK + 1)-long segment.)
                prob += (
                    pulp.lpSum(
                        [
                            w[(d, k, i + j)]
                            for j in range(MAX_WORK_BLOCKS_BEFORE_BREAK + 1)
                        ]
                    )
                    <= MAX_WORK_BLOCKS_BEFORE_BREAK
                )

            if is_full_time_worker(worker, demand_workers):
                # 3. El tiempo de almuerzo debe tomarse de forma CONTINUA y es de 1 hora y
                #    media. Se debe tomar almuerzo una única vez en el día.

                # (Ensure LUNCH_BLOCKS blocks of lunch.)
                prob += pulp.lpSum([l[(k, i)] for i in range(SCHEDULE)]) == LUNCH_BLOCKS

                # (Ensure the lunch block is continuous.)

                #     (Lunch can only happen if the next lunch block is active OR the current
                #      lunch_end block is active.)
                for i in range(SCHEDULE - 1):
                    prob += l[(k, i)] <= l[(k, i + 1)] + lunch_end[(k, i)]

                #     (There can only be one end_lunch block.)
                prob += pulp.lpSum(lunch_end[(k, i)] for i in range(SCHEDULE)) == 1

                # 4. La hora mínima de salida para tomar el almuerzo son las 11:30 am y la hora
                #    máxima para salir a tomar el almuerzo es a la 1:30 pm.
                #    Esto quiere decir que:
                #        i. Una persona NO puede salir a tomar almuerzo a las 11:15 am
                #       ii. Una persona NO puede salir a tomar almuerzo a la 1:45 pm
                #      iii. Es VÁLIDO que una persona tome almuerzo de la 1:30 pm a las 3:00 pm

                # (Ensure no lunch outside of valid hours.)
                prob += pulp.lpSum([l[(k, i)] for i in range(START_LUNCH)]) == 0
                prob += pulp.lpSum([l[(k, i)] for i in range(END_LUNCH, SCHEDULE)]) == 0

                # 5. La jornada laboral de todos los empleados de es MAX_WORK_BLOCKS_TC / 15 horas
                #    diarias si es de TC, en otro caso es de MAX_WORK_BLOCKS_MT / 15 horas. Los
                #    estados de Trabaja y Pausa Activa hacen parte de la jornada laboral. El tiempo
                #    de almuerzo NO constituye tiempo de jornada laboral.

                # (Ensure SCHEDULE blocks of work or breaks for full time workers.)
                prob += (
                    pulp.lpSum([w[(d, k, i)] + b[(d, k, i)] for i in range(SCHEDULE)])
                    == MAX_WORK_BLOCKS_TC
                )

            else:
                # (Ensure SCHEDULE blocks of work or breaks for part time workers.)
                prob += (
                    pulp.lpSum([w[(d, k, i)] + b[(d, k, i)] for i in range(SCHEDULE)])
                    == MAX_WORK_BLOCKS_MT
                )

                # (Ensure no blocks of lunch.)
                prob += pulp.lpSum([l[(k, i)] for i in range(SCHEDULE)]) == 0

            # 6. El horario de los empleados debe ser CONTINUO, desde que comienza la
            #    jornada laboral del empleado este solo puede estar en los estados de
            #    Trabaja, Pausa Activa y Almuerza. Es decir, que el estado Nada solo puede
            #    estar activo al comienzo del día si el empleado no ha comenzado su jornada
            #    laboral o al final del día si el empleado ya completó su jornada laboral.

            # (Define active periods.)
            for i in range(SCHEDULE):
                prob += a[(k, i)] == w[(d, k, i)] + b[(d, k, i)] + l[(k, i)]

            # (Ensure the active block is continuous.)

            #     (Active can only happen if the next active block is active OR the current
            #      active_end block is active.)
            for i in range(SCHEDULE - 1):
                prob += a[(k, i)] <= a[(k, i + 1)] + active_end[(k, i)]

            #     (The last block can be active if the current active_end block is active.)
            prob += active_end[(k, SCHEDULE - 1)] == a[(k, SCHEDULE - 1)]

            #     (Ensure there is only one end block)
            prob += pulp.lpSum(active_end[(k, i)] for i in range(SCHEDULE)) == 1

            # 7. El último estado de la jornada laboral de los empleados debe ser Trabaja.

            # (Work should be 1 when active_end is 1.)
            # for i in range(SCHEDULE):
            #     prob += w[(d, k, i)] >= active_end[(k, i)]

            # 9. Cualquier franja de trabajo debe durar entre 1 y 2 horas.
            # NOOP: Inferred from previous restrictions.

            # Misc

            # Channel Decomposition

            # (Can't work, have a break, or have lunch at the same time.)
            for i in range(SCHEDULE):
                prob += w[(d, k, i)] + b[(d, k, i)] + l[(k, i)] <= 1

        # 8. Debe haber por lo menos 1 empleado en el estado Trabaja en cada franja
        #    horaria.

        # (There is at least 1 work block per column.)
        for i in range(SCHEDULE):
            prob += (
                DEMAND_ARRAY[(d * SCHEDULE) + i]
                * pulp.lpSum(w[(d, k, i)] for k in range(EMPLOYEES))
                >= DEMAND_ARRAY[(d * SCHEDULE) + i]
            )

    # Solve the problem
    prob.solve(solver)

    # Check the solver status and print the results.
    if pulp.LpStatus[prob.status] == "Optimal":
        print("Found an optimal solution!")

        # Display results functions
        print_3d_schedule_channels(w, b, l)
        print("\n")
        print("Objective =", pulp.value(prob.objective))
        generate_week_schedule_csv(
            w,
            b,
            l,
            WORKERS,
            demand_workers["days"].keys(),
            sucursal_id,
            filename="week_schedule_" + str(sucursal_id) + ".csv",
        )
        return {
            "result": (w, b, l),
            "objective_function_result": pulp.value(prob.objective),
        }
    else:
        print_3d_schedule_channels(w, b, l)
        print("Could not find an optimal solution.")
