# Intro to Snakemake

Snakemake is a workflow management system that enables reproducible and scalable data analysis. Workflows are defined in a human-readable, Python-based language and can be seamlessly scaled from a laptop to a cluster without modifying the workflow definition.

## Loading Miniconda3

Miniconda3 is available as a module on the Lane Cluster. Load it using:

```bash
module load miniconda3
```

## Creating a Snakemake Environment

Once Miniconda3 is loaded, create a dedicated conda environment for Snakemake:

```bash
conda create -n snakemake python=3.11
```

Activate the environment:

```bash
conda activate snakemake
```

## Installing Snakemake

With the environment active, install Snakemake via conda-forge:

```bash
conda install -c conda-forge -c bioconda snakemake
```

Confirm the installation:

```bash
snakemake --version
```

---

## Basic Concepts

A Snakemake workflow is defined in a file called `Snakefile`. Each step is called a **rule** and specifies:

- `input`: files the rule depends on
- `output`: files the rule produces
- `shell` or `run`: the command or Python code to execute

Snakemake automatically resolves the order of rules based on input/output dependencies.

---

## Example Workflow 1: Hello World

A minimal workflow that writes a greeting to a file.

**Snakefile:**

```python
rule hello:
    output:
        "hello.txt"
    shell:
        "echo 'Hello, Lane Cluster!' > {output}"
```

Run the workflow:

```bash
snakemake --cores 16
```

**SLURM batch script (`run_hello.sh`):**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate snakemake

snakemake --cores 16
```

```bash
sbatch run_hello.sh
```

---

## Example Workflow 2: File Processing Pipeline

A three-step pipeline that generates data, processes it, and produces a summary.

**Snakefile:**

```python
rule all:
    input:
        "results/summary.txt"

rule generate:
    output:
        "data/raw.txt"
    shell:
        "seq 1 100 > {output}"

rule process:
    input:
        "data/raw.txt"
    output:
        "results/processed.txt"
    shell:
        "awk '{{sum += $1}} END {{print sum}}' {input} > {output}"

rule summarize:
    input:
        "results/processed.txt"
    output:
        "results/summary.txt"
    shell:
        "echo 'Total:' $(cat {input}) > {output}"
```

Run the full pipeline:

```bash
snakemake --cores 16
```

**SLURM batch script (`run_pipeline.sh`):**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate snakemake

snakemake --cores 16
```

```bash
sbatch run_pipeline.sh
```

---

## Example Workflow 3: RNA-seq Alignment

A realistic bioinformatics workflow aligning paired-end reads with HISAT2 and sorting the output with Samtools.

**Snakefile:**

```python
SAMPLES = ["sample1", "sample2", "sample3"]

rule all:
    input:
        expand("results/{sample}.sorted.bam", sample=SAMPLES)

rule align:
    input:
        r1 = "reads/{sample}_R1.fastq.gz",
        r2 = "reads/{sample}_R2.fastq.gz"
    output:
        "results/{sample}.bam"
    params:
        index = "/path/to/genome_index"
    threads: 16
    shell:
        "hisat2 -x {params.index} -1 {input.r1} -2 {input.r2} "
        "--threads {threads} | samtools view -bS - > {output}"

rule sort:
    input:
        "results/{sample}.bam"
    output:
        "results/{sample}.sorted.bam"
    threads: 16
    shell:
        "samtools sort -@ {threads} {input} -o {output}"
```

**SLURM batch script (`run_rnaseq.sh`):**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate snakemake

snakemake --cores 16 \
    --cluster "sbatch -p pool1 --time=08:00:00 --mem=8G --ntasks=16 --cpus-per-task=1" \
    --jobs 10
```

```bash
sbatch run_rnaseq.sh
```

---

## Best Practices

- Always define a `rule all` that lists the final output files so Snakemake knows what to build.
- Use `expand()` to generate lists of filenames from sample names or other variables.
- Use `--dryrun` (`-n`) to preview which rules will execute before actually running:

```bash
snakemake -n
```

- Use `--forcerun` to re-run a specific rule even if its output already exists:

```bash
snakemake --forcerun align
```

- Store environment definitions in `environment.yaml` files and use `conda:` directives per rule for fully reproducible workflows.

---

## References

- Snakemake documentation: [https://snakemake.readthedocs.io/en/stable/]
- Snakemake SLURM profile: [https://github.com/Snakemake-Profiles/slurm]
