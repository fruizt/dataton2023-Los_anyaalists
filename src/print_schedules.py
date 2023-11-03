def print_2d_schedule(matrix_dict):
    """Print a 2D schedule in a human-readable format using color."""

    # Define ANSI escape sequences for colors
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    END = "\033[0m"  # Reset color to default

    symbols = {
        0: "  ",  # For 'Nothing', we print two spaces to keep alignment
        1: f"{GREEN}██{END}",  # Work in green
        2: f"{BLUE}██{END}",  # Break in blue
        3: f"{YELLOW}██{END}",  # Lunch in yellow
    }

    # Extract unique rows and columns from the dictionary keys
    rows = sorted(set([key[0] for key in matrix_dict.keys()]))
    cols = sorted(set([key[1] for key in matrix_dict.keys()]))

    # Print column headers
    column_headers = "   " + " ".join(str(c).zfill(2) for c in cols)
    print(column_headers)

    # Iterate over each row and print its schedule
    for r in rows:
        row_data = [int(matrix_dict[(r, c)].varValue) for c in cols]  # Defaulting to 0 if the key isn't present
        schedule_row = f"{str(r).zfill(2)} " + " ".join(
            symbols[int(value)] for value in row_data
        )
        print(schedule_row)

def print_schedule(x):
    """Print the schedule in a human-readable format using color."""

    # Define ANSI escape sequences for colors
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    END = "\033[0m"  # Reset color to default

    symbols = {
        0: "  ",  # For 'Nothing', we print two spaces to keep alignment
        1: f"{GREEN}██{END}",  # Work in green
        2: f"{BLUE}██{END}",  # Break in blue
        3: f"{YELLOW}██{END}",  # Lunch in yellow
    }

    index_row = " ".join(
        str(i).zfill(2) for i in range(len(x))
    )  # zfill ensures two characters for all indexes
    schedule = " ".join(symbols[int(x[i].varValue)] for i in range(len(x)))

    print(index_row)
    print(schedule)


def print_schedule_bin(x):
    """Print the schedule in a human-readable format."""
    symbols = {
        0: "  ",
        1: "██",
    }
    # index_row = ' '.join(str(i).zfill(2) for i in range(len(x)))  # zfill ensures two characters for all indexes
    schedule = " ".join(symbols[int(x[i].varValue)] for i in range(len(x)))
    # print(index_row)
    print(schedule)
