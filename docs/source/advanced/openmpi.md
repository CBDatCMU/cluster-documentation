# Intro to OpenMPI

## What is OpenMPI

OpenMPI stands for **Open Message Passing Interface**. It is an open-source implementation of the MPI standard — a specification that defines how processes running on different processors, nodes, or machines can communicate with each other by passing messages. OpenMPI is maintained by a consortium of academic, research, and industry partners and is one of the most widely deployed MPI implementations on HPC clusters worldwide.

MPI itself is not a library or a program — it is a standard. OpenMPI is one implementation of that standard, alongside others such as MPICH and Intel MPI. The standard defines a set of communication primitives (send, receive, broadcast, reduce, etc.) and OpenMPI provides the compiled libraries and runtime infrastructure that make those primitives work efficiently on real hardware.

On the Lane Cluster, OpenMPI is available as a module:

```bash
module load openmpi
```

This makes the `mpicc`, `mpicxx`, `mpif90`, and `mpirun` (or `mpiexec`) commands available in your environment, along with the runtime libraries needed to compile and launch MPI programs.

---

## What OpenMPI is Useful For

OpenMPI is designed for **distributed-memory parallel computing** — that is, programs that need to run across multiple processes that do not share memory. This is the dominant model for large-scale scientific computation because it scales beyond the limits of a single node.

Typical use cases include:

- **Computational fluid dynamics** — decomposing a simulation domain across hundreds or thousands of MPI ranks
- **Molecular dynamics** — distributing particle interactions across nodes
- **Genomics and bioinformatics** — parallelizing alignment, assembly, or annotation pipelines that can be partitioned by data
- **Machine learning at scale** — distributed training frameworks often use MPI for gradient synchronization
- **Finite element analysis** — distributing mesh partitions across nodes
- **Climate and weather modeling** — running global models on thousands of cores simultaneously

The fundamental idea is that you launch N copies of your program (called *ranks*), each gets a unique rank ID (from 0 to N-1), and they coordinate by sending and receiving messages. OpenMPI handles the low-level details of routing those messages efficiently over the available network hardware (Ethernet, InfiniBand, shared memory, etc.).

---

## Single-threaded, Multi-threaded, and Multi-core: What is the Difference?

Understanding these three terms is essential before using OpenMPI effectively.

### Single-threaded

A **single-threaded** program has exactly one thread of execution. At any moment, it is doing exactly one thing: instructions execute sequentially, one after another. Most simple programs are single-threaded. A single-threaded MPI program launches many *processes* (each single-threaded), and those processes communicate via message passing. Each process runs on one CPU core.

### Multi-core

**Multi-core** refers to a physical CPU chip that contains multiple independent processing units (cores). A modern server node on the Lane Cluster may have 32, 64, or more cores per socket. A single-threaded program uses only one of those cores and leaves the rest idle. To use multiple cores on the same node, you need either multiple processes (MPI) or multiple threads (OpenMP or pthreads), or a combination of both.

### Multi-threaded

A **multi-threaded** program has multiple threads of execution within a single process. All threads share the same memory space, which makes communication between them cheap — a thread can read a value another thread wrote without any message passing. OpenMP is the dominant multi-threading model for scientific computing and is often used alongside MPI in a *hybrid MPI+OpenMP* model: MPI handles communication between nodes, while OpenMP threads use all cores within a node.

### How They Relate to OpenMPI

| Model | Parallelism | Memory | Scales across nodes? |
|---|---|---|---|
| Single-threaded MPI | Multiple processes, 1 thread each | Distributed (no sharing) | Yes |
| Multi-threaded (OpenMP) | 1 process, multiple threads | Shared within process | No (single node only) |
| Hybrid MPI + OpenMP | Multiple processes, multiple threads each | Distributed between nodes, shared within node | Yes |
| Multi-core (no parallelism) | 1 process, 1 thread | Local | No |

Pure OpenMPI uses the single-threaded-per-rank model by default. Each MPI rank is a separate process with its own private memory. If you want to use all 32 cores on a node with 4 MPI ranks, you would give each rank 8 OpenMP threads — that is the hybrid model.

---

## Loading OpenMPI on the Lane Cluster

```bash
module load openmpi
```

Confirm the version and available compilers:

```bash
mpirun --version
mpicc --version
```

---

## Compiling an MPI Program

OpenMPI provides compiler wrappers that automatically link the MPI libraries:

| Wrapper | Language |
|---|---|
| `mpicc` | C |
| `mpicxx` | C++ |
| `mpif90` | Fortran 90 |
| `mpif77` | Fortran 77 |

Example — compile a C program:

```bash
mpicc -O2 -o my_program my_program.c
```

The wrapper passes the correct include paths and library flags to the underlying compiler (`gcc`, `g++`, etc.) so you do not need to specify them manually.

---

## Running an MPI Program

### Interactive (for testing)

```bash
srun --ntasks=4 --partition=cpu --time=00:10:00 ./my_program
```

Or use `salloc` to get an interactive allocation first, then run inside it:

```bash
salloc --ntasks=4 --partition=cpu --time=01:00:00
srun ./my_program
exit
```

### SLURM batch job

**SLURM batch script (`run_mpi.sh`):**

```bash
#!/bin/bash
#SBATCH --job-name=mpi_job
#SBATCH --output=mpi_job_%j.out
#SBATCH --error=mpi_job_%j.err
#SBATCH --time=04:00:00
#SBATCH --partition=cpu
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4G

module load openmpi

srun ./my_program
```

```bash
sbatch run_mpi.sh
```

Using `srun` inside a SLURM script (rather than `mpirun`) is recommended on the Lane Cluster because SLURM sets up the process placement automatically based on the `#SBATCH` directives.

### Hybrid MPI + OpenMP batch job

```bash
#!/bin/bash
#SBATCH --job-name=hybrid_job
#SBATCH --output=hybrid_job_%j.out
#SBATCH --time=08:00:00
#SBATCH --partition=cpu
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G

module load openmpi

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

srun ./my_hybrid_program
```

This launches 4 nodes × 4 MPI ranks × 8 OpenMP threads = 128 total threads of execution.

---

## Hello World Example

A minimal MPI program in C:

```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    printf("Hello from rank %d of %d\n", rank, size);

    MPI_Finalize();
    return 0;
}
```

Compile and run:

```bash
module load openmpi
mpicc -o hello hello.c
srun --ntasks=4 --partition=cpu --time=00:05:00 ./hello
```

Expected output (order may vary):

```
Hello from rank 0 of 4
Hello from rank 2 of 4
Hello from rank 1 of 4
Hello from rank 3 of 4
```

---

## Common Communication Patterns

### Point-to-point: send and receive

The most basic form of MPI communication — one rank sends a message, another receives it.

```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if (rank == 0) {
        int value = 42;
        MPI_Send(&value, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
        printf("Rank 0 sent value %d to rank 1\n", value);
    } else if (rank == 1) {
        int value;
        MPI_Recv(&value, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Rank 1 received value %d from rank 0\n", value);
    }

    MPI_Finalize();
    return 0;
}
```

### Broadcast: one rank sends to all

`MPI_Bcast` distributes data from one rank (the root) to every other rank. This is the standard way to share parameters or configuration read from a file by rank 0.

```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    int data = 0;
    if (rank == 0) data = 99;

    MPI_Bcast(&data, 1, MPI_INT, 0, MPI_COMM_WORLD);

    printf("Rank %d has data = %d\n", rank, data);

    MPI_Finalize();
    return 0;
}
```

### Reduce: combine values from all ranks

`MPI_Reduce` collects a value from every rank and combines them using an operation (sum, max, min, etc.), delivering the result to the root rank.

```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    double local_sum = rank * 1.0;   /* each rank contributes its rank number */
    double global_sum = 0.0;

    MPI_Reduce(&local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0)
        printf("Global sum = %.1f\n", global_sum);

    MPI_Finalize();
    return 0;
}
```

### Scatter and gather: distribute and collect arrays

`MPI_Scatter` splits an array on the root and sends one chunk to each rank. `MPI_Gather` does the reverse — collects chunks from all ranks back to the root.

```c
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int chunk = 4;
    int *send_buf    = (int *)malloc(size * chunk * sizeof(int));
    int *recv_buf    = (int *)malloc(chunk * sizeof(int));
    int *result_buf  = (int *)malloc(size * chunk * sizeof(int));

    if (rank == 0)
        for (int i = 0; i < size * chunk; i++) send_buf[i] = i;

    MPI_Scatter(send_buf, chunk, MPI_INT, recv_buf, chunk, MPI_INT, 0, MPI_COMM_WORLD);

    /* each rank squares its chunk */
    for (int i = 0; i < chunk; i++) recv_buf[i] *= recv_buf[i];

    MPI_Gather(recv_buf, chunk, MPI_INT, result_buf, chunk, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("Squared values: ");
        for (int i = 0; i < size * chunk; i++) printf("%d ", result_buf[i]);
        printf("\n");
    }

    free(send_buf); free(recv_buf); free(result_buf);
    MPI_Finalize();
    return 0;
}
```

---

## Real-World Examples

### Example 1: Parallel Monte Carlo estimation of π

Each rank independently samples random points inside the unit square and counts how many fall inside the unit circle. The counts are summed with `MPI_Reduce` to produce a global estimate. This is embarrassingly parallel — ranks do not need to communicate until the final reduction.

```c
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    long long local_samples = 10000000LL;
    long long local_hits = 0;

    srand(rank + 1);   /* different seed per rank */

    for (long long i = 0; i < local_samples; i++) {
        double x = (double)rand() / RAND_MAX;
        double y = (double)rand() / RAND_MAX;
        if (x * x + y * y <= 1.0) local_hits++;
    }

    long long global_hits = 0;
    long long global_samples = 0;
    MPI_Reduce(&local_hits,    &global_hits,    1, MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);
    MPI_Reduce(&local_samples, &global_samples, 1, MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0)
        printf("pi ≈ %.6f  (samples: %lld)\n", 4.0 * global_hits / global_samples, global_samples);

    MPI_Finalize();
    return 0;
}
```

**SLURM batch script:**

```bash
#!/bin/bash
#SBATCH --job-name=monte_carlo_pi
#SBATCH --output=pi_%j.out
#SBATCH --time=00:10:00
#SBATCH --partition=cpu
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G

module load openmpi
# Compile on the login node before submitting: mpicc -O2 -o pi pi.c -lm
srun ./pi
```

---

### Example 2: Parallel matrix–vector multiplication

The matrix rows are distributed across ranks using `MPI_Scatter`. Each rank multiplies its local rows by the full vector (broadcast from rank 0) and returns the result with `MPI_Gather`.

```c
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#define N 1024   /* matrix dimension */

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int rows_per_rank = N / size;

    double *A      = NULL;
    double *x      = (double *)malloc(N * sizeof(double));
    double *local_A = (double *)malloc(rows_per_rank * N * sizeof(double));
    double *local_y = (double *)malloc(rows_per_rank * sizeof(double));
    double *y      = NULL;

    if (rank == 0) {
        A = (double *)malloc(N * N * sizeof(double));
        y = (double *)malloc(N * sizeof(double));
        for (int i = 0; i < N * N; i++) A[i] = (double)(i % N + 1);
        for (int i = 0; i < N; i++) x[i] = 1.0;
    }

    MPI_Bcast(x, N, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Scatter(A, rows_per_rank * N, MPI_DOUBLE,
                local_A, rows_per_rank * N, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    for (int i = 0; i < rows_per_rank; i++) {
        local_y[i] = 0.0;
        for (int j = 0; j < N; j++)
            local_y[i] += local_A[i * N + j] * x[j];
    }

    MPI_Gather(local_y, rows_per_rank, MPI_DOUBLE,
               y, rows_per_rank, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    if (rank == 0)
        printf("y[0] = %.1f, y[%d] = %.1f\n", y[0], N - 1, y[N - 1]);

    free(local_A); free(local_y); free(x);
    if (rank == 0) { free(A); free(y); }

    MPI_Finalize();
    return 0;
}
```

**SLURM batch script:**

```bash
#!/bin/bash
#SBATCH --job-name=matvec
#SBATCH --output=matvec_%j.out
#SBATCH --time=00:30:00
#SBATCH --partition=cpu
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2G

module load openmpi
# Compile on the login node before submitting: mpicc -O2 -o matvec matvec.c
srun ./matvec
```

---

### Example 3: Parallel word count across files

Each rank reads and counts words in a different input file. Results are reduced to rank 0 for a global total. This pattern applies to any embarrassingly parallel file-processing pipeline.

```c
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

long count_words(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) return 0;
    long count = 0;
    int in_word = 0, ch;
    while ((ch = fgetc(f)) != EOF) {
        if (isspace(ch)) { in_word = 0; }
        else if (!in_word) { in_word = 1; count++; }
    }
    fclose(f);
    return count;
}

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 2) {
        if (rank == 0) fprintf(stderr, "Usage: %s <directory>\n", argv[0]);
        MPI_Finalize();
        return 1;
    }

    /* argv[1] is the directory; each rank processes file <rank>.txt */
    char filename[256];
    snprintf(filename, sizeof(filename), "%s/%d.txt", argv[1], rank);

    long local_count = count_words(filename);
    printf("Rank %d counted %ld words in %s\n", rank, local_count, filename);

    long global_count = 0;
    MPI_Reduce(&local_count, &global_count, 1, MPI_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0)
        printf("Total words across all files: %ld\n", global_count);

    MPI_Finalize();
    return 0;
}
```

**SLURM batch script:**

```bash
#!/bin/bash
#SBATCH --job-name=wordcount
#SBATCH --output=wordcount_%j.out
#SBATCH --time=00:15:00
#SBATCH --partition=cpu
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2G

module load openmpi
# Compile on the login node before submitting: mpicc -O2 -o wordcount wordcount.c
srun ./wordcount /path/to/text/files
```

---

## Best Practices

- **Match `--ntasks` to your problem size.** More MPI ranks is not always faster — communication overhead grows with rank count. Profile your code to find the scaling sweet spot.
- **Use `srun` instead of `mpirun` in batch scripts.** SLURM's `srun` integrates with the job's resource allocation; `mpirun` can over- or under-subscribe cores if used carelessly.
- **Set `OMP_NUM_THREADS` explicitly** in hybrid jobs. The default can vary and lead to oversubscription.
- **Keep MPI ranks on the same node when possible.** Intra-node communication (shared memory) is orders of magnitude faster than inter-node (network). Use `--ntasks-per-node` to control placement.
- **Use collective operations** (`MPI_Bcast`, `MPI_Reduce`, `MPI_Allreduce`) instead of implementing your own loops of point-to-point messages — the library implementation is highly optimized for the underlying hardware.
- **Always call `MPI_Finalize()`** before your program exits. Failing to do so can leave orphaned processes on the compute nodes.

---

## References

- [OpenMPI documentation](https://docs.open-mpi.org/)
- [MPI standard](https://www.mpi-forum.org/docs/)
- [OpenMPI GitHub](https://github.com/open-mpi/ompi)
