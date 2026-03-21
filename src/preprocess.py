import argparse
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

import pandas as pd


def preprocess_data(data_file: str, output_dir: str) -> None:
    """
    Preprocess raw protein sequence data for model training.

    This function loads the raw data, cleans it, encodes labels, and splits
    it into train/validation/test sets. The split strategy must handle the
    extreme class imbalance in the Pfam dataset.

    Parameters
    ----------
    data_file : str
        Path to the combined raw data CSV file.
    output_dir : str
        Directory where processed files will be saved.

    Steps
    -----
    1. Load the data with pandas
    2. Remove rows with missing values
    3. Encode the 'family_accession' column with LabelEncoder
    4. Design and implement a split strategy that handles class imbalance
    5. Save train.csv, val.csv, and test.csv to output_dir

    Notes
    -----
    sklearn's train_test_split with stratify will fail on this dataset
    because some classes have only one sample. You need to implement
    a custom strategy.
    """
    data_path = Path(data_file)
    output_path = Path(output_dir)


    data = pd.read_csv(data_path)
    data = data.dropna()

    # Label Encoding
    le = LabelEncoder()
    data["family_accession"] = le.fit_transform(data["family_accession"])

    # Séparer normal / rare
    counts = data["family_accession"].value_counts()
    normal = data[data["family_accession"].isin(counts[counts > 5].index)]
    rare = data[data["family_accession"].isin(counts[counts <= 5].index)]

    # Split normal
    train, temp = train_test_split(
        normal, test_size=0.4, random_state=42,
        stratify=normal["family_accession"]
    )

    test, val = train_test_split(
        temp, test_size=0.5, random_state=42,
        stratify=temp["family_accession"]
    )

    # Ajouter les "rare" au train
    train = pd.concat([train, rare], ignore_index=True)

    train.to_csv(output_path / "train.csv", index=False)
    test.to_csv(output_path / "test.csv", index=False)
    val.to_csv(output_path / "validation.csv", index=False)
    






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess Pfam data.")
    parser.add_argument("--data_file", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)

    args = parser.parse_args()

    preprocess_data(args.data_file, args.output_dir)
