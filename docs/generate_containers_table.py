#!/usr/bin/env python3
"""
Generates a Markdown table of Singularity/Apptainer containers available in
lanec2 and inserts it into apptainer.md under the section
"Software available as containers in lanec2", placed before
"## Example 1: Running a Python Script".

Requires GITHUB_TOKEN env var for authenticated API access (avoids rate limits).
"""

import os
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple

ORG = "CBDatCMU"
PROJECT_PREFIX = "singularity"
API_BASE = "https://api.github.com"
APPTAINER_MD = os.path.join(
    os.path.dirname(__file__), "source", "advanced", "apptainer.md"
)

SECTION_HEADER = "## Software available as containers in lanec2"
ANCHOR_HEADER = "## Example 1: Running a Python Script"

STEM_REPOS = [
    "stride", "nanoplot", "star-fusion", "filtlong", "porechop", "anvio",
    "funannotate", "fastq-tools", "meme-suite", "braker2", "rust", "guppy",
    "guppy-gpu", "bsmap", "salmon", "rnaview", "bioformats2raw", "raw2ometiff",
    "flash", "blat", "bedops", "genemark-es", "augustus", "checkm", "ncview",
    "bowtie2", "asciigenome", "fastqc", "sra-toolkit", "gatk", "hmmer",
    "bcftools", "raxml", "spades", "busco", "samtools", "bedtools", "bamtools",
    "fastani", "phylip-suite", "blast", "viennarna", "cutadapt", "bismark",
    "star", "prodigal", "bwa", "picard", "hisat2", "abyss", "octave", "tiger",
    "gent", "methylpy", "fasttree", "vcf2maf", "htslib", "kraken2",
    "aspera-connect", "trimmomatic",
]

UTIL_REPOS = [
    "papis", "hashdeep", "gcalcli", "dua", "vim", "libtiff-tools", "shellcheck",
    "pandiff", "rich-cli", "jq", "jp", "lowcharts", "btop", "aws-cli", "cwltool",
    "circos", "glances", "fdupes", "graphviz", "browsh", "hyperfine", "dust",
    "gnuplot", "pandoc", "mc", "bat", "flac", "visidata", "octave", "ncdu",
    "lazygit", "asciinema", "ffmpeg", "imagemagick", "rclone",
]

VIZ_REPOS = ["gimp", "inkscape"]


def gh_session() -> requests.Session:
    s = requests.Session()
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        s.headers["Authorization"] = f"Bearer {token}"
    s.headers["Accept"] = "application/vnd.github+json"
    return s


SESSION = gh_session()


def release_info_for(full_repo: str) -> str:
    try:
        r = SESSION.get(f"{API_BASE}/repos/{full_repo}/releases/latest", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return (data.get("tag_name") or data.get("name") or "").strip() or "—"
        r = SESSION.get(
            f"{API_BASE}/repos/{full_repo}/tags", params={"per_page": 1}, timeout=10
        )
        if r.status_code == 200 and isinstance(r.json(), list) and r.json():
            return (r.json()[0].get("name") or "").strip() or "—"
    except requests.RequestException:
        pass
    return "—"


def last_commit_date_for(full_repo: str) -> str:
    try:
        r = SESSION.get(
            f"{API_BASE}/repos/{full_repo}/commits", params={"per_page": 1}, timeout=10
        )
        if r.status_code == 200 and isinstance(r.json(), list) and r.json():
            commit = r.json()[0]
            date_str = (
                commit.get("commit", {}).get("committer", {}).get("date")
                or commit.get("commit", {}).get("author", {}).get("date")
                or ""
            ).strip()
            if date_str:
                return date_str.split("T")[0]
            return "—"
    except requests.RequestException:
        pass
    return "—"



def unified_catalog() -> List[Tuple[str, str]]:
    m: Dict[str, str] = {}
    for r in STEM_REPOS:
        m[r] = "Scientific tool"
    for r in UTIL_REPOS:
        m.setdefault(r, "Utility")
    for r in VIZ_REPOS:
        m.setdefault(r, "Remote Desktop Application")
    return sorted(((cat, r) for r, cat in m.items()), key=lambda x: x[1].lower())


def build_table_section(items, latest_map, commit_map) -> str:
    lines = []
    lines.append(SECTION_HEADER)
    lines.append("")
    lines.append("| Category | Name | Latest | Last Commit |")
    lines.append("| --- | --- | --- | --- |")
    for cat, repo in items:
        base = f"https://github.com/{ORG}/{PROJECT_PREFIX}-{repo}"
        lines.append(
            f"| {cat} | [{repo}]({base}) | {latest_map.get(repo, '—')} | {commit_map.get(repo, '—')} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + "\n"


def fetch_data(items):
    latest_map, commit_map = {}, {}

    def fetch_one(repo: str):
        full = f"{ORG}/{PROJECT_PREFIX}-{repo}"
        latest_tag = release_info_for(full)
        last_commit = last_commit_date_for(full)
        return latest_tag, last_commit

    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = {ex.submit(fetch_one, repo): (cat, repo) for cat, repo in items}
        for fut in as_completed(futures):
            cat, repo = futures[fut]
            try:
                latest_tag, last_commit = fut.result()
                latest_map[repo] = latest_tag
                commit_map[repo] = last_commit
            except Exception as e:
                print(f"[warn] {repo}: {e}", file=sys.stderr)
                latest_map[repo] = "—"
                commit_map[repo] = "—"

    return latest_map, commit_map


def update_apptainer_md(section_content: str) -> None:
    with open(APPTAINER_MD, "r", encoding="utf-8") as f:
        original = f.read()

    # Remove existing generated section if present
    if SECTION_HEADER in original:
        start = original.index(SECTION_HEADER)
        # Find where the next ## section begins after our section
        after_section = original.find("\n## ", start + len(SECTION_HEADER))
        if after_section == -1:
            original = original[:start]
        else:
            original = original[:start] + original[after_section + 1:]

    # Insert before the anchor header
    if ANCHOR_HEADER not in original:
        print(f"[error] Could not find anchor '{ANCHOR_HEADER}' in {APPTAINER_MD}", file=sys.stderr)
        sys.exit(1)

    insert_pos = original.index(ANCHOR_HEADER)
    updated = original[:insert_pos] + section_content + original[insert_pos:]

    with open(APPTAINER_MD, "w", encoding="utf-8") as f:
        f.write(updated)


def main() -> None:
    print("Fetching container metadata from GitHub...", file=sys.stderr)
    items = unified_catalog()
    latest_map, commit_map = fetch_data(items)
    section = build_table_section(items, latest_map, commit_map)
    update_apptainer_md(section)
    print(f"Updated {APPTAINER_MD}", file=sys.stderr)


if __name__ == "__main__":
    main()
