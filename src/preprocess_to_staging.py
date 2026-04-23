import argparse
from pathlib import Path
import time
import io
import boto3
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import numpy as np
from numba import njit

import pandas as pd

@njit
def assing_splits(group_starts, group_sizes , n_samples):
    assignments = np.zeros(n_samples , dtype=np.int64)
    n_groups = len(group_starts)
    for g in range(n_groups):
        start = group_starts[g]
        size = group_sizes[g]

        if size == 1:
            assignments[start] = 0
        elif size == 2:
            assignments[start] = 0
            assignments[start + 1] =1
        elif size == 3:
            assignments[start] = 0
            assignments[start + 1] = 1
            assignments[start + 2] = 2
        else:
            n_val = max(1, int(0.1 * size))
            n_test = max(1, int(0.1 * size))
            
            for j in range(size):
                if j < n_val:
                    assignments[start + j] = 1  
                elif j < (n_val + n_test):
                    assignments[start + j] = 2  
                else:
                    assignments[start + j] = 0  
    return assignments
def preprocess_data(bucket_raw: str, bucket_staging: str, input_file:str, output_prefix: str) -> None:
    """
    Preprocess Pfam data from S3 and upload to staging.
    """
    s3 = boto3.client('s3' , endpoint_url='http://localhost:4566')

    # Step 1 : Download from S3
    reponse = s3.get_object(Bucket=bucket_raw, Key=input_file)
    data = pd.read_csv(io.BytesIO(reponse['Body'].read()))

    # Step 2: clean
    data = data.dropna()    #Step 3: encode labels
    label_encoder = LabelEncoder()
    data['class_encoded'] = label_encoder.fit_transform(data['family_accession'])

    #Step 4: sort
    data_sorted = data.sort_values('class_encoded').reset_index(drop=True)

    # Step 5: compute group boundaries
    class_ids = data_sorted['class_encoded'].values
    unique_classes , counts = np.unique(class_ids , return_counts=True)
    starts = np.cumsum(counts) - counts
    starts = starts.astype(np.int64)
    counts = counts.astype(np.int64)

    # Step 6: numba-accelerated split
    # Warm-up (first call compiles the function)
    _ = assing_splits(starts[:10] , counts[:10], int(counts[:10].sum()))
    start_time = time.perf_counter()
    assignements = assing_splits(starts , counts , len(data_sorted))
    t_numba = time.perf_counter() - start_time
    print(f"Numba split : {t_numba:.3f}s")    # Step 7: split dataframe
    train_data = data_sorted[assignements == 0].drop(
        columns = ["family_id", "sequence_name", "family_accession"])
    dev_data = data_sorted[assignements == 1].drop(
        columns = ["family_id", "sequence_name", "family_accession"])
    test_data = data_sorted[assignements == 2].drop(
        columns = ["family_id", "sequence_name", "family_accession"])    # Step 8: upload to staging
    for name , df in [("train", train_data), ("dev", dev_data), ("test", test_data)]:
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        s3.put_object(
            Bucket=bucket_staging,
            Key=f"{output_prefix}_{name}.csv",
            Body=buf.getvalue()
        )
        print(f"{name} uploaded to staging. ")
    # unpload label_mapping and class_weights as in tp1






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess Pfam data to staging.")
    parser.add_argument("--bucket_raw", type=str, required=True, help="S3 bucket name for raw data")
    parser.add_argument("--bucket_staging", type=str, required=True, help="S3 bucket name for staging")
    parser.add_argument("--input_file", type=str, required=True, help="Input file name in raw bucket")
    parser.add_argument("--output_prefix", type=str, required=True, help="Output prefix for staging files")

    args = parser.parse_args()

    preprocess_data(args.bucket_raw, args.bucket_staging, args.input_file, args.output_prefix)
