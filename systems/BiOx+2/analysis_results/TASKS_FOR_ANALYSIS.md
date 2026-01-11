# Analysis Tasks for Claude Web/iOS

This document describes verification and analysis tasks to be performed on the BiOx+2 10 ns production trajectory data.

## Context

- **System**: BiOx+2 (Bidentate oxalate, Mn(II))
- **Simulation**: 10 ns production, 1000 frames
- **Key Question**: Does Mn oxidation state affect lid dynamics?
- **Preliminary Finding**: Lid remains OPEN throughout (Glu162-Mn >11 A)

## Data Files Available

All files are space-separated with `#Frame` header row (except per-residue files).

| File | Columns | Description |
|------|---------|-------------|
| `rmsd_ca.dat` | frame, RMSD | CA RMSD vs reference |
| `rmsd_backbone.dat` | frame, RMSD | Backbone RMSD |
| `rmsf_ca.dat` | residue, RMSF | Per-residue CA RMSF |
| `bfactors.dat` | residue, Bfactor | Crystallographic B-factors |
| `mn1_coordination.dat` | frame, His95, His97, His140, Glu101 | Mn1-ligand distances |
| `mn1_oxalate.dat` | frame, OZ, OY, OX | Mn1-oxalate distances |
| `glu162_mn_distance.dat` | frame, CD, OE1, OE2 | Lid open/closed indicator |
| `lid_rmsd.dat` | frame, RMSD | Lid region RMSD |
| `lid_rmsf.dat` | residue, RMSF | Lid per-residue RMSF |
| `lid_sasa.dat` | frame, SASA | Lid solvent accessibility |
| `radgyr.dat` | frame, RoG | Radius of gyration |
| `mn_mn_distance.dat` | frame, distance | Inter-Mn distance |

---

## Task 1: Verify Structural Stability

**Goal**: Confirm the simulation is equilibrated and stable.

**Steps**:
1. Read `rmsd_ca.dat`
2. Plot RMSD vs frame (time series)
3. Check for:
   - Initial equilibration period (RMSD increasing then plateauing)
   - No large sudden jumps (>0.5 A change in single frame)
   - Final plateau value (should be <3 A for stable protein)

**Expected**: RMSD should plateau around 1.5-2.5 A after initial frames.

**Report**:
- [ ] Mean RMSD after frame 100
- [ ] Standard deviation
- [ ] Any structural events (frame numbers with large jumps)

---

## Task 2: Verify Mn1 Coordination Integrity

**Goal**: Confirm MCPB.py force field maintains proper Mn coordination.

**Steps**:
1. Read `mn1_coordination.dat` (4 distance columns: His95, His97, His140, Glu101)
2. Calculate statistics for each ligand
3. Check for any transient dissociation (distance >3.0 A)

**Expected Values**:
- His-Mn: 2.1-2.5 A
- Glu-Mn: 1.9-2.3 A

**Report**:
- [ ] Mean ± std for each ligand distance
- [ ] Number of frames with any distance >3.0 A (dissociation events)
- [ ] Time series plot of all 4 distances

---

## Task 3: Analyze Oxalate Binding Mode

**Goal**: Characterize how oxalate binds to Mn1.

**Steps**:
1. Read `mn1_oxalate.dat` (3 distance columns: OZ, OY, OX)
2. Calculate statistics for each oxygen
3. Determine binding mode:
   - Bidentate: 2 oxygens <2.5 A
   - Monodentate: 1 oxygen <2.5 A
   - Asymmetric: Mixed

**Preliminary Finding**: OY is ~4 A (non-coordinating), OZ and OX are ~2 A (coordinating).

**Report**:
- [ ] Mean ± std for each Mn-O distance
- [ ] Histogram of each distance
- [ ] Classification of binding mode
- [ ] Any transitions between modes?

---

## Task 4: Analyze Lid Open/Closed State (KEY ANALYSIS)

**Goal**: Determine lid conformation and dynamics.

**Steps**:
1. Read `glu162_mn_distance.dat` (3 columns: CD, OE1, OE2)
2. Create histogram of Glu162_CD-Mn distance
3. Classify states:
   - **Closed**: <4 A
   - **Intermediate**: 4-8 A
   - **Open**: >8 A

**Preliminary Finding**: Average ~11.5 A (fully OPEN).

**Questions to Answer**:
- Is distribution unimodal (single state) or multimodal (transitions)?
- What fraction of frames are open vs closed?
- Are there any transient closing events?

**Report**:
- [ ] Histogram with state boundaries marked
- [ ] Percentage in each state
- [ ] Time series plot
- [ ] Comparison to expected behavior from literature

---

## Task 5: Correlate Lid Position with Other Metrics

**Goal**: Understand what controls lid position.

**Steps**:
1. Calculate correlation between:
   - Glu162-Mn distance vs lid RMSD
   - Glu162-Mn distance vs lid SASA
   - Glu162-Mn distance vs overall RMSD
2. Plot scatter plots

**Report**:
- [ ] Pearson correlation coefficients
- [ ] Interpretation: What opens/closes the lid?

---

## Task 6: Block Averaging for Convergence

**Goal**: Assess statistical reliability of averages.

**Steps**:
1. Divide trajectory into 5 equal blocks (200 frames each)
2. Calculate mean for key metrics in each block:
   - RMSD
   - Glu162-Mn distance
   - Mn1 coordination distances
3. Check if block means agree within uncertainty

**Report**:
- [ ] Table of block averages
- [ ] Standard error of the mean
- [ ] Assessment: Is trajectory converged?

---

## Task 7: Identify Flexibility Hotspots

**Goal**: Find flexible regions beyond the lid.

**Steps**:
1. Read `rmsf_ca.dat`
2. Plot RMSF vs residue number
3. Identify peaks (>0.5 A RMSF)
4. Compare to:
   - Lid region (160-166)
   - Loop regions
   - Terminal regions

**Report**:
- [ ] RMSF profile plot
- [ ] List of flexible regions (residue ranges, RMSF values)
- [ ] Comparison to crystallographic B-factors

---

## Summary Report Template

After completing all tasks, provide a summary:

```
## BiOx+2 Analysis Summary

### Simulation Quality
- Equilibrated: [YES/NO]
- RMSD: [X.XX ± X.XX] A
- Structural events: [NONE / list frames]

### Mn1 Coordination
- All ligands stable: [YES/NO]
- Dissociation events: [count]
- Coordination geometry: [OCTAHEDRAL / DISTORTED]

### Oxalate Binding
- Mode: [BIDENTATE / MONODENTATE / ASYMMETRIC]
- Stable: [YES/NO]

### Lid Dynamics (KEY FINDING)
- Dominant state: [OPEN / CLOSED / MIXED]
- Open fraction: [XX%]
- Glu162-Mn distance: [XX.X ± X.X] A
- Transitions observed: [YES/NO]

### Convergence
- Trajectory converged: [YES/NO]
- Longer simulation needed: [YES/NO]

### Scientific Implications
[Brief interpretation of what these results mean for the research question]
```

---

## Reference Information

See also:
- `ANALYSIS_SUMMARY.md` - Preliminary results and key findings
- `TOPOLOGY_REFERENCE.md` - Atom and residue indices
- `../../analysis/ANALYSIS_PLAN.md` - Full analysis strategy
- `../../claude-notes/literature/LITERATURE_REVIEW.md` - Scientific context
