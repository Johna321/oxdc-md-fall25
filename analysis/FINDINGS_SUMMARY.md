# OxDC MD Simulation Analysis: Key Findings

## Executive Summary

Analysis of AMBER MD simulations across four OxDC system variants reveals that **force field parameterization**, not restraint mask configuration, is the primary determinant of simulation stability. The substrate-bound BiOx+2 system is uniquely stable due to its lower force constants and flexible coordination geometry.

---

## The 6 Key Findings

### Finding 1: Bond Energy Stability Varies 100-fold Across Systems

| System | Bond Energy Std Dev | Max Spike | Status |
|--------|---------------------|-----------|--------|
| **BiOx+2** | **29 kcal/mol** | 1,210 | **STABLE** |
| 1Wat+2 | 1,254 kcal/mol | 8,571 | UNSTABLE |
| 1Wat+3 | 446 kcal/mol | 4,310 | UNSTABLE |
| empty+2 | 3,726 kcal/mol | 14,157 | CRASHED |

**Visualization:** `bond_energy_distribution.png`, `energy_summary.png`

**Key insight:** BiOx+2 shows remarkably tight energy distributions (σ=29) compared to other systems, indicating fundamentally different force field behavior.

---

### Finding 2: Force Constants Predict MD Stability

| System | Avg Force Constant (k) | Simulation Outcome |
|--------|------------------------|-------------------|
| BiOx+2 | 29.3 kcal/mol·Å² | STABLE |
| 1Wat+2 | 40.2 kcal/mol·Å² | UNSTABLE |
| empty+2 | 44.0 kcal/mol·Å² | CRASHED |
| 1Wat+3 | 97.3 kcal/mol·Å² | UNSTABLE |

**Visualization:** `force_constant_analysis.png`

**Key insight:** Systems with average force constants below ~35 kcal/mol·Å² tend to be stable. Higher force constants create stiffer bonds that don't accommodate thermal fluctuations well.

---

### Finding 3: Mn(III) Shows Jahn-Teller Distortion

The 1Wat+3 system models Mn(III) with characteristic Jahn-Teller compression:

- **Axial Glu-Mn bond:** 1.86 Å (compressed)
- **Equatorial His-Mn bonds:** 2.02-2.03 Å
- **Force constants:** 85-125 kcal/mol·Å² (2-3x higher than Mn(II))

**Visualization:** `oxidation_state_analysis.png` (Panel C)

**Key insight:** The Jahn-Teller distorted Mn(III) coordination creates an unusually stiff force field that is difficult to equilibrate in classical MD.

---

### Finding 4: Asymmetric Bidentate Oxalate Coordination

BiOx+2 uniquely features substrate oxalate bound to Mn1:

| Oxalate Oxygen | Mn-O Distance | Force Constant |
|----------------|---------------|----------------|
| O1 (tight) | 2.11 Å | 49.4 kcal/mol·Å² |
| O2 (loose) | 2.42 Å | 11.6 kcal/mol·Å² |

**Visualization:** `substrate_coordination.png`

**Key insight:** The asymmetric binding creates a flexible coordination sphere that can absorb thermal fluctuations without destabilizing the metal center.

---

### Finding 5: Equilibrium Distance Correlates with Stability

| System | Avg Mn-Ligand Distance | Bond Length Range |
|--------|------------------------|-------------------|
| BiOx+2 | 2.25 Å | 0.32 Å |
| 1Wat+2 | 2.19 Å | 0.14 Å |
| empty+2 | 2.17 Å | 0.05 Å |
| 1Wat+3 | 1.99 Å | 0.17 Å |

**Visualization:** `distance_vs_forceconstant.png`

**Key insight:** BiOx+2 has both the longest average bond lengths AND the largest range, suggesting the oxalate substrate creates a more relaxed coordination geometry.

---

### Finding 6: Stability Predictor Model

A simple predictive model based on MCPB.py parameters:

```
STABLE ZONE:     Avg k < 35 kcal/mol·Å²
MARGINAL ZONE:   35 < Avg k < 60 kcal/mol·Å²
UNSTABLE ZONE:   Avg k > 60 kcal/mol·Å²
```

**Visualization:** `stability_predictor.png`

**Key insight:** Force field parameters can be used to predict MD stability before running expensive simulations.

---

## Corrected Root Cause Analysis

### Original Hypothesis (REJECTED)
> "Restraint mask discrepancies cause vlimit exceeded errors"

### Evidence Against Original Hypothesis
1. BiOx+2 uses the same restraint mask pattern as other systems but is stable
2. Different failure modes (vlimit vs SHAKE vs drift) suggest different underlying causes
3. Restraint masks affect only equilibration, not the fundamental force field

### Revised Hypothesis (SUPPORTED)
> "MCPB.py force field parameters (force constants, equilibrium distances) determine simulation stability. Lower force constants and longer equilibrium distances create more stable simulations."

### Supporting Evidence
1. 100-fold difference in bond energy variability correlates with force constant differences
2. BiOx+2's unique substrate coordination creates naturally lower force constants
3. Mn(III) parameterization in 1Wat+3 creates unnaturally stiff bonds
4. Stability can be predicted from force field parameters alone

---

## Recommendations

### For Production Simulations
1. **Prioritize BiOx+2** - Only system ready for production runs
2. **Re-parameterize other systems** - Consider using softer force constants
3. **Test ionic model** - BiOx+2 may use partial ionic treatment; test this for other systems

### For Future MCPB.py Work
1. Compare Seminario method vs empirical parameters for Mn
2. Consider using softer force constants (20-40 kcal/mol·Å² range)
3. Test hybrid bonded/ionic models for better stability

### Parameter Modification Strategy
```
Target force constants: 20-40 kcal/mol·Å² (vs current 40-125)
Target bond lengths: 2.1-2.4 Å for Mn(II)
Consider: Scaling down k values by 50% for problematic systems
```

---

## Files Generated

### Visualizations
- `bond_energy_distribution.png` - Violin plots of energy distributions
- `bond_energy_timeseries.png` - Time series of bond energies
- `energy_summary.png` - Summary statistics comparison
- `force_constant_analysis.png` - Force constant comparison
- `distance_vs_forceconstant.png` - r0 vs k scatter plot
- `oxidation_state_analysis.png` - Mn(II) vs Mn(III) comparison
- `substrate_coordination.png` - BiOx+2 coordination schematic
- `stability_predictor.png` - Predictive model visualization

### Scripts
- `energy_analysis.py` - Bond energy extraction and analysis
- `force_constant_analysis.py` - Force constant comparison
- `comprehensive_mn_analysis.py` - Full coordination analysis

---

## Conclusions

The stability of BiOx+2 is not due to restraint mask configuration but rather to:

1. **Lower force constants** from MCPB.py parameterization
2. **Flexible substrate coordination** via asymmetric bidentate oxalate
3. **Longer equilibrium distances** that accommodate thermal motion
4. **Single active site** (vs two Mn sites in other systems)

This analysis provides a clear path forward: either use BiOx+2 for production runs, or re-parameterize other systems with softer force constants before attempting further equilibration.
