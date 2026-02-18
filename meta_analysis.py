"""
Refined Manual MKDAChi2 Meta-Analysis Script
-------------------------------------------
- Supports CSV (Neurosynth-style) or Python structure
- Proper contrast handling
- Monte Carlo null (10,000 iterations)
- FDR correction (BH, alpha=0.05)
- Saves corrected NIfTI map
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from nimare.dataset import Dataset
from nimare.meta.cbma.mkda import MKDADensity
from nimare.correct import FDRCorrector
from nilearn import plotting


# =====================================================
# INPUT OPTIONS
# =====================================================

CSV_FILE = "nimare_ready.csv"  # Example: "nimare_ready.csv"


MANUAL_DATA = [
    {
        "study_id": "study1",
        "analysis_id": "analysis1",
        "peaks": [
            {"x": 30, "y": -22, "z": 50, "t": 4.1},
            {"x": 32, "y": -20, "z": 48, "t": 3.8},
        ]
    },
    {
        "study_id": "study2",
        "analysis_id": "analysis1",
        "peaks": [
            {"x": -40, "y": 12, "z": 28, "t": 5.2},
        ]
    }
]


# =====================================================
# DATA LOADER
# =====================================================

def load_manual_coordinates(data=None, csv_file=None):

    if csv_file:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip()

        required = {"study_id", "x", "y", "z"}
        if not required.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required}")

        # Clean whitespace (important — you have trailing spaces like Study8_T8 )
        df["study_id"] = df["study_id"].str.strip()

        # Split into study + contrast
        split_ids = df["study_id"].str.split("_", n=1, expand=True)

        df["id"] = split_ids[0]           # Study8
        df["contrast_id"] = split_ids[1]  # T8

        df["space"] = "MNI"

        df = df.dropna(subset=["x", "y", "z"])

        for col in ["x", "y", "z"]:
            df[col] = pd.to_numeric(df[col], errors="raise")

        df = df[np.isfinite(df["x"]) & np.isfinite(df["y"]) & np.isfinite(df["z"])]
        df = df.drop_duplicates(subset=["id", "contrast_id", "x", "y", "z"])


        return df[["id", "contrast_id", "x", "y", "z", "space"]]

# =====================================================
# DF --> NIMARE CONVERTER
# =====================================================
def dataframe_to_nimare(df):
    """
    Convert coordinate DataFrame into NiMARE dictionary format.
    Required columns:
        id
        contrast_id
        x, y, z
        space
    """

    nimare_dict = {}

    for study_id in df["id"].unique():

        study_df = df[df["id"] == study_id]
        nimare_dict[study_id] = {"contrasts": {}}

        for contrast_id in study_df["contrast_id"].unique():

            contrast_df = study_df[study_df["contrast_id"] == contrast_id]

            nimare_dict[study_id]["contrasts"][contrast_id] = {
                "coords": {
                    "space": contrast_df["space"].iloc[0],
                    "x": contrast_df["x"].tolist(),
                    "y": contrast_df["y"].tolist(),
                    "z": contrast_df["z"].tolist(),
                }
            }

    return Dataset(nimare_dict)


# Runs the multilevel kernel density analysis. Potential for other meta analysis methods to be added later.
# =====================================================
# MKDA + FDR PIPELINE
# =====================================================

def run_mkda_fdr_manual(data=None, csv_file=None):

    df = load_manual_coordinates(data=data, csv_file=csv_file)

    if df.empty:
        raise RuntimeError("No coordinates loaded.")

    print(f"Loaded {len(df)} coordinates")
    print(f"{df['id'].nunique()} studies")
    print(f"{df['contrast_id'].nunique()} contrasts")

    dataset = dataframe_to_nimare(df)

    mkda = MKDADensity(  # VERY IMPORTANT: ADJUST  METHOD, ITERATIONS, AND KERNEL VARIABLES
        kernel__r=10,
        kernel__value=1,
        null_method="montecarlo",
        n_iters=10000
    )

    print("Running MKDADensity...")
    results = mkda.fit(dataset)

    print("Applying FDR correction (BH, alpha=0.05)...")
    corrector = FDRCorrector(method="indep", alpha=0.05)
    corrected = corrector.transform(results)


    # Get corrected z-map dynamically
    print("Available maps:", corrected.maps.keys())

    z_map = corrected.get_map("z")  # corrected z

    output_file = "mkda_manual_fdr_z.nii.gz"
    z_map.to_filename(output_file)

    print(f"Saved corrected map to: {output_file}")

    plotting.plot_glass_brain(
        z_map,
        display_mode="lyrz",
        colorbar=True,
        title="MKDA Chi2 (FDR 0.05, 10k MC)"
    )

    plt.show()


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    run_mkda_fdr_manual(
        data=MANUAL_DATA,
        csv_file=CSV_FILE
    )
