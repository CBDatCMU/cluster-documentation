# Intro to Flyte

Flyte is an open-source, cloud-native workflow orchestration platform designed for building scalable, reproducible, and maintainable data and machine learning pipelines. Originally developed at Lyft, Flyte is now a graduated CNCF (Cloud Native Computing Foundation) project and is widely used in production environments for scientific computing and ML workflows.

Unlike shell-based workflow tools, Flyte workflows are written in Python using the `flytekit` SDK, with tasks defined as decorated functions. Flyte handles scheduling, retries, versioning, and resource allocation automatically.

## Why Flyte is Useful for HPC

Flyte addresses several challenges common in HPC and computational biology environments:

- **Reproducibility**: every task execution is versioned and tracked, including inputs, outputs, and container images, making results fully reproducible
- **Scalability**: workflows can fan out across many nodes simultaneously, making it well suited for data-parallel workloads common in bioinformatics and ML
- **Fault tolerance**: built-in retry logic and checkpointing mean a failed node does not restart the entire pipeline
- **Resource specification**: each task declares its own CPU, memory, and GPU requirements, enabling fine-grained resource allocation
- **Data lineage**: Flyte tracks all inputs and outputs as typed artifacts, providing a complete audit trail of how results were produced
- **SLURM integration**: Flyte can submit tasks to SLURM via the `flyteplugins` backend, allowing it to act as a high-level orchestrator on top of the cluster scheduler

---

## Installing Flyte

Flyte workflows are authored using the `flytekit` Python SDK. Load Miniconda3 and create a dedicated environment:

```bash
module load miniconda3
conda create -n flyte python=3.11
conda activate flyte
```

Install `flytekit`:

```bash
pip install flytekit
```

Confirm the installation:

```bash
pyflyte --version
```

---

## Basic Concepts

| Concept | Description |
|---|---|
| **Task** | A single unit of computation, defined as a Python function decorated with `@task` |
| **Workflow** | A composition of tasks that defines execution order and data flow |
| **LaunchPlan** | A versioned, schedulable entry point for a workflow with fixed inputs |
| **FlyteAdmin** | The control plane that manages workflow registration, scheduling, and execution |
| **Propeller** | The execution engine that drives task scheduling and monitors task state |

---

## Example Workflow 1: Hello World

A minimal workflow that takes a name and returns a greeting.

**hello.py:**

```python
from flytekit import task, workflow

@task
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@workflow
def hello_workflow(name: str = "Lane Cluster") -> str:
    return say_hello(name=name)
```

Run locally to test:

```bash
pyflyte run hello.py hello_workflow --name "Lane Cluster"
```

---

## Example Workflow 2: Data Processing Pipeline

A pipeline that reads a list of values, squares each one in parallel, and returns the results.

**pipeline.py:**

```python
from typing import List
from flytekit import task, workflow

@task
def square(x: float) -> float:
    return x ** 2

@task
def summarize(values: List[float]) -> float:
    return sum(values)

@workflow
def processing_pipeline(inputs: List[float]) -> float:
    squared = [square(x=v) for v in inputs]
    return summarize(values=squared)
```

Run locally:

```bash
pyflyte run pipeline.py processing_pipeline --inputs '[1.0,2.0,3.0,4.0]'
```

---

## Example Workflow 3: Bioinformatics Task with Resource Requests

Flyte tasks can declare CPU, memory, and GPU requirements using `Resources`.

**align.py:**

```python
from flytekit import task, workflow, Resources

@task(requests=Resources(cpu="16", mem="32Gi"), limits=Resources(cpu="16", mem="32Gi"))
def align_reads(reads: str, index: str) -> str:
    import subprocess
    output = "aligned.bam"
    subprocess.run(
        ["hisat2", "-x", index, "-U", reads, "|", "samtools", "view", "-bS", "-", "-o", output],
        check=True,
        shell=False,
    )
    return output

@workflow
def alignment_workflow(reads: str, index: str) -> str:
    return align_reads(reads=reads, index=index)
```

---

## Running Flyte Workflows on the Cluster with SLURM

When a Flyte backend is configured with the SLURM plugin, tasks are submitted as SLURM jobs automatically. A SLURM batch script is still needed to launch the `pyflyte run` command itself from a login or head node:

**run_flyte.sh:**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=01:00:00
#SBATCH --mem=4G
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate flyte

pyflyte run --remote pipeline.py processing_pipeline --inputs '[1.0,2.0,3.0,4.0]'
```

Submit the job:

```bash
sbatch run_flyte.sh
```

---

## Best Practices

- Define resource requirements (`cpu`, `mem`, `gpu`) on every `@task` so Flyte can schedule them accurately on the cluster.
- Use typed inputs and outputs — Flyte's type system catches mismatches before execution begins.
- Use `@dynamic` workflows for variable fan-out patterns where the number of parallel tasks is not known at compile time.
- Cache task outputs with `cache=True` and `cache_version` to avoid recomputing identical work across runs:

```python
@task(cache=True, cache_version="1.0")
def expensive_computation(x: float) -> float:
    ...
```

- Register workflows with `pyflyte register` before using `LaunchPlan` scheduling so all versions are tracked in FlyteAdmin.
- Use `flytekit.current_context().working_directory` for temporary file I/O within tasks rather than hardcoded paths.

---

## References

- Flyte documentation: [https://docs.flyte.org]
- flytekit SDK reference: [https://docs.flyte.org/projects/flytekit/en/latest/]
- Flyte GitHub repository: [https://github.com/flyteorg/flyte]
- CNCF project page: [https://www.cncf.io/projects/flyte/]
