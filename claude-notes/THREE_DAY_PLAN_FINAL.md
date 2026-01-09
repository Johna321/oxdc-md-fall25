# OxDC MD Production: Final 3-Day Implementation Plan

## Pre-Implementation Status Summary

| Item | Status | Evidence |
|------|--------|----------|
| heat.cpu.rst7 | COMPLETE | File exists (3 MB) |
| eq1.cpu.rst7 | PARTIAL (60%) | mdinfo: 149000/250000 steps |
| eq2.cpu.rst7 | MISSING | File does not exist |
| prod_mc_gpu_2fs.in | MISSING | Not in mdin_templates/ |
| run_eq_cpu_mc.sbatch | READY | Tested script exists |
| run_prod_gpu_mc.sbatch | READY | Tested script exists |
| cpptraj inputs | READY | 5 analysis scripts exist |

---

## Day 1: Complete Equilibration

### Step 1.1: SSH to HiPerGator
```bash
ssh <gatorlink>@hpg.rc.ufl.edu
```

### Step 1.2: Navigate to BiOx+2 System
```bash
cd /blue/roitberg/john.aitken/oxdc-md-fall25/systems/BiOx+2
```

### Step 1.3: Verify Current State
```bash
ls -la *.rst7 *.mdinfo
# Expected output:
#   heat.cpu.rst7    (should exist, ~3 MB)
#   heat.cpu.mdinfo  (should exist)
#   eq1.cpu.rst7     (should exist, partial checkpoint)
#   eq1.cpu.mdinfo   (should exist, shows 59.6%)
#   NO eq2.cpu.rst7
```

### Step 1.4: Create Production mdin Template
```bash
cat > mdin_templates/prod_mc_gpu_2fs.in << 'EOF'
OxDC Production MD - 10 ns segment (NPT, GPU)
 &cntrl
  imin=0, irest=1, ntx=5,
  dt=0.002, nstlim=5000000,
  ntc=2, ntf=2, cut=10.0,
  ntt=3, gamma_ln=1.0, temp0=300.0, ig=-1,
  ntb=2, ntp=1, barostat=2, pres0=1.0, taup=2.0,
  ntpr=5000, ntwx=5000, ntwr=500000,
  ntxo=2, ioutfm=1, iwrap=1,
  ntr=0,
 /
EOF
```

### Step 1.5: Verify mdin Created
```bash
cat mdin_templates/prod_mc_gpu_2fs.in
# Should show production parameters with ntr=0
```

### Step 1.6: Submit Equilibration Job
```bash
cd slurm
sbatch run_eq_cpu_mc.sbatch
```

### Step 1.7: Note Job ID
```bash
# Record the job ID returned (e.g., "Submitted batch job 19800001")
# Save this: JOB_ID_EQ=<number>
```

### Step 1.8: Monitor Job Progress
```bash
# Check queue status
squeue -u $USER

# Check job output (replace JOBID)
tail -f eq_cpu_mc.<JOBID>.out

# Or check mdinfo periodically
watch -n 60 'cat ../eq1.cpu.mdinfo 2>/dev/null | grep -A2 "Current Timing"'
```

### Step 1.9: Expected Timeline
- eq1 completion: ~4 hours (101000 remaining steps at ~0.6 ns/day)
- eq2 completion: ~6-7 hours (250000 steps)
- Total: ~10-11 hours

### Step 1.10: Verify Completion (Before Leaving Day 1)
```bash
# After job completes, verify outputs exist
ls -la ../*.rst7
# Must have:
#   heat.cpu.rst7
#   eq1.cpu.rst7  (now complete, should be newer timestamp)
#   eq2.cpu.rst7  (NEW - this is critical)

# Check eq2 completed successfully
tail -20 ../eq2.cpu.out
# Should end with timing info, no errors

# Check final mdinfo
cat ../eq2.cpu.mdinfo
# Should show 250000/250000 (100.0%)
```

---

## Day 2: Production Simulation

### Step 2.1: SSH and Navigate
```bash
ssh <gatorlink>@hpg.rc.ufl.edu
cd /blue/roitberg/john.aitken/oxdc-md-fall25/systems/BiOx+2
```

### Step 2.2: Confirm eq2 Completed
```bash
# Critical check - do NOT proceed without this file
ls -la eq2.cpu.rst7
# Must exist and be ~3 MB

# Verify no errors in eq2
grep -i "error\|fail\|warn" eq2.cpu.out | head -20
# Should return nothing or only benign warnings
```

### Step 2.3: Submit Production Job
```bash
cd slurm
sbatch run_prod_gpu_mc.sbatch
```

### Step 2.4: Note Job ID
```bash
# Record: JOB_ID_PROD=<number>
```

### Step 2.5: Monitor Production
```bash
# Check queue
squeue -u $USER

# Monitor output
tail -f prod_gpu_mc.<JOBID>.out

# Check progress via mdinfo
watch -n 300 'cat ../prod.mdinfo 2>/dev/null | grep -A2 "Current Timing"'
```

### Step 2.6: Expected Timeline
- 10 ns production: ~6-8 hours on GPU
- Should complete within 12-hour walltime

### Step 2.7: Verify Production Completion
```bash
ls -la ../prod.*
# Should have:
#   prod.out      (output log)
#   prod.rst7     (final restart)
#   prod.nc       (trajectory, ~500 MB - 1 GB)
#   prod.mdinfo   (timing info)

# Check trajectory size (should be substantial)
du -h ../prod.nc
# Expected: 500 MB - 1 GB for 10 ns

# Verify completion
tail -20 ../prod.out
# Should show final energies and timing
```

### Step 2.8: Quick Sanity Check with cpptraj
```bash
cd ..
module load amber/25

# Quick RMSD check
cpptraj -p 5vg3_solv.prmtop << 'EOF'
trajin prod.nc
autoimage
rms first :1-357@CA out rmsd_quick.dat
run
quit
EOF

# Check RMSD values are reasonable (< 5 Å typically)
tail -20 rmsd_quick.dat
```

---

## Day 3: Analysis

### Step 3.1: SSH and Navigate
```bash
ssh <gatorlink>@hpg.rc.ufl.edu
cd /blue/roitberg/john.aitken/oxdc-md-fall25/systems/BiOx+2
```

### Step 3.2: Load Modules
```bash
module load amber/25
```

### Step 3.3: Create Analysis Output Directory
```bash
mkdir -p analysis_output
```

### Step 3.4: Run RMSD/RMSF Analysis
```bash
cpptraj -p 5vg3_solv.prmtop -i ../../../analysis/cpptraj/rmsd_rmsf.in
# Note: May need to edit paths in the .in file first

# Or run directly:
cpptraj -p 5vg3_solv.prmtop << 'EOF'
trajin prod.nc
autoimage
rms first :1-357@CA out analysis_output/rmsd_backbone.dat
atomicfluct :1-357@CA out analysis_output/rmsf_byres.dat byres
run
quit
EOF
```

### Step 3.5: Run Mn Coordination Analysis
```bash
cpptraj -p 5vg3_solv.prmtop << 'EOF'
trajin prod.nc
autoimage

# Mn-His distances (adjust residue numbers for BiOx+2)
distance Mn1_His95  :M1@MN :95@NE2  out analysis_output/mn_his95.dat
distance Mn1_His97  :M1@MN :97@NE2  out analysis_output/mn_his97.dat
distance Mn1_His140 :M1@MN :140@NE2 out analysis_output/mn_his140.dat
distance Mn1_Glu101 :M1@MN :101@OE1 out analysis_output/mn_glu101.dat

# Mn-Oxalate distances
distance Mn1_Ox_O1 :M1@MN :OXL@O1 out analysis_output/mn_ox_o1.dat
distance Mn1_Ox_O2 :M1@MN :OXL@O2 out analysis_output/mn_ox_o2.dat

run
quit
EOF
```

### Step 3.6: Generate Summary Statistics
```bash
cd analysis_output

# RMSD summary
echo "=== RMSD Statistics ==="
awk 'NR>1 {sum+=$2; sumsq+=$2*$2; n++} END {
  mean=sum/n; std=sqrt(sumsq/n - mean*mean);
  print "Mean RMSD:", mean, "Å"; print "Std Dev:", std, "Å"
}' rmsd_backbone.dat

# Mn coordination summary
echo "=== Mn-Ligand Distances ==="
for f in mn_*.dat; do
  name=$(basename $f .dat)
  awk -v n="$name" 'NR>1 {sum+=$2; n_++} END {print n, "mean:", sum/n_, "Å"}' $f
done
```

### Step 3.7: Check for Stability Issues
```bash
# Look for any distance spikes (> 3.5 Å for Mn-ligand)
echo "=== Checking for Coordination Breaks ==="
for f in mn_*.dat; do
  breaks=$(awk 'NR>1 && $2 > 3.5 {count++} END {print count+0}' $f)
  echo "$(basename $f): $breaks frames with d > 3.5 Å"
done
```

### Step 3.8: Copy Results to Local Machine
```bash
# On local machine:
scp -r <gatorlink>@hpg.rc.ufl.edu:/blue/roitberg/john.aitken/oxdc-md-fall25/systems/BiOx+2/analysis_output ./
```

### Step 3.9: Backup Trajectory
```bash
# On HiPerGator - copy to orange storage if available
cp prod.nc /orange/roitberg/john.aitken/oxdc_backups/BiOx+2_prod_10ns.nc 2>/dev/null || echo "Orange not available"
```

---

## Troubleshooting Reference

### If eq1/eq2 Job Fails
```bash
# Check error log
cat eq_cpu_mc.<JOBID>.err

# Common issues:
# 1. "vlimit exceeded" - force field issue, may need softer params
# 2. "SHAKE failure" - reduce timestep or check coordinates
# 3. "walltime exceeded" - increase #SBATCH --time
```

### If Production Job Fails
```bash
# Check error log
cat prod_gpu_mc.<JOBID>.err

# Common issues:
# 1. "GPU not available" - partition full, resubmit
# 2. "CUDA error" - GPU memory issue, reduce system size or check coords
```

### If Analysis Shows Problems
```bash
# High RMSD (> 5 Å): System may have unfolded
# Check trajectory visually in VMD

# Broken Mn coordination: Check if restraints were properly removed
# Verify prod mdin has ntr=0
```

---

## Checklist Summary

### Day 1 Deliverables
- [ ] eq1.cpu.rst7 complete (new timestamp)
- [ ] eq2.cpu.rst7 exists (~3 MB)
- [ ] eq2.cpu.out shows successful completion

### Day 2 Deliverables
- [ ] prod.nc exists (500 MB - 1 GB)
- [ ] prod.rst7 exists
- [ ] prod.out shows successful completion
- [ ] Quick RMSD check passes

### Day 3 Deliverables
- [ ] rmsd_backbone.dat generated
- [ ] rmsf_byres.dat generated
- [ ] Mn coordination distances analyzed
- [ ] No coordination breaks detected
- [ ] Results copied to local machine

---

## File Manifest (Expected End State)

```
BiOx+2/
├── 5vg3_solv.prmtop          # topology (existing)
├── 5vg3_solv.inpcrd          # initial coords (existing)
├── heat.cpu.rst7             # heating output (existing)
├── eq1.cpu.rst7              # eq1 output (Day 1)
├── eq2.cpu.rst7              # eq2 output (Day 1)
├── prod.nc                   # production trajectory (Day 2)
├── prod.rst7                 # production restart (Day 2)
├── prod.out                  # production log (Day 2)
├── analysis_output/          # (Day 3)
│   ├── rmsd_backbone.dat
│   ├── rmsf_byres.dat
│   ├── mn_his95.dat
│   ├── mn_his97.dat
│   ├── mn_his140.dat
│   ├── mn_glu101.dat
│   ├── mn_ox_o1.dat
│   └── mn_ox_o2.dat
└── mdin_templates/
    └── prod_mc_gpu_2fs.in    # (Step 1.4)
```
