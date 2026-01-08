# OxDC MD Analysis Plan

## Overview

This document outlines the analysis strategy for OxDC molecular dynamics simulations, connecting scientific questions to specific analyses and expected outcomes.

---

## Primary Scientific Questions

### Q1: Does Mn oxidation state affect lid flexibility?

**Hypothesis:** Mn(III) (1Wat+3, empty+3) may stabilize closed lid conformation due to stronger electrostatic interaction with Glu162.

**Analysis:**
| Metric | Script | Expected Difference |
|--------|--------|---------------------|
| Lid RMSF | `lid_dynamics.in` | Mn(II) > Mn(III) |
| Glu162-Mn distance | `lid_dynamics.in` | Mn(III) shorter |
| Open/closed occupancy | H-bond analysis | Mn(III) more closed |
| PC1 variance | `pca_prep.in` | Mn(II) larger amplitude |

**Comparison sets:**
- 1Wat+2 vs 1Wat+3
- empty+2 vs empty+3

---

### Q2: Does substrate binding affect lid dynamics?

**Hypothesis:** Bidentate oxalate (BiOx+2) constrains lid in catalytically competent conformation.

**Analysis:**
| Metric | Script | Expected for BiOx+2 |
|--------|--------|---------------------|
| Lid RMSF | `lid_dynamics.in` | Lower (more constrained) |
| Solvent access to Mn | `lid_dynamics.in` | Reduced |
| Secondary structure | DSSP analysis | More 3₁₀ helix |

**Comparison sets:**
- BiOx+2 vs 1Wat+2 (same oxidation state)
- BiOx+2 vs empty+2 (substrate effect)

---

### Q3: Is the Mn coordination stable throughout production?

**Hypothesis:** MCPB.py parameters maintain octahedral geometry.

**Analysis:**
| Metric | Script | Acceptable Range |
|--------|--------|------------------|
| Mn-His distances | `mn_coordination.in` | 2.0-2.5 Å |
| Mn-Glu distances | `mn_coordination.in` | 1.9-2.3 Å |
| Mn-Ox distances | `mn_coordination.in` | 1.8-2.5 Å |
| Coordination number | radial analysis | 5-6 |

**Alert criteria:**
- Any distance > 3.0 Å: possible dissociation
- Any distance < 1.8 Å: possible clash
- Sudden distance changes: instability

---

### Q4: Is the electron transfer pathway intact?

**Hypothesis:** W96/W274 π-stacking is maintained for inter-subunit electron hopping.

**Analysis:**
| Metric | Script | Expected Values |
|--------|--------|-----------------|
| W-W ring distance | `trp_pair.in` | 3.5-4.5 Å |
| Ring orientation | `trp_pair.in` | Parallel (0° or 180°) |
| Mn-W distances | `trp_pair.in` | ~8.4 Å each |

**Biological relevance:** Disruption would impair catalytic turnover.

---

## Analysis Protocol

### Phase 1: Equilibration Validation (Before Production)

**Run for each system at end of eq3:**

```bash
cpptraj -p 5vg3_solv.prmtop <<EOF
trajin eq3.cpu.rst7
reference 5vg3_solv.inpcrd
rms @CA reference out eq3_rmsd.dat
distance d1 @6032 @1519  # Mn-His example
run
EOF
```

**QC Gates:**
- [ ] RMSD < 2.0 Å
- [ ] All Mn-ligand distances within 0.3 Å of initial
- [ ] Density 0.99 ± 0.02 g/cc

---

### Phase 2: Production Monitoring (During Runs)

**Check every 10 ns segment:**

1. Energy/temperature/pressure stability
2. RMSD drift (should plateau)
3. Mn coordination (no dissociation)

```bash
# Quick check script
tail -500 prod_seg001.out | grep -E "Etot|Temp|Dens"
```

---

### Phase 3: Post-Production Analysis

**Order of analyses:**

1. **Structural stability** (RMSD, RMSF)
   - Identify any structural drift
   - Map flexible vs rigid regions

2. **Mn coordination** (distances, angles)
   - Validate force field performance
   - Identify any transient disruptions

3. **Lid dynamics** (RMSD, H-bonds, SASA)
   - Core thesis question
   - Compare across systems

4. **W96/W274 geometry**
   - Electron pathway integrity

5. **PCA**
   - Identify dominant motions
   - Compare conformational landscapes

6. **Clustering** (if needed)
   - Identify discrete conformational states

---

## Expected Outputs

### Tables for Thesis

| Table | Content | Analysis Source |
|-------|---------|-----------------|
| 1 | System comparison (atoms, charge, Mn flags) | `overview.csv` |
| 2 | Equilibration summary | QC logs |
| 3 | Average Mn-ligand distances ± std | `mn_coordination.in` |
| 4 | Lid RMSF by system | `lid_dynamics.in` |
| 5 | H-bond occupancies | `lid_dynamics.in` |
| 6 | PCA variance explained | `pca_prep.in` |

### Figures for Thesis

| Figure | Content | Analysis Source |
|--------|---------|-----------------|
| 1 | Structure with Mn sites highlighted | PyMOL |
| 2 | RMSD time series overlay | `rmsd_rmsf.in` |
| 3 | RMSF per residue with lid marked | `rmsd_rmsf.in` |
| 4 | Mn-ligand distance distributions | `mn_coordination.in` |
| 5 | Glu162-Mn distance histogram | `lid_dynamics.in` |
| 6 | PC1 vs PC2 scatter | `pca_prep.in` |
| 7 | Representative open/closed structures | clustering |
| 8 | W96/W274 distance time series | `trp_pair.in` |

---

## Comparative Analysis Framework

### Cross-System Comparison

Run identical analyses on all systems, then:

```python
# Pseudocode for comparative analysis
systems = ['BiOx+2', '1Wat+2', '1Wat+3', 'empty+2']

for metric in ['lid_rmsf', 'glu162_mn_dist', 'mn_coordination']:
    data = {sys: load_data(sys, metric) for sys in systems}

    # Statistical comparison
    for sys1, sys2 in combinations(systems, 2):
        ttest = stats.ttest_ind(data[sys1], data[sys2])
        print(f"{sys1} vs {sys2}: p = {ttest.pvalue:.3e}")

    # Plot overlay
    plot_overlay(data, metric)
```

### Convergence Assessment

**For each metric, verify:**

1. Block averaging: divide trajectory into 5 blocks, check if means agree
2. Autocorrelation: ensure sampling is decorrelated
3. Running average: should plateau by end of trajectory

```bash
# Block averaging in cpptraj
cpptraj -p 5vg3_solv.prmtop <<EOF
trajin prod_seg001.nc 1 2000     # Block 1
rms @CA out block1_rmsd.dat
clear trajin
trajin prod_seg001.nc 2001 4000  # Block 2
rms @CA out block2_rmsd.dat
# ... etc
run
EOF
```

---

## Software Requirements

| Tool | Purpose | Module Load |
|------|---------|-------------|
| cpptraj | Trajectory analysis | `amber/25` |
| pytraj | Python cpptraj wrapper | `amber/25` + Python |
| MDAnalysis | Alternative analysis | pip install |
| matplotlib | Plotting | pip install |
| PyMOL | Visualization | `pymol` |
| VMD | Visualization | `vmd` |

---

## File Organization

```
analysis/
├── cpptraj/
│   ├── rmsd_rmsf.in
│   ├── mn_coordination.in
│   ├── lid_dynamics.in
│   ├── trp_pair.in
│   └── pca_prep.in
├── scripts/
│   ├── run_all_analyses.sh
│   ├── compare_systems.py
│   └── plot_results.py
├── results/
│   ├── BiOx+2/
│   ├── 1Wat+2/
│   ├── 1Wat+3/
│   └── empty+2/
└── ANALYSIS_PLAN.md
```

---

## Timeline Integration

| Week | Analysis Tasks |
|------|----------------|
| 1 | Equilibration validation for BiOx+2 |
| 2 | Production monitoring, preliminary RMSD/RMSF |
| 3 | Mn coordination analysis |
| 4 | Lid dynamics analysis |
| 5 | PCA and clustering |
| 6 | Comparative analysis across systems |
| 7 | Figure preparation |
| 8 | Thesis writing |

---

## Troubleshooting Guide

### Common Issues

**Problem:** RMSD continuously increases
- **Cause:** Unequilibrated system or force field issues
- **Solution:** Extend equilibration, check Mn parameters

**Problem:** Mn-ligand distances > 3 Å
- **Cause:** Bond breaking, likely force field issue
- **Solution:** Review MCPB.py parameters, consider restraints

**Problem:** PCA shows no clear clusters
- **Cause:** Insufficient sampling or continuous dynamics
- **Solution:** Extend trajectory, try different collective variables

**Problem:** Analyses give different results on replicas
- **Cause:** Normal stochastic variation or convergence issue
- **Solution:** Run more replicas, use longer trajectories
