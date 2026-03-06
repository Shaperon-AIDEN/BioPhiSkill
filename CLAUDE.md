# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BioPhiSkill is a lightweight, agent-friendly fork of [BioPhi](https://github.com/Merck/BioPhi) (Merck). It removes the web server (Flask/Redis/Celery) and replaces the 22 GB local OASis SQLite database with a hosted Azure REST API. The result is a self-contained Python skill package for antibody humanization and humanness evaluation, callable from AI agents.

## Setup

```bash
# Install (creates conda env 'biophi' with Python 3.9, HMMER, abnumber, and pip deps)
bash install.sh
conda activate biophi
```

The installer auto-applies the ANARCI Python 3.12+ compatibility patch. The `biophi` conda environment is required — the package cannot run in arbitrary Python environments due to the HMMER binary and `abnumber`/`anarci` bioconda dependencies.

**Verify installation:**
```bash
conda activate biophi
python -c "from agent_api import humanize_antibody_sequence; print('OK')"
```

## Running Tests

```bash
conda activate biophi
pytest
```

## Key Architecture

### Entry Point: `agent_api.py`
The sole public API for agent consumption. Two functions:
- `humanize_antibody_sequence(vh_seq, vl_seq=None, ...)` — Sapiens humanization + before/after OASis evaluation
- `evaluate_humanness(vh_seq, vl_seq=None, ...)` — OASis-only evaluation (no humanization)

Both return dicts with `summary`, `before`/`after` metrics, `germlines`, `plot_image`, and `excel_report`.

### Core Library: `biophi/humanization/methods/`
- **`humanization.py`** — Sapiens model integration. `humanize_chain()` dispatches to `sapiens_humanize_chain()`, which calls `sapiens.predict_scores()` per iteration and grafts parental CDRs back unless `humanize_cdrs=True`. Key dataclass: `ChainHumanization` (holds parental chain, humanized chain, per-position scores).
- **`humanness.py`** — OASis evaluation. `get_chain_humanness()` calls the Azure REST API via `requests.post()`. The API endpoint receives a list of 9-mer peptides and returns per-peptide OAS subject counts. Key dataclasses: `ChainHumanness`, `PeptideHumanness`, `AntibodyHumanness`.
- **`stats.py`** — OASis percentile lookup and germline residue frequency tables used by `humanness.py`.

### Compatibility Patch: `patches/anarci_compat.py`
Auto-imported by `agent_api.py` before any `abnumber`/`anarci` imports. Monkey-patches two ANARCI functions (`_domains_are_same`, `_hmm_alignment_to_states`) to handle `None` HSP coordinates from Biopython >= 1.80 on Python 3.12+.

### Dependencies (managed via `environment.yml` + `setup.py`)
- `abnumber` / `anarci` / `hmmer` — antibody numbering (must be installed via bioconda)
- `sapiens >= 1.1.0` — deep learning humanization model (PyTorch-based, downloads from HuggingFace on first run)
- `requests` — Azure OASis REST API calls
- `pandas < 2.2`, `sqlalchemy < 2` — version-pinned due to API changes
- `matplotlib`, `seaborn`, `openpyxl` — plot and Excel report generation

## OASis Azure API

All humanness evaluation calls POST to `https://biophioasisapi.azurewebsites.net/api/peptides/` with `{"peptides": [...], "chain_type": "Heavy"|"Light"}`. Internet access is required at runtime.

## Skill Descriptor

`SKILL.md` is the machine-readable skill descriptor for Claude Code / OpenCode skill loading. It contains the YAML front matter `name: biophi` and the full function reference. Do not rename or restructure it.
