import argparse
from pathlib import Path
import glob
import os
import time
import boto3
import io
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

MAX_WORKER = 4

def read_single_csv(filepath: str):
    data = pd.read_csv(filepath)
    return data

def unpack_data(input_dir: str,bucket_name:str, output_file_name: str) -> None:
    """
    """
    input_path = Path(input_dir)
    s3 = boto3.client('s3' , endpoint_url='http://localhost:4566')

    csv_files = []

    path_files = [f'{input_path}/dev' , f'{input_path}/test' , f'{input_path}/train']
    for path in path_files:
        for file in glob.glob(f'{path}/*'):
            csv_files.append(file)
    start = time.perf_counter()
    with ThreadPoolExecutor() as executor:
        dataframes = executor.map(read_single_csv , csv_files)

    data = pd.concat(dataframes, ignore_index=True)

    end = time.perf_counter()

    csv_buffer = io.StringIO()

    data.to_csv(csv_buffer, index=False)

    s3.put_object(
        Bucket=bucket_name,
        Key=output_file_name,
        Body=csv_buffer.getvalue()
    )

    print(f"Parallele : {end - start}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unpack and combine CSV files.")
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--bucket_name", type=str, required=True)
    parser.add_argument("--output_file_name", type=str, required=True)
    args = parser.parse_args()

    unpack_data(args.input_dir, args.bucket_name ,  args.output_file_name)
