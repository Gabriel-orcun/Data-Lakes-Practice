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

def assing_splits(group_starts, group_sizes , n_samples):
    assignments = np.zeros(n_samples , dtype=np.int64)
    n_groups = len(group_starts)
    for g in range(n_groups):
        start = group_starts[g]
        size = group_sizes[g]
    return assignments
def preprocess_data(data_file: str, output_dir: str) -> None:
    """
"""






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess Pfam data.")
    parser.add_argument("--data_file", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)

    args = parser.parse_args()

    preprocess_data(args.data_file, args.output_dir)
