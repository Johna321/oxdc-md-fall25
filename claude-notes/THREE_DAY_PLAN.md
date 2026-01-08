# 3-Day Implementation Plan

**Goal:** Get BiOx+2 into production and prepare other systems for re-equilibration.

**Philosophy:** Each step below is a literal command or concrete action. No thinking required — just execute.

---

## Day 1: Fix Protocol & Start BiOx+2 Production

### Morning (2-3 hours)

#### Step 1.1: Create Corrected mdin Files for BiOx+2

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Create backup of current mdin files
cp -r mdin_templates mdin_templates_backup

# Create corrected eq2 file
cat > mdin_templates/eq2_fixed.in << 'EOF'
EQ2 NPT MC (1 fs) reduced restraints - CORRECTED MASK
 &cntrl
  imin=0, irest=1, ntx=5,
  nstlim=250000, dt=0.001,
  ntc=2, ntf=2,
  ntb=2, ntp=1, barostat=2, pres0=1.0,
  ntt=3, gamma_ln=2.0,
  ntr=1, restraint_wt=0.5,
  restraintmask='(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
EOF

# Create eq3 file (no restraints, ready for production)
cat > mdin_templates/eq3_npt.in << 'EOF'
EQ3 NPT (2 fs) no restraints - production ready
 &cntrl
  imin=0, ntx=5, irest=1,
  ntb=2, ntp=1, barostat=2, pres0=1.0, taup=2.0,
  ntt=3, gamma_ln=1.0, temp0=300.0,
  ntc=2, ntf=2, dt=0.002, nstlim=250000,
  cut=10.0, iwrap=1,
  ntpr=1000, ntwx=1000, ntwr=50000, ntxo=2, ioutfm=1,
  ntr=0
 /
EOF

echo "Created corrected mdin files"
```

#### Step 1.2: Check BiOx+2 Current Status

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Check what restart files exist
ls -lh *.rst7

# Check last energy/density from eq1
tail -50 eq1.cpu.out | grep -E "NSTEP|Density"

# Verify no vlimit warnings
grep -c "vlimit" eq1.cpu.out
```

**Expected output:** Should show ~145 ps completed, density ~1.01 g/cc, 0 vlimit warnings.

#### Step 1.3: Submit BiOx+2 EQ2

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Create EQ2 run script
cat > run_eq2.sbatch << 'EOF'
#!/bin/bash
#SBATCH --job-name=biox2_eq2
#SBATCH --output=eq2.%j.out
#SBATCH --error=eq2.%j.err
#SBATCH --partition=hpg-milan
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --time=04:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu

module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

srun pmemd.MPI -O \
    -i mdin_templates/eq2_fixed.in \
    -p 5vg3_solv.prmtop \
    -c eq1.cpu.rst7 \
    -ref eq1.cpu.rst7 \
    -o eq2.cpu.out \
    -r eq2.cpu.rst7 \
    -x eq2.cpu.nc \
    -inf eq2.cpu.mdinfo
EOF

# Submit
sbatch run_eq2.sbatch
echo "Submitted eq2 job"
```

### Afternoon (2-3 hours)

#### Step 1.4: While EQ2 Runs, Verify Residue Numbering

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Load AMBER module
module load amber/25

# Check residue info
cpptraj -p 5vg3_solv.prmtop << 'EOF' > residue_info.txt
resinfo
quit
EOF

# Find Glu162 equivalent (search for GLU or GU near residue 160-170)
grep -n "GLU\|GU" residue_info.txt | head -20

# Find His residues
grep -n "HIS\|HID\|HIE\|HIP\|HD" residue_info.txt | head -30

# Find lid region (look for residues 160-166)
sed -n '160,170p' residue_info.txt
```

**Save this output** — needed to correct analysis script residue numbers.

#### Step 1.5: Prepare 1Wat+2 for Re-equilibration

```bash
cd /home/user/oxdc-md-fall25/systems/1Wat+2

# Create corrected heat file with restraints
cat > mdin_templates/heat_fixed.in << 'EOF'
Heating NVT 50 ps (1 fs, SHAKE) WITH RESTRAINTS
 &cntrl
  imin=0, irest=0, ntx=1,
  nstlim=50000, dt=0.001,
  ntc=2, ntf=2,
  ntb=1,
  ntt=3, gamma_ln=2.0, tempi=0.0, temp0=300.0,
  ntr=1, restraint_wt=5.0,
  restraintmask='(!:WAT,WT1,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
 &wt TYPE='TEMP0', istep1=0, istep2=50000, value1=0.0, value2=300.0 /
 &wt TYPE='END' /
EOF

# Create corrected eq1 file
cat > mdin_templates/eq1_fixed.in << 'EOF'
EQ1 NPT MC (1 fs) - CORRECTED MASK
 &cntrl
  imin=0, irest=1, ntx=5,
  nstlim=250000, dt=0.001,
  ntc=2, ntf=2,
  ntb=2, ntp=1, barostat=2, pres0=1.0,
  ntt=3, gamma_ln=2.0,
  ntr=1, restraint_wt=2.0,
  restraintmask='(!:WAT,WT1,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
EOF

# Create corrected eq2 file
cat > mdin_templates/eq2_fixed.in << 'EOF'
EQ2 NPT MC (1 fs) - CORRECTED MASK
 &cntrl
  imin=0, irest=1, ntx=5,
  nstlim=250000, dt=0.001,
  ntc=2, ntf=2,
  ntb=2, ntp=1, barostat=2, pres0=1.0,
  ntt=3, gamma_ln=2.0,
  ntr=1, restraint_wt=0.5,
  restraintmask='(!:WAT,WT1,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
EOF

echo "Created corrected mdin files for 1Wat+2"
```

#### Step 1.6: Repeat for 1Wat+3 and empty+2

```bash
# 1Wat+3
cd /home/user/oxdc-md-fall25/systems/1Wat+3

cat > mdin_templates/heat_fixed.in << 'EOF'
Heating NVT 50 ps WITH RESTRAINTS
 &cntrl
  imin=0, irest=0, ntx=1,
  nstlim=50000, dt=0.001,
  ntc=2, ntf=2, ntb=1,
  ntt=3, gamma_ln=2.0, tempi=0.0, temp0=300.0,
  ntr=1, restraint_wt=5.0,
  restraintmask='(!:WAT,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
 &wt TYPE='TEMP0', istep1=0, istep2=50000, value1=0.0, value2=300.0 /
 &wt TYPE='END' /
EOF

cat > mdin_templates/eq1_fixed.in << 'EOF'
EQ1 NPT MC (1 fs) - CORRECTED
 &cntrl
  imin=0, irest=1, ntx=5,
  nstlim=250000, dt=0.001,
  ntc=2, ntf=2,
  ntb=2, ntp=1, barostat=2, pres0=1.0,
  ntt=3, gamma_ln=2.0,
  ntr=1, restraint_wt=2.0,
  restraintmask='(!:WAT,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
EOF

# empty+2
cd /home/user/oxdc-md-fall25/systems/empty+2

cat > mdin_templates/heat_fixed.in << 'EOF'
Heating NVT 50 ps WITH RESTRAINTS
 &cntrl
  imin=0, irest=0, ntx=1,
  nstlim=50000, dt=0.001,
  ntc=2, ntf=2, ntb=1,
  ntt=3, gamma_ln=2.0, tempi=0.0, temp0=300.0,
  ntr=1, restraint_wt=5.0,
  restraintmask='(!:WAT,WTR,Cl-,MN1,MN2,GU,HD)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
 &wt TYPE='TEMP0', istep1=0, istep2=50000, value1=0.0, value2=300.0 /
 &wt TYPE='END' /
EOF

cat > mdin_templates/eq1_fixed.in << 'EOF'
EQ1 NPT MC (1 fs) - CORRECTED
 &cntrl
  imin=0, irest=1, ntx=5,
  nstlim=250000, dt=0.001,
  ntc=2, ntf=2,
  ntb=2, ntp=1, barostat=2, pres0=1.0,
  ntt=3, gamma_ln=2.0,
  ntr=1, restraint_wt=2.0,
  restraintmask='(!:WAT,WTR,Cl-,MN1,MN2,GU,HD)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
EOF

echo "Created corrected mdin files for 1Wat+3 and empty+2"
```

#### Step 1.7: End of Day 1 - Check EQ2 Status

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Check job status
squeue -u $USER

# If complete, check output
if [[ -f eq2.cpu.rst7 ]]; then
    tail -50 eq2.cpu.out | grep -E "NSTEP|Density"
    grep -c "vlimit" eq2.cpu.out
    echo "EQ2 complete - ready for EQ3"
fi
```

---

## Day 2: BiOx+2 to Production, Start Other Re-equilibrations

### Morning (2-3 hours)

#### Step 2.1: Submit BiOx+2 EQ3

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Create EQ3 submission script
cat > run_eq3.sbatch << 'EOF'
#!/bin/bash
#SBATCH --job-name=biox2_eq3
#SBATCH --output=eq3.%j.out
#SBATCH --error=eq3.%j.err
#SBATCH --partition=hpg-turin
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-gpu=2
#SBATCH --mem=8gb
#SBATCH --time=02:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu

module purge
module load cuda/12.8.1
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

pmemd.cuda -O \
    -i mdin_templates/eq3_npt.in \
    -p 5vg3_solv.prmtop \
    -c eq2.cpu.rst7 \
    -o eq3.gpu.out \
    -r eq3.gpu.rst7 \
    -x eq3.gpu.nc \
    -inf eq3.gpu.mdinfo
EOF

sbatch run_eq3.sbatch
```

#### Step 2.2: Submit Heat Re-runs for Other Systems

```bash
# Create common submission script
create_heat_script() {
    local SYS=$1
    cd /home/user/oxdc-md-fall25/systems/$SYS

    cat > run_heat_fixed.sbatch << EOF
#!/bin/bash
#SBATCH --job-name=${SYS}_heat
#SBATCH --output=heat_fixed.%j.out
#SBATCH --error=heat_fixed.%j.err
#SBATCH --partition=hpg-milan
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --time=02:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu

module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

# Identify correct files
PRMTOP=\$(ls 5vg3*.prmtop 2>/dev/null | head -1)
INPCRD=\$(ls 5vg3*.inpcrd 2>/dev/null | head -1)

echo "Using PRMTOP: \$PRMTOP"
echo "Using INPCRD: \$INPCRD"

srun pmemd.MPI -O \\
    -i mdin_templates/heat_fixed.in \\
    -p \$PRMTOP \\
    -c \$INPCRD \\
    -ref \$INPCRD \\
    -o heat.fixed.out \\
    -r heat.fixed.rst7 \\
    -x heat.fixed.nc \\
    -inf heat.fixed.mdinfo
EOF

    sbatch run_heat_fixed.sbatch
    echo "Submitted heat for $SYS"
}

# Submit for each system
create_heat_script "1Wat+2"
create_heat_script "1Wat+3"
create_heat_script "empty+2"
```

### Afternoon (2-3 hours)

#### Step 2.3: When BiOx+2 EQ3 Completes, QC Check

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Run QC checks
module load amber/25

# Check density
tail -100 eq3.gpu.out | grep Density | tail -5

# Check RMSD
cpptraj -p 5vg3_solv.prmtop << 'EOF'
trajin eq3.gpu.rst7
reference 5vg3_solv.inpcrd
rms RMSD @CA reference
run
EOF

# Check Mn distances (use correct atom indices from mn_bonds.csv)
cpptraj -p 5vg3_solv.prmtop << 'EOF'
trajin eq3.gpu.rst7
distance d1 @6032 @1519
distance d2 @6032 @1560
distance d3 @6032 @1623
distance d4 @6032 @2230
distance d5 @6032 @6036
distance d6 @6032 @6038
run
EOF
```

**QC Pass Criteria:**
- Density: 0.99-1.02 g/cc
- RMSD: < 2.0 Å
- Mn distances: within 0.3 Å of initial

#### Step 2.4: Submit BiOx+2 Production Segment 1

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Copy production mdin
cp /home/user/oxdc-md-fall25/claude-notes/production/prod_template.in mdin_templates/

# Create production submission
cat > run_prod_seg001.sbatch << 'EOF'
#!/bin/bash
#SBATCH --job-name=biox2_prod001
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

pmemd.cuda -O \
    -i mdin_templates/prod_template.in \
    -p 5vg3_solv.prmtop \
    -c eq3.gpu.rst7 \
    -o prod_seg001.out \
    -r prod_seg001.rst7 \
    -x prod_seg001.nc \
    -inf prod_seg001.mdinfo
EOF

sbatch run_prod_seg001.sbatch
echo "Production started for BiOx+2!"
```

#### Step 2.5: Set Up Production Continuation

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Create script for subsequent segments
cat > run_prod_continue.sh << 'EOF'
#!/bin/bash
# Usage: ./run_prod_continue.sh <segment_number>

SEG=$1
PREV=$((SEG - 1))

cat > run_prod_seg$(printf '%03d' $SEG).sbatch << INNEREOF
#!/bin/bash
#SBATCH --job-name=biox2_prod$(printf '%03d' $SEG)
#SBATCH --output=prod_seg$(printf '%03d' $SEG).%j.out
#SBATCH --error=prod_seg$(printf '%03d' $SEG).%j.err
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
    -i mdin_templates/prod_template.in \\
    -p 5vg3_solv.prmtop \\
    -c prod_seg$(printf '%03d' $PREV).rst7 \\
    -o prod_seg$(printf '%03d' $SEG).out \\
    -r prod_seg$(printf '%03d' $SEG).rst7 \\
    -x prod_seg$(printf '%03d' $SEG).nc \\
    -inf prod_seg$(printf '%03d' $SEG).mdinfo
INNEREOF

sbatch run_prod_seg$(printf '%03d' $SEG).sbatch
EOF

chmod +x run_prod_continue.sh
echo "Created continuation script"
```

---

## Day 3: Monitor Production, Continue Re-equilibration

### Morning (2-3 hours)

#### Step 3.1: Check All Job Status

```bash
# Check queue
squeue -u $USER

# Check BiOx+2 production progress
cd /home/user/oxdc-md-fall25/systems/BiOx+2
if [[ -f prod_seg001.mdinfo ]]; then
    cat prod_seg001.mdinfo
fi

# Check other system heat status
for sys in 1Wat+2 1Wat+3 empty+2; do
    echo "=== $sys ==="
    if [[ -f /home/user/oxdc-md-fall25/systems/$sys/heat.fixed.rst7 ]]; then
        echo "Heat complete"
        tail -5 /home/user/oxdc-md-fall25/systems/$sys/heat.fixed.out | grep -E "NSTEP|Density"
        grep -c "vlimit" /home/user/oxdc-md-fall25/systems/$sys/heat.fixed.out
    else
        echo "Heat still running or failed"
    fi
done
```

#### Step 3.2: Submit EQ1 for Systems with Complete Heat

```bash
submit_eq1() {
    local SYS=$1
    cd /home/user/oxdc-md-fall25/systems/$SYS

    if [[ ! -f heat.fixed.rst7 ]]; then
        echo "$SYS: heat not complete"
        return
    fi

    cat > run_eq1_fixed.sbatch << EOF
#!/bin/bash
#SBATCH --job-name=${SYS}_eq1
#SBATCH --output=eq1_fixed.%j.out
#SBATCH --error=eq1_fixed.%j.err
#SBATCH --partition=hpg-milan
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --time=06:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu

module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

PRMTOP=\$(ls 5vg3*.prmtop 2>/dev/null | head -1)

srun pmemd.MPI -O \\
    -i mdin_templates/eq1_fixed.in \\
    -p \$PRMTOP \\
    -c heat.fixed.rst7 \\
    -ref heat.fixed.rst7 \\
    -o eq1.fixed.out \\
    -r eq1.fixed.rst7 \\
    -x eq1.fixed.nc \\
    -inf eq1.fixed.mdinfo
EOF

    sbatch run_eq1_fixed.sbatch
    echo "Submitted eq1 for $SYS"
}

submit_eq1 "1Wat+2"
submit_eq1 "1Wat+3"
submit_eq1 "empty+2"
```

### Afternoon (2-3 hours)

#### Step 3.3: Submit Production Segment 2 (if Segment 1 Complete)

```bash
cd /home/user/oxdc-md-fall25/systems/BiOx+2

if [[ -f prod_seg001.rst7 ]]; then
    ./run_prod_continue.sh 2
    echo "Submitted segment 2"
else
    echo "Segment 1 not complete yet"
fi
```

#### Step 3.4: Run Preliminary Analysis on Equilibration

```bash
cd /home/user/oxdc-md-fall25/analysis

module load amber/25

# Test RMSD analysis on BiOx+2 eq3
cpptraj -p ../systems/BiOx+2/5vg3_solv.prmtop << 'EOF'
trajin ../systems/BiOx+2/eq3.gpu.nc
reference ../systems/BiOx+2/5vg3_solv.inpcrd [ref]
rms RMSD @CA reference out results/biox2_eq3_rmsd.dat
rmsf RMSF @CA out results/biox2_eq3_rmsf.dat byres
run
EOF

echo "Preliminary analysis complete - check results/"
```

#### Step 3.5: Commit Progress to Git

```bash
cd /home/user/oxdc-md-fall25

# Add new files
git add claude-notes/
git add analysis/

# Commit
git commit -m "Add corrected equilibration protocol and analysis pipeline

- Created corrected mdin files with system-specific restraint masks
- Added production input templates and SLURM scripts
- Created cpptraj analysis inputs for RMSD, Mn coordination, lid dynamics
- Documented literature review, protocol audit, and knowledge gaps
- Created 3-day implementation plan

Key finding: Original restraint masks were incorrect, causing instabilities."

# Push (adjust branch name as needed)
git push -u origin claude-research
```

---

## End of Day 3 Checklist

### BiOx+2
- [ ] EQ2 complete
- [ ] EQ3 complete
- [ ] QC passed (density, RMSD, Mn distances)
- [ ] Production segment 1 complete (~10 ns)
- [ ] Production segment 2 running

### Other Systems
- [ ] Corrected mdin files created
- [ ] Heat (with restraints) complete
- [ ] EQ1 running or complete
- [ ] No vlimit warnings in new runs

### Documentation
- [ ] All claude-notes/ documents complete
- [ ] Analysis scripts tested
- [ ] Changes committed and pushed

---

## After 3 Days: What's Next?

### Week 1 of Semester
1. Continue BiOx+2 production (target: 50 ns)
2. Complete re-equilibration of other systems
3. Run preliminary analysis on BiOx+2

### Week 2
1. BiOx+2 reaches 100 ns
2. Start production on second system (1Wat+2 or 1Wat+3)
3. Detailed lid dynamics analysis

### Week 3-4
1. All systems in production
2. Start replica runs
3. Comparative analysis

### Thesis Timeline
- **Month 1:** All production data collected
- **Month 2:** Analysis and figure preparation
- **Month 3:** Writing
- **Month 4:** Revisions and defense prep
