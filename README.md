# BioPhiSkill

<p align="center">
  <strong>Antibody Humanization & Humanness Evaluation — Agent Skill</strong><br>
  Powered by <a href="https://github.com/Merck/Sapiens">Sapiens</a> deep learning and the <a href="https://github.com/Merck/BioPhi">OASis</a> dataset via Azure REST API
</p>

> **BioPhiSkill** is a lightweight, agent-friendly fork of [BioPhi](https://github.com/Merck/BioPhi) (Merck). Web server, Redis, and Celery dependencies have been removed. The 22 GB local OASis database is replaced by a hosted Azure API.

---

## Installation

```bash
# 1. Clone
git clone https://github.com/Shaperon-AIDEN/BioPhiSkill.git
cd BioPhiSkill

# 2. Install (creates conda env 'biophi' with all dependencies)
bash install.sh

# 3. Activate
conda activate biophi
```

### Requirements
- [Conda](https://docs.conda.io/en/latest/miniconda.html) (Miniconda recommended)
- Internet access (Sapiens model downloaded from HuggingFace on first run; OASis API calls)

---

## Quick Start

```python
from agent_api import humanize_antibody_sequence

vh = "EVQLQQSGAELVRPGALVKLSCKASGFNIKDYYMHWVKQRPEQGLEWIGWIDPENGDTEYAPKFQGKATMTADTSSNTAYLQLSSLTSEDTAVYYCNADDHYWGQGTTLTVSS"

result = humanize_antibody_sequence(
    vh_seq=vh,
    vl_seq=None,         # optional light chain
    output_dir="./output"
)
print(result["summary"])
```

---

## API Reference

### `humanize_antibody_sequence(...)` — Full Pipeline

Runs **Sapiens humanization** then evaluates humanness **before and after** via OASis.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `vh_seq` | required | Heavy chain amino acid sequence |
| `vl_seq` | `None` | Light chain amino acid sequence (optional) |
| `scheme` | `"imgt"` | Numbering scheme: `imgt` / `kabat` / `chothia` |
| `cdr_definition` | `"imgt"` | CDR definition: `imgt` / `kabat` / `chothia` |
| `sapiens_iterations` | `1` | Sapiens model iteration count |
| `humanize_cdrs` | `False` | If `True`, CDR regions are also humanized |
| `min_fraction_subjects` | `0.1` | OASis threshold — peptides found in ≥10% of human subjects are "human" |
| `output_dir` | `"output"` | Directory for output files |

**Returns** `dict`:

| Key | Type | Description |
|-----|------|-------------|
| `summary` | `str` | Human-readable text summary (print-ready) |
| `vh_mutations` | `list` | `[{"position": "H1", "from": "E", "to": "Q"}, ...]` |
| `vl_mutations` | `list` | Same for light chain |
| `before` | `dict` | Metrics before humanization (see below) |
| `after` | `dict` | Metrics after humanization |
| `germlines` | `dict` | `{vh_before, vh_after, vl_before, vl_after}` germline gene names |
| `plot_image` | `str` | Absolute path to `humanness_plot.png` |
| `excel_report` | `str` | Absolute path to `humanization_report.xlsx` |

**`before` / `after` dict keys**:

| Key | Description |
|-----|-------------|
| `oasis_identity` | Combined VH+VL OASis identity (%) |
| `oasis_identity_vh` | VH-only OASis identity (%) |
| `oasis_identity_vl` | VL-only OASis identity (%) |
| `oasis_percentile` | VH percentile rank vs human antibody database (%) |
| `germline_content` | % of residues matching closest human germline (VH) |

---

### `evaluate_humanness(...)` — Evaluation Only

Evaluate humanness **without** running Sapiens (e.g. for a sequence already engineered).

```python
from agent_api import evaluate_humanness

result = evaluate_humanness(
    vh_seq="EVQLVESGGGLVQPGR...",
    output_dir="./output"
)
print(result["summary"])
```

Returns the same metrics keys as `before`/`after` above, plus `plot_image`, `excel_report`, `summary`.

---

## Understanding the Results

### OASis Identity
The **fraction of 9-mer peptides** in the antibody V-region that appear in ≥10% of human subjects in the OAS database.

- **< 30%** — Highly non-human (typical murine antibody)
- **30–60%** — Partially human
- **> 80%** — Highly human (clinical candidates typical range)

### OASis Percentile
Rank of the antibody's OASis identity compared to a reference set of clinical-stage human antibodies, reported in **percent**. A value of **50** means the antibody is more human than 50% of clinical antibodies.

### Germline Content
Percentage of residues in the V-region that match the closest human germline gene. After Sapiens humanization this typically increases.

### Humanizing Mutations
Positions where Sapiens changed an amino acid to increase humanness. Format: `{from}{IMGT_position}{to}` (e.g. `EH1Q` = position H1, E→Q).

---

## Output Files

### `humanness_plot.png`
Bar chart of per-peptide OASis subject frequency across the V-region:
- **Green bars** — peptide found in ≥10% of human subjects (human)
- **Red bars** — peptide found in <10% of human subjects (non-human)
- **Orange dashed line** — threshold (default 10%)

Two column view: left = before humanization, right = after.

### `humanization_report.xlsx`
| Sheet | Contents |
|-------|----------|
| **Summary** | OASis identity, percentile, germline content, germline genes (before & after) |
| **Mutations** | All position-level mutations introduced by Sapiens |
| **VH Before / VH After** | Per-peptide humanness detail for heavy chain |
| **VL Before / VL After** | Per-peptide humanness detail for light chain |

---

## Architecture

```
BioPhiSkill/
├── SKILL.md              ← Skill descriptor for Claude Code / OpenCode
├── install.sh            ← One-shot installer
├── agent_api.py          ← Main API (humanize_antibody_sequence, evaluate_humanness)
├── patches/
│   └── anarci_compat.py  ← Auto-applied ANARCI compatibility patch (Python 3.12+)
└── biophi/               ← Core library (Sapiens + OASis logic)
    └── humanization/
        └── methods/
            ├── humanization.py  ← Sapiens & CDR grafting
            └── humanness.py     ← OASis (Azure REST API)
```

---

## Citation

If you use BioPhiSkill, please cite the original BioPhi paper:

> Prihoda et al. (2022) **BioPhi: A platform for antibody design, humanization, and humanness evaluation based on natural antibody repertoires and deep learning**, *mAbs*, 14:1. https://doi.org/10.1080/19420862.2021.2020203
