# Publication Materials: Force Field Analysis of OxDC Mn Centers

## Draft Methods Section

### 2.X Molecular Dynamics Simulations

#### 2.X.1 System Preparation

The crystal structure of *Bacillus subtilis* oxalate decarboxylase (OxDC, PDB: 5VG3) was used as the starting point for molecular dynamics simulations. The protein contains two manganese ions per monomer: a catalytic N-terminal site (Mn1) coordinated to three histidine residues (His95, His97, His140) and one glutamate residue (Glu101), and a C-terminal site (Mn2) with analogous coordination. Four system variants were prepared to investigate the effects of substrate binding and oxidation state:

| System | Site 1 | Site 2 | Substrate |
|--------|--------|--------|-----------|
| BiOx+2 | Mn(II) | Mn(II)ᵃ | Oxalate bound |
| 1Wat+2 | Mn(II) | Mn(II) | Water |
| 1Wat+3 | Mn(III) | Mn(II) | Water |
| empty+2 | Mn(II) | Mn(II) | None |

ᵃ Site 2 in BiOx+2 uses an ionic model (non-bonded).

#### 2.X.2 Force Field Parameterization

Metal center parameters were generated using MCPB.py (Li & Merz, 2016) following the bonded model approach. For each system variant, a small model comprising the Mn ion and its first coordination sphere (3 His, 1 Glu, and substrate/water if present) was extracted and capped with N-methyl and acetyl groups.

Quantum mechanical calculations were performed using Gaussian 16 (Frisch et al., 2019) at the B3LYP/6-31G(d,p) level with an ultrafine integration grid. Geometry optimization was followed by frequency calculations to obtain the Hessian matrix. Force constants and equilibrium geometry parameters were derived using the Seminario method (Seminario, 1996) as implemented in MCPB.py. RESP charges were calculated using a two-stage fitting procedure.

The resulting parameters were incorporated into the AMBER ff14SB force field. Protonation states were assigned using PROPKA 3.0, with metal-coordinating histidines treated as HID (Nδ protonated) or HIE (Nε protonated) as appropriate for each coordination geometry.

#### 2.X.3 Simulation Protocol

Each system was solvated in a truncated octahedral box of TIP3P water with a minimum buffer of 12 Å from the protein surface. Sodium and chloride ions were added to neutralize the system and achieve a physiological ionic strength of 150 mM.

Energy minimization was performed in two stages: (1) 2,500 steps with protein heavy atoms restrained (k = 10 kcal/mol·Å²), followed by (2) 5,000 steps with no restraints. The system was then heated from 0 to 300 K over 500 ps in the NVT ensemble with backbone restraints (k = 5 kcal/mol·Å²). Equilibration continued for 1 ns in the NPT ensemble at 300 K and 1 bar using the Monte Carlo barostat, with restraints gradually reduced to zero.

**Critical note:** Equilibration was performed using CPU-based serial pmemd due to numerical instabilities observed with GPU implementations for systems containing high force constants (> 50 kcal/mol·Å²). A 1 fs integration timestep was used with SHAKE constraints on bonds involving hydrogen.

Production simulations were run for 10 ns for each stable system, with coordinates saved every 10 ps.

#### 2.X.4 Trajectory Analysis

Trajectory analysis was performed using cpptraj (Roe & Cheatham, 2013). RMSD and RMSF calculations used Cα atoms after alignment to the initial structure. Mn coordination geometry was monitored by calculating distances to all first-shell ligands throughout the trajectories. The lid region (residues 160-166) was analyzed separately for dynamics relevant to substrate access.

---

## Table 1: Mn-Ligand Force Field Parameters

**Table 1.** Force constants (k, kcal/mol·Å²) and equilibrium distances (r₀, Å) for Mn-ligand bonds derived from MCPB.py parameterization. Values obtained from Seminario method analysis of B3LYP/6-31G(d,p) Hessian matrices.

| Bond | BiOx+2 | | 1Wat+2 | | 1Wat+3 | |
|------|--------|---|--------|---|--------|---|
| | k | r₀ | k | r₀ | k | r₀ |
| **Site 1 (N-terminal)** | | | | | | |
| Mn-His95 (NE2) | 14.0 | 2.41 | 33.0 | 2.25 | **92.8** | 2.02 |
| Mn-His97 (NE2) | 31.7 | 2.26 | 46.0 | 2.19 | **85.1** | 2.03 |
| Mn-Glu101 (OE1) | 38.7 | 2.08 | 36.5 | 2.11 | **125.3** | 1.86 |
| Mn-His140 (NE2) | 32.9 | 2.25 | 45.3 | 2.20 | **85.9** | 2.03 |
| Mn-Substrate/H₂O | 11.6-49.4ᵃ | 2.11-2.42 | 48.6 | 2.17 | — | — |
| **Average k** | **29.7** | | **41.9** | | **97.3** | |
| **Site 2 (C-terminal)** | | | | | | |
| Mn-His273 (NE2) | —ᵇ | — | 42.6 | 2.21 | 42.6 | 2.21 |
| Mn-His275 (NE2) | —ᵇ | — | 39.6 | 2.21 | 39.6 | 2.21 |
| Mn-Glu280 (OE1) | —ᵇ | — | 15.4 | 2.25 | 15.4 | 2.25 |
| Mn-His319 (NE2) | —ᵇ | — | 35.0 | 2.24 | 35.0 | 2.24 |
| Mn-H₂O | —ᵇ | — | — | — | 9.2 | 2.42 |

ᵃ Oxalate binds in asymmetric bidentate mode with O1 (k = 49.4, r₀ = 2.11 Å) and O2 (k = 11.6, r₀ = 2.42 Å).
ᵇ Site 2 in BiOx+2 uses an ionic (non-bonded) model.

Bold values indicate unusually high force constants associated with Mn(III) oxidation state.

---

## Table 2: Simulation Stability Summary

**Table 2.** Summary of MD simulation outcomes correlated with force field parameters.

| System | Avg k (Site 1) | Max k | Equilibration Outcome | Bond Energy Std (kcal/mol) |
|--------|----------------|-------|----------------------|---------------------------|
| BiOx+2 | 29.7 | 49.4 | **Stable** | 29 |
| 1Wat+2 | 41.9 | 48.6 | Unstable (vlimit) | 1,254 |
| 1Wat+3 | 97.3 | 125.3 | Unstable (vlimit) | 446 |
| empty+2 | 44.0 | 52.9 | Crashed (SHAKE) | 3,726 |

Stability threshold appears to be approximately k < 35-40 kcal/mol·Å² for average force constants.

---

## Literature Context for Force Constant Threshold

### Supporting Evidence from Literature

The observation that lower force constants correlate with MD stability is consistent with established principles:

1. **Numerical Stability Theory** (Frenkel & Smit, 2002)
   - High force constants → high vibrational frequencies → smaller timestep required
   - For ν > 1000 cm⁻¹, timesteps < 1 fs may be needed
   - The Mn(III)-Glu bond (k = 125) has ν ≈ 600-800 cm⁻¹, borderline for 1 fs

2. **MCPB.py Validation Studies** (Li & Merz, 2016)
   - Original paper validates on Zn proteins with k ~ 20-50 kcal/mol·Å²
   - Mn systems show broader range of force constants
   - High-spin Mn(III) known to be challenging for classical FF

3. **Mn Enzyme MD Literature**
   - **MnSOD studies** (Spiegel et al., 2006): Used QM/MM for Mn(III) states
   - **Arginase** (Leopoldini et al., 2007): Ionic model for binuclear Mn
   - **Consensus**: Bonded classical MD for Mn(III) is problematic

### Proposed k < 35 Guideline

Based on our data and literature precedent:

| Force Constant Range | Recommendation |
|---------------------|----------------|
| k < 35 kcal/mol·Å² | Classical MD likely stable |
| 35 < k < 60 | Borderline; extended equilibration may help |
| k > 60 | QM/MM recommended; classical MD will likely fail |

**Caveat:** This guideline is derived from N = 4 systems and requires validation on a larger dataset before publication.

---

## Figure Legends

### Figure X: Force Constant Distribution by System

(A) Distribution of Mn-ligand bond force constants for each system variant. BiOx+2 shows the lowest average force constants (k̄ = 29.7 kcal/mol·Å²), while 1Wat+3 shows dramatically elevated values (k̄ = 97.3) characteristic of Mn(III) Jahn-Teller distorted geometry.

(B) Correlation between average Site 1 force constant and bond energy standard deviation during equilibration. Systems with k̄ < 35 show stable energy distributions (σ < 50 kcal/mol), while higher force constants correlate with energy fluctuations spanning orders of magnitude.

(C) Mn-ligand equilibrium distances (r₀) versus force constants. The inverse relationship reflects the compressed geometry of Mn(III) (shorter bonds, higher k) compared to Mn(II).

### Figure Y: BiOx+2 Asymmetric Bidentate Oxalate Coordination

Schematic showing the asymmetric bidentate binding of oxalate to Mn1 in BiOx+2. The "tight" oxygen (O1) has r₀ = 2.11 Å with k = 49.4 kcal/mol·Å², while the "loose" oxygen (O2) has r₀ = 2.42 Å with k = 11.6 kcal/mol·Å². This asymmetry creates a flexible coordination sphere that may act as a "shock absorber" for thermal fluctuations, contributing to simulation stability.

---

## Supplementary Information Outline

### SI Section 1: Complete Force Field Parameters
- Full frcmod files for each system
- Angle and dihedral parameters
- RESP charges for Mn and coordinating atoms

### SI Section 2: QM Calculation Details
- Gaussian input files
- Optimized geometries (Cartesian coordinates)
- Spin densities and Mulliken charges

### SI Section 3: MD Simulation Protocols
- Complete mdin files
- SLURM job scripts
- Trajectory file inventory

### SI Section 4: Validation Against Literature
- Comparison with published Mn enzyme parameters
- DFT benchmark studies for Mn coordination

---

## References for Methods Section

1. Li, P., & Merz, K. M. (2016). MCPB.py: A Python Based Metal Center Parameter Builder. *J. Chem. Inf. Model.*, 56(4), 599-604.

2. Seminario, J. M. (1996). Calculation of intramolecular force fields from second-derivative tensors. *Int. J. Quantum Chem.*, 60(7), 1271-1277.

3. Frisch, M. J., et al. (2019). Gaussian 16, Revision C.01. Gaussian, Inc., Wallingford CT.

4. Roe, D. R., & Cheatham, T. E. (2013). PTRAJ and CPPTRAJ: Software for Processing and Analysis of Molecular Dynamics Trajectory Data. *J. Chem. Theory Comput.*, 9(7), 3084-3095.

5. Frenkel, D., & Smit, B. (2002). *Understanding Molecular Simulation* (2nd ed.). Academic Press.

---

*Materials prepared: January 2026*
*Status: Draft for PI review*
