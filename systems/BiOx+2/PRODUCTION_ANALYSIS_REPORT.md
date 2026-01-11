# BiOx+2 OxDC 10 ns Production MD Analysis Report

**Date:** January 2026
**Analyst:** Claude (Computational Biology Research Assistant)
**System:** Oxalate Decarboxylase with bidentate oxalate substrate, Mn(II)
**PDB Origin:** 5VG3
**Simulation Duration:** 10 ns production (1000 frames at 10 ps/frame)

---

## Executive Summary

### KEY FINDING: The simulation maintains the 5VG3-like "closed-backbone / Glu162-out" state.

| Metric | Value | Assessment |
|--------|-------|------------|
| Backbone RMSD | 1.98 ± 0.24 Å | Stable |
| Mn1 Coordination | All ligands intact | Excellent |
| Oxalate Binding | Asymmetric bidentate | Persistent |
| **Glu162-Mn Distance** | **11.5 ± 0.5 Å** | **5VG3-like (Glu162-out)** |
| Glu162-in Fraction | **0%** | No catalytic pose sampled |
| Simulation Converged | Yes | Block averages agree |

### Scientific Significance

This result shows that in the Mn(II) oxidation state with bidentate oxalate bound, the enzyme maintains the same conformation as the starting structure (5VG3). Glu162, the catalytically essential proton donor, remains displaced from the Mn center (~11.5 Å) rather than adopting the "Glu162-in" pose (~4.6-5.1 Å) required for proton transfer.

**Importantly:** This is NOT the "open-loop" state (1J58, ~15-16 Å). The lid backbone appears to remain closed; only the Glu162 sidechain is displaced. This is consistent with bidentate oxalate sterically preventing the Glu162-in pose.

Key implications:
1. **Bidentate oxalate may block Glu162-in** — steric clash prevents catalytic positioning
2. **Glu162-in may require oxalate rearrangement** — monodentate transition could enable closure
3. **Backbone conformation needs verification** — RMSD to 1J58 vs 1UW8 would confirm loop state

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
- **Steric constraint on Glu162:** Bidentate oxalate may clash with Glu162-in pose (Zhu et al. 2016)
- **No monodentate intermediate observed:** The proposed O₂ binding step (requiring one open coordination site) was not sampled in 10 ns

---

## 4. Lid Dynamics (KEY FINDING)

### 4.1 Glu162-Mn Distance

| Metric | Value |
|--------|-------|
| CD-Mn1 Mean | 11.54 ± 0.54 Å |
| OE1-Mn1 Mean | 11.73 ± 0.73 Å |
| OE2-Mn1 Mean | 12.28 ± 0.63 Å |

### 4.2 Glu162 Sidechain State Distribution

Using the three-state model from literature:

| State | Distance Range | Fraction | Notes |
|-------|----------------|----------|-------|
| Glu162-in (1UW8-like) | < 6 Å | **0.0%** | Catalytic pose |
| Glu162-out (5VG3-like) | 8-14 Å | **100.0%** | Our state |
| Open-loop (1J58-like) | > 14 Å | **0.0%** | Channel open |

### 4.3 Transition Analysis

- **Transitions toward Glu162-in:** 0
- **Distribution:** Unimodal (Gaussian, p = 0.94)
- **Block consistency:** 11.34-11.72 Å across all blocks

**Glu162 never adopts the catalytically active "in" pose during 10 ns.**

### 4.4 Literature Context (Three-State Model)

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
- Proton transfer requires Glu162 close to Mn-bound water (~2.7-2.8 Å contact)

**At 11.5 Å, direct proton transfer is impossible.**

This suggests:
1. **Bidentate oxalate sterically blocks Glu162-in** — consistent with Zhu et al. 2016 analysis
2. **Glu162-in may require substrate rearrangement** — monodentate binding could create space
3. **Backbone analysis needed** — verify loop is truly "closed" vs "open"

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

**The lid (160-166) shows LOWER flexibility than the global average.**

| Lid Residue | RMSF (Å) |
|-------------|----------|
| 160 (Phe) | 0.66 |
| 161 (Ser) | 0.66 |
| 162 (Glu) | 0.73 |
| 163 (Asn) | 0.69 |
| 164 (Ser) | 0.93 |
| 165 (Thr) | 0.59 |
| 166 (Phe) | 0.77 |

**Interpretation:** The Glu162-out conformation is **stabilized**, not fluctuating. This is consistent with the starting 5VG3 structure being maintained as a stable energy minimum.

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
- May sterically block Glu162-in pose

✓ **Glu162 remains in "out" position throughout**
- Maintains 5VG3-like conformation
- Never approaches catalytic Glu162-in pose

### 7.2 What We Cannot Conclude

✗ **Whether backbone is truly "closed" vs "open"**
- Need RMSD to 1J58 (open) vs 1UW8 (closed) reference
- Glu162-Mn distance alone doesn't distinguish backbone state

✗ **Whether Glu162-in is accessible**
- 10 ns may be too short
- Bidentate oxalate may prevent it entirely

✗ **Whether Mn oxidation state controls lid**
- Need comparative analysis with Mn(III) system

### 7.3 Limitations

1. **Timescale:** 10 ns is ~100× shorter than typical loop transition times (μs)
2. **Single trajectory:** Statistical power limited without replicas
3. **No enhanced sampling:** Standard MD may not overcome energy barriers
4. **Missing backbone analysis:** Need RMSD to reference structures

---

## 8. Future Directions

### 8.1 Immediate Priorities

1. **Backbone conformation analysis** — RMSD of lid residues to 1J58 vs 1UW8
2. **Analyze 1Wat+3 (Mn(III)) system** — Does oxidation state affect lid?
3. **Monitor oxalate binding dynamics** — Does it ever go monodentate?

### 8.2 Follow-up Analyses (See Appendix B)

| Analysis | Purpose | Key Metric |
|----------|---------|------------|
| Lid backbone RMSD | Distinguish open-loop vs closed-backbone | RMSD to 1J58/1UW8 |
| Glu162-water distance | Check for H-bond to Mn-water | Glu162-OE to WAT |
| Oxalate binding dynamics | Detect bidentate→monodentate | OZ/OX distances |

### 8.3 Advanced Methods (if time permits)

| Method | Purpose | Expected Insight |
|--------|---------|------------------|
| Metadynamics | Enhanced sampling | Glu162-in free energy barrier |
| Steered MD | Force-induced Glu162-in | Estimate closure barrier |
| QM/MM | Electronic structure | Electron transfer pathway |

---

## 9. Summary for Thesis

### One-Paragraph Summary

The 10 ns production simulation of BiOx+2 (OxDC with bidentate oxalate and Mn(II)) reveals a stable, well-equilibrated system with intact Mn1 coordination and persistent asymmetric bidentate oxalate binding. The most significant finding is that the Glu162 sidechain remains in the **5VG3-like "Glu162-out" position** throughout the simulation (Glu162-Mn = 11.5 ± 0.5 Å), never adopting the catalytically active "Glu162-in" pose (~4.6-5.1 Å) required for proton transfer. This is distinct from the "open-loop" state (1J58, ~15-16 Å) — the lid backbone appears to remain closed, but the Glu162 sidechain is displaced. The lid shows lower-than-average flexibility (RMSF 0.71 Å vs. 1.03 Å global), indicating the Glu162-out conformation is a stabilized state. The persistent bidentate oxalate binding may sterically prevent Glu162 from adopting the catalytic pose, consistent with Zhu et al.'s structural analysis. Follow-up analysis should verify the backbone conformation (RMSD to 1J58 vs 1UW8) and compare with the Mn(III) system (1Wat+3).

### Key Figures for Thesis

1. `prod_rmsd.png` — Structural stability
2. `prod_mn1_coordination.png` — Force field validation
3. `prod_lid_dynamics.png` — **KEY FIGURE** — Glu162 remains in "out" position
4. `prod_oxalate_binding.png` — Bidentate binding (potential steric constraint)
5. `prod_rmsf.png` — Flexibility profile

---

## 10. References

1. Just VJ et al. (2004) A closed conformation of *B. subtilis* oxalate decarboxylase. *J Biol Chem* 279:19867-75.

2. Saylor BT et al. (2008) The identity of the active site and importance of lid conformations. *Arch Biochem Biophys* 472:114-22.

3. Zhu J et al. (2024) Bidentate Substrate Binding Mode in Oxalate Decarboxylase. *Molecules* 29:4414.

4. Li P & Merz KM (2016) MCPB.py: A Python Based Metal Center Parameter Builder. *J Chem Inf Model* 56:599-604.

5. Dudev T & Lim C (2003) Effect of Carboxylate-Binding Mode on Metal Binding/Selectivity. *Acc Chem Res* 36:42-51.

6. Zhu W et al. (2016) Substrate Binding Mode and Molecular Basis of a Specificity Switch. *Biochemistry* 55:2163-73.

---

## Appendix A: Generated Files

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

## Appendix B: Follow-up Analysis Specification

See `BACKBONE_CONFORMATION_ANALYSIS.md` for detailed analysis protocol.

---

*Report generated: January 2026*
*Analysis Status: COMPLETE for 10 ns production (Glu162 sidechain analysis)*
*Next Steps: Backbone conformation analysis; Compare with 1Wat+3; extend simulation*
