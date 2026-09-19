# Philippine Customs 2015 Dataset Analysis

A Python pipeline that loads the 2015 Philippine Customs dataset, verifies its integrity, aggregates dutiable value by origin country and `tq`, runs consistency checks, and produces summary tables and charts.

## Dataset Information
- **Filename:** `2015.csv`
- **Source URL:** BetterGov.PH / Philippine Customs
- **Download Date:** September 12, 2026
- **File Size:** 493.5 MB (493,500,000 bytes)
- **SHA-256 Hash:** `b3b5a3a95340179a716a05611d51ad4906484d38363d1ac36494a404c04e4370`
- **Expected rows:** 2,236,612
- **Expected sum of `dutiablevaluephp`:** 3,587,267,375,257.0

The dataset is too large for GitHub, so it is **not included** in this repository.

## Requirements
- Python 3.10 or newer
- Git
- Enough free RAM to hold the full CSV in memory (about 4 GB is a safe estimate)
- Dependencies listed in `requirements.txt` (pandas, numpy, matplotlib, seaborn, jupyter, nbconvert)

## Setup & Running

### 1. Clone the repository
```bash
git clone https://github.com/sebastiandeguzman-ai/ph-custom-analysis.git
cd ph-custom-analysis
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the dataset
1. Go to the [BetterGov.PH](https://huggingface.co/datasets/bettergovph/open-customs-data/tree/main/yearly/csv) page and download `2015.csv` (the folder contains other years too, so make sure you pick 2015).
2. Place it in the `data/` folder so the path is `data/2015.csv`.

You don't need to verify the file by hand. The pipeline checks the SHA-256 hash itself and stops if it doesn't match. To check manually anyway:
```bash
# macOS / Linux
sha256sum data/2015.csv

# Windows (PowerShell)
Get-FileHash data\2015.csv -Algorithm SHA256
```

### 5. Run the pipeline
Run this from the **repository root** (the folder containing `main.py`):
```bash
python main.py
```
Loading and hashing a ~500 MB file takes a while, so expect the first phase to be the slowest.

## What the Pipeline Does

| Phase | What happens |
|-------|--------------|
| 1. Load | Confirms the file exists, verifies the SHA-256 hash, loads the CSV, and checks required columns, row count, and the sum of `dutiablevaluephp`. Also logs nulls, duplicate rows, and negative values. |
| 2. Process | Adds `duty_per_weight` and `high_value_flag` (top 25% by dutiable value), then groups by origin country and by origin country × `tq`. |
| 3. Reshape | Builds a pivot table (country × `tq`) and a top-10 countries table. |
| 3. Validate | Cross-checks row counts and sums between the raw data, grouped table, and pivot. Exits with an error if any check fails. |
| 4. Visualize | Saves a bar chart and a heatmap. |

## Outputs
All results are written to the `outputs/` folder (created automatically):

| File | Description |
|------|-------------|
| `grouped.csv` | Row count, valid count, sum, and mean of dutiable value per origin country |
| `grouped_two.csv` | Row count and sum per origin country × `tq` |
| `pivot.csv` | Pivot table of dutiable value (country × `tq`) with totals |
| `top10.csv` | Top 10 origin countries by total dutiable value |
| `validation.csv` | Result of each validation check (expected, actual, tolerance, pass/fail) |
| `audit_log.csv` | Step-by-step log of the pipeline operations |
| `bar.png` | Top 10 origin countries by dutiable value (billions PHP) |
| `heatmap.png` | Dutiable value heatmap by origin country and `tq` |

## Project Structure
```
ph-custom-analysis/
├── data/
│   └── 2015.csv          # download separately (not tracked by git)
├── outputs/              # generated results (created on first run)
├── src/
│   ├── __init__.py
│   ├── config.py         # paths and expected reference values
│   ├── loader.py         # loading, checksum, and data-quality checks
│   ├── processor.py      # feature engineering, grouping, pivot, top 10
│   ├── validator.py      # validation.csv and audit_log.csv
│   └── visualizer.py     # charts (also has an alternate standalone pipeline)
├── main.py               # entry point
├── requirements.txt
└── README.md
```

## Configuration
Paths and reference values live in `src/config.py`:
- `DATA_PATH`: location of the CSV (default `data/2015.csv`)
- `OUTPUT_DIR`: where results are saved (default `outputs`)
- `EXPECTED_SHA256`, `EXPECTED_RAW_ROWS`, `EXPECTED_RAW_SUM`: reference values used for verification

## Optional: Run Individual Modules
```bash
# Only load and verify the dataset
python -m src.loader

# Alternate end-to-end run that also prints a pandas vs. NumPy sum benchmark
python -m src.visualizer
```

## Troubleshooting
- **`FileNotFoundInProjectError`**: `data/2015.csv` is missing. Redo step 4 and make sure you run from the repo root.
- **`ChecksumMismatchError`**: the file is corrupted, incomplete, or a different version. Re-download it.
- **`ModuleNotFoundError: No module named 'src'`**: run `python main.py` from the repository root, not from inside `src/`.
- **`ModuleNotFoundError` for pandas, seaborn, etc.**: activate your virtual environment and rerun `pip install -r requirements.txt`.
- **`MemoryError` or very slow runs**: close other programs; the full CSV is loaded into memory at once.
- **`FAILED CHECK: ...` and the script exits with code 1**: a validation check failed. See `outputs/validation.csv` for expected vs. actual values.
- **`TypeError` or `SyntaxError` on startup**: check that you are using Python 3.10 or newer (`python --version`).
