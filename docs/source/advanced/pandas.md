# Intro to Pandas

![Pandas logo](../_static/images/pandas.png)

Pandas is the most widely used Python library for data manipulation and analysis. It provides two core data structures — `DataFrame` (a two-dimensional table) and `Series` (a single column) — along with a rich set of tools for loading, cleaning, reshaping, aggregating, and exporting tabular data. Pandas is built on top of NumPy and integrates naturally with the broader scientific Python ecosystem, including Matplotlib, Seaborn, Scikit-learn, and Polars.

On the Lane Cluster, Pandas is commonly used for preprocessing datasets before statistical analysis or machine learning, merging experimental results across files, and exploratory data analysis in Jupyter notebooks or batch scripts.

## What Is Pandas Useful For?

- **Data ingestion**: read data from CSV, Excel, JSON, Parquet, SQL databases, and HDF5 files with a single function call
- **Data cleaning**: handle missing values, rename columns, fix data types, remove duplicates, and filter outliers
- **Data transformation**: reshape wide data to long format (and back), merge multiple tables, compute derived columns, and apply custom functions row- or column-wise
- **Aggregation**: group data by one or more keys and compute summary statistics (mean, std, count, percentiles) per group
- **Time series**: resample, roll, and shift time-indexed data for temporal analysis
- **Integration**: export results to any format and pass DataFrames directly to plotting libraries and ML frameworks

---

## Loading Miniconda3

Miniconda3 is available as a module on the Lane Cluster. Load it using:

```bash
module load miniconda3
```

## Creating a Pandas Environment

Create a dedicated conda environment for Pandas:

```bash
conda create -n pandas python=3.11
```

Activate the environment:

```bash
conda activate pandas
```

## Installing Pandas

With the environment active, install Pandas and common companions via conda-forge:

```bash
conda install -c conda-forge pandas numpy matplotlib seaborn
```

Confirm the installation:

```{jupyter-execute}
import pandas as pd
print(pd.__version__)
```

---

## Basic Concepts

- **DataFrame**: a two-dimensional, labeled data structure with columns of potentially different types. Think of it as a spreadsheet or SQL table in memory.
- **Series**: a one-dimensional labeled array. Each column of a DataFrame is a Series.
- **Index**: the row labels of a DataFrame or Series. By default this is an integer range, but it can be set to any unique values (sample IDs, timestamps, gene names).
- **NaN**: Pandas uses `float('nan')` (via NumPy) to represent missing values. Most Pandas operations skip or propagate NaN by default.
- **Vectorized operations**: Pandas operations apply to entire columns at once using NumPy under the hood, making them much faster than Python loops.

---

## Example 1: Creating and Inspecting a DataFrame

This example shows how to build a Pandas DataFrame from a dictionary and perform the basic inspection steps you would run at the start of any data analysis: checking shape, column types, and summary statistics. These steps help catch data quality issues — unexpected types, missing values, implausible ranges — before they propagate into downstream results.

```{jupyter-execute}
import pandas as pd
import numpy as np

np.random.seed(42)
n = 10  # number of samples

# Build a small DataFrame simulating a biological experiment:
# each row is a sample with a condition label, an expression value, and a read count
df = pd.DataFrame({
    "sample":     [f"S{i:02d}" for i in range(n)],
    "condition":  np.random.choice(["control", "treated"], size=n),
    "expression": np.round(np.random.random(n) * 100, 2),
    "count":      np.random.randint(1, 500, size=n),
})

print(df)
```

Inspect the DataFrame structure and basic statistics:

```{jupyter-execute}
# shape returns (n_rows, n_columns)
print("Shape:", df.shape)

# dtypes shows the inferred type of each column
print("\nData types:")
print(df.dtypes)

# describe() computes count, mean, std, min, 25th/50th/75th percentile, and max
# for all numeric columns
print("\nSummary statistics:")
print(df.describe())
```

---

## Example 2: Filtering, Selecting, and Transforming

This example demonstrates the most common data manipulation operations in Pandas: filtering rows by a condition, selecting a subset of columns, and adding derived columns. These operations form the foundation of most data cleaning and feature engineering workflows. The pattern of chaining these steps together on a copy of the data is a standard Pandas idiom.

```{jupyter-execute}
# Keep only samples with expression above 50
df_filtered = df[df["expression"] > 50].copy()

# Add a normalized ratio: expression per read count
# This is a common normalization step to account for sequencing depth differences
df_filtered["ratio"] = df_filtered["expression"] / df_filtered["count"]

# Select only the columns needed for downstream analysis
df_filtered = df_filtered[["sample", "condition", "expression", "count", "ratio"]]

# Sort by ratio descending to rank samples from highest to lowest normalized expression
df_filtered = df_filtered.sort_values("ratio", ascending=False).reset_index(drop=True)

print(df_filtered)
```

---

## Example 3: Group By and Aggregation

This example shows how to compute per-group summary statistics using `groupby`. In research workflows this is used constantly — computing mean expression per condition, average biomarker level per cohort, or total read counts per sample type. The `agg` method allows multiple aggregations to be computed in a single pass, returning a clean summary table.

```{jupyter-execute}
import pandas as pd
import numpy as np

np.random.seed(0)
n = 100_000  # 100,000 rows to show groupby on a non-trivial dataset

# Simulate a dataset with 8 experimental groups and two numeric measurements
df_large = pd.DataFrame({
    "group":  np.random.choice(list("ABCDEFGH"), size=n),
    "value1": np.random.random(n),
    "value2": np.random.random(n),
})

# Group by the 'group' column and compute multiple statistics per group
summary = (
    df_large
    .groupby("group")[["value1", "value2"]]
    .agg(["mean", "std", "sum", "count"])
)

# Flatten the multi-level column index created by agg for readability
summary.columns = ["_".join(col) for col in summary.columns]
summary = summary.reset_index()

print(summary)
```

---

## Example 4: Handling Missing Data

Missing data is one of the most common data quality problems in research datasets. This example simulates a dataset with randomly missing values in two measurement columns and demonstrates the standard Pandas toolkit for detecting, quantifying, and imputing missing values. Choosing the right imputation strategy — dropping, filling with a constant, or using the column mean/median — depends on how much data is missing and what the missing values represent scientifically.

```{jupyter-execute}
import pandas as pd
import numpy as np

np.random.seed(1)
n = 500

# Simulate a proteomics dataset with ~10% missing values in each protein column
df_missing = pd.DataFrame({
    "sample_id": [f"SMP{i:04d}" for i in range(n)],
    "batch":     np.random.choice(["B1", "B2", "B3"], size=n),
    # Set ~10% of values to NaN to simulate instrument dropouts
    "protein_a": [float(v) if np.random.random() > 0.10 else np.nan
                  for v in np.round(np.random.normal(100, 15, n), 2)],
    "protein_b": [float(v) if np.random.random() > 0.10 else np.nan
                  for v in np.round(np.random.normal(50, 10, n), 2)],
})

# Count missing values per column
print("Missing values per column:")
print(df_missing.isnull().sum())

# Show the fraction missing
print("\nFraction missing:")
print(df_missing.isnull().mean().round(3))

# Strategy 1: drop rows where any protein measurement is missing
df_dropped = df_missing.dropna(subset=["protein_a", "protein_b"])
print(f"\nRows after dropping missing: {len(df_dropped)} / {n}")

# Strategy 2: fill missing values with the column mean
# This preserves all rows and keeps the column mean unchanged
df_filled = df_missing.copy()
df_filled["protein_a"] = df_filled["protein_a"].fillna(df_filled["protein_a"].mean())
df_filled["protein_b"] = df_filled["protein_b"].fillna(df_filled["protein_b"].mean())
print(f"\nRows after mean imputation: {len(df_filled)} / {n}")
print(df_filled.describe().loc[["mean", "std"]])
```

---

## Example 5: Merging and Joining DataFrames

In research pipelines, data is rarely stored in a single table. Sample metadata, experimental measurements, and reference annotations typically live in separate files that need to be combined before analysis. This example simulates joining a patient metadata table onto a biomarker measurements table — the equivalent of a SQL LEFT JOIN — and then computing per-biomarker summaries stratified by diagnosis. This is a foundational pattern in clinical cohort studies.

```{jupyter-execute}
import pandas as pd
import numpy as np

np.random.seed(3)
n_patients = 200

# Metadata table: one row per patient with demographic and clinical information
metadata = pd.DataFrame({
    "patient_id": [f"P{i:04d}" for i in range(n_patients)],
    "age":        np.random.randint(20, 80, size=n_patients),
    "sex":        np.random.choice(["M", "F"], size=n_patients),
    "diagnosis":  np.random.choice(["healthy", "disease"], size=n_patients, p=[0.4, 0.6]),
})

# Measurements table: repeated biomarker measurements per patient
# Not every patient has measurements at every visit — sparse design
measurements = pd.DataFrame({
    "patient_id": [f"P{i:04d}" for i in np.random.choice(n_patients, size=800)],
    "biomarker":  np.random.choice(["CRP", "IL6", "TNF"], size=800),
    "value":      np.round(np.random.exponential(scale=10, size=800), 3),
    "visit":      np.random.randint(1, 5, size=800),
})

# Left merge: keep all measurement rows, attach metadata for each patient_id
# Patients in measurements not found in metadata will have NaN in metadata columns
joined = measurements.merge(metadata, on="patient_id", how="left")

# Compute per-biomarker summary statistics split by diagnosis
summary = (
    joined
    .groupby(["biomarker", "diagnosis"])["value"]
    .agg(mean="mean", std="std", median="median", n="count")
    .round(3)
    .reset_index()
)

print(summary)
```

---

## Example 6: Working with Time Series Data

Temporal data is common in clinical studies, environmental monitoring, and systems biology. Pandas has first-class support for time series via its `DatetimeIndex` and rolling/resampling operations. This example simulates a daily patient score dataset, computes a smoothing rolling mean to reduce noise, and resamples the data to weekly averages — operations that are typically used to prepare longitudinal data before visualization or modelling.

```{jupyter-execute}
import pandas as pd
import numpy as np

np.random.seed(9)
n_days = 365  # one year of daily measurements

# Create a daily DatetimeIndex starting from 2024-01-01
dates = pd.date_range(start="2024-01-01", periods=n_days, freq="D")

# Simulate a clinical score with an upward trend and daily noise
trend = np.linspace(40, 70, n_days)              # gradual improvement over the year
noise = np.random.normal(0, 5, size=n_days)      # day-to-day variability
score = np.round(trend + noise, 2)

df_ts = pd.DataFrame({"score": score}, index=dates)
df_ts.index.name = "date"

# 7-day rolling mean smooths out weekly noise while preserving the trend
# min_periods=1 avoids NaN at the start of the series where fewer than 7 days exist
df_ts["rolling_7d"] = df_ts["score"].rolling(window=7, min_periods=1).mean().round(2)

# Cumulative maximum tracks the best score achieved so far
df_ts["cumulative_max"] = df_ts["score"].cummax()

# Resample from daily to weekly frequency, taking the mean of each week
df_weekly = df_ts["score"].resample("W").mean().round(2).rename("weekly_mean")

print("Daily data (first 10 rows):")
print(df_ts.head(10))

print("\nWeekly resampled data (first 8 weeks):")
print(df_weekly.head(8))
```

---

## Best Practices

- Always call `.copy()` when slicing a DataFrame to assign to a new variable. Modifying a slice without `.copy()` can trigger a `SettingWithCopyWarning` and produce unexpected results.
- Use `.loc[]` for label-based indexing and `.iloc[]` for integer-position indexing. Avoid chained indexing (`df[col][row]`) as it is unreliable for assignment.
- Prefer vectorized operations and `apply` over Python loops. Loops over DataFrame rows are orders of magnitude slower than column-wise operations.
- Use categorical dtypes for low-cardinality string columns (e.g., condition, batch, sex) — they reduce memory usage significantly and speed up `groupby` operations.
- Check for missing values with `df.isnull().sum()` early in a pipeline before aggregating or modelling, as NaN values can silently distort results.
- Use `pd.read_parquet()` and `df.to_parquet()` instead of CSV for large files — Parquet preserves data types, compresses data, and reads much faster.

---

## References

- Pandas documentation: [https://pandas.pydata.org/docs/]
- Pandas user guide: [https://pandas.pydata.org/docs/user_guide/index.html]
- Pandas GitHub: [https://github.com/pandas-dev/pandas]
