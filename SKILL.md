---
name: biophi
description: Antibody humanization (Sapiens) and humanness evaluation (OASis) via Azure API. Provides before/after comparison of OASis identity, OASis percentile, germline content, germline genes, and humanizing mutations. Generates plots and Excel reports.
---

# BioPhiSkill

Lightweight antibody engineering skill backed by the **Sapiens** deep learning model and the **Azure OASis REST API**. No local 22GB database required.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Shaperon-AIDEN/BioPhiSkill.git
cd BioPhiSkill

# 2. Run the installer (sets up conda env, installs all dependencies)
bash install.sh

# 3. Activate environment
conda activate biophi
```

> The installer creates a `biophi` conda environment with Python 3.9, HMMER, abnumber, and all pip dependencies. It also auto-applies the ANARCI compatibility patch for newer Python/Biopython versions.

## Quick Test

```bash
conda activate biophi
python -c "from agent_api import humanize_antibody_sequence; print('BioPhiSkill ready!')"
```

---

## Functions

### `humanize_antibody_sequence` — Full Humanization Pipeline

Runs Sapiens humanization and evaluates OASis humanness **before and after**.

```python
from agent_api import humanize_antibody_sequence

result = humanize_antibody_sequence(
    vh_seq="EVQLQQSGAELVRPGALVKLSCKASGFNIKDYYMHWVK...",
    vl_seq=None,                 # optional light chain
    scheme="imgt",               # numbering scheme: imgt / kabat / chothia
    cdr_definition="imgt",       # CDR definition
    sapiens_iterations=1,        # Sapiens iteration count
    humanize_cdrs=False,         # retain parental CDRs (recommended)
    min_fraction_subjects=0.1,   # OASis threshold (10%)
    output_dir="./output"        # where to save plot + Excel
)
print(result["summary"])
```

**Returns**:
| Key | Type | Description |
|-----|------|-------------|
| `summary` | str | Human-readable text summary |
| `vh_mutations` | list | `[{position, from, to}, ...]` for VH |
| `vl_mutations` | list | `[{position, from, to}, ...]` for VL |
| `before` | dict | OASis identity/percentile/germline content (pre-humanization) |
| `after` | dict | OASis identity/percentile/germline content (post-humanization) |
| `germlines` | dict | `{vh_before, vh_after, vl_before, vl_after}` germline gene names |
| `plot_image` | str | Path to `humanness_plot.png` |
| `excel_report` | str | Path to `humanization_report.xlsx` |

**Example output**:
```
[Humanizing Mutations]
  VH: 14 mutations
  VH changes: EH1Q, QH5V, LH12V, VH13K, LH18S…

[OASis Identity (threshold=10%)]
  Combined Before: 37.14%  →  After: 71.43%

[OASis Percentile]
  VH Before: 2.00%  →  After: 34.00%

[Germline Content]
  VH Before: 67.26%  →  After: 77.88%

[Germlines]
  VH Before: IGHV1-69-2*01 / IGHJ4*01
  VH After : IGHV1-2*02 / IGHJ4*01
```

---

### `evaluate_humanness` — OASis-only Evaluation

Evaluates humanness **without humanization** (for e.g. checking a sequence that's already been engineered).

```python
from agent_api import evaluate_humanness

result = evaluate_humanness(
    vh_seq="EVQLVESGGGLVQPGR...",
    vl_seq=None,
    min_fraction_subjects=0.1,
    output_dir="./output"
)
print(result["summary"])
```

**Returns**: `oasis_identity`, `oasis_percentile`, `germline_content`, `germlines`, `plot_image`, `excel_report`, `summary`

---

## OASis Azure API

All humanness evaluations use a hosted Azure REST API (no local DB needed):

- **Endpoint**: `https://biophioasisapi.azurewebsites.net/api/peptides/`
- **Method**: `POST`
- **Payload**: `{"peptides": ["EVQLVESGG", ...], "chain_type": "Heavy"}`
- **Response**: `{"num_total_oas_subjects": N, "hits": [{peptide, num_oas_subjects, num_oas_occurrences}, ...]}`

## Output Files

| File | Description |
|------|-------------|
| `humanness_plot.png` | Bar chart of per-peptide OASis % (green = human ≥ threshold, red = non-human) |
| `humanization_report.xlsx` | Sheets: Summary · Mutations · VH Before · VH After · VL Before · VL After |

## Architecture

```
BioPhiSkill/
├── SKILL.md              ← This file (Skill descriptor for Claude Code / OpenCode)
├── install.sh            ← One-shot installer (conda env + pip + all dependencies)
├── agent_api.py          ← Main entry point for agents
├── patches/
│   └── anarci_compat.py  ← Auto-applied ANARCI patch (Python 3.12 compatibility)
├── biophi/               ← Core library (Sapiens + OASis, Flask/Redis/Celery removed)
│   ├── humanization/
│   │   └── methods/
│   │       ├── humanization.py   ← Sapiens & CDR grafting logic
│   │       └── humanness.py      ← OASis evaluation (uses Azure REST API)
│   └── common/
└── environment.yml       ← Conda environment spec
```
