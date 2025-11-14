# Using Modulefiles on the Lane Cluster

The **Lane Cluster** uses *environment modules* to manage software installations.  
Modules let you easily load, unload, and switch between different versions of tools without altering your shell configuration.

Environment modules are implemented in **Tcl**, but as a user, you’ll primarily *use* them — not write them.

---

## 🔍 Searching for Available Software

To see what software is available through modulefiles:

```bash
module avail
```

This lists all the modules installed on the system.  
You can narrow your search using keywords, for example:

```bash
module avail python
module avail gcc
```

If the output is long, pipe it through `less`:

```bash
module avail | less
```

---

## 📦 Loading and Unloading Modules

To load a module (for example, Python 3.11):

```bash
module load python/3.11
```

To confirm it was loaded:

```bash
module list
```

You can unload it when done:

```bash
module unload python/3.11
```

Or clear all active modules:

```bash
module purge
```

---

## 🧰 Checking Module Information

To learn what a module does and what environment variables it modifies:

```bash
module show python/3.11
```

This displays paths such as `PATH`, `LD_LIBRARY_PATH`, and `PYTHONPATH` that the module sets.

---

## 🧩 Using Modules in Job Scripts

When writing a SLURM batch or shell script for the Lane Cluster, you can include module commands to set up your environment automatically.

Example SLURM script:

```bash
#!/bin/bash
#SBATCH --job-name=example
#SBATCH --output=output.log
#SBATCH --time=01:00:00
#SBATCH --ntasks=1

# Load necessary modules
module load python/3.11
module load gcc/11.2.0

# Run your program
python my_script.py
```

This ensures that when your job runs, the environment matches what you expect.

---

## 🧠 Tips and Best Practices

- Always load modules inside your batch or shell scripts to ensure reproducibility.  
- Use `module list` interactively to check which modules are active before launching long jobs.  
- If a command fails, run `module purge` and reload only what you need.  
- Prefer explicit versions (e.g., `python/3.11`) instead of default aliases.

---

## 🔗 More Resources

- [Environment Modules Project Documentation](http://modules.sourceforge.net/)
- [Tcl Environment Modules GitHub](https://github.com/cea-hpc/modules)
- [Lane Cluster Overview](https://www.cbd.cmu.edu/research/computational-biology-cluster/)
