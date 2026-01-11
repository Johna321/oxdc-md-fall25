# BiOx+2 Production MD Analysis Summary

**Generated:** 2026-01-10
**System:** BiOx+2 (Bidentate oxalate bound, Mn(II) oxidation state)
**Simulation:** 10 ns production (5,000,000 steps @ 2 fs)
**Trajectory:** 1000 frames (10 ps/frame)

---

## Simulation Details

| Parameter | Value |
|-----------|-------|
| Topology | 5vg3_solv.prmtop |
| Atoms | 63,287 |
| Waters | 19,079 (TIP3P) |
| Ions | 9 Cl- |
| Temperature | 300 K (Langevin) |
| Pressure | 1 atm (MC barostat) |
| Timestep | 2 fs |
| GPU Performance | 175 ns/day |

---

## Key Atom/Residue Indices (cpptraj 1-indexed)

### Mn Centers
| Site | Atom | Residue | Charge | Role |
|------|------|---------|--------|------|
| Mn1 | 6033 | MN1 (383) | -0.15 | Catalytic (MCPB.py) |
| Mn2 | 6034 | MN (384) | +2.0 | Structural (Mn2+ ion) |

### Mn1 Coordination Sphere
| Ligand | Residue | Atom Name | Expected Distance |
|--------|---------|-----------|-------------------|
| His95 | HD1 | NE2 | 2.1-2.4 A |
| His97 | HD2 | NE2 | 2.1-2.4 A |
| His140 | HD3 | NE2 | 2.1-2.4 A |
| Glu101 | GU1 | OE1 | 1.9-2.2 A |
| Oxalate | OX1 | OZ,OY,OX | 2.0-2.5 A |

### Flexible Lid
| Residue | Name | Role |
|---------|------|------|
| 160 | PHE | Lid boundary |
| 161 | SER | H-bond (closed) |
| 162 | GLH | Proton donor, key for catalysis |
| 163 | ASN | |
| 164 | SER | H-bond (open) |
| 165 | THR | |
| 166 | PHE | Lid boundary |

---

## Results Summary

### 1. Structural Stability

| Metric | Min | Max | Average | Status |
|--------|-----|-----|---------|--------|
| CA RMSD | 1.28 A | 2.64 A | 1.98 A | STABLE |
| Radius of Gyration | - | - | 24.28 A | COMPACT |

**Interpretation:** The protein maintains stable structure throughout 10 ns with no signs of unfolding or major conformational drift.

### 2. Mn1 Coordination (Catalytic Site)

| Ligand | Average Distance (A) | Expected | Status |
|--------|---------------------|----------|--------|
| His95 NE2 | 2.39 | 2.1-2.4 | OK |
| His97 NE2 | 2.26 | 2.1-2.4 | OK |
| His140 NE2 | 2.24 | 2.1-2.4 | OK |
| Glu101 OE1 | 2.06 | 1.9-2.2 | OK |

**Mn1-Oxalate Binding:**

| Oxygen | Average Distance (A) | Status |
|--------|---------------------|--------|
| OZ | 2.09 | COORDINATING |
| OY | 4.05 | NOT COORDINATING |
| OX | 2.35 | COORDINATING |

**Key Finding:** Oxalate binds ASYMMETRICALLY with only 2 of 3 available oxygens coordinating Mn1. This is unexpected for "bidentate" binding.

### 3. Lid Dynamics (Primary Scientific Question)

**Glu162-Mn1 Distance (open/closed indicator):**

| Atom | Average Distance (A) | Interpretation |
|------|---------------------|----------------|
| CD | 11.54 | OPEN |
| OE1 | 11.73 | OPEN |
| OE2 | 12.28 | OPEN |

**Threshold:** <4 A = closed, >6 A = open

**Key Finding:** The lid remains in the OPEN conformation throughout the entire 10 ns simulation, even with substrate bound!

**Lid RMSF (per residue):**

| Residue | RMSF (A) |
|---------|----------|
| Phe160 | 0.40 |
| Ser161 | 0.31 |
| Glu162 | 0.34 |
| Asn163 | 0.31 |
| Ser164 | 0.51 (most flexible) |
| Thr165 | 0.31 |
| Phe166 | 0.39 |

### 4. Active Site Solvation

| Shell | Waters | Interpretation |
|-------|--------|----------------|
| Inner (3.5 A) | 0.0 | Completely dehydrated |
| Outer (5.0 A) | 0.0 | No water access |

**Key Finding:** Despite open lid, Mn1 active site is fully shielded from bulk solvent.

### 5. Inter-Mn Distance

| Metric | Average |
|--------|---------|
| Mn1-Mn2 | 25.22 A |

This is consistent with literature values (~26 A for the two Mn centers).

### 6. Trp Pair Analysis

The W96-W274 distance of ~39 A indicates these residues are within the same monomer. The inter-subunit electron transfer pathway analysis requires a dimer simulation.

---

## Scientific Conclusions

1. **MCPB.py parameterization is working:** Mn1 coordination geometry is stable and matches expected values.

2. **Asymmetric oxalate binding:** The substrate does not bind in perfect bidentate fashion - one oxygen (OY) is consistently distant from Mn1.

3. **Lid remains OPEN:** This is unexpected! Even with substrate bound, Glu162 stays >11 A from Mn1. Possible explanations:
   - Need longer simulation to sample closing
   - Mn(II) oxidation state favors open conformation
   - Starting structure was open and hasn't closed yet

4. **Dehydrated active site:** Substrate binding effectively excludes water, even with open lid.

---

## Verification Tasks - COMPLETED

All verification tasks have been completed (January 2026). See `PRODUCTION_ANALYSIS_REPORT.md` for full details.

### Task 1: RMSD Convergence - VERIFIED
- [x] Plot rmsd_ca.dat time series - **Figure: prod_rmsd.png**
- [x] Check if RMSD plateaus (indicates equilibration) - **YES, plateaus at ~2.0 A**
- [x] Identify any sudden jumps (structural events) - **NONE detected**

### Task 2: Mn1 Coordination Stability - VERIFIED
- [x] Plot all 4 ligand distances from mn1_coordination.dat - **Figure: prod_mn1_coordination.png**
- [x] Check for any transient dissociation events (>3 A) - **ZERO dissociation events**
- [x] Calculate standard deviations - **All < 0.12 A**

### Task 3: Glu162-Mn1 Distribution - VERIFIED (KEY FINDING)
- [x] Create histogram of glu162_mn_distance.dat - **Figure: prod_lid_dynamics.png**
- [x] Check if distribution is unimodal (single state) or bimodal (two states) - **UNIMODAL (p=0.94)**
- [x] Compare to expected open/closed thresholds - **100% OPEN (>8 A), 0% closed (<4 A)**

### Task 4: Oxalate Binding Mode - VERIFIED
- [x] Plot all 3 Mn-oxalate distances from mn1_oxalate.dat - **Figure: prod_oxalate_binding.png**
- [x] Verify OY stays distant throughout - **YES, OY = 4.05 A consistently**
- [x] Investigate any transitions - **NO transitions; 91.5% bidentate throughout**

### Task 5: Cross-Correlation - VERIFIED
- [x] Check if lid RMSD correlates with Glu162-Mn distance - **r = +0.39 (moderate)**
- [x] Check if RMSD correlates with radius of gyration - **r = +0.08 (weak)**

### Task 6: Statistical Analysis - VERIFIED
- [x] Calculate means and standard deviations for all key metrics - **Complete**
- [x] Perform block averaging (divide into 5 blocks) to assess convergence - **CONVERGED (SEM < 10%)**
- [x] Report 95% confidence intervals - **In block averaging results**

**Analysis Script:** `analysis_scripts/analyze_production.py`
**Generated Figures:** `analysis_results/figures/prod_*.png`

---

## Data Files

| File | Description | Columns |
|------|-------------|---------|
| rmsd_ca.dat | CA RMSD vs frame | frame, RMSD |
| rmsf_ca.dat | Per-residue RMSF | residue, RMSF |
| mn1_coordination.dat | Mn1-ligand distances | frame, His95, His97, His140, Glu101 |
| mn1_oxalate.dat | Mn1-oxalate distances | frame, OZ, OY, OX |
| glu162_mn_distance.dat | Lid indicator | frame, CD, OE1, OE2 |
| lid_rmsd.dat | Lid RMSD | frame, RMSD |
| lid_rmsf.dat | Lid per-residue RMSF | residue, RMSF |
| lid_sasa.dat | Lid solvent accessibility | frame, SASA |
| mn_mn_distance.dat | Inter-Mn distance | frame, distance |
| radgyr.dat | Radius of gyration | frame, RoG |
| bfactors.dat | Crystallographic B-factors | residue, Bfactor |
| hbond_avg.dat | H-bond occupancies | various |
| lid_hbond_avg.dat | Lid H-bond occupancies | various |

---

## Next Steps

1. **Longer simulations:** 100+ ns may be needed to sample lid opening/closing
2. **Compare systems:** Analyze 1Wat+2, empty+2 when available
3. **PCA:** Principal component analysis to identify dominant motions
4. **Replica simulations:** Multiple trajectories for statistical significance
