import argparse
from pathlib import Path
import glob

import pandas as pd


def unpack_data(input_dir: str, output_file: str) -> None:
    """
    Combine multiple CSV files from a directory into a single CSV file.

    This function reads all CSV files in the input directory, concatenates
    them into a single DataFrame, and saves the result to the output path.

    Parameters
    ----------
    input_dir : str
        Path to the directory containing the CSV files to combine.
    output_file : str
        Path where the combined CSV file will be saved.

    Steps
    -----
    1. List all files in the input directory
    2. Filter to keep only .csv files
    3. Read each CSV file into a pandas DataFrame
    4. Concatenate all DataFrames
    5. Save the combined DataFrame to output_file
    """
    input_path = Path(input_dir)
    output_path = Path(output_file)

    concat = pd.DataFrame()
    files = ['dev', 'train' , 'test']

    dfs = []
    for file in files:
        for p in glob.glob(f"{input_path}/{file}/*"):
            dfs.append(pd.read_csv(p))

    concat = pd.concat(dfs, ignore_index=True)
    concat.to_csv(output_path / "data.csv", index=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unpack and combine CSV files.")
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)

    args = parser.parse_args()

    unpack_data(args.input_dir, args.output_file)
