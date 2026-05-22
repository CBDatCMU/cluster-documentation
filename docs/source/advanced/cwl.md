# Common Workflow Language (CWL)

The Common Workflow Language (CWL) is an open standard for describing command-line tools and workflows. CWL workflows are portable, reusable, and can run on any CWL-compatible engine. `cwltool` is the reference implementation and is the recommended engine for running CWL workflows on the Lane Cluster.

## Loading Miniconda3

Miniconda3 is available as a module on the Lane Cluster. Load it using:

```bash
module load miniconda3
```

## Creating a CWL Environment

Create a dedicated conda environment for CWL:

```bash
conda create -n cwl python=3.11
```

Activate the environment:

```bash
conda activate cwl
```

## Installing cwltool

With the environment active, install `cwltool` via conda-forge:

```bash
conda install -c conda-forge cwltool
```

Confirm the installation:

```bash
cwltool --version
```

---

## Basic Concepts

A CWL workflow consists of two types of files:

- **Tool descriptions** (`.cwl`): define individual command-line tools — their inputs, outputs, and the command to run.
- **Job input files** (`.yml` or `.json`): provide concrete input values for a run.

Workflows chain multiple tools together by connecting their inputs and outputs.

---

## Example 1: Hello World

A minimal CWL tool that prints a message.

**hello.cwl:**

```yaml
cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo

inputs:
  message:
    type: string
    inputBinding:
      position: 1

outputs:
  stdout:
    type: stdout
```

**hello-job.yml:**

```yaml
message: "Hello, Lane Cluster!"
```

Run the tool:

```bash
cwltool hello.cwl hello-job.yml
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
conda activate cwl

cwltool hello.cwl hello-job.yml
```

```bash
sbatch run_hello.sh
```

---

## Example 2: File Processing

A tool that counts the number of lines in an input file.

**count-lines.cwl:**

```yaml
cwlVersion: v1.2
class: CommandLineTool
baseCommand: [wc, -l]

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  line_count:
    type: stdout
```

**count-lines-job.yml:**

```yaml
input_file:
  class: File
  path: data/input.txt
```

Run the tool:

```bash
cwltool count-lines.cwl count-lines-job.yml
```

**SLURM batch script (`run_count.sh`):**

```bash
#!/bin/bash
#SBATCH -p pool1
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

module load miniconda3
conda activate cwl

cwltool count-lines.cwl count-lines-job.yml
```

```bash
sbatch run_count.sh
```

---

## Example 3: RNA-seq Alignment Pipeline

A multi-step workflow that aligns paired-end reads with HISAT2 and sorts the output with Samtools.

**align.cwl:**

```yaml
cwlVersion: v1.2
class: CommandLineTool
baseCommand: hisat2

arguments:
  - valueFrom: "$(inputs.index)"
    prefix: -x
  - valueFrom: "$(inputs.reads_r1.path)"
    prefix: "-1"
  - valueFrom: "$(inputs.reads_r2.path)"
    prefix: "-2"
  - valueFrom: "$(inputs.threads)"
    prefix: --threads
  - valueFrom: "| samtools view -bS - > aligned.bam"
    shellQuote: false

inputs:
  index:    { type: string }
  reads_r1: { type: File }
  reads_r2: { type: File }
  threads:  { type: int, default: 16 }

outputs:
  bam:
    type: File
    outputBinding:
      glob: aligned.bam

requirements:
  ShellCommandRequirement: {}
```

**sort.cwl:**

```yaml
cwlVersion: v1.2
class: CommandLineTool
baseCommand: [samtools, sort]

inputs:
  bam:
    type: File
    inputBinding:
      position: 1
  threads:
    type: int
    default: 16
    inputBinding:
      prefix: -@
  output_name:
    type: string
    default: sorted.bam
    inputBinding:
      prefix: -o

outputs:
  sorted_bam:
    type: File
    outputBinding:
      glob: "$(inputs.output_name)"
```

**rnaseq-workflow.cwl:**

```yaml
cwlVersion: v1.2
class: Workflow

inputs:
  index:    string
  reads_r1: File
  reads_r2: File
  threads:  int

outputs:
  sorted_bam:
    type: File
    outputSource: sort/sorted_bam

steps:
  align:
    run: align.cwl
    in:
      index:    index
      reads_r1: reads_r1
      reads_r2: reads_r2
      threads:  threads
    out: [bam]

  sort:
    run: sort.cwl
    in:
      bam:     align/bam
      threads: threads
    out: [sorted_bam]
```

**rnaseq-job.yml:**

```yaml
index: /path/to/genome_index
reads_r1:
  class: File
  path: reads/sample1_R1.fastq.gz
reads_r2:
  class: File
  path: reads/sample1_R2.fastq.gz
threads: 16
```

Run the workflow:

```bash
cwltool rnaseq-workflow.cwl rnaseq-job.yml
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
conda activate cwl

cwltool rnaseq-workflow.cwl rnaseq-job.yml
```

```bash
sbatch run_rnaseq.sh
```

---

## Best Practices

- Keep tool descriptions (`.cwl`) and job input files (`.yml`) separate so tools can be reused with different inputs.
- Use `cwltool --validate` to check a workflow for errors before running:

```bash
cwltool --validate rnaseq-workflow.cwl
```

- Use `cwltool --debug` for verbose output when troubleshooting a failing step.
- Store all input file paths as absolute paths in job files when running on the cluster to avoid working-directory issues.
- Use the `DockerRequirement` or `SoftwareRequirement` hints in tool descriptions to specify software dependencies for portability.

---

## References

- CWL specification: [https://www.commonwl.org/]
- cwltool documentation: [https://github.com/common-workflow-language/cwltool]
