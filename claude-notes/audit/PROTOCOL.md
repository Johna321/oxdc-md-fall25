# Equilibration Protocol Audit

## Current Pipeline Overview

```
[Initial Coords] → [Heat NVT 50ps] → [EQ1 NPT 250ps] → [EQ2 NPT 250ps] → [EQ3 NPT 200ps] → [Production]
     ↓                  ↓                  ↓                  ↓                  ↓
  5vg3_solv.inpcrd   No restraints    2.0 kcal/mol·Å²   0.5 kcal/mol·Å²    No restraints
                      0→300 K          Berendsen→MC       MC barostat         MTTK-ready
                      1 fs              1 fs               1 fs                2 fs
```

---

## Stage-by-Stage Analysis

### Stage 1: Heating (heat_nvt_1fs.in)

**Current Settings:**
```
imin=0, irest=0, ntx=1,
nstlim=50000, dt=0.001,        # 50 ps, 1 fs timestep
ntc=2, ntf=2,                  # SHAKE H-bonds
ntb=1,                         # NVT (constant volume)
ntt=3, gamma_ln=2.0,           # Langevin thermostat
tempi=0.0, temp0=300.0,        # 0→300 K ramp
ntr=0                          # NO RESTRAINTS
```

**Critique:**

| Aspect | Current | Recommended | Risk |
|--------|---------|-------------|------|
| Duration | 50 ps | 50-100 ps | Adequate |
| Timestep | 1 fs | 1 fs (or 0.5 fs early) | OK |
| Ensemble | NVT | NVT | Correct |
| Restraints | **NONE** | 5-10 kcal/mol·Å² | **HIGH RISK** |
| Ramp rate | 6 K/ps | 3-6 K/ps | Borderline |

**Issue:** No restraints during heating allows:
- Metal coordination sphere to distort
- Unnatural protein unfolding
- Solvent penetration into hydrophobic core

**Recommendation:** Add heavy-atom restraints (5.0 kcal/mol·Å²) with system-specific mask.

---

### Stage 2: EQ1 (eq1_mc_cpu_1fs.in)

**Current Settings:**
```
nstlim=250000, dt=0.001,       # 250 ps, 1 fs
ntb=2, ntp=1, barostat=2,      # NPT, isotropic, MC barostat
pres0=1.0,                     # 1 atm
ntt=3, gamma_ln=2.0,           # Langevin
ntr=1, restraint_wt=2.0,       # Restraints ON
restraintmask='(!:WAT,Na+,Cl-)&!@H='  # GENERIC (problematic)
```

**Critique:**

| Aspect | Current | Recommended | Issue |
|--------|---------|-------------|-------|
| Duration | 250 ps | 200-500 ps | Adequate |
| Barostat | MC | MC or Berendsen | Good for equilibration |
| Restraint weight | 2.0 | 2.0-5.0 | OK |
| Restraint mask | Generic | System-specific | **CRITICAL** |

**Issue:** Restraint mask doesn't exclude Mn ions or coordinating residues properly.

---

### Stage 3: EQ2 (eq2_mc_cpu_1fs.in)

**Current Settings:**
```
restraint_wt=0.5               # Reduced from 2.0
# Otherwise same as EQ1
```

**Critique:**

| Aspect | Current | Recommended | Issue |
|--------|---------|-------------|-------|
| Restraint reduction | 2.0→0.5 | 2.0→1.0→0.5 | Abrupt |
| Duration | 250 ps | 250 ps per stage | OK if staged |

**Recommendation:** Insert intermediate stages with gradual restraint release.

---

### Stage 4: EQ3 (eq3a_mttk.mdin)

**Current Settings:**
```
nstlim=100000, dt=0.002,       # 200 ps, 2 fs
ntp=3, barostat=2,             # Anisotropic, MC
taup=3.0,                      # Pressure relaxation
gamma_ln=1.0,                  # Reduced friction
ntr=0                          # No restraints
cut=10.0                       # Explicit cutoff
```

**Critique:**

| Aspect | Current | Recommended | Issue |
|--------|---------|-------------|-------|
| Duration | 200 ps | 200-500 ps | Borderline |
| Timestep | 2 fs | 2 fs | Good for production |
| Pressure coupling | Anisotropic | Anisotropic | Good |
| Cutoff | 10 Å | 10-12 Å | Standard |
| Friction | 1.0 ps⁻¹ | 1.0-2.0 ps⁻¹ | OK |

**Issue:** This is production-ready but short. Should be longer for convergence check.

---

## Equilibration Criteria Assessment

### Current QC Gates (from RUN_PLAN.md)

1. **Density:** 0.99 ± 0.02 g/cc (last 20 ps)
2. **Overflow:** No '*****' lines in output
3. **CA-RMSD:** ≤ 2.0 Å at eq1d & eq2b

**Critique:**

| Gate | Status | Recommendation |
|------|--------|----------------|
| Density | Good metric | Add pressure stability check |
| Overflow | Good metric | Early termination if detected |
| CA-RMSD | Good metric | Add Mn-ligand distance check |
| **MISSING** | - | Temperature stability (±2 K) |
| **MISSING** | - | Total energy plateau |
| **MISSING** | - | Box volume stability |
| **MISSING** | - | Mn coordination number check |

---

## Mn-Specific Considerations

### Current Approach

- MCPB.py bonded model (appropriate)
- No explicit Mn-ligand distance restraints
- Mn included in general heavy-atom restraints (when mask correct)

### Recommended Additions

1. **Mn coordination check:**
```bash
# After each eq stage, verify Mn-ligand distances
cpptraj <<EOF
parm 5vg3_solv.prmtop
trajin eq1.cpu.rst7
distance d1 @6032 @1519   # Mn-His NE2
distance d2 @6032 @1560   # Mn-His NE2
# etc.
run
EOF
```

2. **Optional: NMR-style distance restraints**
```
# In mdin file, add:
nmropt=1,
# In separate file:
&rst iat=6032,1519, r1=1.8, r2=2.1, r3=2.4, r4=2.7, rk2=10.0, rk3=10.0 /
```

---

## Barostat Choice Analysis

| Barostat | EQ Phase | Production | Notes |
|----------|----------|------------|-------|
| Berendsen | ✓ (eq1-2) | ✗ | Fast equilibration, wrong ensemble |
| MC | ✓ | ✓ | Correct NPT, GPU compatible |
| MTTK | ✓ | ✓ | Correct NPT, CPU only |

**Current approach is reasonable:** MC barostat throughout works for both eq and production on GPU.

---

## Timestep Analysis

| Stage | Current | Limit | Safety Margin |
|-------|---------|-------|---------------|
| Heat | 1 fs | 2 fs (with SHAKE) | Good |
| EQ1-2 | 1 fs | 2 fs | Conservative (good for metal sites) |
| EQ3+ | 2 fs | 2 fs | At limit |

**Note:** 1 fs during equilibration is conservative and appropriate for metalloenzymes. The vlimit warnings suggest issues beyond timestep.

---

## Recommended Protocol Modifications

### Option A: Minimal Changes (Quick Fix)

1. Fix restraint masks in all mdin files
2. Add `ntr=1, restraint_wt=5.0` to heating
3. Re-run from heat stage

### Option B: Thorough Protocol (Recommended)

```
[Minimization] → [Heat NVT] → [EQ1a] → [EQ1b] → [EQ1c] → [EQ2] → [EQ3] → [Production]
    5000 cyc     50 ps 1fs    100ps    100ps    100ps    250ps   500ps    100+ ns
    restrained   5.0 kcal    5.0      2.0      1.0      0.5     0.0      0.0
                 0→300K
```

### Option C: Mn-Paranoid Protocol (If Instability Persists)

Add explicit Mn-ligand harmonic restraints throughout equilibration:
```
# In addition to heavy-atom restraints
&rst iat=-1,-1, restraint on Mn-O distances
```

---

## Summary: Root Cause Analysis

**Why are simulations unstable?**

| Factor | Evidence | Severity |
|--------|----------|----------|
| Wrong restraint mask | Mn being restrained, then released | **HIGH** |
| No heating restraints | System destabilizes early | **HIGH** |
| Abrupt restraint release | 2.0→0.5 is steep | MEDIUM |
| Mn SHORT flag (BiOx+2) | 1.306 Å bond indicates strain | MEDIUM |
| SPARSE coordination | CN=4 at Site 2 | MEDIUM |

**Recommended priority:**
1. Fix restraint masks (immediate)
2. Add heating restraints (immediate)
3. Re-equilibrate all systems
4. Check Mn parameters against QM (if problems persist)
