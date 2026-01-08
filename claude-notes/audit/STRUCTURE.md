# Repository Structure Audit

## Current Layout

```
oxdc-md-fall25/
├── .git/
├── .gitattributes          # LFS tracking
├── .gitignore
├── shared/
│   ├── mdin/               # Template mdin files (generic)
│   │   ├── heat_nvt_1fs.in
│   │   ├── eq1_mc_cpu_1fs.in
│   │   └── eq2_mc_cpu_1fs.in
│   └── slurm/              # Template SLURM scripts
│       ├── run_eq_cpu_mc.sbatch
│       ├── run_prod_gpu_mc.sbatch
│       └── test_sander.sbatch
├── figs_cpp/               # cpptraj outputs and visualizations
│   ├── cpptraj_light.in
│   ├── plots.sh
│   ├── *.png, *.gif, *.mp4
│   └── site_frames*.pdb
├── systems/
│   ├── CLAUDE.md           # Project documentation
│   ├── overview.md         # System comparison table
│   ├── analysis_parent/    # Cross-system analysis
│   │   └── overview.csv
│   ├── 1Wat+2/            # Water-coordinated Mn(II)
│   ├── 1Wat+3/            # Water-coordinated Mn(III)
│   ├── BiOx+2/            # Bidentate oxalate Mn(II)
│   ├── empty+2/           # Empty active site Mn(II)
│   ├── empty+3/           # Empty active site Mn(III)
│   └── Nterm_only/        # N-terminal domain only
└── claude-notes/          # [NEW] Analysis and planning docs
    ├── literature/
    ├── audit/
    ├── production/
    └── questions/
```

## Per-System Directory Structure

```
systems/{system}/
├── 5vg3_solv.prmtop       # Solvated topology
├── 5vg3_solv.inpcrd       # Initial coordinates
├── 5vg3_solv.rst7         # Current restart file (if exists)
├── 5vg3_dry.pdb           # Unsolvated reference
├── 5vg3_mcpbpy.pdb        # MCPB.py input structure
├── RUN_PLAN.md            # System-specific strategy
├── mdin_templates/        # AMBER input files
│   ├── heat_nvt_1fs.in    # NVT heating
│   ├── eq1_mc_cpu_1fs.in  # NPT eq (2.0 kcal restraints)
│   ├── eq2_mc_cpu_1fs.in  # NPT eq (0.5 kcal restraints)
│   ├── eq3a_mttk.mdin     # Production-ready (no restraints)
│   └── eq1[a-d].mdin      # Staged equilibration variants
├── slurm/                 # HPC submission scripts
│   ├── run_eq_cpu_mc.sbatch
│   ├── run_eq1_chunked_gpu.sbatch
│   ├── run_prod_gpu_mc.sbatch
│   └── test_sander.sbatch
├── analysis/              # Topology analysis
│   ├── topology_summary.json
│   ├── mn_site_atoms.csv
│   ├── mn_contacts.csv
│   ├── mn_bonds.csv
│   ├── restraint_mask.txt
│   └── rough_density.txt
├── tools/
│   ├── qc_check.py
│   └── qc.sh
└── *.cpu.rst7, *.cpu.out  # Simulation outputs
```

---

## Proposed Reorganization

### Issues with Current Layout

1. **Scattered analysis outputs:** `figs_cpp/` at root, `analysis/` per-system
2. **No central analysis pipeline:** cpptraj scripts ad hoc
3. **Inconsistent naming:** `5vg3_solv.*` vs `coords.rst7` symlinks
4. **Missing production infrastructure:** No `production/` directories
5. **No version control of analysis:** Output files mixed with inputs

### Proposed Structure

```
oxdc-md-fall25/
├── systems/
│   └── {system}/
│       ├── topology/          # [RENAME] from root files
│       │   ├── system.prmtop
│       │   └── system.inpcrd
│       ├── equilibration/     # [MOVE] output files here
│       │   ├── heat.rst7
│       │   ├── eq1.rst7
│       │   └── eq2.rst7
│       ├── production/        # [NEW]
│       │   ├── run_001/
│       │   │   ├── prod.nc
│       │   │   └── prod.rst7
│       │   └── run_002/       # Replicas
│       └── analysis/          # Keep, expand
│           ├── topology/
│           ├── equilibration/
│           └── production/
├── analysis/                  # [NEW] Cross-system analysis
│   ├── cpptraj/
│   │   ├── rmsd.in
│   │   ├── rmsf.in
│   │   └── mn_distances.in
│   ├── scripts/
│   │   └── plot_comparison.py
│   └── results/
│       └── comparative/
├── protocols/                 # [MOVE from shared/]
│   ├── mdin/
│   └── slurm/
└── docs/
    ├── CLAUDE.md
    └── overview.md
```

### Migration Steps (If Pursued)

1. Create new directory structure
2. Move topology files to `topology/`
3. Move output files to `equilibration/`
4. Update SLURM scripts with new paths
5. Create central `analysis/` with standardized scripts
6. Git LFS considerations for large file moves

**Recommendation:** Do NOT reorganize mid-project. Complete current equilibrations first, document structure issues, reorganize before publication prep.

---

## File Inventory by System

| System | prmtop | inpcrd | rst7 files | .out files | .nc files |
|--------|--------|--------|------------|------------|-----------|
| 1Wat+2 | ✓ | ✓ | heat, eq1, eq1a | heat, eq1, eq1a, eq2 | ? |
| 1Wat+3 | ✓ | ✓ | heat, eq1, eq1a, eq1b | heat, eq1, eq1a, eq1b | ? |
| empty+2 | ✓ | ✓ | heat, eq1, eq1a, eq1b | heat, eq1, eq1a, eq1b, eq2 | ? |
| BiOx+2 | ✓ | ✓ | heat, eq1 | heat, eq1 | ? |
| empty+3 | ? | ? | ? | ? | ? |
| Nterm_only | ✓ | ✓ | nested in output/ | nested in output/ | ? |

---

## Git LFS Status

Tracked extensions from `.gitattributes`:
- `.prmtop`, `.parm7`, `.top`
- `.inpcrd`, `.rst7`
- `.nc` (trajectories)
- `.mol2`, `.pdb`
- `.chk`, `.fchk` (Gaussian checkpoints)

**Note:** Trajectory `.nc` files should be excluded from repo and stored separately for publication data archiving.
