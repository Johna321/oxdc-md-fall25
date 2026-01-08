# Production Readiness Assessment

## System Status Summary

| System | Heat | EQ1 | EQ2 | EQ3 | vlimit Warnings | Status |
|--------|------|-----|-----|-----|-----------------|--------|
| **BiOx+2** | ✓ | ~145 ps | ✗ | ✗ | **0** | **MOST READY** |
| 1Wat+2 | ✓ | partial | partial | ✗ | 18,358 | PROBLEMATIC |
| 1Wat+3 | ✓ | partial | ✗ | ✗ | 9,947 | PROBLEMATIC |
| empty+2 | ✓ | partial | partial | ✗ | 17,148 | **CRASHED** |
| empty+3 | ? | ? | ? | ? | ? | UNKNOWN |
| Nterm_only | nested | nested | ? | ? | ? | SEPARATE PROJECT |

---

## Detailed Analysis

### BiOx+2 — PRIORITY SYSTEM

**Status:** Most promising candidate for production

**Evidence:**
- Zero vlimit warnings through heat and eq1
- Density stable at 1.01-1.02 g/cc (within 0.99±0.02 target)
- 145+ ps of eq1 completed

**Current stage:** eq1 in progress (~145 ps of 250 ps)

**Next steps:**
1. Complete eq1 (remaining ~105 ps)
2. Run eq2 (250 ps, 0.5 kcal restraints)
3. Run eq3 (200+ ps, no restraints)
4. Begin production

**Estimated time to production:**
- eq1 completion: ~1 hour (CPU)
- eq2: ~2 hours (CPU)
- eq3: ~1 hour (GPU)
- **Total: ~4 hours**

**Blocking issues:**
- Restraint mask is wrong (using generic template)
- Should fix mask before continuing

---

### 1Wat+2 — SIGNIFICANT ISSUES

**Status:** High vlimit warnings indicate instability

**Evidence:**
- 18,358 vlimit exceeded in eq1.cpu.out
- 2,419 vlimit exceeded in heat.cpu.out
- Suggests rapid atomic velocities → unstable simulation

**Root cause hypothesis:**
1. Mn coordination sphere restrained incorrectly
2. Strain builds during restrained phases
3. Released suddenly causing velocity spikes

**Next steps:**
1. **STOP current run**
2. Fix restraint masks
3. Re-equilibrate from minimization or heat

---

### 1Wat+3 — SIGNIFICANT ISSUES

**Status:** Similar to 1Wat+2

**Evidence:**
- 9,947 vlimit warnings across stages
- Lower than 1Wat+2 but still problematic

**Next steps:** Same as 1Wat+2

---

### empty+2 — CRASHED

**Status:** Simulation crashed with "Coordinate resetting cannot be accomplished"

**Error message:**
```
Coordinate resetting cannot be accomplished,
deviation is too large
iter_cnt, my_bond_idx, i and j are : 4 2132 4322 4323
```

**Interpretation:**
- SHAKE algorithm failed
- Atoms 4322-4323 are part of bond 2132
- Bond length deviated beyond SHAKE tolerance

**Root cause:** Same as above — Mn site instability propagating

**Next steps:**
1. Identify atoms 4322-4323 (likely near Mn site)
2. Fix restraint masks
3. Re-equilibrate from scratch
4. Consider reducing initial timestep to 0.5 fs

---

### empty+3 — UNKNOWN

**Status:** No simulation data found

**Next steps:**
1. Verify topology and coordinates exist
2. Use same corrected protocol as empty+2

---

### Nterm_only — SEPARATE PROJECT

**Status:** Different simulation setup (N-terminal domain only)

**Location:** Output files in `output/` subdirectory

**Relevance:** May be useful for comparison but different scope

---

## Readiness Timeline

### Immediate (Day 1)

| Task | System | Time Est. |
|------|--------|-----------|
| Fix restraint masks | All | 1 hour |
| Complete BiOx+2 eq1 | BiOx+2 | 1 hour |
| Re-start heat with fixed protocol | 1Wat+2, 1Wat+3, empty+2 | Submit jobs |

### Short-term (Day 2-3)

| Task | System | Time Est. |
|------|--------|-----------|
| BiOx+2 eq2-eq3 | BiOx+2 | 3 hours |
| **BiOx+2 production start** | BiOx+2 | 12-24 hours per 10 ns |
| Re-equilibration | Other systems | Ongoing |

### Production Run Timeline

**BiOx+2 target:**
- Start production: Day 2
- 10 ns checkpoint: Day 3
- 100 ns target: ~10 days (GPU)

**Other systems:**
- Dependent on re-equilibration success
- Estimate 3-5 days to production readiness

---

## Resource Requirements

### UFHPC Allocation

| Stage | Partition | Time/Run | GPU Hours |
|-------|-----------|----------|-----------|
| Heat | hpg-milan (CPU) | 1 hr | 0 |
| EQ1-2 | hpg-milan (CPU) | 2 hr each | 0 |
| EQ3 | hpg-turin (GPU) | 1 hr | 1 |
| Production 10ns | hpg-turin (GPU) | 4-6 hr | 5-6 |
| Production 100ns | hpg-turin (GPU) | 40-60 hr | 50-60 |

**Total for BiOx+2 (100 ns):** ~60 GPU hours

**Total for all 4 systems (100 ns each × 3 replicas):**
- 4 systems × 3 replicas × 60 hr = 720 GPU hours

---

## QC Gates Before Production

### Required Checks

1. **Density:** 0.99 ± 0.02 g/cc over last 50 ps of eq3
2. **No vlimit:** Zero vlimit warnings in eq2-eq3
3. **CA RMSD:** < 2.0 Å from starting structure
4. **Mn distances:** All Mn-ligand distances within ± 0.3 Å of initial
5. **Energy plateau:** Total energy shows no drift over last 100 ps

### QC Script Template

```bash
#!/bin/bash
# qc_pre_production.sh
SYSTEM=$1
PRMTOP="${SYSTEM}/5vg3_solv.prmtop"
RST="${SYSTEM}/eq3.cpu.rst7"

# Check density from last output
tail -100 ${SYSTEM}/eq3.cpu.out | grep Density | tail -5

# Check for vlimit
grep -c "vlimit" ${SYSTEM}/eq3.cpu.out

# RMSD check (requires cpptraj)
cpptraj -p $PRMTOP <<EOF
trajin $RST
reference ${SYSTEM}/5vg3_solv.inpcrd
rms ToRef @CA reference
go
EOF
```

---

## Recommendations

### Priority Order

1. **BiOx+2:** Fix mask, complete equilibration, start production
2. **1Wat+3:** Re-equilibrate with corrected protocol
3. **1Wat+2:** Re-equilibrate with corrected protocol
4. **empty+2:** Re-equilibrate with 0.5 fs timestep initially
5. **empty+3:** Set up and equilibrate

### Why BiOx+2 First?

1. Zero instability warnings — most stable system
2. Bidentate oxalate binding is scientifically interesting
3. Has SHORT flag but handles it well → good validation of protocol
4. Can get publishable data fastest

### Thesis-Ready Timeline

| Milestone | Target Date | Requirement |
|-----------|-------------|-------------|
| BiOx+2 100 ns | 2 weeks | Single trajectory |
| BiOx+2 3×100 ns | 4 weeks | Replica analysis |
| Second system 100 ns | 5 weeks | Comparative |
| All 4 systems | 8 weeks | Full dataset |
