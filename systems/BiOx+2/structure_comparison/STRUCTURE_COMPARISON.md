# OxDC Lid Conformation Structure Comparison

## Purpose

This document compares the two lid conformations provided by the grad student, labeled as "Closed_comfirmation" and "Open_comfirmation". We need to understand what these labels mean in terms of OxDC biochemistry and lid dynamics.

## Source Files

| File | Source Folder | Description |
|------|---------------|-------------|
| `closed_5vg3_dry.pdb` | Closed_comfirmation/pH_4/BiOx+2/ | "Closed" conformation |
| `open_5vg3open.pdb` | Open_comfirmation/pH4/empty+2/ | "Open" conformation |

Both files originate from PDB 5VG3 (Angerhofer lab, 2017).

## Key Measurements

### Glu162 (Proton Donor) Positions

**Glu162 CD (sidechain carboxyl carbon):**

| Conformation | X | Y | Z |
|--------------|---|---|---|
| "Closed" | 27.819 | 1.202 | 87.864 |
| "Open" | 30.916 | 7.653 | 94.836 |

**Glu162 CA (backbone):**

| Conformation | X | Y | Z |
|--------------|---|---|---|
| "Closed" | 31.146 | 3.300 | 87.613 |
| "Open" | 32.486 | 6.711 | 91.374 |

### Mn1 Position (Catalytic Metal)

| Atom | X | Y | Z |
|------|---|---|---|
| Mn1 | 34.180 | 4.575 | 79.852 |

(Same in both conformations - only the lid moves)

### Calculated Distances

| Distance | "Closed" | "Open" |
|----------|----------|--------|
| Glu162 CD → Mn1 | **10.77 Å** | **15.64 Å** |
| Glu162 OE1 → Mn1 | 11.72 Å | ~17 Å |
| Glu162 OE2 → Mn1 | 10.47 Å | ~16 Å |

### Lid CA Backbone Movement (residues 160-166)

| Residue | "Closed" CA-Mn1 | "Open" CA-Mn1 | Movement |
|---------|-----------------|---------------|----------|
| Phe160 | 10.88 Å | 10.88 Å | 0.00 Å (hinge) |
| Ser161 | 10.67 Å | 11.74 Å | 1.58 Å |
| **Glu162** | **8.43 Å** | **11.84 Å** | **5.25 Å** |
| Asn163 | 10.84 Å | 12.67 Å | 6.71 Å |
| Ser164 | 10.43 Å | 9.54 Å | 4.16 Å |
| Thr165 | 7.32 Å | 7.44 Å | 0.93 Å |
| Phe166 | 9.14 Å | 9.14 Å | 0.00 Å (hinge) |

**Key observation:** Phe160 and Phe166 act as hinges; the middle residues (161-165) swing between conformations.

## Critical Questions for Literature Review

1. **What is the crystallographic basis for "open" vs "closed" nomenclature in OxDC?**
   - Which PDB structures show these conformations?
   - Are they from different crystal forms, pH conditions, or alternate conformations in the same structure?

2. **What are the actual Glu162-Mn distances in published crystal structures?**
   - PDB 5VG3 (our source)
   - PDB 1J58 (Just et al. 2004, reported as "closed")
   - PDB 1UW8 (if exists)
   - Any other OxDC structures

3. **Is there a "catalytically closed" state distinct from crystallographic "closed"?**
   - Does Glu162 ever approach Mn closely enough to coordinate (2-3 Å)?
   - Or is proton donation to substrate indirect (Glu162 → substrate → Mn)?

4. **What does the mechanism require?**
   - Glu162 donates proton to oxalate substrate
   - How close must Glu162 be to oxalate for proton transfer?
   - What is the Glu162-oxalate distance in each conformation?

5. **What do mutagenesis studies tell us?**
   - E162A eliminates decarboxylase activity
   - S161A increases Km 10× (affects closed state stability)
   - What hydrogen bonds define the closed state?

## Oxalate Position (in BiOx+2 "Closed" structure)

| Atom | X | Y | Z | Mn1 Distance |
|------|---|---|---|--------------|
| CZ | 33.256 | 3.149 | 79.238 | ~1.5 Å |
| CX | 33.412 | 3.487 | 80.732 | ~1.5 Å |
| OZ | 34.075 | 3.662 | 78.366 | 1.75 Å (coordinating) |
| OX | 34.331 | 4.260 | 81.110 | 1.31 Å (coordinating) |
| OY | 32.306 | 2.350 | 78.847 | ~4 Å (non-coordinating) |

**Glu162 OE2 → Oxalate distances (in "Closed"):**
- → OX_OV: 7.54 Å (closest)
- → OX_CX: 8.97 Å
- → OX_OY: 9.59 Å

## Summary of What We Know

1. Both "Closed" and "Open" conformations have Glu162 >10 Å from Mn1
2. The "Closed" conformation has Glu162 ~5 Å closer than "Open"
3. Neither conformation positions Glu162 close enough for direct Mn coordination
4. Glu162 is 7.5+ Å from the nearest oxalate atom even in "Closed"

## What We Need to Clarify

- Is the "Closed_comfirmation" the actual closed state observed in crystal structures?
- Or is there a more closed state (not in these files) where Glu162 approaches the active site?
- What does the catalytic mechanism actually require in terms of distances?
