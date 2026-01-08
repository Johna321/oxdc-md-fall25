# Parameter Consistency Audit

## Executive Summary

**CRITICAL FINDING:** Restraint masks in mdin templates are INCONSISTENT with system-specific requirements. This may explain simulation instabilities.

---

## 1. Restraint Mask Discrepancy

### Templates vs System-Specific Masks

| System | Template Mask | System-Specific Mask | Mismatch |
|--------|---------------|---------------------|----------|
| 1Wat+2 | `(!:WAT,Na+,Cl-)&!@H=` | `(!:WAT,WT1,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=` | **YES** |
| 1Wat+3 | `(!:WAT,Na+,Cl-)&!@H=` | `(!:WAT,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=` | **YES** |
| empty+2 | `(!:WAT,Na+,Cl-)&!@H=` | `(!:WAT,WTR,Cl-,MN1,MN2,GU,HD)&!@H=` | **YES** |
| BiOx+2 | `(!:WAT,Na+,Cl-)&!@H=` | `(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H=` | **YES** |

### Impact Analysis

**With template mask `(!:WAT,Na+,Cl-)&!@H=`:**

| Residue | In Mask? | Effect |
|---------|----------|--------|
| MN1/MN2 | **MISSING** | Mn ions RESTRAINED during equilibration |
| GU (Glutamate analogs) | **MISSING** | Mn-coordinating Glu RESTRAINED |
| HD (Histidine variants) | **MISSING** | Mn-coordinating His RESTRAINED |
| OX (Oxalate) | **MISSING** | Substrate analog RESTRAINED |
| Na+ | **INCLUDED** | Nonexistent in systems (Cl- used) |
| WT/WTR (Waters) | **MISSING** | Coordinating waters RESTRAINED |

### Consequence

**Metal coordination sphere is being rigidly restrained** when it should be allowed to equilibrate. This:
1. Prevents natural relaxation of MCPB.py parameters
2. Creates strain that releases suddenly when restraints decrease
3. Likely cause of vlimit exceeded warnings and crashes

---

## 2. mdin Parameter Comparison

### Heating Stage (heat_nvt_1fs.in)

| Parameter | Value | Status |
|-----------|-------|--------|
| `imin` | 0 | ✓ Correct (MD run) |
| `irest` | 0 | ✓ Correct (new run) |
| `ntx` | 1 | ✓ Correct (coords only) |
| `nstlim` | 50000 | ✓ 50 ps |
| `dt` | 0.001 | ✓ 1 fs |
| `ntc` | 2 | ✓ SHAKE H-bonds |
| `ntf` | 2 | ✓ Omit H-bond forces |
| `ntb` | 1 | ✓ NVT |
| `ntt` | 3 | ✓ Langevin |
| `gamma_ln` | 2.0 | ✓ Standard collision freq |
| `tempi` | 0.0 | ✓ Start cold |
| `temp0` | 300.0 | ✓ Target temp |
| `ntr` | 0 | **CONCERN** - No restraints during heating |

**Issue:** Heating without restraints on a metalloenzyme can cause coordination sphere disruption. Literature recommends restraining heavy atoms during heating.

### Equilibration Stage 1 (eq1_mc_cpu_1fs.in)

| Parameter | Value | Status |
|-----------|-------|--------|
| `nstlim` | 250000 | ✓ 250 ps |
| `dt` | 0.001 | ✓ 1 fs |
| `ntb` | 2 | ✓ NPT |
| `ntp` | 1 | ✓ Isotropic scaling |
| `barostat` | 2 | ✓ Monte Carlo barostat |
| `pres0` | 1.0 | ✓ 1 atm |
| `ntr` | 1 | ✓ Restraints on |
| `restraint_wt` | 2.0 | ✓ Moderate restraints |
| `restraintmask` | `(!:WAT,Na+,Cl-)&!@H=` | **WRONG** (see above) |

### Equilibration Stage 2 (eq2_mc_cpu_1fs.in)

| Parameter | Value | Status |
|-----------|-------|--------|
| `restraint_wt` | 0.5 | ✓ Reduced restraints |
| Other | Same as eq1 | Same issues |

### Production-Ready (eq3a_mttk.mdin)

| Parameter | Value | Status |
|-----------|-------|--------|
| `nstlim` | 100000 | Only 200 ps |
| `dt` | 0.002 | ✓ 2 fs |
| `ntp` | 3 | Anisotropic scaling |
| `barostat` | 2 | ✓ MC barostat |
| `taup` | 3.0 | ✓ Pressure coupling |
| `gamma_ln` | 1.0 | Reduced friction |
| `cut` | 10.0 | ✓ Explicit cutoff |
| `ntr` | 0 | ✓ No restraints |

**Note:** eq3a_mttk is not true production - only 200 ps. Need longer production input.

---

## 3. Cross-System Parameter Consistency

### Consistent Parameters (Good)

All systems share:
- Force field: ff14SB (implied from MCPB.py workflow)
- Water model: TIP3P (from topology analysis)
- Timestep: 1 fs (eq), 2 fs (prod)
- Thermostat: Langevin
- Barostat: Monte Carlo

### Inconsistent Parameters (Investigate)

| Parameter | 1Wat+2 | 1Wat+3 | empty+2 | BiOx+2 |
|-----------|--------|--------|---------|--------|
| Mn residue names | MN1, MN2 | MN1, MN2 | MN1, MN2 | MN1, MN |
| Water residue names | WAT, WT1, WTR | WAT, WTR | WAT, WTR | WAT |
| Ion types | Cl-, MN1, MN2 | Cl-, MN1, MN2 | Cl-, MN1, MN2 | Cl- |

**Note:** BiOx+2 has different Mn naming (`MN1, MN` vs `MN1, MN2`).

---

## 4. Equilibration Strategy Consistency

| System | Strategy | Mn Flags | Current Stage |
|--------|----------|----------|---------------|
| 1Wat+2 | gpu-chunked | None | eq1a (vlimit warnings) |
| 1Wat+3 | gpu-chunked | None | eq1b (vlimit warnings) |
| empty+2 | cpu-bridge | SPARSE (6030) | eq1b (**CRASHED**) |
| BiOx+2 | cpu-bridge | SHORT, SPARSE | eq1 (~145 ps) |

### Strategy Rationale

- **gpu-chunked:** For well-behaved Mn sites, direct GPU MD
- **cpu-bridge-then-gpu:** For flagged Mn sites, use CPU sander first (more stable) then switch to GPU

**Observation:** Even gpu-chunked systems show vlimit warnings, suggesting issues beyond Mn site stability.

---

## 5. Specific Discrepancies Requiring Action

### Priority 1: Restraint Mask Correction

Create system-specific mdin files with correct masks:

```bash
# BiOx+2 example
restraintmask='(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H=',
```

### Priority 2: Add Heating Restraints

Modify `heat_nvt_1fs.in` to include restraints:
```
ntr=1, restraint_wt=5.0,
restraintmask='<system-specific>',
```

### Priority 3: Staged Restraint Release

Current: eq1 (2.0) → eq2 (0.5) → eq3 (0.0)

Recommended: eq1a (5.0) → eq1b (2.0) → eq1c (1.0) → eq1d (0.5) → eq2 (0.1) → eq3 (0.0)

### Priority 4: Mn-specific Restraints

Consider adding explicit Mn-ligand distance restraints using NMR restraints or AMBER's `nmropt` for Mn coordination geometry.

---

## 6. Verification Commands

```bash
# Check what atoms are selected by a mask
cpptraj -p 5vg3_solv.prmtop <<EOF
parm 5vg3_solv.prmtop
select '(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H='
quit
EOF

# Verify Mn atoms are NOT selected (should be excluded from restraints)
cpptraj -p 5vg3_solv.prmtop <<EOF
parm 5vg3_solv.prmtop
select @MN
select '(!:WAT,Na+,Cl-)&!@H=' | @MN
quit
EOF
```

---

## Recommendations

1. **IMMEDIATE:** Fix restraint masks in all mdin files
2. **IMMEDIATE:** Re-equilibrate systems from heat stage with corrected protocol
3. **SHORT-TERM:** Create system-specific mdin template copies
4. **SHORT-TERM:** Add heating restraints
5. **MEDIUM-TERM:** Consider staged equilibration (eq1a-d approach)
6. **LONG-TERM:** Validate Mn parameters against QM reference
