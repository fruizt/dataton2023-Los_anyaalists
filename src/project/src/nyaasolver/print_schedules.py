import csv
from datetime import datetime, timedelta


def print_3d_schedule_channels(work_matrix, break_matrix, lunch_matrix):
    """Print a 3D schedule (including days) in a human-readable format using color."""

    # Define ANSI escape sequences for colors
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    END = "\033[0m"  # Reset color to default

    # Define the symbols for printing the schedule
    symbols = {
        "work": f"{GREEN}██{END}",
        "break": f"{BLUE}██{END}",
        "lunch": f"{YELLOW}██{END}",
    }

    # Extract unique days, rows (employees), and columns (time blocks) from the dictionary keys
    days = sorted(set([key[0] for key in work_matrix.keys()]))
    rows = sorted(set([key[1] for key in work_matrix.keys()]))
    cols = sorted(set([key[2] for key in work_matrix.keys()]))

    # Define day names for printing
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    # Iterate through each day
    for d in days:
        print(f"\n{day_names[d]} Schedule:")
        column_headers = "   " + " ".join(str(c).zfill(2) for c in cols)
        print(column_headers)

        # Iterate through each row for the current day
        for r in rows:
            row_data = []
            # Iterate through each time block for the current row and day
            for c in cols:
                work_value = round(work_matrix.get((d, r, c), 0).varValue)
                break_value = round(break_matrix.get((d, r, c), 0).varValue)
                lunch_value = round(lunch_matrix.get((r, c), 0).varValue)

                # Check each matrix to see if the activity is scheduled
                if work_value == 1:
                    row_data.append(symbols["work"])
                elif break_value == 1:
                    row_data.append(symbols["break"])
                elif lunch_value == 1:
                    row_data.append(symbols["lunch"])
                elif work_value == 0 and break_value == 0 and lunch_value == 0:
                    row_data.append("  ")
                else:
                    row_data.append("??")
            # Join the row data with a space for separation between blocks
            schedule_row = f"{str(r).zfill(2)} " + " ".join(row_data)
            print(schedule_row)


def print_2d_schedule_channels(work_matrix, break_matrix):
    """Print a 2D schedule in a human-readable format using color."""

    # Define ANSI escape sequences for colors
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    END = "\033[0m"  # Reset color to default

    # Define the symbols for printing the schedule
    symbols = {
        "work": f"{GREEN}██{END}",
        "break": f"{BLUE}██{END}",
    }

    # Extract unique rows and columns from the dictionary keys
    rows = sorted(set([key[0] for key in work_matrix.keys()]))
    cols = sorted(set([key[1] for key in work_matrix.keys()]))

    # Print column headers
    column_headers = "   " + " ".join(str(c).zfill(2) for c in cols)
    print(column_headers)

    # Iterate over each row and print its schedule
    for r in rows:
        row_data = []
        # Iterate through each time block for the current row and day
        for c in cols:
            work_value = round(work_matrix.get((r, c), 0).varValue)
            break_value = round(break_matrix.get((r, c), 0).varValue)

            # Check each matrix to see if the activity is scheduled
            if work_value == 1:
                row_data.append(symbols["work"])
            elif break_value == 1:
                row_data.append(symbols["break"])
            elif work_value == 0 and break_value == 0:
                row_data.append("  ")
            else:
                row_data.append("??")
        # Join the row data with a space for separation between blocks
        schedule_row = f"{str(r).zfill(2)} " + " ".join(row_data)
        print(schedule_row)


def calculate_time(c):
    # Define the starting time and the starting franja
    base_time = datetime.strptime("7:30", "%H:%M")
    base_franja = 30

    # Calculate the new time and franja
    new_time = base_time + timedelta(minutes=15 * c)
    new_franja = base_franja + c

    # Format the new time in the desired format
    time_str = new_time.strftime("%H:%M")
    return time_str, new_franja


def generate_saturday_schedule_csv(
    work_matrix, break_matrix, employee_ids, dates, suc_code, filename="schedule.csv"
):
    # Define mappings for activities to CSV states
    activity_to_state = {
        "work": "Trabaja",
        "break": "Pausa Activa",
        "lunch": "Almuerza",
        "none": "Nada",
    }

    rows = sorted(set([key[0] for key in work_matrix.keys()]))
    cols = sorted(set([key[1] for key in work_matrix.keys()]))
    # Prepare data for CSV
    csv_data = []

    # Iterate through each day, employee, and time block
    for d, date in enumerate(dates):
        if d == 5:
            for c in cols:
                for r, employee_id in enumerate(employee_ids):
                    work_value = round(work_matrix.get((r, c), 0).varValue)
                    break_value = round(break_matrix.get((r, c), 0).varValue)

                    # Determine the state for the CSV
                    if work_value == 1:
                        state = activity_to_state["work"]
                    elif break_value == 1:
                        state = activity_to_state["break"]
                    else:
                        state = activity_to_state["none"]

                    # Calculate time and hora_franja
                    time, time_franja = calculate_time(c)

                    # Create a row for the CSV
                    csv_row = {
                        "suc_cod": suc_code,  # Assuming this is a fixed value
                        "documento": employee_id,
                        "fecha": date,
                        "hora": time,
                        "estado": state,
                        "hora_franja": time_franja,
                    }
                    csv_data.append(csv_row)

    # Write the data to a CSV file
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["suc_cod", "documento", "fecha", "hora", "estado", "hora_franja"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)


def generate_week_schedule_csv(
    work_matrix,
    break_matrix,
    lunch_matrix,
    employee_ids,
    dates,
    suc_code,
    filename="schedule.csv",
):
    # Define mappings for activities to CSV states
    activity_to_state = {
        "work": "Trabaja",
        "break": "Pausa Activa",
        "lunch": "Almuerza",
        "none": "Nada",
    }

    days = sorted(set([key[0] for key in work_matrix.keys()]))
    rows = sorted(set([key[1] for key in work_matrix.keys()]))
    cols = sorted(set([key[2] for key in work_matrix.keys()]))
    # Prepare data for CSV
    csv_data = []

    # Iterate through each day, employee, and time block
    for d, date in enumerate(dates):
        print(">> date:", date)
        print(">> d:", d)
        if d <= 4:
            for c in cols:
                for r, employee_id in enumerate(employee_ids):
                    work_value = round(work_matrix.get((d, r, c), 0).varValue)
                    break_value = round(break_matrix.get((d, r, c), 0).varValue)
                    lunch_value = round(lunch_matrix.get((r, c), 0).varValue)

                    # Determine the state for the CSV
                    if work_value == 1:
                        state = activity_to_state["work"]
                    elif break_value == 1:
                        state = activity_to_state["break"]
                    elif lunch_value == 1:
                        state = activity_to_state["lunch"]
                    else:
                        state = activity_to_state["none"]

                    # Calculate time and hora_franja
                    time, time_franja = calculate_time(c)

                    # Create a row for the CSV
                    csv_row = {
                        "suc_cod": suc_code,
                        "documento": employee_id,
                        "fecha": date,
                        "hora": time,
                        "estado": state,
                        "hora_franja": time_franja,
                    }
                    csv_data.append(csv_row)

    # Write the data to a CSV file
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["suc_cod", "documento", "fecha", "hora", "estado", "hora_franja"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
