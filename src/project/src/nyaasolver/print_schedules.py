import csv
import numpy as np


def write_array_to_csv(array, file_path):
    np.savetxt(file_path, array, delimiter=",")


def write_matrix_to_csv(matrix, file_path):
    with open(file_path, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(matrix)


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
                lunch_value = round(lunch_matrix.get((d, r, c), 0).varValue)

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


# def print_3d_schedule(matrix_dict):
#     """Print a 3D schedule (including days) in a human-readable format using color."""

#     # Define ANSI escape sequences for colors
#     GREEN = "\033[92m"
#     BLUE = "\033[94m"
#     YELLOW = "\033[93m"
#     END = "\033[0m"  # Reset color to default

#     symbols = {
#         0: "  ",  # For 'Nothing', we print two spaces to keep alignment
#         1: f"{GREEN}██{END}",  # Work in green
#         2: f"{BLUE}██{END}",  # Break in blue
#         3: f"{YELLOW}██{END}",  # Lunch in yellow
#     }

#     # Extract unique days, rows (employees), and columns (time blocks) from the dictionary keys
#     days = sorted(set([key[0] for key in matrix_dict.keys()]))
#     rows = sorted(set([key[1] for key in matrix_dict.keys()]))
#     cols = sorted(set([key[2] for key in matrix_dict.keys()]))

#     # Define day names for printing
#     day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]

#     for d in days:
#         # Print the day header
#         print(f"\n{day_names[d]} Schedule:")
#         # Print column headers for time blocks
#         column_headers = "   " + " ".join(str(c).zfill(2) for c in cols)
#         print(column_headers)

#         # Iterate over each row (employee) and print its schedule for the day
#         for r in rows:
#             row_data = [
#                 int(matrix_dict.get((d, r, c), 0).varValue) for c in cols
#             ]  # Defaulting to 0 if the key isn't present
#             schedule_row = f"{str(r).zfill(2)} " + " ".join(
#                 symbols[int(value)] for value in row_data
#             )
#             print(schedule_row)


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


# def print_2d_schedule(matrix_dict):
#     """Print a 2D schedule in a human-readable format using color."""

#     # Define ANSI escape sequences for colors
#     GREEN = "\033[92m"
#     BLUE = "\033[94m"
#     YELLOW = "\033[93m"
#     END = "\033[0m"  # Reset color to default

#     symbols = {
#         0: "  ",  # For 'Nothing', we print two spaces to keep alignment
#         1: f"{GREEN}██{END}",  # Work in green
#         2: f"{BLUE}██{END}",  # Break in blue
#         3: f"{YELLOW}██{END}",  # Lunch in yellow
#     }

#     # Extract unique rows and columns from the dictionary keys
#     rows = sorted(set([key[0] for key in matrix_dict.keys()]))
#     cols = sorted(set([key[1] for key in matrix_dict.keys()]))

#     # Print column headers
#     column_headers = "   " + " ".join(str(c).zfill(2) for c in cols)
#     print(column_headers)

#     # Iterate over each row and print its schedule
#     for r in rows:
#         row_data = [
#             int(matrix_dict[(r, c)].varValue) for c in cols
#         ]  # Defaulting to 0 if the key isn't present
#         schedule_row = f"{str(r).zfill(2)} " + " ".join(
#             symbols[int(value)] for value in row_data
#         )
#         print(schedule_row)


# def print_schedule(x):
#     """Print the schedule in a human-readable format using color."""

#     # Define ANSI escape sequences for colors
#     GREEN = "\033[92m"
#     BLUE = "\033[94m"
#     YELLOW = "\033[93m"
#     END = "\033[0m"  # Reset color to default

#     symbols = {
#         0: "  ",  # For 'Nothing', we print two spaces to keep alignment
#         1: f"{GREEN}██{END}",  # Work in green
#         2: f"{BLUE}██{END}",  # Break in blue
#         3: f"{YELLOW}██{END}",  # Lunch in yellow
#     }

#     index_row = " ".join(
#         str(i).zfill(2) for i in range(len(x))
#     )  # zfill ensures two characters for all indexes
#     schedule = " ".join(symbols[int(x[i].varValue)] for i in range(len(x)))

#     print(index_row)
#     print(schedule)


# def print_schedule_bin(x):
#     """Print the schedule in a human-readable format."""
#     symbols = {
#         0: "  ",
#         1: "██",
#     }
#     # index_row = ' '.join(str(i).zfill(2) for i in range(len(x)))  # zfill ensures two characters for all indexes
#     schedule = " ".join(symbols[int(x[i].varValue)] for i in range(len(x)))
#     # print(index_row)
#     print(schedule)
