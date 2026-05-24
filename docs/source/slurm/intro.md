# Introduction to SLURM

**SLURM** (Simple Linux Utility for Resource Management) is an open-source, fault-tolerant, and highly scalable cluster management and job scheduling system used on many of the world's supercomputers and high-performance computing (HPC) clusters, including the Lane Cluster.

SLURM serves three key functions:

- **Resource allocation** — grants users exclusive or shared access to compute nodes for a defined period
- **Job execution** — starts, executes, and monitors jobs on the allocated nodes
- **Queue management** — arbitrates contention for resources using a configurable scheduling policy

When you submit a job, SLURM places it in a queue (called a *partition*). The scheduler evaluates pending jobs against available resources and cluster policies, then dispatches jobs to compute nodes on your behalf. You never SSH directly to a compute node to run work; instead, SLURM manages that interaction for you.

> **Note:** Never run computationally intensive work directly on the login node. Always use SLURM to submit jobs to compute nodes.

---

## sbatch — Submit a Batch Job

`sbatch` is the primary command for submitting non-interactive (batch) jobs to the cluster. You write a shell script that describes both the resource requirements and the work to be done, then hand it to SLURM.

### Basic usage

```bash
sbatch my_job.sh
```

### A minimal job script

```bash
#!/bin/bash
#SBATCH --job-name=my_analysis
#SBATCH --output=my_analysis_%j.out
#SBATCH --error=my_analysis_%j.err
#SBATCH --time=02:00:00
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

module load python
python my_analysis.py
```

Lines beginning with `#SBATCH` are SLURM directives. They are ignored by Bash but parsed by SLURM before the job runs. The `%j` token is replaced with the job ID at runtime.

### Common `sbatch` directives

| Directive | Purpose | Example |
|---|---|---|
| `--job-name` | Label shown in `squeue` | `--job-name=align` |
| `--output` | Standard output file | `--output=run_%j.out` |
| `--error` | Standard error file | `--error=run_%j.err` |
| `--time` | Wall-clock time limit (`D-HH:MM:SS`) | `--time=4:00:00` |
| `--partition` | Queue to submit to | `--partition=gpu` |
| `--nodes` | Number of nodes | `--nodes=2` |
| `--ntasks` | Total MPI tasks | `--ntasks=16` |
| `--ntasks-per-node` | Tasks per node | `--ntasks-per-node=8` |
| `--cpus-per-task` | CPU threads per task | `--cpus-per-task=8` |
| `--mem` | Memory per node | `--mem=32G` |
| `--mem-per-cpu` | Memory per CPU core | `--mem-per-cpu=4G` |
| `--gres` | Generic resources (e.g., GPUs) | `--gres=gpu:1` |
| `--array` | Submit a job array | `--array=0-99` |
| `--dependency` | Hold until another job finishes | `--dependency=afterok:12345` |
| `--mail-type` | Email notification events | `--mail-type=END,FAIL` |
| `--mail-user` | Address for notifications | `--mail-user=you@cmu.edu` |
| `--account` | Charge to a specific account | `--account=mygroup` |
| `--constraint` | Require specific node features | `--constraint=avx512` |
| `--exclusive` | Reserve entire node(s) | `--exclusive` |

### GPU job example

```bash
#!/bin/bash
#SBATCH --job-name=gpu_train
#SBATCH --output=gpu_train_%j.out
#SBATCH --time=08:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

module load cuda
python train.py --epochs 50
```

### Job array example

Job arrays allow you to run the same script many times with a varying index, useful for parameter sweeps or processing many input files.

```bash
#!/bin/bash
#SBATCH --job-name=sweep
#SBATCH --output=sweep_%A_%a.out
#SBATCH --array=0-9
#SBATCH --time=01:00:00
#SBATCH --partition=cpu
#SBATCH --mem=8G

python run_experiment.py --config configs/config_${SLURM_ARRAY_TASK_ID}.yaml
```

`%A` expands to the array job ID and `%a` to the task index.

### Job dependency example

```bash
# Submit first stage
jid=$(sbatch --parsable stage1.sh)

# Submit second stage; only runs if stage 1 succeeded
sbatch --dependency=afterok:$jid stage2.sh
```

Dependency types: `after`, `afterok`, `afternotok`, `afterany`, `singleton`.

---

## srun — Run a Job Step

`srun` launches job steps, either within an existing allocation or by creating a one-off allocation itself. Unlike `sbatch`, it blocks: your terminal waits until the step finishes.

### Within a batch script

Inside an `sbatch` script, `srun` is the recommended way to launch parallel executables because it correctly handles MPI task placement:

```bash
#!/bin/bash
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=2
#SBATCH --time=04:00:00
#SBATCH --partition=cpu

srun my_mpi_program --input data.h5
```

Each call to `srun` inside a batch script is a *job step* that SLURM tracks separately. You can inspect steps with `squeue --steps` or `sacct`.

### Interactive use (without an existing allocation)

`srun` can allocate resources on the fly and drop you into an interactive shell or run a single command:

```bash
# Run a single command interactively
srun --partition=cpu --time=00:30:00 --mem=4G hostname

# Start an interactive Bash session
srun --partition=cpu --time=01:00:00 --cpus-per-task=4 --mem=8G --pty bash
```

> **Note:** For a full interactive session where you need to run multiple commands, `salloc` is usually more convenient than `srun --pty bash`.

### Common `srun` flags

| Flag | Description |
|---|---|
| `--ntasks` | Number of parallel tasks (MPI ranks) |
| `--cpus-per-task` | Threads per task |
| `--nodes` | Number of nodes to use |
| `--partition` | Partition to run in |
| `--time` | Time limit for this step |
| `--gres` | Generic resources (e.g., GPUs) |
| `--pty` | Allocate a pseudo-terminal (required for interactive shells) |
| `--label` | Prefix output lines with task index |
| `--mpi` | MPI implementation hint (`pmix`, `pmi2`, `none`) |

### MPI example

```bash
#!/bin/bash
#SBATCH --ntasks=32
#SBATCH --time=06:00:00
#SBATCH --partition=cpu

module load openmpi
srun --mpi=pmix ./simulation
```

---

## salloc — Request an Interactive Allocation

`salloc` obtains a resource allocation and (by default) starts a shell in that allocation on the login node, from which you can then use `srun` to launch work on the compute nodes. It is the standard way to get an interactive session for iterative development and debugging.

### Basic usage

```bash
salloc --partition=cpu --time=02:00:00 --cpus-per-task=4 --mem=16G
```

Once SLURM grants the allocation, your shell prompt returns. The environment variable `$SLURM_JOB_ID` is set. You can then:

```bash
# Run commands on the compute node
srun hostname
srun python debug_script.py

# When done, release the allocation
exit
```

### GPU interactive session

```bash
salloc --partition=gpu --time=01:00:00 --gres=gpu:1 --cpus-per-task=8 --mem=32G
```

### Multi-node interactive session

```bash
salloc --partition=cpu --nodes=2 --ntasks-per-node=16 --time=04:00:00
```

### Common `salloc` flags

| Flag | Description |
|---|---|
| `--partition` | Partition to allocate from |
| `--time` | Maximum wall time |
| `--nodes` | Number of nodes |
| `--ntasks` | Total tasks (MPI ranks) |
| `--cpus-per-task` | CPU threads per task |
| `--mem` | Memory per node |
| `--gres` | Generic resources (e.g., GPUs) |
| `--account` | Charge to a specific account |
| `--immediate` | Fail immediately if resources are unavailable |
| `--no-shell` | Obtain allocation but do not start a shell |

> **Tip:** Set a reasonable `--time` limit on interactive allocations. If you forget to `exit`, SLURM will automatically cancel the job when the time limit is reached, freeing resources for others.

---

## squeue — View the Job Queue

`squeue` displays the state of jobs in the SLURM scheduling queue.

```bash
# Show your own jobs
squeue --user=$USER

# Show all jobs in a partition
squeue --partition=gpu

# Show jobs with custom output columns
squeue --user=$USER --format="%.10i %.20j %.8T %.12M %.12l %.6D %R"

# Watch queue in real time (refresh every 5 seconds)
watch -n 5 squeue --user=$USER
```

### Common output fields (`--format` tokens)

| Token | Meaning |
|---|---|
| `%i` | Job ID |
| `%j` | Job name |
| `%T` | State (`PENDING`, `RUNNING`, `COMPLETING`, …) |
| `%M` | Time used so far |
| `%l` | Time limit |
| `%D` | Number of nodes |
| `%R` | Reason (why pending, or which node running on) |
| `%P` | Partition |
| `%u` | Username |

---

## scancel — Cancel Jobs

`scancel` cancels pending or running jobs and job steps.

```bash
# Cancel a specific job
scancel 12345

# Cancel all your jobs
scancel --user=$USER

# Cancel all your pending jobs
scancel --user=$USER --state=PENDING

# Cancel a specific job array task
scancel 12345_3

# Cancel a job step (job 12345, step 2)
scancel 12345.2

# Send a signal instead of killing (e.g., for checkpointing)
scancel --signal=USR1 12345
```

---

## sacct — View Job Accounting

`sacct` reports accounting information for completed and running jobs from the SLURM database. It is the primary tool for reviewing how much CPU, memory, and time a job actually consumed.

```bash
# Accounting summary for a specific job
sacct --jobs=12345 --format=JobID,JobName,Elapsed,ReqMem,MaxRSS,State,ExitCode

# All your jobs from today
sacct --user=$USER --starttime=today

# Jobs from a date range
sacct --user=$USER --starttime=2026-01-01 --endtime=2026-01-31
```

### Useful `--format` fields

| Field | Description |
|---|---|
| `JobID` | Job (and step) identifier |
| `JobName` | Job name |
| `State` | Final state (`COMPLETED`, `FAILED`, `CANCELLED`, …) |
| `Elapsed` | Wall-clock time used |
| `ReqMem` | Memory requested |
| `MaxRSS` | Peak memory consumed (useful for tuning future requests) |
| `CPUTime` | CPU time charged |
| `ExitCode` | Exit status of the job |
| `Partition` | Partition used |
| `NodeList` | Nodes the job ran on |

---

## sinfo — View Cluster State

`sinfo` reports the state of partitions and nodes.

```bash
# Summary of all partitions
sinfo

# Node-level detail
sinfo --Node --long

# Filter to a specific partition
sinfo --partition=gpu

# Show only idle nodes
sinfo --state=idle
```

### Common node states

| State | Meaning |
|---|---|
| `idle` | Node is available |
| `alloc` | Node is fully allocated |
| `mix` | Node is partially allocated |
| `drain` | Node is being taken offline (no new jobs) |
| `down` | Node is unavailable |

---

## scontrol — Inspect and Modify SLURM Entities

`scontrol` is an administrative and diagnostic tool for viewing and modifying SLURM configuration and job state.

```bash
# Show detailed information about a job
scontrol show job 12345

# Show details about a node
scontrol show node node001

# Show partition details
scontrol show partition cpu

# Hold a pending job (prevent it from starting)
scontrol hold 12345

# Release a held job
scontrol release 12345

# Modify a pending job's time limit
scontrol update JobID=12345 TimeLimit=08:00:00

# Requeue a failed or cancelled job
scontrol requeue 12345
```

> **Note:** Some `scontrol` modifications (e.g., changing `TimeLimit` beyond the partition maximum) require administrator privileges.

---

## sprio — View Job Priority

`sprio` shows the priority components used by the SLURM scheduler to rank pending jobs.

```bash
# Show priorities for your jobs
sprio --user=$USER

# Show all pending jobs with priority breakdown
sprio --long
```

Priority factors typically include fair-share (historical usage), job age, and requested resources. A higher priority value means the job is more likely to start sooner.

---

## sstat — Monitor a Running Job

`sstat` reports real-time resource usage for running jobs. It is complementary to `sacct`, which only reports completed jobs.

```bash
# Monitor CPU and memory of running job
sstat --jobs=12345 --format=JobID,AveCPU,AveRSS,MaxRSS,AveDiskRead,AveDiskWrite
```

`sstat` only works on jobs that are currently running. For completed jobs, use `sacct`.

---

## sreport — Generate Usage Reports

`sreport` generates cluster usage reports from accounting data. It is mainly used by administrators but can be useful for understanding group usage.

```bash
# Cluster utilization for the past month
sreport cluster utilization start=2026-04-01 end=2026-04-30

# Top users by CPU hours
sreport user top start=2026-04-01
```

---

## Environment Variables Set by SLURM

When a job runs, SLURM populates several environment variables that your script can reference:

| Variable | Description |
|---|---|
| `$SLURM_JOB_ID` | Unique job identifier |
| `$SLURM_JOB_NAME` | Job name |
| `$SLURM_NODELIST` | List of assigned nodes |
| `$SLURM_NTASKS` | Total number of tasks |
| `$SLURM_CPUS_PER_TASK` | CPUs allocated per task |
| `$SLURM_MEM_PER_NODE` | Memory per node (MB) |
| `$SLURM_ARRAY_JOB_ID` | Parent job ID for array jobs |
| `$SLURM_ARRAY_TASK_ID` | Index of the current array task |
| `$SLURM_SUBMIT_DIR` | Directory from which the job was submitted |
| `$SLURM_TMPDIR` | Node-local temporary directory (fast scratch) |

---

## Best Practices

- **Do not run work on the login node.** The login node is shared by all users for job submission, file management, and compilation only.
- **Request realistic resources.** Over-requesting CPUs, memory, or time delays your jobs and wastes cluster capacity. Use `sacct --format=MaxRSS,Elapsed` on past jobs to calibrate future requests.
- **Set a time limit.** Jobs without a time limit (or with very large limits) may wait longer in the queue due to backfill scheduling constraints.
- **Use job arrays** for parameter sweeps instead of submitting hundreds of independent jobs manually.
- **Use `$SLURM_TMPDIR`** for temporary files during a job — it is local to the compute node and much faster than network storage.
- **Check your jobs early.** Monitor output files shortly after a job starts to catch configuration errors before the full wall time is consumed.
- **Use job dependencies** to chain stages of a pipeline rather than submitting them all at once and hoping the timing works out.
