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

### 1. Install the Python dependencies

Required for **all** builds.

```bash
# Clone this repository
git clone https://github.com/CBDatCMU/lanec2-docs.git
cd lanec2-docs

# Create and activate a conda environment
conda create -n lane-documentation python=3.12 -y
conda activate lane-documentation

# Install dependencies
pip install -r docs/requirements.txt
```

> **Python 3.12 or newer is required.** `sphinx-autodoc-typehints==3.10.2` declares `Requires-Python >=3.12`; on 3.11 the install fails with `No matching distribution found`.

`docs/requirements.txt` is what builds the documentation. The root `requirements.txt` is a superset that also carries tooling for working on the cluster itself — install that one instead if you want the full environment.

Note that several pages under `docs/source/advanced/` use `{jupyter-execute}` blocks, which run real code during the build. That is why `dask`, `duckdb`, `numpy`, `pandas` and `polars` are documentation build dependencies and not optional extras.

### 2. Install LaTeX

Required **only for PDF output**. Skip this if you only need HTML — use `./build.sh --html-only`.

Sphinx emits LaTeX that depends on a wide set of packages (`fncychap`, `tabulary`, `framed`, `titlesec`, `wrapfig`, `capt-of`, `needspace`) plus the FreeFont family, because `conf.py` sets `latex_engine = 'xelatex'`. **A minimal distribution such as BasicTeX or TinyTeX will not work** — install a full distribution.

#### macOS

```bash
brew install --cask mactex-no-gui
```

The `-no-gui` cask installs the full TeX Live distribution (~6 GB) without the TeXShop, BibDesk and LaTeXiT applications. It includes `latexmk`. If you prefer the GUI tools, use `mactex` instead. Without Homebrew, download the MacTeX installer from [tug.org/mactex](https://tug.org/mactex/).

After installing, open a new terminal so `/Library/TeX/texbin` is on your `PATH`.

> **Already have BasicTeX?** Installing MacTeX over it is the simplest fix. Upgrading BasicTeX in place with `tlmgr` tends to fail once your local TeX Live release is older than the remote repository, which produces a `Cross release updates are only supported with...` error.

#### Windows

Install [MiKTeX](https://miktex.org/download) or [TeX Live](https://tug.org/texlive/windows.html):

```powershell
# MiKTeX (recommended - installs missing packages on demand)
winget install MiKTeX.MiKTeX

# or the full TeX Live distribution
winget install TeXLive.TeXLive
```

With MiKTeX, also install `latexmk` and set the package installer to automatic:

```powershell
miktex packages install latexmk
miktex packages install fncychap tabulary framed titlesec wrapfig capt-of needspace
```

Run the build from **Git Bash** or **WSL**, since `build.sh` is a Bash script.

#### Linux

```bash
sudo apt install texlive-full latexmk        # Debian/Ubuntu
sudo dnf install texlive-scheme-full latexmk # Fedora/RHEL
```

### 3. Build

```bash
./build.sh              # HTML and PDF
./build.sh --html-only  # HTML only (no LaTeX required)
./build.sh --pdf-only   # PDF only
./build.sh --clean      # Remove build output and temporary files
```

Output lands in `docs/build/html/index.html` and `docs/build/pdf/`. The script wipes `docs/build/` before each run and sweeps up LaTeX intermediates, `__pycache__/` and `.DS_Store` files afterwards. It checks for its dependencies up front and tells you what to install if anything is missing.

To build the HTML without the script, the original Make target still works:

```bash
make -C docs html
open docs/build/html/index.html
```

### Live preview (optional)
```bash
sphinx-autobuild docs/source docs/build/html
```
Then open the URL shown in your terminal to see live updates as you edit the documentation.

## 📡 Publishing

The documentation is published at **[lanec2.readthedocs.io](https://lanec2.readthedocs.io)**.

Builds are driven by `.readthedocs.yaml` at the repository root. Read the Docs calls `sphinx-build` directly and **ignores `docs/Makefile`**, so the containers table that the `html` target normally generates is produced by a `build.jobs.pre_build` step instead.

That step runs `docs/generate_containers_table.py`, which queries the GitHub API for `CBDatCMU/singularity-*` repositories. Set `GITHUB_TOKEN` under **Admin → Environment Variables** in the Read the Docs project, otherwise the build hits the 60 requests/hour anonymous rate limit and the table is published incomplete.

To set the project up from scratch:

1. Sign in to [readthedocs.org](https://readthedocs.org) with GitHub.
2. **Import a Project**, connect the `CBDatCMU` organization, and select `lanec2-docs`. An organization owner must authorize the Read the Docs GitHub App so it can install the webhook.
3. Set the project **Name** to `lanec2` so the published URL is `lanec2.readthedocs.io`. Read the Docs derives the slug from the name, so leaving it as the repository name would publish to `lanec2-docs.readthedocs.io`.
4. Add the `GITHUB_TOKEN` environment variable described above.
5. Push to `main`. The webhook triggers a build.

## 🧩 Contributing

Contributions and corrections are welcome!  
If you find errors or want to suggest improvements, please open an issue or pull request.

---

© 2025 [Ray and Stephanie Lane Computational Biology Department](https://www.cbd.cmu.edu/) at [School of Computer Science](https://www.cs.cmu.edu/) in [Carnegie Mellon University](https://www.cmu.edu/). 