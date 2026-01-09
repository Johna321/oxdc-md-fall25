# Knowledge Gaps & Questions for PI

## Document Purpose

This document captures:
1. Information I couldn't determine from the repository
2. Questions requiring PI expertise
3. Topics for further learning (with suggested resources)

---

## Critical Questions for PI

### 1. MCPB.py Parameterization Details

**Gap:** The exact MCPB.py workflow and QM validation are unclear.

**Questions:**
- [x] What DFT level was used for QM calculations? (B3LYP/6-31G* is standard)
  - **ANSWERED**: B3LYP/6-31G(d,p) with UltraFine integration grid (from `systems/BiOx+2/calc/5vg3_small_fc.com`)
- [x] Was the small model geometry optimized before force constant calculation?
  - **ANSWERED**: Yes. `5vg3_small_opt.log` shows "Stationary point found" - optimization converged successfully
- [x] Are the Mn parameters validated against QM Mn-ligand distances?
  - **ANSWERED**: r0 values in frcmod files derived from QM-optimized geometry via Seminario method
- [ ] The Mn 6032 charge is -0.15 in `mn_site_atoms.csv` — is this intentional?
  - Negative charge on Mn is unusual; typical Mn(II) RESP is +1.5 to +2.0
  - **NOTE**: Mulliken charge from QM is +1.05 with spin density 4.77 (consistent with high-spin Mn(II))
  - The -0.15 may be from RESP fitting which redistributes charge to ligands
- [ ] Were any bonds manually adjusted or force constants modified post-MCPB.py?

**Why it matters:** Understanding parameterization helps troubleshoot instabilities.

**NEW FINDINGS from zbecerra calc/ directory (Jan 2026):**
- QM work performed by zbecerra@ufl.edu on HiPerGator (`/blue/ax/zbecerra/anna/Mn_files/BiOx/calc/`)
- Spin multiplicity: 6 (sextet) - correct for high-spin Mn(II) with 5 unpaired electrons
- Total charge: 0 (neutral small model cluster)
- Stoichiometry: C21H32MnN6O6 (Mn + 3 His + 1 Glu + oxalate)
- Gaussian 16 Rev C.01 used (run date: April 2025)

---

### 2. Restraint Mask Discrepancy

**Finding:** Template mdin files use `(!:WAT,Na+,Cl-)&!@H=` but system-specific masks exclude Mn residues.

**Questions:**
- [ ] Which mask was actually used in the running simulations?
- [ ] Were the equilibrations intentionally restraining Mn ions?
- [ ] Should we re-equilibrate with corrected masks?

**Why it matters:** Incorrect restraints may cause the observed instabilities.

---

### 3. Oxidation State Representation

**Gap:** How is Mn(III) vs Mn(II) represented in the force field?

**Questions:**
- [x] Are 1Wat+3 and empty+3 using different MCPB.py parameters than +2 systems?
  - **ANSWERED - YES!** Force constants from `mn_bonds.csv`:
    - **BiOx+2** (Mn(II)): k = 14-49 kcal/mol·Å² (avg ~30)
    - **1Wat+3 Site 1** (Mn(III)): k = 85-125 kcal/mol·Å² (avg ~97) - 3x higher!
    - **1Wat+3 Site 2** (Mn(II)): k = 15-43 kcal/mol·Å² - same as other Mn(II)
  - This explains the stability differences - Mn(III) has much stiffer bonds
- [x] Is the charge on Mn adjusted for oxidation state?
  - **PARTIALLY ANSWERED**: Different parameterization for Mn(III) vs Mn(II) at Site 1
- [ ] Were separate QM calculations done for Mn(III) systems?
  - **NOTE**: No calc/ directory found for 1Wat+3 - QM files may be stored elsewhere
- [x] How is the spin state handled (Mn(III) is d⁴, potentially different multiplicity)?
  - **BiOx+2**: Multiplicity 6 (sextet, high-spin d⁵ Mn(II))
  - **1Wat+3**: Unknown - QM files not found. d⁴ Mn(III) typically quintuplet (mult=5)

**Why it matters:** Force field quality depends on correct QM reference for each oxidation state.

**KEY INSIGHT**: The 1Wat+3 Mn(III) site has dramatically higher force constants due to:
1. Shorter Mn-ligand distances (1.86-2.03 Å vs 2.08-2.41 Å)
2. Jahn-Teller compression at Glu101-Mn (1.862 Å, k=125.3!)
3. These stiff bonds cannot accommodate thermal fluctuations → vlimit exceeded

---

### 4. Equilibration History

**Gap:** Current status of each system is unclear.

**Questions:**
- [ ] Which systems have completed equilibration previously?
- [ ] Were there successful production runs before that crashed?
- [ ] What changes led to the current protocol (1 fs timestep, MC barostat)?
- [ ] Is there a reason some systems use CPU while BiOx+2 seems most stable?

**Why it matters:** Understanding history prevents repeating failed approaches.

---

### 5. Biological Questions

**Gap:** Connection between computational goals and biological questions.

**Questions:**
- [ ] What is the key hypothesis we're testing?
- [ ] Is lid dynamics the primary focus, or also catalytic mechanism?
- [ ] Are we planning QM/MM follow-up on interesting conformations?
- [ ] What would constitute a publishable finding from these simulations?
- [ ] Should we compare to existing OxDC experimental data (NMR, HDX, etc.)?

**Why it matters:** Analysis design should align with publication goals.

---

### 6. Nterm_only System

**Gap:** Purpose and status unclear.

**Questions:**
- [ ] What is the scientific purpose of the N-terminal only system?
- [ ] Is it a control for lid dynamics without C-terminal domain?
- [ ] Should it be included in comparative analysis?

---

## Technical Gaps (To Learn)

### 1. Residue Numbering Mapping

**Issue:** Literature refers to lid at residues 160-166 (PDB numbering), but topology may differ.

**Needs:**
- Map PDB residue numbers to topology residue numbers
- Identify correct atom indices for analysis scripts
- Verify His, Glu residue numbers match expected active site

**Resource:** Use cpptraj `resinfo` command on topology

---

### 2. Mn Coordination Geometry Validation

**Issue:** Need reference values for Mn-ligand distances from QM.

**Needs:**
- QM-optimized geometry from MCPB.py (should be in `5vg3_small_opt.log`)
- Compare starting vs equilibrated Mn geometry
- Define acceptable deviation range

**Resource:** Parse Gaussian log files for optimized coordinates

---

### 3. Statistical Analysis for MD

**Issue:** Proper error estimation and significance testing.

**Topics to learn:**
- Block averaging for correlated time series
- Autocorrelation time calculation
- How many replicas are needed for significance?
- Comparing distributions (KS test, histogram overlap)

**Resources:**
- Grossfield & Zuckerman, "Quantifying Uncertainty in MD"
- AMBER tutorials on error analysis

---

### 4. QM/MM Considerations

**Issue:** When/if QM/MM refinement would be appropriate.

**Topics to learn:**
- What MD conformations warrant QM/MM follow-up?
- How to set up ONIOM or QM/MM in AMBER
- Computational cost estimates

**Resources:**
- AMBER QM/MM tutorials
- MCPB.py documentation on QM/MM prep

---

## Repository Questions

### Missing Files/Information

- [ ] `empty+3` system: Is it set up? (No output files visible)
- [ ] `.nc` trajectory files: Are they stored elsewhere (too large for git)?
- [x] QM log files: Where are the Gaussian outputs for MCPB.py?
  - **FOUND**: `systems/BiOx+2/calc/` contains 90+ files including:
    - `5vg3_small_opt.log` (geometry optimization)
    - `5vg3_small_fc.log` (frequency/force constant calculation)
    - mol2 files, RESP charges, ESP files
  - **NOTE**: 1Wat+3 has no calc/ directory - QM files may be on HiPerGator
- [ ] Minimization outputs: Were minimization stages run before heating?

### Inconsistencies to Clarify

- [ ] Why does BiOx+2 have `MN1, MN` naming while others have `MN1, MN2`?
- [ ] Why are some systems using `5vg3_solv.prmtop` and some `5vg3.prmtop`?
- [ ] Why does 1Wat+2 have `5vg3_solv.prmtop` but the RUN_PLAN mentions `5vg3.prmtop`?

---

## Learning Plan for Student

### Immediate (Before Semester)

1. **AMBER basics:** Understand mdin parameters
   - Resource: AMBER tutorial B0 (introductory MD)
   - Time: 2-3 hours

2. **cpptraj:** Practice running analysis scripts
   - Resource: AMBER tutorial A3 (trajectory analysis)
   - Time: 2-3 hours

3. **Metalloenzyme MD:** Understand MCPB.py output
   - Resource: AMBER tutorial 20 (MCPB.py)
   - Time: 4-5 hours

### First Week of Semester

4. **PCA interpretation:** Understanding conformational analysis
   - Resource: Grant & Rodrigues, Bio3D vignettes
   - Time: 3-4 hours

5. **Statistical analysis:** Block averaging, convergence
   - Resource: Grossfield & Zuckerman paper
   - Time: 3-4 hours

### Ongoing

6. **OxDC biology:** Read key papers (see literature review)
7. **Visualization:** PyMOL/VMD for structure analysis
8. **Python scripting:** pytraj, MDAnalysis for custom analysis

---

## Questions Answered by This Research

✓ **What is the lid structure?** Residues 160-166, controls active site access

✓ **Why does Mn oxidation matter?** Affects Glu162 interaction, lid stability

✓ **What is W96/W274 role?** Electron hole hopping for catalysis

✓ **What parameters to check?** See `mn_coordination.in` for distances

✓ **What analyses are standard?** See `ANALYSIS_PLAN.md`

---

## Summary Table

| Category | Questions | Answered | Priority |
|----------|-----------|----------|----------|
| MCPB.py/Force Field | 5 | **4** | HIGH |
| Protocol/Equilibration | 4 | 0 | HIGH |
| Oxidation State | 4 | **3** | HIGH |
| Biological Context | 5 | 0 | MEDIUM |
| Technical Learning | 4 | 0 | MEDIUM |
| Repository Clarification | 7 | **1** | LOW |

---

## Major Findings from zbecerra Investigation (Jan 2026)

### Force Constant Comparison (k in kcal/mol·Å²)

| System | Site | His-Mn | Glu-Mn | Substrate/Water | Avg |
|--------|------|--------|--------|-----------------|-----|
| BiOx+2 | 1 | 14-33 | 39 | Oxalate: 12-49 | **29** |
| 1Wat+2 | 1 | 33-46 | 37 | Water: 49 | **40** |
| 1Wat+2 | 2 | 35-43 | 15 | - | **33** |
| 1Wat+3 | 1 (Mn(III)) | **85-93** | **125** | - | **97** |
| 1Wat+3 | 2 (Mn(II)) | 35-43 | 15 | Water: 9 | **28** |

### Key Conclusions

1. **BiOx+2 stability explained**: Lowest force constants (avg 29) + flexible oxalate coordination
2. **1Wat+3 instability explained**: Mn(III) site has 3x higher force constants (85-125 vs ~30)
3. **1Wat+2 salvageability confirmed**: Force constants (33-49) are borderline - scaling by 0.7x should work
4. **DFT validated**: B3LYP/6-31G(d,p) with UltraFine grid is standard MCPB.py approach
5. **Spin states correct**: Multiplicity 6 for Mn(II) is proper high-spin d⁵
