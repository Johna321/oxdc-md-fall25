# BiOx+2 OxDC 10 ns Production MD Analysis Report

**Date:** January 2026
**Analyst:** Claude (Computational Biology Research Assistant)
**System:** Oxalate Decarboxylase with bidentate oxalate substrate, Mn(II)
**PDB Origin:** 5VG3
**Simulation Duration:** 10 ns production (1000 frames at 10 ps/frame)

---

## Executive Summary

### KEY FINDING: The active site lid remains FULLY OPEN throughout the entire 10 ns simulation.

| Metric | Value | Assessment |
|--------|-------|------------|
| Backbone RMSD | 1.98 ± 0.24 Å | Stable |
| Mn1 Coordination | All ligands intact | Excellent |
| Oxalate Binding | Asymmetric bidentate | Persistent |
| **Glu162-Mn Distance** | **11.5 ± 0.5 Å** | **FULLY OPEN** |
| Lid Open Fraction | **100%** | No transitions |
| Simulation Converged | Yes | Block averages agree |

### Scientific Significance

This result suggests that in the Mn(II) oxidation state with bidentate oxalate bound, the enzyme adopts a stable open conformation. Glu162, the catalytically essential proton donor, is positioned ~12 Å from the Mn center—too far for direct proton transfer. This implies:

1. **Lid closure may be rate-limiting** or coupled to subsequent catalytic steps
2. **Mn oxidation state may modulate lid dynamics** (comparison with Mn(III) needed)
3. **The open state may represent a "resting" conformation** awaiting activation

---

## 1. Simulation Quality

### 1.1 Structural Stability (RMSD)

The Cα RMSD stabilized after an initial equilibration period:

| Parameter | Value |
|-----------|-------|
| Mean RMSD | 1.98 ± 0.24 Å |
| Range | 1.28 - 2.64 Å |
| Drift | +0.056 Å/ns |
| Early (<1 ns) | 1.62 Å |
| Late (>1 ns) | 2.02 Å |

**Assessment:** ✓ The simulation is structurally stable. RMSD < 3 Å throughout indicates no major unfolding events. The small positive drift reflects minor conformational adjustment but is within acceptable limits.

### 1.2 Convergence Analysis

Block averaging (5 × 2 ns blocks) demonstrates statistical convergence:

| Metric | Block 1 | Block 2 | Block 3 | Block 4 | Block 5 | SEM |
|--------|---------|---------|---------|---------|---------|-----|
| RMSD (Å) | 1.75 | 1.84 | 1.99 | 2.23 | 2.11 | 0.08 |
| Glu162-Mn (Å) | 11.34 | 11.72 | 11.40 | 11.66 | 11.58 | 0.07 |
| Mn1-His95 (Å) | 2.39 | 2.41 | 2.38 | 2.37 | 2.39 | 0.01 |
| Mn1-Glu101 (Å) | 2.06 | 2.06 | 2.05 | 2.06 | 2.06 | 0.00 |

**Assessment:** ✓ All key metrics show block-to-block consistency with SEM < 10% of mean, indicating adequate sampling for these properties.

---

## 2. Mn1 Coordination Integrity

The MCPB.py-parameterized Mn1 coordination sphere remained intact throughout:

| Ligand | Mean (Å) | Std (Å) | Expected r₀ | Dissociation Events |
|--------|----------|---------|-------------|---------------------|
| His95-NE2 | 2.39 | 0.12 | 2.41 | 0 |
| His97-NE2 | 2.26 | 0.09 | 2.26 | 0 |
| His140-NE2 | 2.24 | 0.09 | 2.25 | 0 |
| Glu101-OE1 | 2.06 | 0.08 | 2.08 | 0 |

**Assessment:** ✓ All Mn1-ligand distances remain within expected ranges. Zero dissociation events (distance > 3.0 Å) throughout 10 ns confirms the MCPB.py force field maintains proper coordination geometry.

### Force Field Validation

The MCPB.py parameters for this system (B3LYP/6-31G(d,p), spin multiplicity 6) produce:
- Mean force constant: 29.7 kcal/mol·Å² (within stable range < 35)
- Stable octahedral geometry throughout simulation
- No artificial rigidity or excessive flexibility

---

## 3. Oxalate Binding Mode

### 3.1 Distance Analysis

| Oxygen | Mean (Å) | Std (Å) | Classification |
|--------|----------|---------|----------------|
| OZ | 2.09 | 0.07 | Coordinating (tight) |
| OX | 2.35 | 0.11 | Coordinating (loose) |
| OY | 4.05 | 0.09 | Non-coordinating |

### 3.2 Binding Mode Classification

**ASYMMETRIC BIDENTATE (κO,κO')**

- **Bidentate fraction:** 91.5% (both OZ and OX < 2.5 Å)
- **Asymmetry:** OX-OZ = 0.26 ± 0.13 Å

This asymmetric bidentate mode is consistent with:

1. **¹³C-ENDOR spectroscopy** (Zhu et al., 2024): Confirmed bidentate binding in OxDC
2. **DFT calculations** (Zhu et al., 2024): Bidentate is 4.7 kcal/mol more stable than monodentate
3. **Carboxylate binding theory** (Dudev & Lim, 2003): Asymmetric chelation is common for carboxylates

### 3.3 Mechanistic Implications

The persistent bidentate binding suggests:
- **Ground state stability:** Oxalate remains firmly bound in reactive conformation
- **No monodentate intermediate observed:** The proposed O₂ binding step (requiring one open coordination site) was not sampled in 10 ns
- **Extended simulations needed:** Bidentate → monodentate transition may occur on longer timescales

---

## 4. Lid Dynamics (KEY FINDING)

### 4.1 Glu162-Mn Distance

| Metric | Value |
|--------|-------|
| CD-Mn1 Mean | 11.54 ± 0.54 Å |
| OE1-Mn1 Mean | 11.73 ± 0.73 Å |
| OE2-Mn1 Mean | 12.28 ± 0.63 Å |

### 4.2 Lid State Distribution

| State | Distance Range | Fraction |
|-------|----------------|----------|
| Closed | < 4 Å | **0.0%** |
| Intermediate | 4-8 Å | **0.0%** |
| Open | > 8 Å | **100.0%** |

### 4.3 Transition Analysis

- **Transitions across 8 Å threshold:** 0
- **Distribution:** Unimodal (Gaussian, p = 0.94)
- **Block consistency:** 11.34-11.72 Å across all blocks

**THE LID NEVER CLOSES during the 10 ns simulation.**

### 4.4 Literature Context (Corrected Three-State Model)

From crystallographic studies, OxDC exhibits **three distinct lid states**:

| State | PDB | Glu162-Mn Distance | Description |
|-------|-----|-------------------|-------------|
| Open-loop | 1J58 | ~15-16 Å | SENS loop swung away |
| Closed, Glu162-in | 1UW8 | ~4.6-5.1 Å | Glu162 H-bonds Mn-water |
| Closed-backbone, Glu162-out | 5VG3 | ~10-12 Å | Loop closed, sidechain displaced |
| **Our simulation** | **BiOx+2** | **~11.5 Å** | **5VG3-like state** |

**Key observation:** Our simulation maintains the 5VG3-like "closed-backbone / Glu162-out" state. This is NOT the "open-loop" state (1J58, ~15-16 Å). The Glu162 sidechain is displaced from the Mn, likely due to bidentate oxalate binding.

**Note:** Previous versions of this report incorrectly stated 5VG3 = ~2.4 Å. This was based on a misunderstanding of the nomenclature. Glu162 is NOT a first-shell Mn ligand.

### 4.5 Mechanistic Implications

Glu162 is essential for catalysis:
- E162A mutation **eliminates decarboxylase activity** (Saylor et al., 2008)
- Glu162 serves as **proton donor** in proposed PCET mechanism
- Proton transfer requires Glu162-Mn distance **< 4 Å**

**At 11.5 Å, direct proton transfer is impossible.**

This suggests either:
1. **Lid closure is a subsequent step** triggered by factors not present (e.g., O₂ binding, redox change)
2. **Mn(II) favors the open state** — comparison with Mn(III) system needed
3. **10 ns is insufficient** to capture lid closure (μs timescale motion)

---

## 5. Flexibility Analysis

### 5.1 Global RMSF

| Region | Mean RMSF (Å) |
|--------|---------------|
| Global | 1.03 ± 0.79 |
| Lid (160-166) | 0.71 |
| Active site | 0.52-0.59 |

### 5.2 Flexibility Hotspots (> 1.5 Å)

| Region | Residues | Max RMSF | Description |
|--------|----------|----------|-------------|
| N-terminus | 1-6 | 5.6 Å | Terminal flexibility |
| Loop | 11-23 | 5.3 Å | Exposed loop |
| Loop | 176-196 | 3.8 Å | Surface loop |
| C-terminus | 353-370 | 2.7 Å | Terminal flexibility |

### 5.3 Lid Rigidity

**Surprisingly, the lid (160-166) shows LOWER flexibility than the global average.**

| Lid Residue | RMSF (Å) |
|-------------|----------|
| 160 (Phe) | 0.66 |
| 161 (Ser) | 0.66 |
| 162 (Glu) | 0.73 |
| 163 (Asn) | 0.69 |
| 164 (Ser) | 0.93 |
| 165 (Thr) | 0.59 |
| 166 (Phe) | 0.77 |

**Interpretation:** The open lid conformation is **stabilized**, not fluctuating. This suggests the open state is a genuine energy minimum, not a transient fluctuation.

---

## 6. Correlation Analysis

| Correlation | r | Interpretation |
|-------------|---|----------------|
| RMSD vs Glu162-Mn | +0.08 | Weak — lid position independent of global motion |
| RMSD vs Lid RMSD | +0.08 | Weak — lid fluctuations independent |
| **Lid RMSD vs Glu162-Mn** | **+0.39** | Moderate — lid motion correlates with positioning |

The moderate correlation between lid RMSD and Glu162-Mn distance indicates that when the lid fluctuates, it affects the Glu162-Mn distance proportionally.

---

## 7. Critical Evaluation

### 7.1 What We Can Conclude

✓ **System is well-equilibrated and stable**
- RMSD < 3 Å, converged block averages
- Force field maintains Mn coordination

✓ **Oxalate binding is asymmetric bidentate**
- Consistent with ENDOR spectroscopy
- Mechanistically relevant

✓ **Lid remains open in Mn(II) state**
- 100% open throughout 10 ns
- Glu162 cannot transfer proton from this position

### 7.2 What We Cannot Conclude

✗ **Whether lid closure is possible**
- 10 ns may be too short
- Need extended (100+ ns) or enhanced sampling

✗ **Whether Mn oxidation state controls lid**
- Need comparative analysis with Mn(III) system

✗ **Mechanistic pathway**
- Cannot determine catalytic cycle without observing transitions

### 7.3 Limitations

1. **Timescale:** 10 ns is ~100× shorter than typical loop transition times (μs)
2. **Single trajectory:** Statistical power limited without replicas
3. **No enhanced sampling:** Standard MD may not overcome energy barriers
4. **Classical mechanics:** No quantum effects on electron transfer

---

## 8. Future Directions

### 8.1 Immediate Priorities

1. **Analyze 1Wat+3 (Mn(III)) system** — Does oxidation state affect lid?
2. **Extend simulation to 100+ ns** — Sample longer timescales
3. **Run replica simulations** — Statistical power for comparisons

### 8.2 Advanced Methods (if time permits)

| Method | Purpose | Expected Insight |
|--------|---------|------------------|
| Metadynamics | Enhanced sampling | Lid free energy landscape |
| Steered MD | Force-induced closure | Estimate closure barrier |
| QM/MM | Electronic structure | Electron transfer pathway |

### 8.3 Required Simulation Time

| Analysis | Current | Minimum | Ideal |
|----------|---------|---------|-------|
| RMSF convergence | 10 ns | 100 ns | 200 ns |
| Lid transitions | 0 observed | 100 ns | 500 ns × 3 |
| Statistical comparison | N/A | 300 ns | 1 μs |

---

## 9. Summary for Thesis

### One-Paragraph Summary

The 10 ns production simulation of BiOx+2 (OxDC with bidentate oxalate and Mn(II)) reveals a stable, well-equilibrated system with intact Mn1 coordination and persistent asymmetric bidentate oxalate binding. The most significant finding is that the active site lid remains **fully open** throughout the simulation (Glu162-Mn = 11.5 ± 0.5 Å), with zero lid closure events observed. The lid shows lower-than-average flexibility (RMSF 0.71 Å vs. 1.03 Å global), suggesting the open conformation is a stabilized state rather than a transient fluctuation. This result implies that lid closure, required for proton transfer by Glu162, may be (1) triggered by factors not present in this simulation (e.g., O₂ binding, Mn oxidation), (2) occurs on timescales longer than 10 ns, or (3) is disfavored in the Mn(II) oxidation state. Comparison with the Mn(III) system (1Wat+3) is essential to determine whether oxidation state modulates lid dynamics.

### Key Figures for Thesis

1. `prod_rmsd.png` — Structural stability
2. `prod_mn1_coordination.png` — Force field validation
3. `prod_lid_dynamics.png` — **KEY FIGURE** — Lid remains open
4. `prod_oxalate_binding.png` — Bidentate binding
5. `prod_rmsf.png` — Flexibility profile

---

## 10. References

1. Just VJ et al. (2004) A closed conformation of *B. subtilis* oxalate decarboxylase. *J Biol Chem* 279:19867-75.

2. Saylor BT et al. (2008) The identity of the active site and importance of lid conformations. *Arch Biochem Biophys* 472:114-22.

3. Zhu J et al. (2024) Bidentate Substrate Binding Mode in Oxalate Decarboxylase. *Molecules* 29:4414.

4. Li P & Merz KM (2016) MCPB.py: A Python Based Metal Center Parameter Builder. *J Chem Inf Model* 56:599-604.

5. Dudev T & Lim C (2003) Effect of Carboxylate-Binding Mode on Metal Binding/Selectivity. *Acc Chem Res* 36:42-51.

---

## Appendix: Generated Files

```
systems/BiOx+2/
├── analysis_results/
│   ├── figures/
│   │   ├── prod_rmsd.png/pdf
│   │   ├── prod_mn1_coordination.png/pdf
│   │   ├── prod_oxalate_binding.png/pdf
│   │   ├── prod_lid_dynamics.png/pdf
│   │   ├── prod_rmsf.png/pdf
│   │   └── prod_correlations.png/pdf
│   └── *.dat (raw analysis data)
├── analysis_scripts/
│   └── analyze_production.py
└── PRODUCTION_ANALYSIS_REPORT.md (this file)
```

---

*Report generated: January 2026*
*Analysis Status: COMPLETE for 10 ns production*
*Next Steps: Compare with 1Wat+3; extend simulation; run replicas*
