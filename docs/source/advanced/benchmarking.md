# Benchmarking the Lane Cluster

This page documents a systematic benchmark across two core computational biology workloads — matrix multiplication and sequence alignment — run on multiple PSC compute nodes. The goal is to characterize the computational limits and performance characteristics of each node so that researchers can make informed decisions about which node to use for a given workload.

Benchmark scripts and raw results are available in the following repositories:
- [benchmark-matrix-multiplication](https://github.com/CBDatCMU/benchmark-matrix-multiplication)
- [benchmark-sequence-alignment](https://github.com/CBDatCMU/benchmark-sequence-alignment)

---

## Nodes Tested

| Node | CPU | Cores | RAM | OS | Python |
|---|---|---|---|---|---|
| **lanec1** | Intel Xeon E5620 @ 2.40 GHz | 8 | 23.4 GB | CentOS 7 | 3.6.4 |
| **lanec2** | Intel Xeon Silver 4314 @ 2.40 GHz (max 3.4 GHz) | 64 | 62 GB | RHEL 9 | 3.9.25 |
| **Bridges-2 (GPU node v010/v020)** | AMD EPYC 7742 @ 2.25 GHz | 128 | 251 GB | RHEL 8 | 3.6.8 |

> **Note on package installation:** `lanec1` runs GLIBC 2.17, which is incompatible with modern Conda/Miniconda installers (require GLIBC ≥ 2.28). All package installation on `lanec1` was done via `pip install --user`.

---

## Part 1: Matrix Multiplication

Matrix multiplication is a core operation in many computational biology workflows, including dimensionality reduction (PCA), machine learning, and coexpression analysis. This benchmark measures wall time, CPU time, and peak memory usage for NumPy dense matrix multiplication across a range of matrix sizes. The primary goal is to identify the maximum matrix size each node can handle and to characterize how performance scales with problem size.

Multiplying two N×N `float64` matrices requires approximately **3 × N² × 8 bytes** of RAM simultaneously (two input matrices plus one output matrix).

### Environment Setup

**lanec1:**
```bash
module load python36
pip3 install numpy --user
python3 -c "import numpy; print(numpy.__version__)"  # 1.19.5
```

**lanec2:**
```bash
curl https://bootstrap.pypa.io/pip/3.9/get-pip.py -o get-pip.py
python3 get-pip.py --user
python3 -m pip install numpy --user
python3 -c "import numpy; print(numpy.__version__)"  # 2.0.2
```

**Bridges-2:**
```bash
module load anaconda3
pip install numpy --user
```

### Results — lanec1

numpy 1.19.5 · float64 · 3 repeats per size

| N | Wall Time (s) | CPU Time (s) | Peak Memory (MB) | Status |
|---|---|---|---|---|
| 500 | 0.004 | 0.035 | 1.9 | ✅ |
| 1,000 | 0.030 | 0.239 | 7.6 | ✅ |
| 2,000 | 0.229 | 1.801 | 30.5 | ✅ |
| 4,000 | 1.898 | 14.396 | 122.1 | ✅ |
| 6,000 | 6.309 | 49.021 | 274.7 | ✅ |
| 8,000 | 14.466 | 112.792 | 488.3 | ✅ |
| 10,000 | 27.455 | 214.400 | 763.0 | ✅ |
| 14,000 | 74.186 | 581.729 | 1,495.4 | ✅ |
| 18,000 | 160.061 | 1,244.993 | 2,471.9 | ✅ |
| 20,000 | 218.74 | — | 3,051.8 | ✅ |
| 24,000 | 371.49 | — | 4,394.5 | ✅ |
| 28,000 | 741.36 | — | 5,981.4 | ✅ |
| 32,000 | — | — | — | ❌ MemoryError |

### Results — lanec2

numpy 2.0.2 · float64 · 1 repeat per size

| N | Wall Time (s) | CPU Time (s) | Peak Memory (MB) | Status |
|---|---|---|---|---|
| 500 | 0.004 | 0.053 | 1.9 | ✅ |
| 1,000 | 0.007 | 0.351 | 7.6 | ✅ |
| 2,000 | 0.039 | 2.352 | 30.5 | ✅ |
| 4,000 | 0.269 | 15.836 | 122.1 | ✅ |
| 6,000 | 0.737 | 44.034 | 274.7 | ✅ |
| 8,000 | 1.733 | 105.331 | 488.3 | ✅ |
| 10,000 | 3.115 | 190.387 | 763.0 | ✅ |
| 14,000 | 8.489 | 524.398 | 1,495.4 | ✅ |
| 18,000 | 16.382 | 1,016.214 | 2,471.9 | ✅ |
| 20,000 | 23.116 | 1,439.532 | 3,051.8 | ✅ |
| 24,000 | 38.235 | 2,388.118 | 4,394.5 | ✅ |
| 28,000 | 63.177 | 3,955.744 | 5,981.5 | ✅ |
| 32,000 | 90.878 | 5,701.352 | 7,812.5 | ✅ |
| 36,000 | 120.229 | 7,548.843 | 9,887.7 | ✅ |

### Results — Bridges-2 (GPU node v020)

numpy · float64 · 1 repeat per size

| N | Wall Time (s) | CPU Time (s) | Peak Memory (MB) | Status |
|---|---|---|---|---|
| 500 | 0.002 | 0.009 | 1.9 | ✅ |
| 1,000 | 0.006 | 0.030 | 7.6 | ✅ |
| 2,000 | 0.043 | 0.214 | 30.5 | ✅ |
| 4,000 | 0.324 | 1.510 | 122.1 | ✅ |
| 6,000 | 1.040 | 4.942 | 274.7 | ✅ |
| 8,000 | 2.419 | 11.624 | 488.3 | ✅ |
| 10,000 | 4.697 | 22.733 | 763.0 | ✅ |
| 14,000 | 12.806 | 62.498 | 1,495.4 | ✅ |
| 18,000 | 26.307 | 128.915 | 2,471.9 | ✅ |
| 20,000 | 35.670 | 175.051 | 3,051.8 | ✅ |
| 24,000 | 61.569 | 302.875 | 4,394.5 | ✅ |
| 28,000 | 97.116 | 478.596 | 5,981.5 | ✅ |
| 32,000 | 143.797 | 709.597 | 7,812.5 | ✅ |
| 36,000 | 201.782 | 996.589 | 9,887.7 | ✅ |
| 40,000 | 280.972 | 1,389.067 | 12,207.0 | ✅ |

### Cross-Node Comparison — Matrix Multiplication

| N | lanec1 (s) | lanec2 (s) | Bridges-2 (s) | lanec2 speedup | Bridges-2 speedup |
|---|---|---|---|---|---|
| 1,000 | 0.030 | 0.007 | 0.006 | 4.3× | 5.0× |
| 4,000 | 1.898 | 0.269 | 0.324 | 7.1× | 5.9× |
| 10,000 | 27.455 | 3.115 | 4.697 | 8.8× | 5.8× |
| 18,000 | 160.061 | 16.382 | 26.307 | 9.8× | 6.1× |
| 28,000 | 741.36 | 63.177 | 97.116 | 11.7× | 7.6× |
| 32,000 | ❌ OOM | 90.878 | 143.797 | — | — |
| 36,000 | ❌ OOM | 120.229 | 201.782 | — | — |
| 40,000 | ❌ OOM | ❌ OOM | 280.972 | — | — |

### Interpretation

- Wall time scales as **O(N³)** and memory as **O(N²)** on all nodes — confirmed empirically.
- **lanec2 is ~9–12× faster than lanec1** due to 64 CPU cores (vs. 8), AVX-512 SIMD, and a newer NumPy version. CPU time is ~63× wall time on lanec2, confirming full 64-core utilization.
- **Bridges-2 is ~5–8× faster than lanec1**, but slower than lanec2 for CPU workloads — GPU nodes have fewer CPU cores available per job (~5 cores active based on CPU/wall time ratio).
- **Memory limits by node:** lanec1 fails at N=32,000; lanec2 supports up to N=36,000 (~9.9 GB); Bridges-2 supports up to N=40,000 (~12.2 GB).
- For CPU matrix multiplication, **lanec2 is the best choice**. Use Bridges-2 only when matrices exceed lanec2's memory capacity.

---

## Part 2: Sequence Alignment

Pairwise sequence alignment is one of the most fundamental tasks in computational biology. This benchmark tests two classic dynamic programming algorithms — Needleman-Wunsch (global alignment) and Smith-Waterman (local alignment) — across three nodes to characterize scaling behavior and cross-hardware performance differences.

Both algorithms have **O(N²)** time and space complexity, where N is the sequence length.

### Environment Setup

**lanec1:**
```bash
module load python36
pip3 install biopython --user
python3 -c "import Bio; print(Bio.__version__)"  # 1.79
```

**lanec2:**
```bash
curl https://bootstrap.pypa.io/pip/3.9/get-pip.py -o get-pip.py
python3 get-pip.py --user
python3 -m pip install biopython --user
```

**Bridges-2:**
```bash
module load anaconda3
pip install biopython --user
```

### Algorithm Overview

- **Needleman-Wunsch (global alignment)**: fills an N×M scoring matrix comparing every position in both sequences end-to-end, then traces back the optimal global alignment. The alignment score can be negative when sequences are dissimilar overall. Use when you expect two sequences to be similar across their full length.
- **Smith-Waterman (local alignment)**: same DP structure, but resets to zero whenever the running score drops below zero. Only the best-matching local region is retained, and the score is always non-negative. Use when searching for a conserved region or motif within a longer sequence.

### Results — lanec1

biopython 1.79 · random DNA sequences · 1 repeat per length

| Length (bp) | Algorithm | Wall Time (s) | CPU Time (s) | Peak Memory (MB) |
|---|---|---|---|---|
| 100 | Needleman-Wunsch | 0.021 | 0.021 | 0.4 |
| 100 | Smith-Waterman | 0.013 | 0.013 | 0.1 |
| 500 | Needleman-Wunsch | 0.738 | 0.738 | 8.6 |
| 500 | Smith-Waterman | 0.532 | 0.532 | 2.0 |
| 1,000 | Needleman-Wunsch | 3.476 | 3.476 | 34.5 |
| 1,000 | Smith-Waterman | 2.587 | 2.587 | 7.7 |
| 2,000 | Needleman-Wunsch | 14.673 | 14.673 | 137.6 |
| 2,000 | Smith-Waterman | 10.997 | 10.997 | 30.7 |
| 3,000 | Needleman-Wunsch | 33.992 | 33.991 | 309.4 |
| 3,000 | Smith-Waterman | 25.558 | 25.557 | 68.9 |
| 5,000 | Needleman-Wunsch | 95.374 | 95.371 | 859.0 |
| 5,000 | Smith-Waterman | 72.944 | 72.943 | 191.2 |
| 8,000 | Needleman-Wunsch | 249.321 | 249.314 | 2,198.4 |
| 8,000 | Smith-Waterman | 189.032 | 189.025 | 489.0 |
| 10,000 | Needleman-Wunsch | 396.631 | 396.607 | 3,434.6 |
| 10,000 | Smith-Waterman | 297.938 | 297.887 | 763.8 |

### Results — lanec2

| Length (bp) | Algorithm | Wall Time (s) | CPU Time (s) | Peak Memory (MB) |
|---|---|---|---|---|
| 100 | Needleman-Wunsch | 0.016 | 0.016 | 0.4 |
| 100 | Smith-Waterman | 0.008 | 0.008 | 0.1 |
| 500 | Needleman-Wunsch | 0.608 | 0.607 | 8.6 |
| 500 | Smith-Waterman | 0.419 | 0.419 | 1.9 |
| 1,000 | Needleman-Wunsch | 2.860 | 2.857 | 34.5 |
| 1,000 | Smith-Waterman | 2.124 | 2.122 | 7.7 |
| 2,000 | Needleman-Wunsch | 12.288 | 12.275 | 137.6 |
| 2,000 | Smith-Waterman | 9.414 | 9.405 | 30.7 |
| 3,000 | Needleman-Wunsch | 28.393 | 28.358 | 309.4 |
| 3,000 | Smith-Waterman | 21.786 | 21.765 | 68.9 |
| 5,000 | Needleman-Wunsch | 80.064 | 79.973 | 858.9 |
| 5,000 | Smith-Waterman | 61.601 | 61.544 | 191.1 |
| 8,000 | Needleman-Wunsch | 206.664 | 206.441 | 2,198.3 |
| 8,000 | Smith-Waterman | 160.274 | 160.127 | 488.9 |
| 10,000 | Needleman-Wunsch | 324.202 | 323.873 | 3,434.5 |
| 10,000 | Smith-Waterman | 251.391 | 251.160 | 763.7 |

### Results — Bridges-2 (GPU node v010)

| Length (bp) | Algorithm | Wall Time (s) | CPU Time (s) | Peak Memory (MB) |
|---|---|---|---|---|
| 100 | Needleman-Wunsch | 0.021 | 0.021 | 0.4 |
| 100 | Smith-Waterman | 0.013 | 0.013 | 0.1 |
| 500 | Needleman-Wunsch | 0.738 | 0.738 | 8.6 |
| 500 | Smith-Waterman | 0.532 | 0.532 | 1.9 |
| 1,000 | Needleman-Wunsch | 2.019 | 2.019 | 34.5 |
| 1,000 | Smith-Waterman | 1.528 | 1.528 | 7.7 |
| 2,000 | Needleman-Wunsch | 8.809 | 8.809 | 137.6 |
| 2,000 | Smith-Waterman | 6.728 | 6.728 | 30.7 |
| 3,000 | Needleman-Wunsch | 20.132 | 20.132 | 309.4 |
| 3,000 | Smith-Waterman | 15.610 | 15.610 | 68.9 |
| 5,000 | Needleman-Wunsch | 56.515 | 56.515 | 859.0 |
| 5,000 | Smith-Waterman | 44.499 | 44.499 | 191.2 |
| 8,000 | Needleman-Wunsch | 146.263 | 146.263 | 2,198.4 |
| 8,000 | Smith-Waterman | 116.956 | 116.956 | 488.9 |
| 10,000 | Needleman-Wunsch | 229.174 | 229.174 | 3,434.6 |
| 10,000 | Smith-Waterman | 179.524 | 179.524 | 763.8 |

### Cross-Node Comparison — Sequence Alignment

| Length (bp) | Algorithm | lanec1 (s) | lanec2 (s) | Bridges-2 (s) | lanec2 speedup | Bridges-2 speedup |
|---|---|---|---|---|---|---|
| 1,000 | Needleman-Wunsch | 3.476 | 2.860 | 2.019 | 1.22× | 1.72× |
| 1,000 | Smith-Waterman | 2.587 | 2.124 | 1.528 | 1.22× | 1.69× |
| 5,000 | Needleman-Wunsch | 95.374 | 80.064 | 56.515 | 1.19× | 1.69× |
| 5,000 | Smith-Waterman | 72.944 | 61.601 | 44.499 | 1.18× | 1.64× |
| 10,000 | Needleman-Wunsch | 396.631 | 324.202 | 229.174 | 1.22× | 1.73× |
| 10,000 | Smith-Waterman | 297.938 | 251.391 | 179.524 | 1.18× | 1.66× |

### Interpretation

- Both algorithms scale as **O(N²)** in time and memory across all nodes — confirmed empirically.
- **Smith-Waterman is ~25% faster and uses ~4.5× less memory** than Needleman-Wunsch at all lengths (e.g., at 10,000 bp: SW uses 764 MB vs. NW's 3,435 MB).
- **CPU time ≈ wall time on all nodes** — pure-Python DP is single-core with no automatic multithreading. Peak memory is also identical across nodes, as it depends only on the algorithm and sequence length.
- **lanec2 is ~1.2× faster than lanec1** and **Bridges-2 is ~1.7× faster** — both speedups reflect CPU clock differences only, not parallelism or GPU acceleration.
- NW at 10,000 bp uses **3.4 GB RAM**, approaching lanec1's practical limit for global alignment. SW at the same length uses only 764 MB.

---

## Part 3: Parallel Sequence Alignment

Since sequence alignment is inherently single-core, a natural way to accelerate throughput for large batches of sequence pairs is to parallelize across pairs using Python's `multiprocessing` module. This benchmark measures how alignment throughput scales with the number of worker processes on **lanec1** (8 cores).

### Method

- Algorithm: Smith-Waterman (pure Python, biopython unavailable on lanec1)
- Sequence pairs: batches of randomly generated DNA sequences
- Workers: 1, 2, 4, 8 (= all available cores on lanec1)
- Metric: wall time, pairs per second, speedup vs. 1 worker

### Results — lanec1

| Seq Length (bp) | Pairs | Workers | Wall Time (s) | Pairs/sec | Speedup |
|---|---|---|---|---|---|
| 500 | 200 | 1 | 51.957 | 3.849 | 1.00× |
| 500 | 200 | 2 | 26.260 | 7.616 | 1.98× |
| 500 | 200 | 4 | 13.931 | 14.357 | 3.73× |
| 500 | 200 | 8 | 7.823 | 25.566 | 6.64× |
| 1,000 | 100 | 1 | 108.770 | 0.919 | 1.00× |
| 1,000 | 100 | 2 | 56.315 | 1.776 | 1.93× |
| 1,000 | 100 | 4 | 30.968 | 3.229 | 3.51× |
| 1,000 | 100 | 8 | 18.545 | 5.392 | 5.87× |
| 2,000 | 40 | 1 | 182.126 | 0.220 | 1.00× |
| 2,000 | 40 | 2 | 91.889 | 0.435 | 1.98× |
| 2,000 | 40 | 4 | 55.531 | 0.720 | 3.28× |
| 2,000 | 40 | 8 | 28.880 | 1.385 | 6.31× |
| 5,000 | 16 | 1 | 498.527 | 0.032 | 1.00× |
| 5,000 | 16 | 2 | 248.072 | 0.065 | 2.01× |
| 5,000 | 16 | 4 | 126.784 | 0.126 | 3.93× |
| 5,000 | 16 | 8 | 67.538 | 0.237 | 7.38× |

### Interpretation

- Parallelization delivers **near-linear speedup** — at 8 workers, speedup ranges from 5.87× (1,000 bp) to 7.38× (5,000 bp) out of a theoretical maximum of 8×.
- **Longer sequences parallelize more efficiently** because computation time dominates process-spawning overhead at larger sequence lengths.
- On nodes with more cores (lanec2: 64, Bridges-2: 128+), batch alignment throughput would scale proportionally higher.

---

## When to Use Which Node and Algorithm

### Choosing a node

| Scenario | Recommended Node | Reason |
|---|---|---|
| Small workloads (sequences < 3,000 bp, matrices N < 8,000) | **lanec1** | Sufficient; no queue required |
| Matrix multiplication, any size | **lanec2** | ~10× faster than lanec1; supports N up to 36,000+ |
| Matrix N > 28,000 and N ≤ 36,000 | **lanec2** | More CPU cores; lanec1 runs out of memory |
| Matrix N > 36,000 | **Bridges-2** | More RAM; tested up to N = 40,000 |
| Single sequence alignment, speed matters | **Bridges-2** | ~1.7× faster single-core CPU than lanec1 |
| Batch alignment (many pairs) | **lanec2** or **Bridges-2** | More cores → higher parallel throughput |
| GPU-accelerated workloads (CuPy, PyTorch) | **Bridges-2 GPU node** | Only node with NVIDIA V100 GPUs |

### Choosing an alignment algorithm

| Scenario | Recommended Algorithm | Reason |
|---|---|---|
| Comparing two full-length sequences of similar length (e.g., orthologous genes across species) | **Needleman-Wunsch** | Global alignment gives a meaningful end-to-end score |
| Searching for a conserved motif or domain within a longer sequence | **Smith-Waterman** | Local alignment finds the best matching region regardless of what surrounds it |
| Memory is constrained (sequences > 5,000 bp) | **Smith-Waterman** | Uses ~4.5× less memory than NW at the same length |
| Speed is the priority | **Smith-Waterman** | ~25% faster than NW at all lengths |
| Running a large batch of alignments in parallel | **Smith-Waterman** | Faster per pair; lower memory per worker process |
| You need a global alignment score (e.g., for phylogenetic distance) | **Needleman-Wunsch** | SW score is not meaningful as a global similarity measure |

> **General recommendation:** Prefer Smith-Waterman unless you specifically require a global alignment. It is faster, uses significantly less memory, and is the more appropriate choice for most database search and motif-finding tasks in computational biology.

---

## Summary

| Benchmark | Node | Result | Key Finding |
|---|---|---|---|
| Matrix multiplication | lanec1 | Max N = 28,000 | N ≥ 32,000 fails with MemoryError |
| Matrix multiplication | lanec2 | Max tested N = 36,000 ✅ | ~10× faster than lanec1; 64-core BLAS parallelism |
| Matrix multiplication | Bridges-2 (v020) | Max tested N = 40,000 ✅ | ~6× faster than lanec1; CPU-limited on GPU node (~5 cores) |
| Sequence alignment | lanec1 | All lengths ≤ 10,000 bp ✅ | NW uses 3.4 GB at 10,000 bp; SW recommended |
| Sequence alignment | lanec2 | All lengths ≤ 10,000 bp ✅ | ~1.2× faster than lanec1 (single-core CPU difference) |
| Sequence alignment | Bridges-2 | All lengths ≤ 10,000 bp ✅ | ~1.7× faster than lanec1 (single-core CPU difference) |
| Parallel alignment | lanec1 (8 cores) | Up to 7.38× speedup at 8 workers | Near-linear scaling; longer sequences parallelize more efficiently |

---

## References

- NumPy documentation: <https://numpy.org/doc/>
- Biopython documentation: <https://biopython.org/docs/>
- benchmark-matrix-multiplication repo: <https://github.com/CBDatCMU/benchmark-matrix-multiplication>
- benchmark-sequence-alignment repo: <https://github.com/CBDatCMU/benchmark-sequence-alignment>
- Smith-Waterman algorithm: Smith, T.F. & Waterman, M.S. (1981). *Journal of Molecular Biology*, 147(1), 195–197.
- Needleman-Wunsch algorithm: Needleman, S.B. & Wunsch, C.D. (1970). *Journal of Molecular Biology*, 48(3), 443–453.
