"""
NiMARE MKDA Environment Test
----------------------------
Verifies:
- NiMARE installation
- MKDADensity estimator
- FDRCorrector
- Nilearn plotting
- End-to-end minimal MKDA run
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import nimare
import nilearn

from nimare.dataset import Dataset
from nimare.meta.cbma.mkda import MKDADensity
from nimare.correct import FDRCorrector
from nilearn import plotting


print("NiMARE version:", nimare.__version__)
print("Nilearn version:", nilearn.__version__)
print("NumPy version:", np.__version__)
print("Pandas version:", pd.__version__)


# ---------------------------------------------------
# Minimal Test Dataset (very small)
# ---------------------------------------------------

test_dict = {
    "study1": {
        "contrasts": {
            "contrast1": {
                "coords": {
                    "space": "MNI",
                    "x": [30, 32],
                    "y": [-22, -20],
                    "z": [50, 48],
                }
            }
        }
    },
    "study2": {
        "contrasts": {
            "contrast1": {
                "coords": {
                    "space": "MNI",
                    "x": [-40],
                    "y": [12],
                    "z": [28],
                }
            }
        }
    },
}

print("\nCreating NiMARE Dataset...")
dataset = Dataset(test_dict)
print("Dataset created successfully.")


# ---------------------------------------------------
# Run MKDADensity (small iteration count for testing)
# ---------------------------------------------------

print("\nRunning MKDADensity (test mode, 10 iterations)...")

mkda = MKDADensity(
    kernel__r=10,
    kernel__value=1,
    null_method="montecarlo",
    n_iters=10,  # keep small for environment test
)

results = mkda.fit(dataset)

print("MKDADensity completed.")


# ---------------------------------------------------
# Apply FDR correction
# ---------------------------------------------------

print("\nApplying FDR correction...")

corrector = FDRCorrector(method="indep", alpha=0.05)
corrected = corrector.transform(results)

print("Available maps:", corrected.maps.keys())

z_map = corrected.get_map("z")

print("Z-map successfully generated.")


# ---------------------------------------------------
# Save test output
# ---------------------------------------------------

output_file = "mkda_test_output.nii.gz"
z_map.to_filename(output_file)

print(f"Test NIfTI file saved: {output_file}")


# ---------------------------------------------------
# Optional: quick glass brain visualization
# ---------------------------------------------------

print("\nDisplaying glass brain (close window to finish test)...")

plotting.plot_glass_brain(
    z_map,
    display_mode="lyrz",
    colorbar=True,
    title="MKDA Test (FDR)"
)

plt.show()

print("\nEnvironment test completed successfully.")
