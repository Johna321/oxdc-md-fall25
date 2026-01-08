# Root Cause Analysis: System Stability Differences

## Executive Summary

**My original restraint mask hypothesis was WRONG.**

The true cause of simulation instability is **force field parameter differences** between systems, particularly:
1. Higher force constants in water-coordinated systems (1Wat+2, 1Wat+3)
2. Missing coordination ligand in empty+2 (CN=4 vs CN=5-6)
3. BiOx+2 uses fundamentally different parameterization (ionic model at Site 2)

---

## Evidence: Bond Energy Analysis

| System | Mean (kcal/mol) | Std Dev | Max | Stability |
|--------|-----------------|---------|-----|-----------|
| **BiOx+2** | 1127 | 29 | 1210 | **STABLE** |
| 1Wat+2 | 1848 | 1254 | 8571 | UNSTABLE |
| 1Wat+3 | 1405 | 446 | 4310 | MODERATE |
| **empty+2** | 4330 | 3726 | 14157 | **CRASHED** |

**Key insight:** BiOx+2's bond energy variance is 43× lower than 1Wat+2.

---

## Force Field Parameter Comparison

### Mn-Ligand Force Constants (k, kcal/mol·Å²)

| Bond | BiOx+2 | 1Wat+2 | 1Wat+3 | empty+2 |
|------|--------|--------|--------|---------|
| Mn-His1 | **14.0** | 33.0 | **92.8** | 52.9 |
| Mn-His2 | **31.7** | 46.0 | **85.1** | 43.3 |
| Mn-Glu | 38.7 | 36.5 | **125.3** | 27.1 |
| Mn-His3 | **32.9** | 45.3 | **85.9** | 52.6 |

**Pattern:**
- BiOx+2: Lowest force constants (14-49)
- 1Wat+3: Highest force constants (85-125) — Mn(III) parameters
- 1Wat+2/empty+2: Intermediate (27-53)

### Equilibrium Bond Distances (r₀, Å)

| Bond | BiOx+2 | 1Wat+2 | 1Wat+3 |
|------|--------|--------|--------|
| Mn-His1 | 2.41 | 2.25 | **2.02** |
| Mn-His2 | 2.26 | 2.19 | **2.03** |
| Mn-Glu | 2.08 | 2.11 | **1.86** |
| Mn-His3 | 2.25 | 2.20 | **2.03** |

**1Wat+3 has shorter equilibrium distances** — expected for Mn(III) due to smaller ionic radius.

---

## Mechanistic Explanation

### Why BiOx+2 is Stable

1. **Lower force constants:** Small deviations from equilibrium cause small energy penalties
2. **Ionic model at Site 2:** `Mn2+` type (charge +2.0) uses non-bonded interactions, inherently more forgiving
3. **Bidentate oxalate:** Provides structural rigidity via chelation
4. **Higher coordination number (CN=6):** More ligands = more stabilization

### Why 1Wat+2/1Wat+3 Have vlimit Issues

1. **Higher force constants:** Small deviations cause large energy corrections → velocity spikes
2. **Bonded model at both sites:** All Mn-ligand interactions are explicit bonds
3. **Single water ligand:** Less rigid than bidentate oxalate
4. **1Wat+3 worse than 1Wat+2:** Mn(III) parameters have even higher force constants

### Why empty+2 Crashed

1. **Missing ligand (CN=4):** SPARSE flag indicates under-coordination
2. **No stabilizing water or substrate:** Less constraint on Mn geometry
3. **SHAKE failure:** Extreme bond deviations (up to 14157 kcal/mol) exceeded SHAKE tolerance

---

## The Restraint Mask is a Red Herring

### Why I Was Wrong

My original argument: "Incorrect restraint masks cause Mn to be restrained, then suddenly released"

**Counter-arguments:**

1. **Same incorrect mask in all systems** — but only BiOx+2 is stable
2. **BiOx+2 has zero vlimit** — despite using same generic mask
3. **vlimit occurs during equilibration** — when restraints are still active
4. **SHAKE failure (empty+2)** — happens within constrained bonds, not restraint release

### The Mask Issue is Real But Minor

The restraint mask discrepancy IS a problem for:
- Reference structure accuracy
- Reproducibility
- Best practices

But it's NOT the cause of simulation instability.

---

## Revised Hypothesis: Coordination Chemistry Rules

| Factor | Stable | Unstable |
|--------|--------|----------|
| Force constants | Lower (< 50) | Higher (> 80) |
| Coordination number | 5-6 | 4 |
| Site 2 model | Ionic (Mn2+) | Bonded (M2) |
| Ligand rigidity | Bidentate chelate | Monodentate water |

---

## Implications for Project

### Immediate Actions

1. **Do NOT re-equilibrate based on restraint mask fix** — won't solve instability
2. **Proceed with BiOx+2 production** — genuinely stable system
3. **Investigate MCPB.py parameters** for other systems

### For Unstable Systems

Options:
1. **Re-parameterize with MCPB.py** using different QM settings
2. **Use modified bonded model (MBM)** to reduce bond rigidity
3. **Add explicit Mn-ligand distance restraints** (not heavy-atom restraints)
4. **Consider hybrid ionic/bonded model** like BiOx+2 Site 2

### For Thesis

This finding is itself a significant result:
- **Force field quality varies dramatically** between coordination environments
- **Mn(III) parameters may be unreliable** for MD (literature gap)
- **Bidentate vs monodentate ligands** affect simulation stability

---

## Questions for PI

1. Were MCPB.py parameters validated against QM reference structures?
2. Why does BiOx+2 use ionic model (Mn2+) at Site 2 while others use bonded model (M2)?
3. Were different QM levels used for Mn(II) vs Mn(III) systems?
4. Should we re-parameterize 1Wat+2/1Wat+3 with lower force constants?

---

## Technical Notes

### vlimit Exceeded

From AMBER documentation:
> "Exceeded vlimits are generally indicative of overlapping atoms... the van der waals clash is supplying a repulsive force significantly large to induce such large velocities."

But in this case, it's the **bond/angle force corrections** driving high velocities, not vdW clashes.

### SHAKE Failure (empty+2)

Error: `Coordinate resetting cannot be accomplished, deviation is too large`

This occurs when bond lengths deviate beyond SHAKE tolerance (~0.0001 Å for hydrogen bonds). The extreme bond energies (14157 kcal/mol) indicate severe strain that propagates to SHAKE-constrained bonds.

---

## Conclusion

**BiOx+2 is stable because of its unique parameterization:**
1. Lower Mn-ligand force constants
2. Ionic model at C-terminal site
3. Bidentate oxalate providing structural rigidity

**The restraint mask issue, while real, is NOT the cause of instability in other systems.**

The real issue is force field parameter quality, which likely requires re-parameterization with MCPB.py or alternative approaches.
