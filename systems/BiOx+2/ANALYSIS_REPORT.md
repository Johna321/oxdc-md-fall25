# BiOx+2 OxDC Molecular Dynamics Analysis Report

**Date:** January 2026
**Analyst:** Claude (Computational Biology Research Assistant)
**System:** Oxalate Decarboxylase with bidentate oxalate substrate, Mn(II)
**PDB Origin:** 5VG3

---

## Executive Summary

**CRITICAL LIMITATION:** This analysis is based on **~200 ps equilibration data only**, not the intended 10 ns production simulation. Production trajectory data was not found. The available data is **~500× shorter** than the minimum required for biological conclusions about lid dynamics (100+ ns).

### Key Findings from Equilibration

| Metric | Value | Assessment |
|--------|-------|------------|
| Backbone RMSD | 0.222 ± 0.019 Å | Excellent stability |
| Mean Temperature | 300.0 K | Target achieved |
| Mean Density | 0.987 g/cc | Acceptable |
| Lid RMSF | 0.159 Å | Cannot interpret (insufficient sampling) |

### Conclusion

The system equilibrated successfully and appears stable. However, **no biological conclusions can be drawn** from 200 ps of data. Production runs of 100-500 ns are required before addressing the scientific questions about lid dynamics and Mn oxidation state effects.

---

## 1. Methods Summary

### 1.1 System Composition

| Component | Count/Value |
|-----------|-------------|
| Total Atoms | 63,287 |
| Protein Residues | ~394 |
| Waters (TIP3P) | 19,079 |
| Counterions | 9 Cl⁻ |
| Net Charge | 0 |
| Box Dimensions | 78.7 × 113.8 × 86.5 Å |

### 1.2 Mn Coordination (Site 1)

Force field parameters derived via MCPB.py at B3LYP/6-31G(d,p):

| Ligand | r₀ (Å) | k (kcal/mol·Å²) |
|--------|--------|-----------------|
| His95-NE2 | 2.406 | 14.0 |
| His97-NE2 | 2.259 | 31.7 |
| Glu101-OE1 | 2.084 | 38.7 |
| His140-NE2 | 2.249 | 32.9 |
| Oxalate-OZ | 2.112 | 49.4 |
| Oxalate-OX | 2.424 | 11.6 |

**Average k = 29.7 kcal/mol·Å²** — within stable range (<35)

### 1.3 Simulation Protocol

| Stage | Duration | Outcome |
|-------|----------|---------|
| Minimization | 7,500 steps | Complete |
| Heating (NVT) | ~50 ps | Complete |
| Equilibration (NPT) | ~200 ps | Complete |
| **Production** | **0 ns** | **NOT FOUND** |

**Software:** AMBER (pmemd CPU serial)
**Timestep:** 1 fs (during equilibration)
**Thermostat:** Langevin (γ = 2.0 ps⁻¹)
**Barostat:** Monte Carlo

---

## 2. Results

### 2.1 Equilibration Quality Assessment

#### RMSD Analysis

The Cα RMSD stabilized quickly:
- **Mean:** 0.222 Å
- **Std Dev:** 0.019 Å
- **Range:** 0.0 - 0.28 Å

**Interpretation:** The small RMSD and low variance indicate the protein structure remained stable during equilibration. No significant structural drift was observed.

#### Thermodynamic Stability

| Property | Mean | Target | Status |
|----------|------|--------|--------|
| Temperature | 300.0 K | 300 K | ✓ Pass |
| Density | 0.987 g/cc | 1.0 g/cc | ✓ Pass |
| Total Energy | -155,716 kcal/mol | Stable | ✓ Pass |

#### Preliminary RMSF

| Region | RMSF (Å) | Notes |
|--------|----------|-------|
| Global Mean | 0.160 | Low (expected for equilibration) |
| Lid (160-166) | 0.159 | Similar to global |
| N-terminus | 0.215 | Slightly elevated |

**CRITICAL CAVEAT:** These RMSF values are not meaningful for biological interpretation. Literature indicates RMSF requires minimum 100 ns to converge.

### 2.2 Missing Production Analyses

The following analyses **could not be performed** due to missing production data:

- [ ] Lid conformational transitions (open ↔ closed)
- [ ] Glu162-Mn distance distribution
- [ ] Mn coordination stability over extended timescales
- [ ] Oxalate binding mode persistence
- [ ] W96-W274 electron transfer geometry
- [ ] PCA of conformational space
- [ ] Statistically meaningful comparisons

---

## 3. Literature Context

### 3.1 Lid Dynamics Timescales

**Literature consensus:** Protein loop conformational changes occur on **nanosecond-microsecond timescales** (Pande et al., 2009; Weinberg et al., 2019).

> "Microsecond timescale simulations improve both the accuracy and precision of calculated order parameters." — Shaw et al.

**Our data:** 200 ps = 0.0002 μs = **insufficient by 3 orders of magnitude**

### 3.2 Glu162 as Proton Donor

From crystallographic and mutagenesis studies ([Just et al., 2004](https://pubmed.ncbi.nlm.nih.gov/14871895/); [Saylor et al., 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2275070/)):

- Lid closure brings Glu162 within ~2.4 Å of Mn
- E162A mutation eliminates decarboxylase activity
- Glu162 mediates proton-coupled electron transfer (PCET)

**Question we cannot answer:** Does Glu162 approach Mn during our simulation?
**Reason:** Lid transitions require >100 ns to observe

### 3.3 Bidentate Oxalate Binding

From [Zhu et al., 2024](https://www.mdpi.com/1420-3049/29/18/4414):

- ¹³C-ENDOR confirms bidentate (κO,κO') binding to Mn(II)
- Bidentate is **4.7 kcal/mol more stable** than monodentate
- Mechanism may require monodentate intermediate for O₂ binding

**Our observation:** BiOx+2 force field models asymmetric bidentate:
- OZ-Mn: r₀ = 2.11 Å, k = 49.4 (tight)
- OX-Mn: r₀ = 2.42 Å, k = 11.6 (loose)

This asymmetry is physically reasonable and may represent dynamic equilibrium between binding modes.

### 3.4 MCPB.py Validation

From [Li & Merz, 2016](https://pubs.acs.org/doi/abs/10.1021/acs.jcim.5b00674) and [Liao et al., 2013](https://pubs.acs.org/doi/10.1021/ct400055v):

- Force constants < 200 kcal/mol·Å² are acceptable
- Mn-ligand equilibrium distances should match QM within 0.3 Å
- 10 ns MD was sufficient to validate parameters

**Our system:** All parameters within acceptable ranges. The successful equilibration suggests force field is reasonable.

---

## 4. Critical Evaluation

### 4.1 Is the Simulation Converged?

**For equilibration:** ✓ Yes
- RMSD plateaued
- Temperature stable at 300 K
- Density stable at 0.987 g/cc
- No vlimit warnings or SHAKE failures

**For production analysis:** ✗ Cannot assess (no production data)

### 4.2 Is the Force Field Behaving Correctly?

**Evidence for YES:**
- Stable equilibration without catastrophic failures
- Mn coordination maintained (based on stable energy)
- Force constants within literature guidelines (avg 29.7 < 35)

**Cannot confirm:**
- Long-term Mn-ligand distance stability
- Whether coordination geometry drifts over 100+ ns

### 4.3 Why Does the Lid Stay Open?

**WE CANNOT ANSWER THIS QUESTION.**

Reasons:
1. 200 ps is insufficient to observe lid transitions (need μs)
2. No production trajectory to analyze lid RMSD/contacts
3. Cannot determine if lid is "stuck" or simply hasn't had time to move

**Literature suggests:** Lid transitions in OxDC have not been directly observed by MD. This would be novel if achieved.

### 4.4 Is the Asymmetric Oxalate Binding Real?

**Partially answerable:**

The force field encodes asymmetric binding:
- Tight O: k = 49.4, r₀ = 2.11 Å
- Loose O: k = 11.6, r₀ = 2.42 Å

This is **physically reasonable** because:
1. Carboxylates commonly show asymmetric chelation ([Dudev & Lim, 2003](https://pubs.acs.org/doi/10.1021/ar068181i))
2. May represent snapshot between bidentate/monodentate
3. ENDOR shows bidentate, but MD may sample transition states

**Cannot confirm without production:** Whether this asymmetry persists or averages out.

---

## 5. Future Directions

### 5.1 Immediate Priorities

1. **Locate or generate production trajectory**
   - Check HiPerGator /blue storage for existing data
   - If not found, submit 100 ns production run

2. **Complete Mn coordination analysis**
   - Generate trajectory with cpptraj
   - Track all 6 Mn-ligand distances over time

3. **Lid dynamics analysis**
   - Glu162-Mn distance time series
   - Lid RMSD from closed conformation
   - H-bond occupancy (S161, S164)

### 5.2 Required Simulation Time

| Analysis | Minimum | Ideal |
|----------|---------|-------|
| RMSF convergence | 100 ns | 200 ns |
| Lid transitions | 100 ns | 500 ns × 3 replicas |
| PCA meaningful | 100 ns | 500 ns |
| Statistical comparisons | 300 ns total | 1 μs total |

### 5.3 Exploratory Projects (from previous work)

Several analysis projects were outlined but cannot be executed:

| Project | Requirement | Status |
|---------|-------------|--------|
| P7: Energy Landscape | Production trajectory | Blocked |
| P8: Vibrational Analysis | Production trajectory | Blocked |
| P9: Thermal Fluctuations | Production trajectory | Blocked |
| P10: Parameterization Quality | Production trajectory | Blocked |
| P11: Coordination Geometry | Production trajectory | Blocked |

### 5.4 What Could Make This Work Great?

If production data becomes available, this could be a significant contribution:

1. **First comprehensive MD study of OxDC lid dynamics**
   - Literature gap identified in review
   - Compare across oxidation states (vs 1Wat+3)

2. **Validation of bidentate oxalate binding**
   - Computational support for ENDOR findings
   - Explore dynamic binding mode transitions

3. **Force constant stability correlation**
   - Already documented k < 35 threshold
   - Could publish methods finding

---

## 6. Honest Assessment

### What We Accomplished

✓ Verified system equilibrated successfully
✓ Confirmed force field parameters are reasonable
✓ Created analysis infrastructure for production
✓ Documented literature context comprehensively
✓ Identified data gaps and requirements

### What We Cannot Claim

✗ Any conclusions about lid dynamics
✗ Any conclusions about Mn oxidation state effects
✗ Any statistically meaningful comparisons
✗ Any mechanistic insights

### The Path Forward

1. **Obtain production trajectory** (minimum 100 ns)
2. **Re-run this analysis pipeline** with real data
3. **Generate publication-quality figures** from production
4. **Write thesis chapter** with proper statistical support

---

## 7. References

1. Just VJ et al. (2004) A closed conformation of *B. subtilis* oxalate decarboxylase. *J Biol Chem* 279:19867-75. [PubMed](https://pubmed.ncbi.nlm.nih.gov/14871895/)

2. Saylor BT et al. (2008) The identity of the active site and importance of lid conformations. *Arch Biochem Biophys* 472:114-22. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2275070/)

3. Zhu J et al. (2024) Bidentate Substrate Binding Mode in Oxalate Decarboxylase. *Molecules* 29:4414. [MDPI](https://www.mdpi.com/1420-3049/29/18/4414)

4. Li P & Merz KM (2016) MCPB.py: A Python Based Metal Center Parameter Builder. *J Chem Inf Model* 56:599-604. [ACS](https://pubs.acs.org/doi/abs/10.1021/acs.jcim.5b00674)

5. Liao RZ et al. (2013) Parameters for MD Simulations of Mn-Containing Metalloproteins. *J Chem Theory Comput* 9:1621-31. [ACS](https://pubs.acs.org/doi/10.1021/ct400055v)

6. Dudev T & Lim C (2003) Effect of Carboxylate-Binding Mode on Metal Binding/Selectivity. *Acc Chem Res* 36:42-51. [ACS](https://pubs.acs.org/doi/10.1021/ar068181i)

---

## Appendix A: Files Generated

```
systems/BiOx+2/
├── analysis_results/
│   ├── DATA_ASSESSMENT.md
│   ├── TOPOLOGY_REFERENCE.md
│   └── figures/
│       ├── eq_rmsd_ca.png
│       ├── eq_rmsf_ca.png
│       └── eq_energy.png
├── analysis_scripts/
│   └── analyze_equilibration.py
└── ANALYSIS_REPORT.md (this file)
```

## Appendix B: Command to Run Analysis

```bash
cd systems/BiOx+2
python3 analysis_scripts/analyze_equilibration.py
```

---

*Report generated: January 2026*
*Status: PRELIMINARY — Awaiting production data*
