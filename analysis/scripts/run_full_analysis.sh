#!/bin/bash
#
# Master Analysis Script for BiOx+2 Production Trajectories
# Run after production completes to execute all analyses
#
# Usage: ./run_full_analysis.sh [--dry-run] [--segment N]
#
# Created: January 2026
# For: OxDC MD Simulation Project

set -e  # Exit on error

# ============================================================
# Configuration
# ============================================================

SYSTEM="BiOx+2"
BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SYSDIR="${BASEDIR}/systems/${SYSTEM}"
ANALYSIS_DIR="${BASEDIR}/analysis"
CPPTRAJ_DIR="${ANALYSIS_DIR}/cpptraj"
RESULTS_DIR="${ANALYSIS_DIR}/results/${SYSTEM}"

PRMTOP="${SYSDIR}/5vg3.prmtop"
REFERENCE="${SYSDIR}/5vg3.inpcrd"

# Parse arguments
DRY_RUN=false
SEGMENT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --segment) SEGMENT=$2; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ============================================================
# Helper Functions
# ============================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

run_cpptraj() {
    local input=$1
    local description=$2
    log "Running: $description"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  [DRY RUN] cpptraj -p $PRMTOP -i $input"
    else
        cpptraj -p "$PRMTOP" -i "$input" 2>&1 | tee -a "${RESULTS_DIR}/cpptraj.log"
    fi
}

# ============================================================
# Setup
# ============================================================

log "=== BiOx+2 Production Analysis Pipeline ==="
log "System directory: ${SYSDIR}"
log "Results directory: ${RESULTS_DIR}"

# Create results directory
mkdir -p "${RESULTS_DIR}"
mkdir -p "${RESULTS_DIR}/rmsd"
mkdir -p "${RESULTS_DIR}/rmsf"
mkdir -p "${RESULTS_DIR}/mn_coordination"
mkdir -p "${RESULTS_DIR}/lid_dynamics"
mkdir -p "${RESULTS_DIR}/trp_pair"
mkdir -p "${RESULTS_DIR}/pca"
mkdir -p "${RESULTS_DIR}/figures"

# ============================================================
# Find Production Trajectories
# ============================================================

log "Searching for production trajectories..."
TRAJS=()
if [[ -n "$SEGMENT" ]]; then
    # Specific segment requested
    TRAJS=("${SYSDIR}/prod_seg${SEGMENT}.nc")
else
    # Find all production segments
    for f in "${SYSDIR}"/prod_seg*.nc "${SYSDIR}"/prod*.nc; do
        [[ -f "$f" ]] && TRAJS+=("$f")
    done
fi

if [[ ${#TRAJS[@]} -eq 0 ]]; then
    log "WARNING: No production trajectories found!"
    log "Looking for equilibration trajectories instead..."
    for f in "${SYSDIR}"/eq*.nc; do
        [[ -f "$f" ]] && TRAJS+=("$f")
    done
fi

log "Found ${#TRAJS[@]} trajectory files:"
for t in "${TRAJS[@]}"; do
    log "  - $(basename "$t")"
done

# ============================================================
# Create Temporary cpptraj Inputs with Correct Paths
# ============================================================

log "Creating analysis input files..."

# RMSD/RMSF Analysis
cat > "${RESULTS_DIR}/rmsd_rmsf.in" << EOF
# RMSD and RMSF Analysis for BiOx+2
parm ${PRMTOP}
reference ${REFERENCE} [ref]
EOF
for t in "${TRAJS[@]}"; do
    echo "trajin $t" >> "${RESULTS_DIR}/rmsd_rmsf.in"
done
cat >> "${RESULTS_DIR}/rmsd_rmsf.in" << 'EOF'
autoimage
center :1-382 mass origin

# RMSD calculations
rms RMSD_bb @CA,C,N reference out rmsd/rmsd_backbone.dat
rms RMSD_ca @CA reference out rmsd/rmsd_ca.dat

# RMSF calculations
rmsf RMSF_ca @CA out rmsf/rmsf_ca.dat byres
atomicfluct BFACTORS @CA out rmsf/bfactors.dat byres bfactor

run
EOF

# Mn Coordination Analysis
cat > "${RESULTS_DIR}/mn_coordination.in" << EOF
# Mn Coordination Geometry Analysis for BiOx+2
parm ${PRMTOP}
EOF
for t in "${TRAJS[@]}"; do
    echo "trajin $t" >> "${RESULTS_DIR}/mn_coordination.in"
done
cat >> "${RESULTS_DIR}/mn_coordination.in" << 'EOF'
autoimage

# Site 1 (N-terminal, catalytic) - Mn atom 6032
# Mn-His distances
distance Mn1_His95 @6032 @1519 out mn_coordination/mn1_his.dat
distance Mn1_His97 @6032 @1560 out mn_coordination/mn1_his.dat
distance Mn1_His140 @6032 @2230 out mn_coordination/mn1_his.dat

# Mn-Glu distance
distance Mn1_Glu101 @6032 @1623 out mn_coordination/mn1_glu.dat

# Mn-Oxalate distances (bidentate binding)
distance Mn1_Ox_O1 @6032 @6036 out mn_coordination/mn1_oxalate.dat
distance Mn1_Ox_O2 @6032 @6038 out mn_coordination/mn1_oxalate.dat

# Site 2 (C-terminal) - Check if ionic or bonded
# These may need adjustment based on actual topology

# Mn-Mn distance (intra-subunit)
distance Mn_Mn @6032 @6033 out mn_coordination/mn_mn.dat

run
EOF

# Lid Dynamics Analysis (residues 160-166 in PDB numbering)
cat > "${RESULTS_DIR}/lid_dynamics.in" << EOF
# Lid Dynamics Analysis for BiOx+2
parm ${PRMTOP}
reference ${REFERENCE} [ref]
EOF
for t in "${TRAJS[@]}"; do
    echo "trajin $t" >> "${RESULTS_DIR}/lid_dynamics.in"
done
cat >> "${RESULTS_DIR}/lid_dynamics.in" << 'EOF'
autoimage

# Lid RMSD (residues 160-166 - adjust to topology numbering)
# Note: May need to verify residue numbers match topology
rms LidRMSD :160-166@CA reference out lid_dynamics/lid_rmsd.dat

# Lid RMSF
rmsf LidRMSF :160-166@CA out lid_dynamics/lid_rmsf.dat byres

# Glu162-Mn distance (key interaction)
# Adjust atom indices as needed
distance Glu162_Mn :162@OE1 @6032 out lid_dynamics/glu162_mn.dat

# Lid solvent accessible surface area
surf LidSASA :160-166 out lid_dynamics/lid_sasa.dat

# H-bonds involving lid residues
hbond LidHB :160-166 out lid_dynamics/lid_hbonds.dat avgout lid_dynamics/lid_hbonds_avg.dat

run
EOF

# W96/W274 Analysis
cat > "${RESULTS_DIR}/trp_pair.in" << EOF
# Tryptophan Pair Analysis (W96/W274 electron transfer pathway)
parm ${PRMTOP}
EOF
for t in "${TRAJS[@]}"; do
    echo "trajin $t" >> "${RESULTS_DIR}/trp_pair.in"
done
cat >> "${RESULTS_DIR}/trp_pair.in" << 'EOF'
autoimage

# W96-W274 ring center distance
# Note: Adjust residue numbers to match topology
distance W_W_dist :96@CG,CD1,CD2,NE1,CE2,CE3,CZ2,CZ3,CH2 :274@CG,CD1,CD2,NE1,CE2,CE3,CZ2,CZ3,CH2 out trp_pair/trp_distance.dat

# Individual Trp-Mn distances
distance W96_Mn @6032 :96@CG out trp_pair/w96_mn.dat
distance W274_Mn @6033 :274@CG out trp_pair/w274_mn.dat

run
EOF

# ============================================================
# Run Analyses
# ============================================================

log "=== Running Analyses ==="
cd "${RESULTS_DIR}"

run_cpptraj "rmsd_rmsf.in" "RMSD/RMSF Analysis"
run_cpptraj "mn_coordination.in" "Mn Coordination Analysis"
run_cpptraj "lid_dynamics.in" "Lid Dynamics Analysis"
run_cpptraj "trp_pair.in" "Tryptophan Pair Analysis"

# ============================================================
# Summary
# ============================================================

log "=== Analysis Complete ==="
log "Results saved to: ${RESULTS_DIR}"
log ""
log "Output files:"
find "${RESULTS_DIR}" -name "*.dat" -type f | head -20

log ""
log "Next steps:"
log "1. Run visualization: python3 ${ANALYSIS_DIR}/scripts/plot_production_analysis.py"
log "2. Check convergence: compare first half vs second half of trajectory"
log "3. Generate figures for thesis"
