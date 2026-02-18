# MKDA Chi-squared Coordinate Based Meta Analysis Pipeline

# Overview
The repository provides a reproducible implementation of Multilevel Kernel Density Analysis (MKDA Chi-squared)
for coordinate based meta-analysis (CBMA) of neuroimaging studies. The pipeline is implemented in Python using
* NiMARE
* Nilearn
* A virtual environment
The workflow supports structured CSV input (neurosynth-style) or Python defined coordinate data.
It performs:
1. Construction of a NiMARE Dataset
2. MKDA density estimation
3. Monte-Carlo based null inference with 10,000 iters
4. False Discovery Rate (FDR) correction using the Benjamini-Hochberg procedure
5. Export of corrected statistical maps in NIfTI format
### Intended for transparent, extensible, and fully script-based CBMA research.

# Theoretical Background
## Coordinate Based Meta-Analysis (CBMA)
CBMA aggregates reported peak activation coordinates from independant neuroimaging studies to identify spatial
convergence across experiments. Unlike image-based meta analyisis, CBMA relies solely on reported peak coordinates
in standardized stereotaxic space (MNI coordinates).
## Multilevel Kernel Density analysis (MKDA)
MKDA is a random-effects CBMA method in which:
* Each contrast contributes a binary indicator map derived from spherical kernels placed at reported coordinates.
* Study level contributions are modeled to avoid within-study clustering bias.
* Statistical inference is performed against a null distribution generated via spatial permutation.
In this implementation, MKDA is computed via:
      MKDADensity(
          kernel__r=10,
          kernel__value=1,
          null_method="montecarlo",
          n_iters=10000
      )
Null distributions are estimated using 10,000 Monte Carlo iterations.

# Multiple Comparisons Correction
Voxel-wise inference is corrected using False Discovery Rate (FDR) control:
      FDRCorrector(method="indep", alpha=0.05)
This corresponds to the Benjamini-Hochberg procedure under independence assumptions

# Repository Structure
.

├── mkda_manual.py

├── test_nimare_environment.py

├── nimare_ready.csv, or the intended .csv file

└── README.md
## mkda_manual.py
Primary analysis pipeline.
* Loads coordinate data
* Converts to NiMARE dataset
* Runs MKDA
* Applies FDR correction
* Saves corrected Z-statistic Map
## test_nimare_environment.py
Environment validation script that:
* Confirms package versions
* Runs a minimal MKDA analysis
* Saves a test NIfTI file
* Displays a glass brain visualization

# Input data Format
## CSV (recommended)
Required columns: study_id,x,y,z
Conventions:
* study_id should encode study and contrast (e.g Study8_T8)
* Coordinates must be in MNI space
* Duplicate coordinates automatically removed
* Missing or non-numeric values excluded.
Example:

    Study1_T1,30,-22,50
    Study1_T1,32,-20,48
    Study2_T1,-40,12,28
  
## Python Data Structure
Alternatively, coordinates may be passed as a structured Python object:

  MANUAL_DATA = [
      {
          "study_id": "study1",
          "analysis_id": "analysis1",
          "peaks": [
              {"x": 30, "y": -22, "z": 50, "t": 4.1}
          ]
      }
  ]

# Installation
It is recommended to run the pipeline inside a dedicated virtual environment.

python -m venv nimare_env
source nimare_env/bin/activate
pip install nimare nilearn pandas numpy matplotlib

# Execution 
To run the full MKDA analysis:
  python mkda_manual.py
Output:
  mkda_manual_fdr_z.nii.gz
The script will:
* Print study and contrast counts
* Run Monte Carlo inference
* Apply FDR correction
* Save a corrected Z-map
* Display a glass brain visualization

# Output
Primary output: Voxel-wise FDR-corrected Z-statistic map (.nii.gz)
The NIfTI file can be opened in neuroimaging software such as FSL, SPM, AFNI, or Nilearn-based viewers.

# Reproducibility
All parameters governing:
* Kernel radius
* Null Estimation method
* Monte Carlo iteration count
* FDR threshold
are explicitly defined within the script to ensure computational transparency.
To verify environment reproducibility:
  python test_nimare_environment.py

# Methodological Considerations
* Coordinates must be reported in MNI space
* MKDA is a random-effects method and assumes independance across studies
* Monte Carlo null estimation runtime scales with iteration count and dataset size
* FDR correction assumes independence or positive dependence across tests.
Users should report:
* Kernel radius
* Number of iterations
* Correction method
* Statistical threshold
* Number of included studies and contrasts
in any resulting publication.

# Citation
If using this pipeline in academic work, please cite:
* NiMARE
* The original MKDA methodological publication
Additionally, cite any dataset sources used in the meta-analysis.

# Intended Use
This repository is designed for:
* Research reproducibility
* Methods development
* Transparent CBMA workflows
* Extension to alternative CBMA methods (e.g., ALE)


