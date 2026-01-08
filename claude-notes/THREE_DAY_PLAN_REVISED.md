# Revised 3-Day Implementation Plan (January 2026)

## Critical Update: Root Cause Correction

**Previous hypothesis (REJECTED):** Restraint mask errors cause instabilities
**Corrected hypothesis (SUPPORTED):** Force field parameters (force constants, bond lengths) determine stability

### Key Findings Summary
| System | Avg k | Status | Recommendation |
|--------|-------|--------|----------------|
| BiOx+2 | 29.3 | STABLE | **Production ready** |
| 1Wat+2 | 40.2 | UNSTABLE | Monitor, may need softer k |
| 1Wat+3 | 97.3 | UNSTABLE | Mn(III) issue - needs QM/MM or re-param |
| empty+2 | 44.0 | CRASHED | Needs investigation |

---

## Day 1: BiOx+2 Production Setup + Analysis Validation

### Block 1.1: Environment Setup (15 min)

```bash
# SSH to HPC
ssh john.aitken@hpg.rc.ufl.edu

# Navigate to project
cd /blue/ax/john.aitken/oxdc-md-fall25

# Load modules (UFHPC specific)
module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

# Verify AMBER loaded
which pmemd.cuda
```

### Block 1.2: Check BiOx+2 Current State (15 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

# List all restart files
ls -lh *.rst7 2>/dev/null
ls -lh *.cpu.rst7 2>/dev/null

# Check most recent equilibration output
LATEST_OUT=$(ls -t *.out 2>/dev/null | head -1)
echo "Most recent output: $LATEST_OUT"

# Check density (should be ~1.01 g/cc)
tail -100 $LATEST_OUT | grep -E "Density" | tail -5

# Check for vlimit warnings (should be 0)
echo "vlimit count: $(grep -c 'vlimit' $LATEST_OUT 2>/dev/null || echo '0')"

# Check for SHAKE failures (should be 0)
echo "SHAKE failures: $(grep -c 'SHAKE' $LATEST_OUT 2>/dev/null || echo '0')"
```

**Expected output:**
- Density: 1.00-1.02 g/cc
- vlimit: 0
- SHAKE: 0

### Block 1.3: Create Production mdin File (10 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

# Create mdin_templates directory if it doesn't exist
mkdir -p mdin_templates

# Create production input (10 ns segment, 2 fs timestep)
cat > mdin_templates/prod_10ns.in << 'EOF'
Production NPT (2 fs) - 10 ns segment
 &cntrl
  imin=0, ntx=5, irest=1,
  ntb=2, ntp=1, barostat=2, pres0=1.0, taup=2.0,
  ntt=3, gamma_ln=1.0, temp0=300.0,
  ntc=2, ntf=2, dt=0.002,
  nstlim=5000000,
  cut=10.0, iwrap=1,
  ntpr=5000, ntwx=5000, ntwr=50000,
  ntxo=2, ioutfm=1,
  ntr=0
 /
EOF

echo "Created prod_10ns.in"
cat mdin_templates/prod_10ns.in
```

### Block 1.4: Identify Correct Input Files (10 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

# Find prmtop
PRMTOP=$(ls -1 *.prmtop 2>/dev/null | head -1)
echo "PRMTOP: $PRMTOP"

# Find most recent restart file
RESTART=$(ls -t *.rst7 2>/dev/null | head -1)
echo "RESTART: $RESTART"

# Verify both exist
if [[ -f "$PRMTOP" && -f "$RESTART" ]]; then
    echo "Files verified - ready for production"
else
    echo "ERROR: Missing files"
    ls -la
fi
```

### Block 1.5: Create Production SLURM Script (10 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

# Get filenames from previous step
PRMTOP=$(ls -1 *.prmtop 2>/dev/null | head -1)
RESTART=$(ls -t *.rst7 2>/dev/null | head -1)

cat > run_prod_seg001.sbatch << EOF
#!/bin/bash
#SBATCH --job-name=biox2_p001
#SBATCH --output=prod_seg001.%j.out
#SBATCH --error=prod_seg001.%j.err
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

module purge
module load cuda/12.8.1
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

pmemd.cuda -O \\
    -i mdin_templates/prod_10ns.in \\
    -p $PRMTOP \\
    -c $RESTART \\
    -o prod_seg001.out \\
    -r prod_seg001.rst7 \\
    -x prod_seg001.nc \\
    -inf prod_seg001.mdinfo

echo "Segment 001 complete"
EOF

echo "Created run_prod_seg001.sbatch"
```

### Block 1.6: Submit Production Job (5 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

# Submit
sbatch run_prod_seg001.sbatch

# Note the job ID
JOBID=$(squeue -u $USER --format="%i %j" | grep biox2_p001 | awk '{print $1}')
echo "Submitted job: $JOBID"

# Save job ID for tracking
echo "$JOBID prod_seg001 $(date)" >> production_log.txt
```

### Block 1.7: Create Continuation Script (15 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

PRMTOP=$(ls -1 *.prmtop 2>/dev/null | head -1)

cat > continue_production.sh << 'SCRIPT'
#!/bin/bash
# Usage: ./continue_production.sh <segment_number>
# Example: ./continue_production.sh 2

SEG=$1
PREV=$((SEG - 1))
SEG_FMT=$(printf '%03d' $SEG)
PREV_FMT=$(printf '%03d' $PREV)

if [[ ! -f "prod_seg${PREV_FMT}.rst7" ]]; then
    echo "ERROR: Previous segment restart not found: prod_seg${PREV_FMT}.rst7"
    exit 1
fi

PRMTOP=$(ls -1 *.prmtop 2>/dev/null | head -1)

cat > run_prod_seg${SEG_FMT}.sbatch << EOF
#!/bin/bash
#SBATCH --job-name=biox2_p${SEG_FMT}
#SBATCH --output=prod_seg${SEG_FMT}.%j.out
#SBATCH --error=prod_seg${SEG_FMT}.%j.err
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

module purge
module load cuda/12.8.1
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

pmemd.cuda -O \\
    -i mdin_templates/prod_10ns.in \\
    -p $PRMTOP \\
    -c prod_seg${PREV_FMT}.rst7 \\
    -o prod_seg${SEG_FMT}.out \\
    -r prod_seg${SEG_FMT}.rst7 \\
    -x prod_seg${SEG_FMT}.nc \\
    -inf prod_seg${SEG_FMT}.mdinfo
EOF

sbatch run_prod_seg${SEG_FMT}.sbatch
echo "Submitted segment $SEG"
echo "$(date) prod_seg${SEG_FMT}" >> production_log.txt
SCRIPT

chmod +x continue_production.sh
echo "Created continue_production.sh"
```

### Block 1.8: Validate Analysis Scripts (30 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/analysis/scripts

# Test energy_analysis.py (requires simulation output)
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
# Quick syntax check
exec(open('energy_analysis.py').read().split('# Main execution')[0])
print("energy_analysis.py: syntax OK")
PYEOF

# Test force_constant_analysis.py
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
exec(open('force_constant_analysis.py').read().split('# Main execution')[0])
print("force_constant_analysis.py: syntax OK")
PYEOF

# Run force constant analysis (doesn't need trajectories)
python3 force_constant_analysis.py
echo "Force constant analysis complete - check ../results/"
```

### Block 1.9: Create cpptraj Analysis Inputs (20 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/analysis

mkdir -p cpptraj

# RMSD/RMSF analysis
cat > cpptraj/rmsd_rmsf.in << 'EOF'
# Load topology (update path as needed)
parm ../systems/BiOx+2/*.prmtop

# Load trajectories (update for production)
trajin ../systems/BiOx+2/prod_seg*.nc

# Set reference
reference ../systems/BiOx+2/*.inpcrd [ref]

# Calculate RMSD
rms RMSD_CA @CA reference out results/rmsd_ca.dat
rms RMSD_BB @C,CA,N reference out results/rmsd_bb.dat

# Calculate RMSF
rmsf RMSF_CA @CA out results/rmsf_ca.dat byres

# Run
run
EOF

# Mn coordination analysis
cat > cpptraj/mn_coordination.in << 'EOF'
parm ../systems/BiOx+2/*.prmtop
trajin ../systems/BiOx+2/prod_seg*.nc

# Mn-ligand distances (update atom numbers from mn_bonds.csv)
# BiOx+2 Site 1: Mn @6032
distance Mn_His95  @6032 @1519 out results/mn_his95.dat
distance Mn_His97  @6032 @1560 out results/mn_his97.dat
distance Mn_Glu101 @6032 @1623 out results/mn_glu101.dat
distance Mn_His140 @6032 @2230 out results/mn_his140.dat
distance Mn_OxO1   @6032 @6036 out results/mn_ox_o1.dat
distance Mn_OxO2   @6032 @6038 out results/mn_ox_o2.dat

run
EOF

# Lid dynamics (residues 160-166)
cat > cpptraj/lid_dynamics.in << 'EOF'
parm ../systems/BiOx+2/*.prmtop
trajin ../systems/BiOx+2/prod_seg*.nc

reference ../systems/BiOx+2/*.inpcrd [ref]

# Lid RMSD (adjust residue numbers after checking)
rms Lid_RMSD :160-166@CA reference out results/lid_rmsd.dat

# Lid-substrate distance
distance Lid_Ox :162@CA :OX@OX out results/lid_oxalate_dist.dat

run
EOF

echo "Created cpptraj input files in cpptraj/"
ls -la cpptraj/
```

### Block 1.10: End of Day 1 Status Check (10 min)

```bash
# Check job status
squeue -u $USER

# Check if production has started
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2
if [[ -f prod_seg001.mdinfo ]]; then
    echo "=== Production Status ==="
    cat prod_seg001.mdinfo
else
    echo "Production starting..."
fi

# Commit progress
cd /blue/ax/john.aitken/oxdc-md-fall25
git add -A
git status
```

---

## Day 2: Monitor Production + System Evaluation

### Block 2.1: Morning Check (15 min)

```bash
ssh john.aitken@hpg.rc.ufl.edu
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

# Check job status
squeue -u $USER

# Check production progress
if [[ -f prod_seg001.mdinfo ]]; then
    cat prod_seg001.mdinfo
    echo ""
    echo "=== Energy Summary (last 20 steps) ==="
    tail -40 prod_seg001.out | grep -E "NSTEP|Etot|Density"
fi
```

### Block 2.2: If Segment 1 Complete - Quality Check (30 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

if [[ -f prod_seg001.rst7 ]]; then
    echo "Segment 1 complete - running QC checks"

    module load amber/25

    # Check final density
    tail -50 prod_seg001.out | grep Density | tail -3

    # Check energy stability (no huge spikes)
    grep "Etot" prod_seg001.out | awk '{print $3}' | tail -100 > /tmp/etot.dat
    echo "Energy stats (last 100 steps):"
    awk 'BEGIN{min=1e10;max=-1e10;sum=0;n=0}
         {if($1<min)min=$1; if($1>max)max=$1; sum+=$1; n++}
         END{print "Min:",min,"Max:",max,"Mean:",sum/n,"Range:",max-min}' /tmp/etot.dat

    # Check for warnings
    echo "Warning counts:"
    echo "  vlimit: $(grep -c 'vlimit' prod_seg001.out 2>/dev/null || echo 0)"
    echo "  SHAKE:  $(grep -c 'SHAKE' prod_seg001.out 2>/dev/null || echo 0)"

    # Submit segment 2 if QC passes
    echo ""
    echo "Ready to continue? Run: ./continue_production.sh 2"
else
    echo "Segment 1 still running - check again later"
    squeue -u $USER
fi
```

### Block 2.3: Submit Segment 2 (if QC passed) (5 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

# Verify restart exists
if [[ -f prod_seg001.rst7 ]]; then
    ./continue_production.sh 2
else
    echo "ERROR: prod_seg001.rst7 not found"
fi
```

### Block 2.4: Evaluate Other Systems - 1Wat+2 (30 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/1Wat+2

echo "=== 1Wat+2 Evaluation ==="

# Check existing equilibration
LATEST_OUT=$(ls -t *.out 2>/dev/null | head -1)
if [[ -n "$LATEST_OUT" ]]; then
    echo "Latest output: $LATEST_OUT"
    echo "vlimit count: $(grep -c 'vlimit' $LATEST_OUT 2>/dev/null || echo 0)"
    echo "SHAKE count: $(grep -c 'SHAKE' $LATEST_OUT 2>/dev/null || echo 0)"

    echo ""
    echo "Last 10 energy outputs:"
    tail -100 $LATEST_OUT | grep "NSTEP" | tail -10
fi

# Check force constants from mn_bonds.csv
if [[ -f analysis/mn_bonds.csv ]]; then
    echo ""
    echo "Force constants (should avg <40 for stability):"
    cat analysis/mn_bonds.csv
fi

# Decision tree
echo ""
echo "RECOMMENDATION:"
VLIMIT=$(grep -c 'vlimit' $LATEST_OUT 2>/dev/null || echo 0)
if [[ $VLIMIT -gt 10 ]]; then
    echo "  -> Too many vlimit warnings ($VLIMIT)"
    echo "  -> Consider re-parameterization with softer force constants"
    echo "  -> Or try extended heating with smaller timestep"
else
    echo "  -> May be salvageable with careful equilibration"
    echo "  -> Create extended eq1 with 1 fs timestep"
fi
```

### Block 2.5: Evaluate 1Wat+3 (Mn(III) System) (30 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/1Wat+3

echo "=== 1Wat+3 Evaluation (Mn(III) System) ==="

# This system has fundamentally different parameters (Jahn-Teller)
if [[ -f analysis/mn_bonds.csv ]]; then
    echo "Force constants (Mn(III) - expect high values):"
    cat analysis/mn_bonds.csv
    echo ""
    echo "NOTE: Force constants >80 are typical for Mn(III)"
    echo "      This is NOT a bug - it's the correct parameterization"
    echo "      BUT it makes classical MD challenging"
fi

LATEST_OUT=$(ls -t *.out 2>/dev/null | head -1)
if [[ -n "$LATEST_OUT" ]]; then
    echo ""
    echo "vlimit count: $(grep -c 'vlimit' $LATEST_OUT 2>/dev/null || echo 0)"
fi

echo ""
echo "RECOMMENDATION for 1Wat+3:"
echo "  1. This system models Mn(III) - high k is expected"
echo "  2. Options:"
echo "     a) Accept limited equilibration, use for short runs"
echo "     b) Re-parameterize with artificially softened k (loses accuracy)"
echo "     c) Switch to QM/MM for production (most rigorous)"
echo "  3. Prioritize BiOx+2 production first"
```

### Block 2.6: Evaluate empty+2 (30 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/empty+2

echo "=== empty+2 Evaluation ==="

LATEST_OUT=$(ls -t *.out 2>/dev/null | head -1)
if [[ -n "$LATEST_OUT" ]]; then
    echo "Latest output: $LATEST_OUT"
    echo "vlimit count: $(grep -c 'vlimit' $LATEST_OUT 2>/dev/null || echo 0)"
    echo "SHAKE count: $(grep -c 'SHAKE' $LATEST_OUT 2>/dev/null || echo 0)"

    # Check if simulation crashed
    if grep -q "error\|Error\|ERROR\|Abort" $LATEST_OUT; then
        echo ""
        echo "*** CRASH DETECTED ***"
        grep -i "error\|abort" $LATEST_OUT | tail -5
    fi
fi

if [[ -f analysis/mn_bonds.csv ]]; then
    echo ""
    echo "Force constants:"
    cat analysis/mn_bonds.csv
fi

echo ""
echo "RECOMMENDATION for empty+2:"
echo "  This system crashed - root cause analysis needed"
echo "  1. Check which Mn site has problematic parameters"
echo "  2. Consider running only Site 2 (structural site)"
echo "  3. Lower priority until BiOx+2 production complete"
```

### Block 2.7: Create System Status Summary (20 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25

cat > SYSTEM_STATUS.md << 'EOF'
# OxDC System Status Summary

| System | Avg k | Status | Production Ready | Notes |
|--------|-------|--------|------------------|-------|
| BiOx+2 | 29.3 | STABLE | YES | Currently in production |
| 1Wat+2 | 40.2 | UNSTABLE | NO | vlimit warnings |
| 1Wat+3 | 97.3 | UNSTABLE | NO | Mn(III) high k expected |
| empty+2 | 44.0 | CRASHED | NO | Needs investigation |

## Immediate Priorities

1. **BiOx+2**: Continue production (target 100 ns)
2. **1Wat+2**: Attempt softer equilibration protocol
3. **1Wat+3**: Document as Mn(III) reference; consider QM/MM
4. **empty+2**: Analyze crash; lowest priority

## Updated Strategy

Given that force field parameters (not restraint masks) determine stability,
the path forward for non-BiOx+2 systems requires either:

1. Re-parameterization with softer force constants
2. QM/MM production runs
3. Enhanced equilibration protocols with smaller timesteps

BiOx+2 should be prioritized for thesis-critical production data.
EOF

cat SYSTEM_STATUS.md
```

### Block 2.8: End of Day 2 Check (10 min)

```bash
# Check all job status
squeue -u $USER

# Production progress
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2
echo "=== BiOx+2 Production Progress ==="
ls -lh prod_seg*.nc 2>/dev/null
cat production_log.txt 2>/dev/null

# Commit status update
cd /blue/ax/john.aitken/oxdc-md-fall25
git add SYSTEM_STATUS.md
git commit -m "Add system status summary after force field analysis"
```

---

## Day 3: Analysis Pipeline + Documentation

### Block 3.1: Morning Production Check (15 min)

```bash
ssh john.aitken@hpg.rc.ufl.edu
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2

# Job status
squeue -u $USER

# Check all completed segments
echo "=== Completed Production Segments ==="
for seg in prod_seg*.nc; do
    if [[ -f "$seg" ]]; then
        SIZE=$(ls -lh "$seg" | awk '{print $5}')
        echo "$seg: $SIZE"
    fi
done

# Submit next segment if previous complete
LAST_SEG=$(ls prod_seg*.rst7 2>/dev/null | sort | tail -1 | grep -oP '\d{3}')
if [[ -n "$LAST_SEG" ]]; then
    NEXT_SEG=$((10#$LAST_SEG + 1))
    echo "Last complete segment: $LAST_SEG"
    echo "Ready to submit segment: $NEXT_SEG"

    # Check if job already running
    if ! squeue -u $USER | grep -q "biox2_p"; then
        ./continue_production.sh $NEXT_SEG
    else
        echo "Production job already running"
    fi
fi
```

### Block 3.2: Run Analysis on Available Data (45 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/analysis

module load amber/25

# Count available trajectory frames
PRMTOP=$(ls ../systems/BiOx+2/*.prmtop | head -1)
NC_FILES=$(ls ../systems/BiOx+2/prod_seg*.nc 2>/dev/null | wc -l)

echo "Available production trajectories: $NC_FILES segments"

if [[ $NC_FILES -gt 0 ]]; then
    echo "Running RMSD analysis..."

    # Create analysis input with actual files
    cat > cpptraj/run_analysis.in << EOF
parm $PRMTOP
$(for f in ../systems/BiOx+2/prod_seg*.nc; do echo "trajin $f"; done)

reference $(ls ../systems/BiOx+2/*.inpcrd | head -1) [ref]

# RMSD
rms RMSD_CA @CA reference out results/rmsd_ca.dat
rms RMSD_BB @C,CA,N reference out results/rmsd_bb.dat

# RMSF
rmsf RMSF_CA @CA out results/rmsf_ca.dat byres

# Mn coordination
distance Mn_His95  @6032 @1519 out results/mn_his95.dat
distance Mn_His97  @6032 @1560 out results/mn_his97.dat
distance Mn_Glu101 @6032 @1623 out results/mn_glu101.dat
distance Mn_His140 @6032 @2230 out results/mn_his140.dat

run
EOF

    cpptraj -i cpptraj/run_analysis.in

    echo ""
    echo "=== Analysis Results ==="
    for f in results/*.dat; do
        if [[ -f "$f" ]]; then
            echo "$f: $(wc -l < $f) frames"
        fi
    done
fi
```

### Block 3.3: Generate Publication Figures (30 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/analysis/scripts

# Run all visualization scripts
echo "Generating figures..."

python3 energy_analysis.py 2>/dev/null && echo "energy_analysis: OK" || echo "energy_analysis: SKIP (need data)"
python3 force_constant_analysis.py && echo "force_constant_analysis: OK"
python3 comprehensive_mn_analysis.py && echo "comprehensive_mn_analysis: OK"
python3 project7_energy_landscape.py && echo "project7: OK"
python3 project8_vibrational_analysis.py && echo "project8: OK"
python3 project9_thermal_fluctuations.py && echo "project9: OK"
python3 project10_parameterization_quality.py && echo "project10: OK"
python3 project11_coordination_geometry.py && echo "project11: OK"
python3 exploratory_ml_stability.py && echo "exploratory_ml: OK"

echo ""
echo "Generated figures in ../results/:"
ls -la ../results/*.png 2>/dev/null
```

### Block 3.4: RMSD/RMSF Visualization (if data available) (20 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/analysis

# Create RMSD plot if data exists
if [[ -f results/rmsd_ca.dat ]]; then
    python3 << 'PYEOF'
import matplotlib.pyplot as plt
import numpy as np

# Load RMSD data
data = np.loadtxt('results/rmsd_ca.dat')
time = data[:, 0] / 1000  # Convert to ns
rmsd = data[:, 1]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, rmsd, 'b-', linewidth=0.5, alpha=0.7)
ax.axhline(y=np.mean(rmsd), color='r', linestyle='--', label=f'Mean: {np.mean(rmsd):.2f} Å')

ax.set_xlabel('Time (ns)', fontsize=12)
ax.set_ylabel('RMSD (Å)', fontsize=12)
ax.set_title('BiOx+2 Production: Backbone RMSD', fontsize=14)
ax.legend()

plt.tight_layout()
plt.savefig('results/production_rmsd.png', dpi=150)
print('Saved: results/production_rmsd.png')
PYEOF
else
    echo "No RMSD data yet - skip plotting"
fi
```

### Block 3.5: Compile Documentation (30 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/claude-notes

# Create executive summary
cat > EXECUTIVE_SUMMARY.md << 'EOF'
# OxDC MD Simulation Project: Executive Summary

## Problem Statement
Four OxDC system variants were prepared for MD simulation, but only one (BiOx+2) achieves stable production.

## Root Cause (Corrected)
**Force field parameters**, not restraint masks, determine stability:
- BiOx+2: avg k = 29 kcal/mol·Å² → STABLE
- Others: avg k = 40-97 kcal/mol·Å² → UNSTABLE

## Key Findings
1. Lower force constants enable thermal fluctuations without energy spikes
2. BiOx+2's substrate provides flexible coordination geometry
3. 1Wat+3 models Mn(III) with inherently high force constants (Jahn-Teller)
4. Stability can be predicted from MCPB.py parameters

## Recommendations
1. **Immediate**: Run BiOx+2 production (100 ns target)
2. **Short-term**: Attempt softer equilibration for 1Wat+2
3. **Long-term**: Consider re-parameterization or QM/MM for Mn(III) systems

## Deliverables Created
- Literature review with 12+ references
- 8 publication-quality figures
- Analysis scripts for RMSD, Mn coordination, stability
- Interactive web demo for stability prediction
- Rigorous critique of all findings
- Research journal with future directions

## Status
- BiOx+2: IN PRODUCTION
- 1Wat+2: PENDING re-equilibration
- 1Wat+3: REQUIRES special handling (Mn(III))
- empty+2: LOWEST priority
EOF

cat EXECUTIVE_SUMMARY.md
```

### Block 3.6: Final Git Commit (15 min)

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25

# Stage all new files
git add -A

# Create comprehensive commit
git commit -m "$(cat <<'EOF'
Complete research preparation and force field analysis

Major findings:
- Root cause: force field parameters (not restraint masks) determine stability
- BiOx+2 (k=29) stable; others (k=40-97) unstable
- Mn(III) in 1Wat+3 has Jahn-Teller-driven high force constants
- Literature supports all key findings

Deliverables:
- Extended literature review with 12+ references
- 11 analysis projects with visualizations
- Interactive web demo for stability prediction
- Rigorous Socratic critique of all claims
- Research journal with future directions
- Revised 3-day implementation plan

Analysis scripts:
- energy_analysis.py, force_constant_analysis.py
- comprehensive_mn_analysis.py
- Projects 7-11 covering energy landscape, vibrations, thermal fluctuations
- exploratory_ml_stability.py

Documentation:
- FINDINGS_SUMMARY.md, ROOT_CAUSE_ANALYSIS.md
- LITERATURE_REVIEW_EXTENDED.md, RESEARCH_JOURNAL.md
- RIGOROUS_CRITIQUE.md, EXECUTIVE_SUMMARY.md
- THREE_DAY_PLAN_REVISED.md (this file)

BiOx+2 production: IN PROGRESS
EOF
)"

# Push to remote
git push -u origin claude/oxdc-repo-prep-EjqCu

echo "All work committed and pushed"
```

### Block 3.7: End of Day 3 Final Checklist

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              DAY 3 COMPLETION CHECKLIST                      ║"
echo "╠══════════════════════════════════════════════════════════════╣"

# BiOx+2 production
echo -n "║ BiOx+2 production started:        "
if ls systems/BiOx+2/prod_seg*.nc &>/dev/null; then
    echo "✓ YES                   ║"
else
    echo "✗ NO                    ║"
fi

# Figures generated
echo -n "║ Analysis figures generated:       "
FIG_COUNT=$(ls analysis/results/*.png 2>/dev/null | wc -l)
echo "$FIG_COUNT files                   ║"

# Documentation complete
echo -n "║ Documentation complete:           "
if [[ -f claude-notes/EXECUTIVE_SUMMARY.md ]]; then
    echo "✓ YES                   ║"
else
    echo "✗ NO                    ║"
fi

# Git pushed
echo -n "║ Git committed and pushed:         "
if git status | grep -q "nothing to commit"; then
    echo "✓ YES                   ║"
else
    echo "✗ PENDING               ║"
fi

echo "╚══════════════════════════════════════════════════════════════╝"

echo ""
echo "=== NEXT STEPS ==="
echo "1. Monitor BiOx+2 production (./continue_production.sh N)"
echo "2. Run cpptraj analysis after 50 ns collected"
echo "3. Meet with PI to discuss Mn(III) handling strategy"
echo "4. Begin thesis writing with current figures"
```

---

## Post-3-Day Continuation Commands

### Daily Production Monitoring

```bash
# Quick status check (run daily)
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2
squeue -u $USER
ls -lh prod_seg*.nc | tail -5
cat production_log.txt | tail -5
```

### Submit Next Segment

```bash
# When previous segment completes
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2
LAST=$(ls prod_seg*.rst7 | sort | tail -1 | grep -oP '\d{3}')
./continue_production.sh $((10#$LAST + 1))
```

### Run Analysis After 50 ns

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25/analysis
cpptraj -i cpptraj/run_analysis.in
python3 scripts/plot_production_rmsd.py
```

### Weekly Backup

```bash
cd /blue/ax/john.aitken/oxdc-md-fall25
git add -A
git commit -m "Weekly backup: $(date +%Y-%m-%d)"
git push
```

---

## Troubleshooting Quick Reference

### Job Failed
```bash
# Check error file
cat prod_seg*.err | tail -50

# Common fixes:
# - Out of time: increase --time in sbatch
# - Out of memory: increase --mem
# - GPU issue: try different partition
```

### vlimit Warning Appears
```bash
# Check energy
grep "Etot" prod_seg*.out | tail -20 | awk '{print $3}'

# If energies spike >10000, restart from last good checkpoint
# If consistent, system may be fundamentally unstable
```

### Trajectory Corrupted
```bash
# Check trajectory
cpptraj -p *.prmtop << 'EOF'
trajin prod_seg001.nc
trajinfo
EOF

# If corrupted, restart from previous .rst7
```

---

*This plan represents the culmination of comprehensive force field analysis. Execute commands in order. Adjust paths for your HPC environment.*
