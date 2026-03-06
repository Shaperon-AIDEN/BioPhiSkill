---
name: biophi
description: Antibody humanization (Sapiens) and humanness evaluation (OASis) via Azure API. Provides before/after comparison of OASis identity, OASis percentile, germline content, germline genes, and humanizing mutations. Generates plots and Excel reports.
---

# BioPhiSkill

Lightweight antibody engineering skill backed by the **Sapiens** deep learning model and the **Azure OASis REST API** (no local 22GB database required).

## Environment Setup

```bash
# From the BioPhiSkill directory:
conda create -n biophi python=3.9
conda activate biophi
conda install -c bioconda -c conda-forge abnumber hmmer
pip install -e .
pip install matplotlib seaborn openpyxl
```

> **Note**: The ANARCI library (installed via `abnumber`) must be patched for Python 3.12 compatibility. The patch is already applied in `venv_test` at `/Users/Sungmin/workspace/BioPhi`.

## Functions

### 1. `humanize_antibody_sequence` — Full Humanization Pipeline

Runs Sapiens humanization and evaluates OASis humanness **before and after**.

```python
import sys
sys.path.insert(0, "/Users/Sungmin/workspace/BioPhi/BioPhiSkill")

from agent_api import humanize_antibody_sequence

result = humanize_antibody_sequence(
    vh_seq="EVQLQQSGAELVRPGALVKLSCKASGFNIKDYYMHWVK...",
    vl_seq=None,                 # optional light chain
    scheme="imgt",               # numbering scheme: imgt / kabat / chothia
    cdr_definition="imgt",       # CDR definition
    sapiens_iterations=1,        # Sapiens iterations
    humanize_cdrs=False,         # retain parental CDRs
    min_fraction_subjects=0.1,   # OASis threshold (10%)
    output_dir="./output"
)
```

**Returns**:
| Key | Type | Description |
|-----|------|-------------|
| `summary` | str | Full human-readable summary |
| `vh_mutations` | list | `[{position, from, to}, ...]` for VH |
| `vl_mutations` | list | `[{position, from, to}, ...]` for VL |
| `before` | dict | OASis identity/percentile/germline content (pre-humanization) |
| `after` | dict | OASis identity/percentile/germline content (post-humanization) |
| `germlines` | dict | VH/VL germline gene names before and after |
| `plot_image` | str | Path to saved `humanness_plot.png` |
| `excel_report` | str | Path to saved `humanization_report.xlsx` |

**Example Output**:
```
[Humanizing Mutations]
  VH: 14 mutations
  VH changes: EH1Q, QH5V, LH12V, VH13K, LH18S…

[OASis Identity (threshold=10%)]
  Combined Before: 37.14%  →  After: 71.43%

[OASis Percentile]
  VH Before: 0.02  →  After: 0.34

[Germline Content]
  VH Before: 67.26%  →  After: 77.88%

[Germlines]
  VH Before: IGHV1-69-2*01 / IGHJ4*01
  VH After : IGHV1-2*02 / IGHJ4*01
```

---

### 2. `evaluate_humanness` — OASis-only Evaluation (no humanization)

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

## OASis API

All humanness evaluations call the Azure REST API:

- **Endpoint**: `https://biophioasisapi.azurewebsites.net/api/peptides/`
- **Method**: POST
- **Payload**: `{"peptides": ["EVQLVESGG", ...], "chain_type": "Heavy"}`
- **Response**: `{"num_total_oas_subjects": N, "hits": [{peptide, num_oas_subjects, num_oas_occurrences}, ...]}`

## Output Files

| File | Description |
|------|-------------|
| `humanness_plot.png` | Bar chart of per-peptide OASis % before and after humanization (red = non-human, green = human) |
| `humanization_report.xlsx` | Sheets: Summary \| Mutations \| VH Before \| VH After \| VL Before \| VL After |
