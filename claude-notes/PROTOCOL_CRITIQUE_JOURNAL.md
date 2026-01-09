# Critical Review Journal: 3-Day Plan Protocol Analysis

*A Socratic examination of my proposed 3-day implementation plan against established practices and existing infrastructure.*

---

## Question 1: Is Module Loading on Login Nodes Viable?

### My Original Proposal
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
```

### Evidence from Existing Infrastructure

**Exhibit A: run_eq_cpu_mc.sbatch (lines 19-22)**
```bash
module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25   # cpu build
```
All module loading occurs **inside** the SLURM script, not on login nodes.

**Exhibit B: run_prod_gpu_mc.sbatch (lines 17-21)**
```bash
module purge
module load cuda/12.8.1
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25
```
Same pattern—modules loaded within the compute job.

### Technical Analysis

| Location | Module Loading | Consequences |
|----------|---------------|--------------|
| Login Node | ⚠️ Questionable | May work for simple commands (ls, cat); cluster policy may prohibit compute-intensive tools |
| SLURM Job | ✓ Correct | Guaranteed correct environment on compute nodes |
| Interactive Session | ✓ Acceptable | `srun --pty bash` provides compute resources |

### HPC Best Practices

1. **Login nodes are for**: File management, editing, job submission
2. **Login nodes are NOT for**: Running AMBER, cpptraj, Python analysis
3. **UFHPC Policy**: Heavy computation on login nodes can result in job termination and warnings

### Counter-Argument to My Proposal

**Claim I Made**: "Run cpptraj on login node for quick analysis"
```bash
# From my Block 3.2
module load amber/25
cpptraj -i cpptraj/run_analysis.in
```

**Problems**:
1. cpptraj on large trajectories is CPU-intensive
2. May violate cluster fair-use policies
3. Could be killed mid-execution

### Verdict: PARTIALLY INCORRECT ❌

**Revised Recommendation**: All module loading and AMBER/cpptraj execution should occur within:
1. SLURM batch jobs (preferred)
2. Interactive sessions via `srun --pty --mem=4gb --time=01:00:00 bash`

**Corrected Block 3.2**:
```bash
# Submit analysis as batch job, OR use interactive session:
srun --partition=hpg-milan --account=ax --qos=ax \
     --mem=4gb --time=01:00:00 --pty bash

# Then inside interactive session:
module load amber/25
cd /blue/ax/john.aitken/oxdc-md-fall25/analysis
cpptraj -i cpptraj/run_analysis.in
```

---

## Question 2: Should We Run EQ2 Before Production?

### My Original Proposal

In some blocks, I suggested going directly from eq1 to production, or was ambiguous about the necessity of eq2.

### Evidence from Existing Infrastructure

**Exhibit A: run_eq_cpu_mc.sbatch (lines 72-77)**
```bash
# eq1 (NPT Monte Carlo, 1 fs) — reference = heat start if ntr=1
run_stage eq1_mc_cpu_1fs.in heat.cpu.rst7 \
          eq1.cpu eq1.cpu.rst7 eq1.cpu.nc eq1.cpu.mdinfo

# eq2 (NPT Monte Carlo, 1 fs) — reference = eq1 start if ntr=1
run_stage eq2_mc_cpu_1fs.in eq1.cpu.rst7 \
          eq2.cpu eq2.cpu.rst7 eq2.cpu.nc eq2.cpu.mdinfo
```
**Clear sequence**: heat → eq1 → eq2

**Exhibit B: run_prod_gpu_mc.sbatch (line 24)**
```bash
START=eq2.cpu.rst7
```
**Production explicitly requires eq2.cpu.rst7 as input.**

**Exhibit C: Current BiOx+2 State**
```
$ ls -la /home/user/oxdc-md-fall25/systems/BiOx+2/*.rst7
heat.cpu.rst7   ✓ exists (50 ps heating complete)
eq1.cpu.rst7    ✓ exists (148/250 ps, ~60% complete)
eq2.cpu.rst7    ✗ MISSING
```

### Equilibration Protocol Analysis

| Stage | Purpose | Duration | Restraints |
|-------|---------|----------|------------|
| Heat | Gradual temperature increase | 50 ps | None (ntr=0) |
| EQ1 | Density equilibration with restraints | 250 ps | Strong (wt=2.0) |
| EQ2 | Density equilibration, relaxing restraints | 250 ps | Reduced (wt=0.5) |
| Production | Data collection | >10 ns | None (ntr=0) |

### Why EQ2 Is Essential

1. **Restraint Relaxation**: EQ1 uses restraint_wt=2.0, EQ2 uses 0.5
   - Going 2.0 → 0.0 directly can cause structural distortions
   - Gradual relaxation prevents energy spikes

2. **Density Stabilization**: Additional 250 ps ensures:
   - Proper water equilibration around solute
   - Stable pressure response to barostat
   - Mn coordination sphere settlement

3. **Literature Standard**: Most metalloenzyme MD protocols use 2-3 NPT equilibration stages

### Counter-Argument Analysis

**Potential objection**: "BiOx+2 is already stable at eq1—why not skip eq2?"

**Rebuttal**:
1. eq1 only 60% complete (148/250 ps)
2. Even if complete, restraint_wt=2.0 is still active
3. Production with active restraints would be scientifically invalid
4. The existing protocol was designed for a reason—deviating without justification is risky

### Verdict: YES, EQ2 IS REQUIRED ✓

**Critical Action**: Before ANY production, BiOx+2 needs:
1. Complete eq1 (remaining ~100 ps)
2. Run full eq2 (250 ps)
3. Verify eq2.cpu.rst7 exists before production

---

## Question 3: My Protocol vs. Existing Templates

### Comparison Table

| Parameter | My Proposed Protocol | Existing Protocol | Assessment |
|-----------|---------------------|-------------------|------------|
| **Heat ntr** | ntr=1, wt=5.0 | ntr=0 (no restraints) | Existing is simpler, but mine may be safer for metals |
| **EQ1 restraint mask** | System-specific (complex) | `(!:WAT,Na+,Cl-)&!@H=` | Existing is more generic and portable |
| **EQ2 included** | Sometimes omitted | Always included | Existing is correct |
| **Timestep** | 2 fs proposed for prod | 1 fs in equilibration | Both correct (SHAKE allows 2 fs) |
| **Barostat** | MC (barostat=2) | MC (barostat=2) | Identical ✓ |

### Detailed Analysis

#### A. Restraint Mask Comparison

**My Proposed Masks** (system-specific):
```bash
# BiOx+2
restraintmask='(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H='
# 1Wat+2
restraintmask='(!:WAT,WT1,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H='
```

**Existing Mask** (generic):
```bash
restraintmask='(!:WAT,Na+,Cl-)&!@H='
```

**Analysis**:
- My masks explicitly exclude metal-related residues (MN1, MN2, GU, HD)
- This was based on my (now-corrected) hypothesis about restraint masks causing instability
- The existing mask is simpler and works for BiOx+2 (only 1 vlimit in 148 ps)

**Evidence that existing mask works**:
```
BiOx+2 eq1: 148000 steps, vlimit count = 1, density = 1.01 g/cc
```

**Verdict on masks**: The existing generic mask is **adequate**. My system-specific masks were over-engineered based on an incorrect hypothesis.

#### B. Heat Protocol Comparison

**My Proposed Heat**:
```bash
ntr=1, restraint_wt=5.0
restraintmask='...'
```

**Existing Heat** (heat_nvt_1fs.in):
```bash
imin=0, irest=0, ntx=1,
nstlim=50000, dt=0.001,
ntc=2, ntf=2, ntb=1,
ntt=3, gamma_ln=2.0, tempi=0.0, temp0=300.0,
# NO ntr - no restraints!
```

**Analysis**:
- Existing heat uses NO restraints during heating
- This is actually riskier for metalloenzymes where coordination geometry matters
- However, it worked for BiOx+2

**Trade-off**:
| Approach | Risk | Benefit |
|----------|------|---------|
| No restraints (existing) | Coordination may distort | Simpler, fewer parameters |
| With restraints (mine) | Over-restraint could cause tension | Metal site preserved |

**Verdict**: For metalloenzymes, restraints during heating are **recommended** by literature, but the existing protocol works for this specific system.

#### C. Missing Production mdin

**Critical Finding**: The SLURM script references `mdin_templates/prod_mc_gpu_2fs.in` but this file doesn't exist in the repository.

```bash
$ find /home/user/oxdc-md-fall25 -name "*prod*2fs*"
# No results
```

**Implication**: Production cannot proceed until this file is created.

**My prod_template.in** (from claude-notes/production/):
```bash
Production NPT (2 fs) - 10 ns segment
 &cntrl
  imin=0, ntx=5, irest=1,
  ntb=2, ntp=1, barostat=2, pres0=1.0, taup=2.0,
  ntt=3, gamma_ln=1.0, temp0=300.0,
  ntc=2, ntf=2, dt=0.002,
  nstlim=5000000,
  cut=10.0, iwrap=1,
  ntpr=5000, ntwx=5000, ntwr=50000,
  ntxo=2, ioutfm=1, ntr=0
 /
```

This is reasonable and should be placed in `mdin_templates/prod_mc_gpu_2fs.in`.

---

## Summary of Corrections Needed

### Must Fix
1. **All analysis commands**: Wrap in SLURM jobs or interactive sessions
2. **Complete eq1**: BiOx+2 eq1 is only 60% done
3. **Run eq2**: Required before production
4. **Create production mdin**: Copy prod_template.in to correct location

### Acceptable As-Is
1. **Production parameters**: My prod_template.in is reasonable
2. **Module versions**: Matching existing scripts
3. **SLURM parameters**: Partition, account, QOS correct

### Consider But Not Critical
1. **Restraints during heating**: Could add for extra safety with metals
2. **System-specific masks**: Not needed if generic mask works

---

## Revised Day 1 Critical Path

```bash
# 1. Login and create interactive session for any analysis
ssh john.aitken@hpg.rc.ufl.edu
srun --partition=hpg-milan --account=ax --qos=ax \
     --mem=4gb --time=02:00:00 --pty bash

# 2. Check BiOx+2 current state
cd /blue/ax/john.aitken/oxdc-md-fall25/systems/BiOx+2
ls -la *.rst7
# Expected: heat.cpu.rst7 ✓, eq1.cpu.rst7 ✓, eq2.cpu.rst7 ✗

# 3. If eq1 incomplete, re-run full equilibration
# (The run_eq_cpu_mc.sbatch will restart cleanly)
sbatch slurm/run_eq_cpu_mc.sbatch

# 4. Wait for eq2.cpu.rst7 to exist
# 5. Create production mdin if missing
cp /path/to/prod_template.in mdin_templates/prod_mc_gpu_2fs.in

# 6. THEN submit production
sbatch slurm/run_prod_gpu_mc.sbatch
```

---

## Confidence Assessment

| Original Claim | Correction Needed | Confidence in Correction |
|----------------|-------------------|-------------------------|
| Module load on login | Yes—use jobs/interactive | **High** (standard HPC practice) |
| Skip eq2 | No—eq2 required | **Very High** (verified from existing scripts) |
| System-specific masks | Not needed | **Medium** (generic works but specific may be safer) |
| Production ready | No—eq2 missing | **Very High** (verified file doesn't exist) |

---

## Key Takeaway

> **My original 3-day plan had the right ideas but skipped critical steps.** The existing infrastructure has a well-designed protocol:
>
> `heat → eq1 → eq2 → production`
>
> BiOx+2 is at eq1 (60% complete). The correct path is:
> 1. Complete eq1 + eq2 using existing run_eq_cpu_mc.sbatch
> 2. Create missing prod mdin file
> 3. Submit production using existing run_prod_gpu_mc.sbatch
>
> No reinvention needed—just complete the existing protocol.
