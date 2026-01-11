# OxDC Lid Conformation Nomenclature: Research Clarification

**Date:** January 11, 2026
**Purpose:** Clarify the "open" vs "closed" lid nomenclature confusion in OxDC structures

---

## Executive Summary

### THE CRITICAL FINDING

**Our 10 ns simulation shows Glu162-Mn = 11.5 Å, which is the OPEN conformation.**

According to literature:
- **Open (1J58)**: Glu162 is ~10-12 Å from Mn (substrate entry/exit state)
- **Closed (1UW8)**: Glu162 is ~2-4 Å from Mn (catalytically active state)

**Our simulation started from 5VG3, which literature describes as having a "closed" conformation, yet our Glu162 is 11.5 Å from Mn (open).** This suggests either:
1. The lid opened during equilibration/production
2. The 5VG3 structure has mixed open/closed conformations across subunits
3. The nomenclature in the parameterization directory ("Closed_comfirmation") may be inaccurate

---

## 1. Key PDB Structures and Lid States

| PDB | Description | pH | Lid State | Glu162 Status |
|-----|-------------|-----|-----------|---------------|
| **1J58** | Original high-pH structure | ~7 | **OPEN** | Away from Mn (~10-12 Å) |
| **1UW8** | Just et al. 2004 | ~7 | **CLOSED** | Close to Mn (~2-4 Å), 3₁₀ helix |
| **5VG3** | Angerhofer 2017, active pH | 4.6 | **Ambiguous** | See below |

### 5VG3 Lid Status (Critical Ambiguity)

The literature describes 5VG3 in contradictory ways:

1. **"Closed conformation of 5VG3 provides the best structural model for the catalytically competent active site"** ([BioRxiv](https://www.biorxiv.org/content/10.1101/426874v1.full))

2. **"Using the 'open' configuration, where E162 does not occlude the accessibility of the active site"** ([BioRxiv](https://www.biorxiv.org/content/10.1101/426874v1.full))

**Resolution:** 5VG3 likely contains BOTH conformations across different subunits in the hexamer, with the analysis using the "open" configuration for channel accessibility studies.

---

## 2. What "Open" and "Closed" Really Mean

### Definition from [Just et al. 2004 JBC](https://pubmed.ncbi.nlm.nih.gov/14871895/)

The lid (residues 161-165, sometimes cited as 160-166) can exist in two conformations:

#### OPEN Conformation
- Glu162 is **away from Mn** (estimated ~10-12 Å)
- Substrate channel is **accessible**
- Glu162 forms H-bonds with Asp297, His299, Thr44
- Allows **substrate entry** and **product release**
- Observed in 1J58 crystal structure

#### CLOSED Conformation
- Glu162 is **close to Mn** (~2-4 Å)
- Lid forms a **3₁₀ helix**
- Active site is **shielded from solvent**
- Glu162 can act as **proton donor** during catalysis
- Observed in 1UW8 crystal structure

### Mechanistic Role

From [Saylor et al. 2007 Biochemistry](https://pubmed.ncbi.nlm.nih.gov/17680775/):

> "The flexibility and stability of lid conformations are important in catalysis... D297A and H299A mutations disrupted hydrogen bonds between the lid and a neighbouring subunit only when in the open conformation."

From [PMC2275070](https://pmc.ncbi.nlm.nih.gov/articles/PMC2275070/):

> "The original closed conformation of the SENST lid is only present in the absence of substrate or other small carboxylate ligands. E162 may not function as a transient base in shuttling a proton back and forth but rather as a gating mechanism that locks the loop in the closed conformation during catalysis."

---

## 3. Our Simulation Results vs. Literature

### What We Observed

| Metric                | Our Value    | Literature Interpretation |
| --------------------- | ------------ | ------------------------- |
| Glu162 CD - Mn1       | 11.5 ± 0.5 Å | **OPEN** conformation     |
| Glu162 OE1 - Mn1      | 11.7 ± 0.7 Å | **OPEN** conformation     |
| Glu162 OE2 - Mn1      | 12.3 ± 0.6 Å | **OPEN** conformation     |
| Open fraction         | 100%         | Persistent open state     |
| Transitions to closed | 0            | No lid closure events     |

### Expected for "Closed" Conformation

Based on [1UW8 structure](https://www.rcsb.org/structure/1UW8) and literature:
- Glu162 OE - Mn distance: **~2-4 Å**
- Should be within H-bonding distance of substrate/intermediates
- Should form 3₁₀ helix in lid region

**Our simulation does NOT show the closed conformation at any point.**

---

## 4. Possible Explanations

### Hypothesis 1: Lid Opened During Equilibration

5VG3 may have been crystallized with partial closed conformation, but during MD equilibration at 300K, the lid relaxed to the thermodynamically favored open state in Mn(II) oxidation state.

**Evidence for:**
- Mn(II) may favor open lid (different electrostatics than Mn(III))
- 10 ns is short; lid may not have time to re-close

**Evidence against:**
- Starting structure should have been closed if labeled "closed_comfirmation"

### Hypothesis 2: 5VG3 is Actually Open (or Mixed)

The 5VG3 structure may have the lid in open conformation despite being at active pH.

**Evidence for:**
- BioRxiv paper mentions using "open configuration" for analysis
- Acetate binding may not induce full closure
- Different subunits may have different conformations

### Hypothesis 3: Mn Oxidation State Controls Lid

Mn(II) (our simulation) vs Mn(III) (catalytic state) may have different lid equilibria.

**Evidence for:**
- Mn(III) has different charge and coordination preferences
- Literature emphasizes Mn(III) is required for catalysis
- Jahn-Teller distortion in Mn(III) may alter active site geometry

---

## 5. Parameterization Directory Naming

### The "Closed_comfirmation" Directory Issue

The parameterization directory is named `zbecerra-anna-closed_comf-BiOx/`, suggesting it was intended to be the "closed" conformation.

**Possible explanations:**
1. **Typo in directory name** ("comfirmation" → "conformation")
2. **Misunderstanding of lid state** at time of parameterization
3. **5VG3 was assumed to be closed** based on literature, but may actually have open lid
4. **Open/closed refers to something else** (e.g., substrate channel, not lid specifically)

### Recommendation

**We should measure the Glu162-Mn distance in the starting structure (5vg3_dry.pdb or equivalent) to determine the actual starting lid state before equilibration.**

---

## 6. Key Literature Sources

### Primary References

1. **Just VJ et al. (2004)** "A Closed Conformation of *Bacillus subtilis* Oxalate Decarboxylase OxdC Provides Evidence for the True Identity of the Active Site" [JBC](https://www.jbc.org/article/S0021-9258(20)67099-5/fulltext)
   - First description of closed lid conformation (1UW8)
   - Glu162 close to Mn in closed state

2. **Saylor et al. (2007)** "The identity of the active site of oxalate decarboxylase and the importance of the stability of active-site lid conformations" [PMC2275070](https://pmc.ncbi.nlm.nih.gov/articles/PMC2275070/)
   - Mutagenesis studies of lid residues
   - D297A, H299A affect open conformation stability

3. **Burg et al. (2018)** "The Structure of Oxalate Decarboxylase at its Active pH" [BioRxiv](https://www.biorxiv.org/content/10.1101/426874v1.full)
   - 5VG3 structure description
   - Mentions both open and closed configurations

### Key PDB Entries

| PDB | Resolution | Lid State | Reference |
|-----|------------|-----------|-----------|
| 1J58 | 1.75 Å | Open | Reinhardt 2003 |
| 1UW8 | 2.00 Å | Closed | Just 2004 |
| 5VG3 | 1.45 Å | Mixed/Ambiguous | Angerhofer 2017 |
| 2UY8 | 2.50 Å | R92A mutant | Saylor 2007 |
| 2UY9 | 2.10 Å | E162A mutant | Saylor 2007 |
| 2UYA | 2.45 Å | Δ162-163 | Saylor 2007 |
| 2UYB | 2.10 Å | S161A mutant | Saylor 2007 |

---

## 7. Conclusions and Next Steps

### Conclusions

1. **Our simulation shows the OPEN lid conformation** (Glu162-Mn ~11.5 Å)
2. **Literature "closed" = Glu162 close to Mn (~2-4 Å)**, not what we observe
3. **5VG3 lid state is ambiguous** in literature; may have mixed conformations
4. **Mn(II) may thermodynamically favor the open state**

### Recommended Next Steps

1. **Measure Glu162-Mn in starting structure** (before any MD)
   - If starting distance is ~11 Å → structure was already open
   - If starting distance is ~2-4 Å → lid opened during equilibration

2. **Compare with 1Wat+3 (Mn(III))**
   - Does Mn(III) favor closed lid?
   - This would support oxidation state control hypothesis

3. **Download and analyze 1UW8 (true closed) structure**
   - Measure Glu162-Mn distance for reference
   - Compare to our simulation

4. **Consider future simulation from 1UW8**
   - Start from confirmed closed structure
   - See if lid stays closed or opens

---

## 8. Summary Table

| State | Glu162-Mn Distance | Substrate Access | Proton Transfer Possible | PDB Example |
|-------|-------------------|------------------|--------------------------|-------------|
| **OPEN** | ~10-12 Å | Yes | No | 1J58, **Our sim** |
| **CLOSED** | ~2-4 Å | No | Yes | 1UW8 |
| **Intermediate** | ~4-8 Å | Partial | Maybe | Some mutants |

**Our BiOx+2 simulation: Glu162-Mn = 11.5 Å → OPEN state, consistent with 1J58**

---

*Report generated from comprehensive literature search, January 2026*
