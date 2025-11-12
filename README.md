# Lane Cluster Documentation

Welcome to the **Lane Cluster Documentation** — a guide designed to help students, researchers, and collaborators effectively use the **Lane Cluster**, a high-performance computing (**HPC**) resource maintained by the **[Ray and Stephanie Lane Computational Biology Department](https://www.cbd.cmu.edu/)** at **[Carnegie Mellon University](https://www.cmu.edu/)**.

## 📘 About

This documentation provides practical instructions and reference material for navigating and using the Lane Cluster environment.  
It is intended for both new and experienced users conducting computational biology research or data-intensive analyses.

Topics covered include:

- Connecting to the cluster via SSH or remote environments  
- Submitting and monitoring computational jobs  
- Managing storage and data organization  
- Using software modules and HPC tools  
- Best practices for collaboration and resource usage  

## 🚀 Getting Started

You can view the full documentation by building it locally or accessing it online (if published).  

### Build locally

```bash
# Clone this repository
git clone https://github.com/CBDatCMU/cluster-documentation.git
cd cluster-documentation

# Create and activate a conda environment
conda create -n lane-documentation python=3.11 -y
conda activate lane-documentation

# Install dependencies
pip install -r requirements.txt

# Build the HTML documentation
make -C docs html

# Open the result
open docs/build/html/index.html
```

### Live preview (optional)
```bash
sphinx-autobuild docs/source docs/build/html
```
Then open the URL shown in your terminal to see live updates as you edit the documentation.

## 🧩 Contributing

Contributions and corrections are welcome!  
If you find errors or want to suggest improvements, please open an issue or pull request.

---

© 2025 [Carnegie Mellon University](https://www.cmu.edu/).  
Maintained by the [Ray and Stephanie Lane Computational Biology Department](https://www.cbd.cmu.edu/).