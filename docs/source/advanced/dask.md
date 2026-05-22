# Dask

Dask is a flexible Python library for parallel and distributed computing. It scales familiar Python interfaces — NumPy, Pandas, and scikit-learn — from a single laptop to a large HPC cluster with minimal code changes. On the Lane Cluster, Dask is particularly useful for benchmarking memory and compute performance across nodes.

## Loading Miniconda3

Miniconda3 is available as a module on the Lane Cluster. Load it using:

```bash
module load miniconda3
```

## Creating a Dask Environment

Create a dedicated conda environment for Dask:

```bash
conda create -n dask python=3.11
```

Activate the environment:

```bash
conda activate dask
```

## Installing Dask

With the environment active, install Dask and optional dependencies:

```bash
conda install -c conda-forge dask distributed bokeh
```

- `dask` — core library with array, dataframe, and bag collections
- `distributed` — scheduler for multi-node parallel execution
- `bokeh` — enables the Dask diagnostic dashboard

Confirm the installation:

```python
python -c "import dask; print(dask.__version__)"
```

---

## Basic Concepts

Dask has two layers:

- **Collections**: high-level interfaces (`dask.array`, `dask.dataframe`, `dask.bag`) that mirror NumPy, Pandas, and itertools but operate lazily — computations are only executed when `.compute()` is called.
- **Schedulers**: execute the task graph. The `distributed` scheduler supports multi-process and multi-node execution and provides a live dashboard at `http://localhost:8787`.

---

## Example 1: Benchmarking Array Operations

Compare the time to perform a large matrix multiplication using NumPy versus Dask.

**benchmark_array.py:**

```python
import time
import numpy as np
import dask.array as da

size = 10_000

# NumPy benchmark
x_np = np.random.random((size, size))
start = time.perf_counter()
result_np = np.dot(x_np, x_np)
np_time = time.perf_counter() - start
print(f"NumPy:  {np_time:.2f}s")

# Dask benchmark
x_da = da.random.random((size, size), chunks=(2000, 2000))
start = time.perf_counter()
result_da = da.dot(x_da, x_da).compute()
dask_time = time.perf_counter() - start
print(f"Dask:   {dask_time:.2f}s")
print(f"Speedup: {np_time / dask_time:.2f}x")
```

Run the benchmark:

```bash
python benchmark_array.py
```

**SLURM batch script (`run_benchmark_array.sh`):**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate dask

python benchmark_array.py
```

```bash
sbatch run_benchmark_array.sh
```

---

## Example 2: Benchmarking DataFrame Operations

Compare groupby aggregation performance on a large dataset using Pandas versus Dask.

**benchmark_dataframe.py:**

```python
import time
import numpy as np
import pandas as pd
import dask.dataframe as dd

n_rows = 10_000_000

df_pd = pd.DataFrame({
    "group": np.random.choice(["A", "B", "C", "D"], size=n_rows),
    "value": np.random.random(n_rows),
})

# Pandas benchmark
start = time.perf_counter()
result_pd = df_pd.groupby("group")["value"].mean()
pd_time = time.perf_counter() - start
print(f"Pandas: {pd_time:.2f}s")

# Dask benchmark
df_dd = dd.from_pandas(df_pd, npartitions=16)
start = time.perf_counter()
result_dd = df_dd.groupby("group")["value"].mean().compute()
dask_time = time.perf_counter() - start
print(f"Dask:   {dask_time:.2f}s")
print(f"Speedup: {pd_time / dask_time:.2f}x")
```

Run the benchmark:

```bash
python benchmark_dataframe.py
```

**SLURM batch script (`run_benchmark_dataframe.sh`):**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate dask

python benchmark_dataframe.py
```

```bash
sbatch run_benchmark_dataframe.sh
```

---

## Example 3: Benchmarking with the Distributed Scheduler

Use the `distributed` scheduler to parallelize a CPU-bound task across multiple workers and measure throughput.

**benchmark_distributed.py:**

```python
import time
import numpy as np
from dask.distributed import Client, LocalCluster

def compute_chunk(seed):
    rng = np.random.default_rng(seed)
    x = rng.random((2000, 2000))
    return np.linalg.svd(x, compute_uv=False).sum()

if __name__ == "__main__":
    n_tasks = 16

    # Single-threaded baseline
    start = time.perf_counter()
    results = [compute_chunk(i) for i in range(n_tasks)]
    serial_time = time.perf_counter() - start
    print(f"Serial:      {serial_time:.2f}s")

    # Dask distributed
    cluster = LocalCluster(n_workers=16, threads_per_worker=1)
    client = Client(cluster)
    print(f"Dashboard:   {client.dashboard_link}")

    start = time.perf_counter()
    futures = client.map(compute_chunk, range(n_tasks))
    results = client.gather(futures)
    dask_time = time.perf_counter() - start
    print(f"Distributed: {dask_time:.2f}s")
    print(f"Speedup:     {serial_time / dask_time:.2f}x")

    client.close()
    cluster.close()
```

Run the benchmark:

```bash
python benchmark_distributed.py
```

**SLURM batch script (`run_benchmark_distributed.sh`):**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate dask

python benchmark_distributed.py
```

```bash
sbatch run_benchmark_distributed.sh
```

---

## Example 4: Scaling Across SLURM Nodes

Use `dask-jobqueue` to spawn Dask workers as SLURM jobs and benchmark a large computation across multiple nodes.

Install `dask-jobqueue`:

```bash
conda install -c conda-forge dask-jobqueue
```

**benchmark_slurm.py:**

```python
import time
import dask.array as da
from dask.distributed import Client
from dask_jobqueue import SLURMCluster

cluster = SLURMCluster(
    queue="pool1",
    cores=16,
    memory="8GB",
    walltime="08:00:00",
    job_extra_directives=["--ntasks=16", "--cpus-per-task=1"],
)

cluster.scale(jobs=4)

client = Client(cluster)
print(f"Dashboard: {client.dashboard_link}")

x = da.random.random((20_000, 20_000), chunks=(2000, 2000))

start = time.perf_counter()
result = (x + x.T).mean().compute()
elapsed = time.perf_counter() - start

print(f"Result:  {result:.6f}")
print(f"Elapsed: {elapsed:.2f}s")

client.close()
cluster.close()
```

**SLURM batch script (`run_benchmark_slurm.sh`):**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate dask

python benchmark_slurm.py
```

```bash
sbatch run_benchmark_slurm.sh
```

---

## Best Practices

- Use `dask.array` and `dask.dataframe` when data is too large to fit in memory — Dask will process it in chunks.
- Choose chunk sizes so each chunk fits comfortably in memory (typically 100 MB–1 GB per chunk).
- Use the dashboard (`http://localhost:8787`) to monitor task progress, memory usage, and worker utilization in real time.
- Prefer `client.map()` over loops of `client.submit()` for submitting many tasks of the same type.
- Call `client.close()` and `cluster.close()` at the end of scripts to release SLURM resources promptly.

---

## References

- Dask documentation: [https://docs.dask.org/en/stable/]
- Dask distributed: [https://distributed.dask.org/en/stable/]
- dask-jobqueue: [https://jobqueue.dask.org/en/latest/]
