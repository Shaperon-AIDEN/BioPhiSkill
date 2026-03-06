#!/usr/bin/env bash
# =============================================================================
# BioPhiSkill Installer
# 
# Usage:
#   git clone https://github.com/Shaperon-AIDEN/BioPhiSkill.git
#   cd BioPhiSkill
#   bash install.sh
# =============================================================================
set -e

PYTHON_VERSION="3.9"
ENV_NAME="biophi"

echo "================================================"
echo "  BioPhiSkill Installer"
echo "================================================"

# 1. Check conda
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Please install Miniconda or Anaconda first."
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# 2. Check HMMER (required by abnumber/anarci)
if ! command -v hmmscan &> /dev/null; then
    echo "[INFO] hmmer not found in PATH — will install via conda"
    INSTALL_HMMER="yes"
else
    echo "[INFO] hmmer already available: $(hmmscan -h 2>&1 | head -1)"
    INSTALL_HMMER="no"
fi

# 3. Create / reuse conda environment
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "[INFO] Conda environment '${ENV_NAME}' already exists. Skipping creation."
else
    echo "[INFO] Creating conda environment '${ENV_NAME}' (Python ${PYTHON_VERSION})..."
    conda create -y -n "${ENV_NAME}" python="${PYTHON_VERSION}"
fi

# 4. Install HMMER via conda if needed (must be on same env)
if [ "$INSTALL_HMMER" = "yes" ]; then
    echo "[INFO] Installing hmmer and abnumber via conda..."
    conda install -y -n "${ENV_NAME}" -c bioconda -c conda-forge abnumber hmmer
else
    echo "[INFO] Installing abnumber via conda..."
    conda install -y -n "${ENV_NAME}" -c bioconda -c conda-forge abnumber
fi

# 5. Install Python package and all pip dependencies
echo "[INFO] Installing BioPhiSkill package..."
conda run -n "${ENV_NAME}" pip install -e ".[viz]" --quiet

echo ""
echo "================================================"
echo "  Installation complete!"
echo ""
echo "  Activate with:"
echo "    conda activate ${ENV_NAME}"
echo ""
echo "  Quick test:"
echo "    python -c \"from agent_api import humanize_antibody_sequence; print('OK')\""
echo "================================================"
