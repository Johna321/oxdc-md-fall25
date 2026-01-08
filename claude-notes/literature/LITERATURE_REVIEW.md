# OxDC MD Literature Review

**Compiled:** January 2026
**Purpose:** Inform production MD setup, analysis design, and thesis writing for OxDC metalloenzyme simulations

---

## Table of Contents
1. [OxDC Structure & Mechanism](#1-oxdc-structure--mechanism)
2. [Flexible Loop (Lid) Dynamics](#2-flexible-loop-lid-dynamics)
3. [Electron Transfer & Mn Coordination](#3-electron-transfer--mn-coordination)
4. [Related Mn Enzyme MD Studies](#4-related-mn-enzyme-md-studies)
5. [MCPB.py Parameterization](#5-mcpbpy-parameterization)
6. [Metalloenzyme MD Best Practices](#6-metalloenzyme-md-best-practices)
7. [Key Papers to Read in Full](#7-key-papers-to-read-in-full)
8. [Analysis Implications](#8-analysis-implications)

---

## 1. OxDC Structure & Mechanism

### Enzyme Overview
- **Source:** *Bacillus subtilis* stress-induced enzyme (low pH response)
- **PDB 5VG3:** Structure at pH 4.6 (Angerhofer & Burg, 2017) — **your reference structure**
- **Quaternary structure:** Hexamer (264 kDa), two trimeric units, bicupin superfamily
- **Reaction:** Oxalate → CO₂ + formate (redox-neutral disproportionation)
- **Cofactors:** Mn²⁺/Mn³⁺ (both domains), O₂ (obligatory co-catalyst)

### Active Site Location Debate
| Site | Domain | Residue # | Proposed Function |
|------|--------|-----------|-------------------|
| Site 1 | N-terminal | ~56-233 | **Catalytic** (current consensus) |
| Site 2 | C-terminal | ~234-379 | Structural / electron donor |

**Evidence for Site 1 catalytic role:**
- Contains substrate channel (open/closed conformations)
- Formate ion bound in crystal structures
- Glu162 positioned as proton donor
- D297A/H299A mutations (remote from Site 2) reduced Vmax 50% by disrupting lid H-bonds

### Substrate Binding Mode
**Controversy:** Mono- vs. bidentate oxalate coordination

| Study | Method | Finding |
|-------|--------|---------|
| Early mechanistic | Assumed | Monodentate (to accommodate O₂) |
| ENDOR ¹³C-oxalate | Experimental | **Bidentate** (κO,κO') confirmed |
| QM/MM ongoing | Computational | Exploring dynamic binding modes |

**Implication for your sims:** BiOx+2 system models bidentate coordination — validate this during production

---

## 2. Flexible Loop (Lid) Dynamics

### Critical Structural Element
**Lid residues: 160-166** (some sources cite 161-165)

The lid controls:
1. Substrate access to active site
2. Solvent exclusion during catalysis
3. Intermediate radical protection
4. Catalytic specificity (decarboxylase vs oxidase)

### Key Residues

| Residue | Role | Mutation Effect |
|---------|------|-----------------|
| **Ser161** | H-bond in closed conformation | S161A: Km ↑10×, activity 15% |
| **Glu162** | Proton donor, gating | E162A: eliminates decarboxylase |
| **Ser164** | H-bond in open conformation | Stabilizes open state |
| **Thr165** | Conformational flexibility | T165P: activity 3% (restricted lid) |
| **Asp297** | Inter-subunit H-bond (open lid) | Remote from Site 2; D297A Vmax 50% |
| **His299** | Inter-subunit H-bond (open lid) | H299A similar effect |

### Conformational States
1. **Open:** Substrate entry, Glu162 away from Mn
2. **Closed:** Glu162 approaches Mn (~2.4Å), 3₁₀ helix forms, solvent excluded

**Analysis target:** Monitor lid RMSD/dihedral angles, Glu162-Mn distance, H-bond occupancy to S161/S164

### Literature Gap
> "Very few MD studies have examined OxDC lid dynamics directly. Most computational work is QM/MM on active site."

**Your thesis opportunity:** First comprehensive MD study of lid dynamics across oxidation states

---

## 3. Electron Transfer & Mn Coordination

### Inter-subunit Electron Hopping
**Tryptophan pair W96/W274** forms π-stacked bridge between subunits

| Parameter | Value |
|-----------|-------|
| Intra-subunit Mn-Mn distance | 25.9 Å |
| Inter-subunit Mn-Mn distance | **21.5 Å** (via W96/W274) |
| Mn → indole ring distance | ~8.4 Å |
| Hop length | ~8.5 Å × 2 |

### Experimental Validation
| Mutation | Activity | Interpretation |
|----------|----------|----------------|
| W→F | ~10% WT | Hopping eliminated |
| W→Y | ~80% WT | Redox properties preserved |

### Proposed Mechanism
1. O₂ binds at C-terminal Mn (Site 2)
2. Electron hole hops via W274 → W96
3. N-terminal Mn oxidizes to Mn³⁺
4. Mn³⁺ activates substrate for decarboxylation

**Analysis target:** Monitor W96-W274 distance, stacking geometry, Mn coordination geometry

### Mn Coordination Environments (from your topology)

**BiOx+2 Site 1 (Mn 6032):**
| Ligand | Atom | Distance (Å) | Notes |
|--------|------|--------------|-------|
| HD1 | NE2 | 2.241 | His |
| HD2 | NE2 | 2.441 | His |
| GU1 | OE1 | 2.040 | Glu |
| HD3 | NE2 | 2.222 | His |
| OX1 | OZ | 1.747 | **Oxalate** |
| OX1 | OX | 1.306 | **Oxalate** (SHORT flag) |

**BiOx+2 Site 2 (Mn 6033):**
| Ligand | Atom | Distance (Å) | Notes |
|--------|------|--------------|-------|
| HID | NE2 | 2.203 | His |
| HIP | NE2 | 2.181 | His |
| GLU | OE1 | 2.051 | Glu |
| HIP | NE2 | 2.274 | His |

**Flags:** Site 1 SHORT (1.306 Å bond), Site 2 SPARSE (CN=4)

---

## 4. Related Mn Enzyme MD Studies

### MnSOD (Manganese Superoxide Dismutase)

**Why relevant:** Well-studied Mn enzyme with similar coordination chemistry

| Aspect | MnSOD | OxDC |
|--------|-------|------|
| Mn geometry | Trigonal bipyramidal | Octahedral |
| Ligands | 3 His + 1 Asp + OH⁻/H₂O | 3 His + 1 Glu + substrate |
| Cycle | Mn²⁺ ↔ Mn³⁺ | Mn²⁺ ↔ Mn³⁺ |
| O₂ role | Substrate | Co-catalyst |

**Key MnSOD MD findings:**
- QM/MM accurately reproduced reduction potentials (0.30±0.01 V calc vs 0.26-0.40 V exp)
- Y34 nitration affects dynamics → restricts ligand access
- Five-coordinate ↔ six-coordinate equilibrium at 296K

### Arginase

**Why relevant:** Binuclear Mn enzyme with QM/MM studies

**Key findings:**
- Mn ions play **structural/electrostatic** role (not direct charge transfer)
- OH⁻ bridging two Mn is the nucleophile
- Metal ions critical for active site geometry maintenance
- "Metal coordinating regions remained motionless" while loops showed high plasticity

**Implication:** Expect Mn coordination to be stable; lid dynamics are where the action is

---

## 5. MCPB.py Parameterization

### Validation Criteria (from AMBER tutorial)

| Parameter | Acceptable Range |
|-----------|------------------|
| Bond force constants (Mn-ligand) | < 200 kcal/(mol·Å²) |
| Equilibrium bond distance | < 2.8 Å |
| Angle force constants | < 100 kcal/(mol·rad²) |
| Equilibrium angles | > 100° |
| Metal RESP charge | < oxidation state |
| vdW radius | > 1.0 Å |

### Your System Status
From `mn_site_atoms.csv`:
- Mn 6032 charge: -0.15 (unusual — should verify)
- Mn 6033 charge: +2.0 (expected for Mn²⁺)

**Question for PI:** Was the Mn 6032 charge intentional? Negative charge on Mn is unusual.

### Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| Coordination bond breaks during QM | Try different DFT functional/basis |
| Distorted geometry in MD | Use harmonic restraints on Mn-ligand |
| vlimit exceeded | Reduce timestep, increase restraints |

### Your Observed Issues
- **empty+2:** Crashed ("Coordinate resetting cannot be accomplished")
- **1Wat+2/1Wat+3:** vlimit exceeded warnings

These suggest force field parameter problems or insufficient equilibration restraints.

---

## 6. Metalloenzyme MD Best Practices

### From Springer Chapter (Ryde et al.)

1. **Use bonded model** for tightly coordinated metals (MCPB.py approach)
2. **Validate against QM:** Compare Mn-ligand distances, angles with DFT
3. **Extended equilibration:** Metal sites need longer equilibration
4. **Multiple trajectories:** Run 3-5 replicas for statistics

### Equilibration Protocol Recommendations

| Stage | Duration | Restraints | Timestep |
|-------|----------|------------|----------|
| Minimization | 5000+ steps | Heavy atoms 10 kcal/mol·Å² | — |
| Heating (NVT) | 50-100 ps | Heavy atoms 5 kcal/mol·Å² | 1 fs |
| Eq1 (NPT) | 100-200 ps | Heavy atoms 2 kcal/mol·Å² | 1 fs |
| Eq2 (NPT) | 100-200 ps | Backbone 0.5 kcal/mol·Å² | 1-2 fs |
| Eq3 (NPT) | 200+ ps | None (or Mn-ligand only) | 2 fs |

### Production Recommendations

| Parameter | Recommended | Your Current |
|-----------|-------------|--------------|
| Timestep | 2 fs (SHAKE) | 1-2 fs ✓ |
| Barostat | Monte Carlo or MTTK | MC/Berendsen (eq), MTTK (prod) |
| Thermostat | Langevin (γ=2) | γ_ln=2.0 ✓ |
| Cutoff | 10-12 Å | Check current |
| Production length | 100-500 ns per replica | TBD |
| Replicas | 3-5 | 1 (current) |

### Statistical Significance
For loop dynamics, literature suggests:
- **Minimum:** 100 ns × 3 replicas = 300 ns aggregate
- **Ideal:** 500 ns × 5 replicas = 2.5 μs aggregate
- **Convergence metric:** Block averaging of RMSF, ensure plateau

---

## 7. Key Papers to Read in Full

### Must Read (directly relevant)

| Paper | DOI | Why Important |
|-------|-----|---------------|
| Just et al. 2004, JBC | 10.1074/jbc.M310849200 | Closed OxdC structure, lid importance |
| Saylor et al. 2012, Biochemistry | 10.1021/bi300255c | Lid mutations, specificity |
| Angerhofer et al. 2021, JBC | 10.1016/j.jbc.2021.100857 | **Electron hopping mechanism** |
| Reinhardt et al. 2003, Biochemistry | 10.1021/bi0200965 | Original 1.75Å structure |
| Zhu et al. (bidentate) | 10.3390/molecules29184414 | **Substrate binding mode** |

### Should Read (methodological)

| Paper | DOI | Why Important |
|-------|-----|---------------|
| Li & Merz, 2016, JCIM | 10.1021/acs.jcim.5b00674 | **MCPB.py methodology** |
| Liao et al. 2013, JCTC | 10.1021/ct400055v | Mn parameters for MD |
| Ryde et al., Springer | 10.1007/978-90-481-3034-4_11 | Metalloenzyme MD strategies |

### Recommended Reviews

| Paper | Topic |
|-------|-------|
| Frontiers Research Topic 2021 | MD of metalloproteins (editorial overview) |
| Neugebauer et al. 2024, JAFC | OxDC mechanisms review |

---

## 8. Analysis Implications

Based on this literature review, your analysis should address:

### Primary Questions

1. **Lid dynamics:** Do Mn oxidation state/ligand affect lid flexibility?
   - Compare RMSF of residues 160-166 across systems
   - Track Glu162 Cα-Mn distance over time
   - H-bond occupancy: S161-backbone, S164-backbone

2. **Mn coordination stability:** Do MCPB.py parameters maintain geometry?
   - Mn-ligand distances (target: within 0.3Å of starting)
   - Coordination number over time
   - Compare to QM reference if available

3. **Inter-subunit communication:** Does W96-W274 geometry remain conducive?
   - Inter-ring distance and angle
   - Correlation with any Mn events

4. **Substrate binding (BiOx+2):** Does bidentate mode persist?
   - Both Mn-O(oxalate) distances
   - Carboxylate plane orientation

### Specific Atom Masks (cpptraj)

```
# Lid residues (check exact numbering in your system)
:160-166@CA           # Lid Cα for RMSD
:162@CD,OE1,OE2       # Glu162 carboxylate
:161@CB,OG            # Ser161

# Mn coordination (BiOx+2)
@MN                   # Both Mn atoms
:382,383              # Mn residues
:OX1                  # Oxalate

# Tryptophan pair
:96@CG,CD1,CD2,CE2,CE3,CZ2,CZ3,CH2,NE1   # W96 indole
:274@CG,CD1,CD2,CE2,CE3,CZ2,CZ3,CH2,NE1  # W274 indole
```

---

## Citations

1. Just VJ et al. (2004) J Biol Chem 279:19867-19875. DOI: [10.1074/jbc.M310849200](https://doi.org/10.1074/jbc.M310849200)
2. Angerhofer A et al. (2021) J Biol Chem 297:100857. DOI: [10.1016/j.jbc.2021.100857](https://doi.org/10.1016/j.jbc.2021.100857)
3. Reinhardt LA et al. (2003) Biochemistry 42:4193-4202. DOI: [10.1021/bi0200965](https://doi.org/10.1021/bi0200965)
4. Li P & Merz KM (2016) J Chem Inf Model 56:599-604. DOI: [10.1021/acs.jcim.5b00674](https://doi.org/10.1021/acs.jcim.5b00674)
5. Liao RZ et al. (2013) J Chem Theory Comput 9:1621-1631. DOI: [10.1021/ct400055v](https://doi.org/10.1021/ct400055v)
6. Krebs C et al. (2007) Biochemistry 46:8069-8077. DOI: [10.1021/bi700947s](https://doi.org/10.1021/bi700947s)

---

*Document auto-generated from web research. Verify DOIs before citing.*
