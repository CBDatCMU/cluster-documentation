# Using SLURM on the Lane Cluster

SLURM (Simple Linux Utility for Resource Management) is the workload manager used on the Lane Cluster. It schedules and runs computational jobs on the cluster’s compute nodes. This guide introduces the essential SLURM commands and explains how to submit, monitor, and manage jobs effectively.

## Submitting a Batch Job

Batch jobs are submitted with the `sbatch` command. Below is an example job script:

```bash
#!/bin/bash
#SBATCH --job-name=test_job
#SBATCH --output=output.txt
#SBATCH --time=01:00:00
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

module load python
python my_script.py
```

Submit the job:

```bash
sbatch my_job.sh
```

## Checking Job Status

```bash
squeue -u $USER
```

## Canceling Jobs

```bash
scancel <jobid>
```

## Running an Interactive Job

```bash
salloc --partition=cpu --time=01:00:00 --cpus-per-task=2 --mem=4G
```

## Viewing Job Output

```bash
tail -f output.txt
```

## Specifying Resources

| Purpose | Directive | Example |
|---------|-----------|---------|
| Job name | `--job-name` | `--job-name=align` |
| Output file | `--output` | `--output=run.out` |
| Time limit | `--time` | `--time=4:00:00` |
| Partition | `--partition` | `--partition=cpu` |
| CPUs | `--cpus-per-task` | `--cpus-per-task=8` |
| Memory | `--mem` | `--mem=32G` |
| GPUs | `--gres` | `--gres=gpu:1` |
| Array jobs | `--array` | `--array=0-99` |

## Job Arrays

```bash
#!/bin/bash
#SBATCH --job-name=array_example
#SBATCH --output=array_%A_%a.out
#SBATCH --array=0-9

python script.py $SLURM_ARRAY_TASK_ID
```

## Monitoring Resource Usage

```bash
sacct -j <jobid> --format=JobID,Elapsed,ReqMem,MaxRSS,State
```

## Best Practices

- Never run computations on the login node.
- Request only the resources you need.
- Use job arrays for parameter sweeps.
- Check your output files regularly.
