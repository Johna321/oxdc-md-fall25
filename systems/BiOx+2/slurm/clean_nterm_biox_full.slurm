#!/bin/bash
#SBATCH --job-name=OxDC_test
#SBATCH --output=clean_nterm_full_%j.out
#SBATCH --error=clean_nterm_full_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --partition=hpg-turin
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --cpus-per-gpu=2
#SBATCH --gpus-per-task=1


echo "========================================="
echo "OxDC MD - EQ2"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start: $(date)"
echo "========================================="

# Load AMBER 25 (auto-loads CUDA 12.8.1)
module purge
module load cuda/12.8.1
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

# Output directory
OUTPUT_DIR="clean_BiOx2_${SLURM_JOB_ID}"
mkdir -p $OUTPUT_DIR
cd $OUTPUT_DIR

# System selection (change this for different systems)
SYSTEM="Nterm_BiOx+2"
PRMTOP="../../Closed_comfirmation/pH_4/Nterm_only/BiOx+2/5vg3_solv.prmtop"
INPCRD="../../Closed_comfirmation/pH_4/Nterm_only/BiOx+2/5vg3_solv.inpcrd"


# Verify files exist
echo ""
echo "Verifying input files..."
if [ ! -f "$PRMTOP" ]; then
  echo "ERROR: Topology not found: $PRMTOP"
  exit 1
fi
if [ ! -f "$INPCRD" ]; then
  echo "ERROR: Coordinates not found: $INPCRD"
  exit 1
fi

echo "Topology: $(basename $PRMTOP) ($(ls -lh $PRMTOP | awk '{print $5}'))"
echo "Coordinates: $(basename $INPCRD) ($(ls -lh $INPCRD | awk '{print $5}'))"

# Check GPU
echo ""
echo "GPU Information:"
nvidia-smi --query-gpu=name,memory.total,memory.free,temperature.gpu --format=csv

# ============================================================================
# PHASE 1: MINIMIZATION (10,000 steps)
# ============================================================================

echo ""
echo "========================================="
echo "PHASE 1: Minimization"
echo "========================================="

cat >min.in <<'EOF'
 &cntrl
  imin   = 1,
  ntmin  = 1,
  maxcyc = 10000,
  ncyc   = 2500,

  ntpr   = 100,
  ntwr   = 1000,

  cut    = 10.0,
  ntb    = 1,
  ntp    = 0,
  nmropt = 0
 /
 &wt TYPE='END', /
LISTOUT=POUT
EOF

START=$(date +%s)
pmemd.cuda -O \
  -i min.in \
  -p $PRMTOP \
  -c $INPCRD \
  -ref $INPCRD \
  -o min.out \
  -r min.rst7 \
  -inf min.mdinfo

EXIT_CODE=$?
RUNTIME=$(($(date +%s) - START))

if [ $EXIT_CODE -ne 0 ]; then
  echo "Minimization FAILED (exit code $EXIT_CODE)"
  exit 1
fi

# Check convergence
RMS=$(tail -50 min.out | grep "NSTEP.*ENERGY.*RMS" -A1 | tail -1 | awk '{print $3}')
echo "Minimization completed in ${RUNTIME}s"
echo "  Final RMS gradient: $RMS"

if (($(echo "$RMS > 1.0" | bc -l))); then
  echo "WARNING: Poor convergence (RMS > 1.0)"
fi

# ============================================================================
# PHASE 2: HEATING (50 ps, 0→300K)
# ============================================================================

echo ""
echo "========================================="
echo "PHASE 2: Heating (0→300K)"
echo "========================================="

cat >heat.in <<'EOF'
Heating from 0 to 300K over 50ps
 &cntrl
  imin   = 0,
  ntx    = 1,
  irest  = 0,
  nmropt = 0,

  nstlim = 25000,      ! 50ps at 2fs timestep
  dt     = 0.002,
  ntc    = 2,
  ntf    = 2,	       ! SHAKE for 2 fs

  ntpr   = 500,
  ntwr   = 5000,
  ntwx   = 5000,
  ntxo   = 2,

  cut    = 10.0,
  ntb    = 1,		! NVT

  ntt    = 3,
  gamma_ln = 2.0,
  temp0  = 300.0,

 /

 &wt TYPE='TEMP0', istep1=0, istep2=25000, value1=0.0, value2=300.0, /
 &wt TYPE='END' /
EOF

START=$(date +%s)
pmemd.cuda -O \
  -i heat.in \
  -p $PRMTOP \
  -c min.rst7 \
  -ref min.rst7 \
  -o heat.out \
  -r heat.rst7 \
  -x heat.nc \
  -inf heat.mdinfo

EXIT_CODE=$?
RUNTIME=$(($(date +%s) - START))

if [ $EXIT_CODE -ne 0 ]; then
  echo "Heating FAILED (exit code $EXIT_CODE)"
  exit 1
fi

echo "✓ Heating completed in ${RUNTIME}s"

# ============================================================================
# PHASE 3: EQUILIBRATION 1 (1 ns NPT, restraints 200→50)
# ============================================================================

echo ""
echo "========================================="
echo "PHASE 3: Equilibration 1 (1 ns)"
echo "========================================="

cat >eq1.in <<'EOF'
Equilibration 1: 1ns NPT with high restraints
 &cntrl
  iwrap  = 1,
  imin   = 0,
  ntx    = 5,
  irest  = 1,
  nmropt = 0,

  nstlim = 500000,     ! 1ns at 2fs timestep
  dt     = 0.002,

  ntc    = 2,          ! <<< SHAKE
  ntf    = 2,

  ntpr   = 5000,
  ntwr   = 50000,
  ntwx   = 5000,
  ntxo   = 2,

  cut    = 10.0,
  ntb    = 2,
  ntp    = 1,
  barostat = 1,
  pres0  = 1.0,
  taup   = 5.0,         ! gentle Berendsen

  ntt    = 3,
  gamma_ln = 2.0,
  temp0  = 300.0,
  ntr=1, restraint_wt=5.0, ! <<< pos. restraints (not NMR)
  restraintmask='!:WAT,Na+,Cl- & !@H='
 /
 &wt TYPE='END', /
EOF

START=$(date +%s)
pmemd.cuda -O \
  -i eq1.in \
  -p $PRMTOP \
  -c heat.rst7 \
  -ref heat.rst7 \
  -o eq1.out \
  -r eq1.rst7 \
  -x eq1.nc \
  -inf eq1.mdinfo

EXIT_CODE=$?
RUNTIME=$(($(date +%s) - START))

if [ $EXIT_CODE -ne 0 ]; then
  echo "Equilibration 1 FAILED (exit code $EXIT_CODE)"
  exit 1
fi

echo "Equilibration 1 completed in ${RUNTIME}s"

# ============================================================================
# PHASE 4: EQUILIBRATION 2 (200ps NPT, restraints 50→20)
# ============================================================================

echo ""
echo "========================================="
echo "PHASE 4: Equilibration 2 (1 ns)"
echo "========================================="

cat >eq2.in <<'EOF'
Equilibration 2: 1ns NPT with medium restraints
 &cntrl
  iwrap  = 1,
  imin   = 0,
  ntx    = 5,
  irest  = 1,
  nmropt = 0,

  nstlim = 100000,     ! 200 ps @ 2 fs; can use 50000 for 100 ps
  dt     = 0.002,
  ntc=2, ntf=2,        ! SHAKE on bonds to H

  ntpr   = 1000,
  ntwr   = 5000,
  ntwx   = 1000,
  ntxo   = 2,

  cut    = 10.0,
  ntb    = 2,
  ntp    = 1,
  barostat = 1,        ! gentle Berendsen
  pres0  = 1.0,
  taup   = 5.0,

  ntt    = 3,
  gamma_ln = 2.0,
  temp0  = 300.0,

  ntr=1,
  restraint_wt=5.0,
  restraintmask='!:WAT,Na+,Cl- & !@H='  ! heavy non-solvent atoms
 /
 &wt TYPE='END', /
EOF

START=$(date +%s)
pmemd.cuda -O \
  -i eq2.in \
  -p $PRMTOP \
  -c eq1.rst7 \
  -ref eq1.rst7 \
  -o eq2.out \
  -r eq2.rst7 \
  -x eq2.nc \
  -inf eq2.mdinfo

EXIT_CODE=$?
RUNTIME=$(($(date +%s) - START))

if [ $EXIT_CODE -ne 0 ]; then
  echo "Equilibration 2 FAILED (exit code $EXIT_CODE)"
  exit 1
fi

echo "Equilibration 2 completed in ${RUNTIME}s"


# ============================================================================
# FINAL SUMMARY
# ============================================================================

echo ""
echo "========================================="
echo " MD PROTOCOL UP TO EQ2 COMPLETED!"
echo "========================================="
echo "System: $SYSTEM"
echo ""
echo "Files generated:"
ls -lh *.rst7 *.nc *.out | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Job completed: $(date)"
echo "========================================="

