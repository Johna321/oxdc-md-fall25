# Backbone Conformation Analysis Specification

**Purpose:** Distinguish "open-loop" vs "closed-backbone" states by analyzing lid backbone position, not just Glu162 sidechain distance.

**Date:** January 2026
**Status:** Ready for execution

---

## Background

Our Glu162-Mn distance analysis (~11.5 Å) tells us about the **sidechain position** but doesn't distinguish:
- **Closed-backbone / Glu162-out** (5VG3): Loop backbone closed, sidechain displaced (~10-12 Å)
- **Open-loop** (1J58): Loop backbone swung away (~15-16 Å)

To properly classify our trajectory, we need backbone-specific metrics.

---

## Analysis 1: Lid Backbone RMSD to Reference Structures

### Concept
Calculate RMSD of lid backbone atoms (residues 160-166, CA/C/N/O only) to:
1. **1J58 (open-loop)** — expect HIGH RMSD if we're in closed-backbone state
2. **1UW8 (closed, Glu162-in)** — expect LOW RMSD if backbone is closed
3. **5VG3 (closed, Glu162-out)** — our starting structure

### Required Files
- `1j58_lid_reference.pdb` — Lid residues 160-166 from PDB 1J58
- `1uw8_lid_reference.pdb` — Lid residues 160-166 from PDB 1UW8
- `5vg3_lid_reference.pdb` — Lid residues 160-166 from PDB 5VG3 (or use frame 1)

### cpptraj Commands

```
# Load trajectory
parm 5vg3_solv.prmtop
trajin prod.nc

# Create reference from first frame (5VG3-like)
reference prod.nc 1 [ref_5vg3]

# RMSD of lid backbone to reference structures
# Note: You'll need to align reference PDBs to match residue numbering

# Backbone RMSD of lid (residues 160-166) to first frame
rms lid_bb_rmsd :160-166@CA,C,N,O ref [ref_5vg3] out lid_backbone_rmsd.dat

# Alternative: Track CA positions directly
distance lid_ca_mn1 :162@CA :383@MN out lid_ca_mn1.dat

# Track backbone center of mass
center :160-166@CA,C,N,O mass out lid_com.dat
```

### Expected Results

| Metric | Closed-backbone (5VG3-like) | Open-loop (1J58-like) |
|--------|----------------------------|----------------------|
| Lid RMSD to 5VG3 | < 2 Å | > 4 Å |
| Lid RMSD to 1J58 | > 4 Å | < 2 Å |
| Glu162 CA - Mn1 | ~8-10 Å | ~11-13 Å |

---

## Analysis 2: Glu162 Cα Distance to Mn1 (Backbone Proxy)

### Concept
The Cα position reports on backbone conformation, independent of sidechain rotamers.

### cpptraj Commands

```
# Glu162 CA to Mn1 distance (backbone position proxy)
distance glu162_ca_mn1 :162@CA :383@MN out glu162_ca_mn1.dat

# Compare to CD (sidechain) - we already have this
# If CA and CD track together, sidechain follows backbone
# If CA stable but CD variable, sidechain is flexible on fixed backbone
```

### Expected Classification

| State | Glu162 CA - Mn1 | Glu162 CD - Mn1 |
|-------|-----------------|-----------------|
| Closed, Glu162-in (1UW8) | ~7-8 Å | ~4.6-5.1 Å |
| Closed, Glu162-out (5VG3) | ~8-10 Å | ~10-12 Å |
| Open-loop (1J58) | ~11-13 Å | ~15-16 Å |

---

## Analysis 3: Glu162 to Mn-Bound Water Distance

### Concept
In the Glu162-in state (1UW8), Glu162 OE1/OE2 H-bonds to a Mn-bound water (~2.7-2.8 Å).
This is the catalytically relevant contact.

### cpptraj Commands

```
# Find waters near Mn1 (within 3.5 Å)
# Then calculate distance from Glu162 OE to closest water oxygen

# Option 1: Distance to all waters within Mn coordination sphere
# This requires knowing which water is Mn-bound

# Option 2: Minimum distance from Glu162 OE to any water
# (less specific but informative)

distance glu162_oe1_wat :162@OE1 :WAT@O out glu162_oe1_water.dat
distance glu162_oe2_wat :162@OE2 :WAT@O out glu162_oe2_water.dat

# Check for H-bond occupancy
hbond glu162_hbonds :162 solventdonor :WAT solventacceptor :WAT out glu162_hbonds.dat
```

### Expected Results

| State | Glu162 OE - Mn-water |
|-------|---------------------|
| Glu162-in (1UW8) | ~2.7-2.8 Å |
| Glu162-out (5VG3/our sim) | > 5 Å |

---

## Analysis 4: Oxalate Binding Mode Dynamics

### Concept
Check if oxalate ever transitions from bidentate to monodentate, which could create space for Glu162-in.

### cpptraj Commands

```
# We already track OZ, OX, OY distances to Mn1
# Calculate binding mode per frame

# Bidentate: both OZ < 2.5 Å AND OX < 2.5 Å
# Monodentate: only one < 2.5 Å
# Dissociated: neither < 2.5 Å

# Already have from existing analysis:
# mn1_oxalate.dat with columns: frame, OZ, OY, OX

# Post-process to classify:
# Frame, OZ, OX, Mode
```

---

## Analysis 5: Solvent Channel Analysis

### Concept
In open-loop state, solvent has access to active site. Count waters near Mn1.

### cpptraj Commands

```
# Count waters within 5 Å of Mn1
watershell :383@MN out mn1_watershell.dat lower 3.5 upper 5.0

# Or use radial distribution function
radial mn1_water_rdf :383@MN :WAT@O out mn1_water_rdf.dat 0.1 10.0
```

### Expected Results

| State | Waters within 5 Å of Mn1 |
|-------|-------------------------|
| Closed-backbone | 0-2 |
| Open-loop | 3-5+ |

---

## Complete cpptraj Input File

Save as `backbone_analysis.in`:

```
# Backbone Conformation Analysis for BiOx+2
# Purpose: Distinguish open-loop vs closed-backbone states

parm 5vg3_solv.prmtop
trajin prod.nc

# Reference for RMSD
reference prod.nc 1 [ref_frame1]

# Analysis 1: Lid backbone RMSD to first frame
rms lid_bb_rmsd :160-166@CA,C,N,O ref [ref_frame1] out analysis_results/lid_backbone_rmsd.dat

# Analysis 2: Backbone proxy - Glu162 CA to Mn1
distance glu162_ca_mn1 :162@CA :383@MN out analysis_results/glu162_ca_mn1.dat

# For comparison: Already-computed sidechain distances
distance glu162_cd_mn1 :162@CD :383@MN out analysis_results/glu162_cd_mn1_check.dat

# Analysis 3: Glu162 to nearest water (H-bond proxy)
# Note: This finds minimum distance to any water oxygen
closest 1 :162@OE1,OE2 :WAT@O closestout analysis_results/glu162_closest_water.dat

# Analysis 4: Mn1 coordination waters
watershell :383@MN out analysis_results/mn1_watershell.dat lower 0.0 upper 3.5

# Analysis 5: Wider water shell
watershell :383@MN out analysis_results/mn1_water_5A.dat lower 0.0 upper 5.0

# Analysis 6: Lid center of mass trajectory
center :160-166@CA mass out analysis_results/lid_com.dat

run
```

---

## Execution Instructions

```bash
# Navigate to BiOx+2 directory
cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Run cpptraj
cpptraj -i analysis_scripts/backbone_analysis.in

# Verify output files
ls analysis_results/
```

---

## Post-Processing Python Script

Save as `analyze_backbone.py`:

```python
#!/usr/bin/env python3
"""
Post-process backbone conformation analysis results.
Classifies trajectory frames into open-loop vs closed-backbone states.
"""

import numpy as np
import matplotlib.pyplot as plt

# Load data
lid_rmsd = np.loadtxt('analysis_results/lid_backbone_rmsd.dat', skiprows=1)
ca_mn = np.loadtxt('analysis_results/glu162_ca_mn1.dat', skiprows=1)
cd_mn = np.loadtxt('analysis_results/glu162_cd_mn1_check.dat', skiprows=1)

# Extract columns (frame, value)
frames = lid_rmsd[:, 0]
rmsd_values = lid_rmsd[:, 1]
ca_distances = ca_mn[:, 1]
cd_distances = cd_mn[:, 1]

# Classification thresholds (adjust based on reference RMSD calculations)
# These are estimates - refine after comparing to 1J58/1UW8 references
CLOSED_BACKBONE_CA_THRESHOLD = 10.0  # Å - CA < 10 = closed-backbone
OPEN_LOOP_CA_THRESHOLD = 12.0        # Å - CA > 12 = open-loop

# Classify each frame
def classify_frame(ca_dist, cd_dist):
    if ca_dist < CLOSED_BACKBONE_CA_THRESHOLD:
        if cd_dist < 6.0:
            return "Closed, Glu162-in"
        elif cd_dist < 14.0:
            return "Closed, Glu162-out"
        else:
            return "Unknown"
    elif ca_dist > OPEN_LOOP_CA_THRESHOLD:
        return "Open-loop"
    else:
        return "Intermediate"

classifications = [classify_frame(ca, cd) for ca, cd in zip(ca_distances, cd_distances)]

# Count states
from collections import Counter
state_counts = Counter(classifications)
print("State Distribution:")
for state, count in state_counts.items():
    print(f"  {state}: {count} frames ({100*count/len(classifications):.1f}%)")

# Statistics
print(f"\nGlu162 CA-Mn1: {np.mean(ca_distances):.2f} ± {np.std(ca_distances):.2f} Å")
print(f"Glu162 CD-Mn1: {np.mean(cd_distances):.2f} ± {np.std(cd_distances):.2f} Å")
print(f"Lid backbone RMSD: {np.mean(rmsd_values):.2f} ± {np.std(rmsd_values):.2f} Å")

# Plot
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# CA distance time series
axes[0, 0].plot(frames, ca_distances, 'b-', alpha=0.7, label='CA-Mn1')
axes[0, 0].plot(frames, cd_distances, 'r-', alpha=0.7, label='CD-Mn1')
axes[0, 0].axhline(CLOSED_BACKBONE_CA_THRESHOLD, color='g', linestyle='--', label='Closed threshold')
axes[0, 0].set_xlabel('Frame')
axes[0, 0].set_ylabel('Distance (Å)')
axes[0, 0].set_title('Glu162 Backbone vs Sidechain Position')
axes[0, 0].legend()

# Lid RMSD
axes[0, 1].plot(frames, rmsd_values, 'k-', alpha=0.7)
axes[0, 1].set_xlabel('Frame')
axes[0, 1].set_ylabel('RMSD (Å)')
axes[0, 1].set_title('Lid Backbone RMSD to Frame 1')

# CA vs CD scatter
axes[1, 0].scatter(ca_distances, cd_distances, c=frames, cmap='viridis', alpha=0.5, s=10)
axes[1, 0].set_xlabel('Glu162 CA-Mn1 (Å)')
axes[1, 0].set_ylabel('Glu162 CD-Mn1 (Å)')
axes[1, 0].set_title('Backbone vs Sidechain Position')
axes[1, 0].axvline(CLOSED_BACKBONE_CA_THRESHOLD, color='g', linestyle='--')
axes[1, 0].axhline(6.0, color='r', linestyle='--', label='Glu162-in threshold')
plt.colorbar(axes[1, 0].collections[0], ax=axes[1, 0], label='Frame')

# State distribution
states = list(state_counts.keys())
counts = [state_counts[s] for s in states]
axes[1, 1].bar(states, counts, color=['green', 'blue', 'red', 'gray'][:len(states)])
axes[1, 1].set_ylabel('Frame Count')
axes[1, 1].set_title('State Distribution')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('analysis_results/figures/backbone_analysis.png', dpi=150)
plt.savefig('analysis_results/figures/backbone_analysis.pdf')
print("\nFigure saved to analysis_results/figures/backbone_analysis.png")
```

---

## Reference Structure Preparation (Optional Enhancement)

To get proper RMSD values to 1J58 and 1UW8, you'll need to:

1. Download 1J58 and 1UW8 from PDB
2. Extract residues 160-166 (adjust for numbering differences)
3. Align to our topology's residue numbering
4. Save as reference PDB files

```bash
# Example using PyMOL or similar:
# fetch 1j58
# select lid_1j58, resi 160-166 and name CA+C+N+O
# save 1j58_lid_reference.pdb, lid_1j58
```

---

## Expected Outcome

If our trajectory is truly in "closed-backbone / Glu162-out" state:
- ✓ Lid backbone RMSD to frame 1 should be LOW (< 2 Å)
- ✓ Glu162 CA-Mn1 should be ~8-10 Å (backbone in closed position)
- ✓ Glu162 CD-Mn1 should be ~10-12 Å (sidechain displaced)
- ✓ No transitions toward open-loop (CA > 12 Å)
- ✓ No transitions toward Glu162-in (CD < 6 Å)

---

## Summary

| Analysis | Metric | Classifies |
|----------|--------|-----------|
| Lid backbone RMSD | RMSD to references | Open vs Closed backbone |
| Glu162 CA-Mn1 | Backbone position | Backbone state |
| Glu162 CD-Mn1 | Sidechain position | Glu162-in vs Glu162-out |
| Glu162-water | H-bond distance | Catalytic readiness |
| Mn1 watershell | Water count | Solvent access |

---

*Specification created: January 2026*
*Status: Ready for execution on BiOx+2 production trajectory*
