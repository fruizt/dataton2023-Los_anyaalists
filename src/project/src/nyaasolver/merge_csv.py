import os
import pandas as pd
import glob

def merge_csv_files():
    cur_dir = os.getcwd()    
    directory_path = os.path.join(cur_dir, 'result')
    output_file = os.path.join(directory_path, 'final_result.csv')

    # Use glob to match all csv files in the directory
    files_to_merge = glob.glob(os.path.join(directory_path, '*.csv'))

    # Read each CSV file and store them in a list
    dataframes = [pd.read_csv(file) for file in files_to_merge if file != output_file]

    # Concatenate all the dataframes into a single dataframe
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Convert fecha to datetime for proper sorting
    merged_df['fecha'] = pd.to_datetime(merged_df['fecha'], format='ISO8601')

    # Sort the dataframe
    sorted_df = merged_df.sort_values(by=['suc_cod', 'fecha', 'hora_franja'])

    # Write the sorted dataframe to a new CSV file
    sorted_df.to_csv(output_file, index=False)
    print(f'Merged and sorted {len(dataframes)} files into {output_file}')