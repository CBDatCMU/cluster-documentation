# Spack

![Spack logo](https://raw.githubusercontent.com/spack/spack/refs/heads/develop/share/spack/logo/spack-logo-white-text.svg)

Spack is a multi-platform package manager that builds and installs multiple versions and configurations of software. It works on Linux, macOS, Windows, and many supercomputers. Spack is non-destructive: installing a new version of a package does not break existing installations, so many configurations of the same package can coexist

## Introduction

Spack is a flexible package manager designed specifically for high-performance computing (HPC) environments. Unlike traditional system package managers or Conda, Spack allows users to build, install, and manage multiple versions of scientific software with different compilers, MPI implementations, and build configurations — all side by side.

In HPC systems such as the Lane Cluster, software stacks are often complex:

- Applications depend on specific compiler versions
- MPI libraries must match both hardware and software
- Performance can vary significantly based on build options
- Users frequently need reproducible, isolated environments

Spack addresses these challenges by:

- Explicitly modeling dependencies and build configurations
- Supporting multiple compilers, MPI libraries, and variants
- Allowing reproducible environment definitions via `spack.yaml`
- Avoiding conflicts with system-wide software

On the Lane Cluster, Spack is especially useful for:

- MPI-based scientific applications (e.g., OpenMPI, PETSc)
- Bioinformatics and computational biology tools
- GPU-enabled machine learning frameworks
- Reproducible research workflows shared across users and nodes

---

## Prerequisites

Spack is written in Python and requires a working **Python interpreter (Python 3.6 or newer)** to run.

On most HPC systems, including the Lane Cluster, this requirement is typically satisfied by the system Python. Spack does **not** require Conda and does **not** manage Python environments.

---

## Installing Spack on the Lane Cluster

### Using a system module (recommended)

If Spack is available as a module on the Lane Cluster, load it using:

```bash
module load spack
```

### Confirm that Spack is available

```bash
spack --version
```

If the command returns a version number, Spack has been loaded successfully and is ready for use.

### Installing Spack locally (alternative)

If Spack is not provided as a system module, it can be installed in a user directory without administrative privileges:

```bash
git clone https://github.com/spack/spack.git
cd spack
source share/spack/setup-env.sh
```

To make Spack available in future sessions, add the following line to your shell configuration file (e.g., ~/.bashrc or ~/.zshrc):

source ~/spack/share/spack/setup-env.sh

### Confirm the installation

```bash
spack --version
```

## Basic Usage

### Search for available packages

```bash
spack list
spack search openmpi
```

### Install a package

```bash
spack install openmpi
```

### List installed packages

```bash
spack find
```

### Load a package into the current environment

```bash
spack load openmpi
```

### Unload a package

```bash
spack unload openmpi
```

## Environment Management

Spack environments provide a reproducible way to manage project-specific dependencies.

### Create and activate an environment

```bash
spack env create mpi-env
spack env activate mpi-env
```

### Add packages to the environment

```bash
spack add openmpi
```

### Resolve dependencies and install all packages

```bash
spack concretize
spack install
```

Each environment is defined by a spack.yaml file, which can be shared with collaborators to reproduce the same software stack on other nodes or systems.

## Example Workflow 1: Installing OpenMPI

This example demonstrates installing and testing OpenMPI using Spack on a compute node in pool1.

Request an interactive compute node salloc -p pool1 --time=01:00:00

### Create and activate OpenMPI an environment

```bash
module load spack
spack env create openmpi-env
spack env activate openmpi-env
```

### Install OpenMPI

```bash
spack add openmpi
spack concretize
spack install
```

### Verify the installation

```bash
spack load openmpi
mpirun --version
```

If the command returns a version number, OpenMPI has been built and linked successfully on the compute node.

## Example Workflow 2: Bioinformatics Workflo

**Use case:**  
A researcher needs a reproducible and isolated environment for RNA-seq analysis using tools such as HISAT2, Samtools, and Python scientific libraries.

**Approach:**  
Spack environments are used to define package specifications, resolve complex dependency chains, and install compatible versions in a unified prefix.

```bash
spack env create bio-env
spack env activate bio-env
spack add hisat2 samtools python@3.10 py-biopython py-numpy py-pandas
spack concretize
spack install
```

### Integration with Conda and Apptainer

Spack is designed to complement other software management tools commonly used in HPC environments, rather than replace them.

- **Conda** is well suited for Python-centric workflows, rapid experimentation, and lightweight data analysis. It excels at managing Python packages and prebuilt binaries but offers limited control over compilers and low-level system dependencies.

- **Spack** is optimized for building performance-critical, compiled software such as MPI libraries, numerical solvers, and GPU-enabled frameworks. It provides fine-grained control over compilers, build variants, and dependency resolution.

- **Apptainer (Singularity)** can be used to containerize Spack-built software, enabling portability across nodes or clusters while preserving optimized native libraries.

A common pattern is to use **Spack to build core system-level dependencies** (e.g., MPI, CUDA, math libraries) and layer **Conda environments or Apptainer containers** on top for application-level dependencies and reproducibility.

---

## Best Practices

- Use **Spack environments (`spack env`)** to define reproducible software stacks for projects and research workflows.

- Prefer building and testing packages on **compute nodes** rather than login nodes to avoid resource limitations and build failures.

- Reuse existing builds whenever possible to reduce compilation time and disk usage:
  
```bash
spack install --reuse
```

Periodically remove unused packages to reclaim disk space:

```bash
spack gc --all
```

## References

- Spack documentation, *Spack: A package manager for HPC*, available at: [https://spack.readthedocs.io/en/latest/index.html]
