# Reproducibility package

This package accompanies the Matters Arising "Diagnosis-conditional concept labels undermine dermatologist-like AI explanations of melanoma" by Gonzalo Nápoles and Isel Grau. The Matters Arising responds to Chanda et al., Nature Communications 15, 524 (2024).

## Contents

| File | Purpose |
| --- | --- |
| `01_reproduce_manuscript.ipynb` | Reproduces every number, Table 1 and Figure 1 of the manuscript, with one assertion per check (41 checks) |
| `02_supplementary_evidence.ipynb` | Analyses behind the manuscript that did not fit in its word limit |
| `make_figure1.py` | Standalone script that redraws Figure 1 and writes its source data |
| `source_data/` | Source data of Table 1 and Figure 1 |
| `requirements.txt` | Python packages with pinned versions |

## Data

We use the public files that Chanda et al. released on Figshare. Download `metadata_gt.csv` and `Datasets.zip` into a folder named `data` next to this folder, or set the environment variable `CHANDA_DATA` to another location. The code unzips `Datasets.zip` on its first run.

## Usage

We tested the code with Python 3.12.

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace 01_reproduce_manuscript.ipynb
jupyter nbconvert --to notebook --execute --inplace 02_supplementary_evidence.ipynb
python make_figure1.py ../data source_data
```

Each notebook runs in a few seconds and stops at the first value that differs from the manuscript. The last section of the first notebook lists all checks with the computed and reported values.
