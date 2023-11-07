import os
import pandas as pd
import glob

def merge_csv_files(directory_path, output_file):
    """
    Merge all CSV files in the given directory into a single CSV file.

    Parameters:
    - directory_path: Path to the directory containing the CSV files.
    - output_file: Path for the output merged CSV file.
    """
    # Change the working directory to the directory containing CSV files
    os.chdir(directory_path)

    # Use glob to match all csv files in the directory
    files_to_merge = glob.glob('*.csv')

    # Read each CSV file and store them in a list
    dataframes = [pd.read_csv(file) for file in files_to_merge]

    # Concatenate all the dataframes into a single dataframe
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Convert fecha to datetime for proper sorting
    merged_df['fecha'] = pd.to_datetime(merged_df['fecha'], dayfirst=True)

    # Sort the dataframe
    sorted_df = merged_df.sort_values(by=['suc_cod', 'fecha', 'hora_franja'])

    # Write the sorted dataframe to a new CSV file
    sorted_df.to_csv(output_file, index=False)
    print(f'Merged and sorted {len(files_to_merge)} files into {output_file}')


# Example usage:
# Provide the directory where your CSV files are located
directory_path = r'C:\Users\test\Documents\GitHub\dataton2023-Los_anyaalists\result'
# Provide the desired output file name
output_file = 'result.csv'

# Call the function to merge the CSV files
merge_csv_files(directory_path, output_file)
