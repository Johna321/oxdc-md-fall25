#!/bin/bash
#SBATCH --job-name=oxdc_prod
#SBATCH --output=prod_%j.out
#SBATCH --error=prod_%j.err
#SBATCH --partition=hpg-turin
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-gpu=2
#SBATCH --mem=8gb
#SBATCH --time=12:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu

###############################################################################
# OxDC Production MD Script
#
# Usage:
#   sbatch run_prod.sbatch <system_dir> <segment_num>
#
# Example:
#   sbatch run_prod.sbatch BiOx+2 1
#
# This script runs a 10 ns production segment and supports continuation.
###############################################################################

set -euo pipefail

# Parse arguments
SYSTEM_DIR="${1:-BiOx+2}"
SEGMENT="${2:-1}"

cd "/home/user/oxdc-md-fall25/systems/${SYSTEM_DIR}"
echo "Working directory: $(pwd)"
echo "Segment: ${SEGMENT}"

# Module setup
module purge
module load cuda/12.8.1
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

export CUDA_VISIBLE_DEVICES=0

# File paths
PRMTOP="5vg3_solv.prmtop"
MDIN="../claude-notes/production/prod_template.in"

# Determine input coordinates
if [[ "${SEGMENT}" -eq 1 ]]; then
    # First segment: use equilibration output
    if [[ -f "eq3.cpu.rst7" ]]; then
        INPCRD="eq3.cpu.rst7"
    elif [[ -f "eq2.cpu.rst7" ]]; then
        echo "WARNING: Using eq2.rst7 (eq3 not found)"
        INPCRD="eq2.cpu.rst7"
    else
        echo "ERROR: No suitable restart file found"
        exit 1
    fi
else
    # Continuation: use previous segment's restart
    PREV_SEGMENT=$((SEGMENT - 1))
    INPCRD="prod_seg$(printf '%03d' ${PREV_SEGMENT}).rst7"
    if [[ ! -f "${INPCRD}" ]]; then
        echo "ERROR: Previous segment restart not found: ${INPCRD}"
        exit 1
    fi
fi

# Output file naming
PREFIX="prod_seg$(printf '%03d' ${SEGMENT})"

# Verify inputs
[[ -f "${PRMTOP}" ]] || { echo "ERROR: Topology not found: ${PRMTOP}"; exit 1; }
[[ -f "${INPCRD}" ]] || { echo "ERROR: Coordinates not found: ${INPCRD}"; exit 1; }
[[ -f "${MDIN}" ]] || { echo "ERROR: Input file not found: ${MDIN}"; exit 1; }

echo "========================================="
echo "Topology:    ${PRMTOP}"
echo "Coordinates: ${INPCRD}"
echo "Input:       ${MDIN}"
echo "Output:      ${PREFIX}.*"
echo "========================================="

# Run production
pmemd.cuda -O \
    -i "${MDIN}" \
    -p "${PRMTOP}" \
    -c "${INPCRD}" \
    -o "${PREFIX}.out" \
    -r "${PREFIX}.rst7" \
    -x "${PREFIX}.nc" \
    -inf "${PREFIX}.mdinfo"

# Verify output
if [[ -f "${PREFIX}.rst7" ]]; then
    echo "Segment ${SEGMENT} completed successfully"
    echo "Output files:"
    ls -lh ${PREFIX}.*

    # Quick density check
    echo ""
    echo "Final density values:"
    tail -100 "${PREFIX}.out" | grep "Density" | tail -3
else
    echo "ERROR: Production failed - no restart file generated"
    exit 1
fi

# Auto-submit next segment (optional - uncomment to enable)
# NEXT_SEGMENT=$((SEGMENT + 1))
# if [[ ${NEXT_SEGMENT} -le 10 ]]; then
#     echo "Submitting segment ${NEXT_SEGMENT}..."
#     sbatch run_prod.sbatch "${SYSTEM_DIR}" ${NEXT_SEGMENT}
# fi

echo "Done."
