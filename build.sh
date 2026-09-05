#!/usr/bin/env bash
#
# build.sh - Build the HTML and PDF output of the Lane Cluster documentation.
#
# Usage:
#   ./build.sh              Build both HTML and PDF
#   ./build.sh --html-only  Build only HTML
#   ./build.sh --pdf-only   Build only PDF
#   ./build.sh --clean      Remove all build output and temporary files, then exit
#   ./build.sh --help       Show this message
#
# Output:
#   docs/build/html/index.html
#   docs/build/pdf/*.pdf

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$REPO_ROOT/docs"
BUILD_DIR="$DOCS_DIR/build"
HTML_DIR="$BUILD_DIR/html"
LATEX_DIR="$BUILD_DIR/latex"
PDF_DIR="$BUILD_DIR/pdf"

BUILD_HTML=1
BUILD_PDF=1

# --- Output helpers -------------------------------------------------------

info()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn()  { printf '\033[1;33mwarning:\033[0m %s\n' "$*" >&2; }
error() { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; }

usage() {
    sed -n '3,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

# --- Argument parsing -----------------------------------------------------

CLEAN_ONLY=0
while [ $# -gt 0 ]; do
    case "$1" in
        --html-only) BUILD_PDF=0 ;;
        --pdf-only)  BUILD_HTML=0 ;;
        --clean)     CLEAN_ONLY=1 ;;
        -h|--help)   usage; exit 0 ;;
        *)           error "unknown option: $1"; usage; exit 2 ;;
    esac
    shift
done

# --- Cleaning -------------------------------------------------------------

# Remove build output in its entirety. Every run starts from scratch so that
# renamed or deleted pages never linger in the output.
clean_build() {
    info "Cleaning build directory"
    rm -rf "$BUILD_DIR"
}

# Remove intermediates left behind by LaTeX, Python and macOS. Keeps the
# finished html/ and pdf/ directories.
clean_trash() {
    info "Cleaning temporary files"

    rm -rf "$BUILD_DIR/doctrees" "$LATEX_DIR"

    find "$REPO_ROOT" \
        \( -name '__pycache__' -o -name '.ipynb_checkpoints' -o -name '.pytest_cache' \) \
        -type d -prune -exec rm -rf {} + 2>/dev/null || true

    find "$REPO_ROOT" -type f \
        \( -name '.DS_Store' -o -name '*.pyc' -o -name '*~' \
           -o -name '*.aux' -o -name '*.idx' -o -name '*.ilg' -o -name '*.ind' \
           -o -name '*.out' -o -name '*.toc' -o -name '*.fls' \
           -o -name '*.fdb_latexmk' -o -name '*.synctex.gz' \) \
        -delete 2>/dev/null || true
}

if [ "$CLEAN_ONLY" -eq 1 ]; then
    clean_build
    clean_trash
    info "Clean complete"
    exit 0
fi

# --- Preflight ------------------------------------------------------------

# Sphinx and its extensions are required for every build. Invoke it through
# `python3 -m sphinx` so the active conda/virtual environment is used even when
# the sphinx-build wrapper is not on PATH.
check_sphinx() {
    if ! python3 -c 'import sphinx' >/dev/null 2>&1; then
        error "Sphinx is not installed in the active Python environment."
        printf '\n'
        printf '  Active interpreter: %s\n' "$(command -v python3)"
        printf '\n'
        printf '  Install the documentation dependencies:\n'
        printf '\n'
        printf '      conda create -n lane-documentation python=3.11 -y\n'
        printf '      conda activate lane-documentation\n'
        printf '      pip install -r requirements.txt\n'
        printf '\n'
        exit 1
    fi
}

# The PDF build additionally needs a LaTeX toolchain. BasicTeX ships xelatex
# but almost none of the packages the Sphinx LaTeX writer emits, so check for a
# representative package rather than just the binary.
check_latex() {
    local missing=0

    if ! command -v xelatex >/dev/null 2>&1; then
        error "xelatex not found."
        missing=1
    elif ! kpsewhich fncychap.sty >/dev/null 2>&1; then
        error "The LaTeX installation is missing packages Sphinx requires (fncychap.sty not found)."
        error "This usually means BasicTeX is installed rather than the full TeX Live."
        missing=1
    fi

    if [ "$missing" -eq 1 ]; then
        printf '\n'
        printf '  Install the full TeX Live distribution:\n'
        printf '\n'
        printf '      brew install --cask mactex-no-gui     # macOS, ~6 GB\n'
        printf '      sudo apt install texlive-full latexmk  # Debian/Ubuntu\n'
        printf '\n'
        printf '  Or build HTML only:\n'
        printf '\n'
        printf '      ./build.sh --html-only\n'
        printf '\n'
        exit 1
    fi
}

# --- Builders -------------------------------------------------------------

build_html() {
    info "Building HTML"
    make -C "$DOCS_DIR" html
    info "HTML written to $HTML_DIR/index.html"
}

build_pdf() {
    info "Building PDF"

    # Regenerate the containers table, matching what the html target does.
    ( cd "$DOCS_DIR" && python3 generate_containers_table.py )

    python3 -m sphinx -M latex "$DOCS_DIR/source" "$BUILD_DIR"

    local tex_file
    tex_file="$(find "$LATEX_DIR" -maxdepth 1 -name '*.tex' -print -quit)"
    if [ -z "$tex_file" ]; then
        error "Sphinx did not produce a .tex file in $LATEX_DIR"
        exit 1
    fi

    if command -v latexmk >/dev/null 2>&1; then
        info "Running latexmk"
        ( cd "$LATEX_DIR" && latexmk -xelatex -interaction=nonstopmode -halt-on-error "$(basename "$tex_file")" )
    else
        # latexmk is absent (BasicTeX does not bundle it). Run xelatex directly.
        # Three passes resolve the table of contents and cross-references.
        warn "latexmk not found; running xelatex directly (3 passes)"
        local pass
        for pass in 1 2 3; do
            info "xelatex pass $pass/3"
            ( cd "$LATEX_DIR" && xelatex -interaction=nonstopmode -halt-on-error "$(basename "$tex_file")" ) >/dev/null
        done
    fi

    local pdf_file
    pdf_file="$(find "$LATEX_DIR" -maxdepth 1 -name '*.pdf' -print -quit)"
    if [ -z "$pdf_file" ]; then
        error "No PDF was produced. See the LaTeX log in $LATEX_DIR"
        exit 1
    fi

    mkdir -p "$PDF_DIR"
    cp "$pdf_file" "$PDF_DIR/"
    info "PDF written to $PDF_DIR/$(basename "$pdf_file")"
}

# --- Main -----------------------------------------------------------------

check_sphinx
if [ "$BUILD_PDF" -eq 1 ]; then
    check_latex
fi

clean_build

if [ "$BUILD_HTML" -eq 1 ]; then
    build_html
fi

if [ "$BUILD_PDF" -eq 1 ]; then
    build_pdf
fi

clean_trash

info "Build complete"
