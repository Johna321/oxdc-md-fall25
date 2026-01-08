# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains AMBER molecular dynamics simulation setups for oxalate decarboxylase (OxDC) protein systems with varying Mn coordination environments. Each system directory represents a different active site configuration based on PDB 5VG3.

## System Variants

Six system variants exist, each in its own directory:
- **1Wat+2, 1Wat+3**: Water-coordinated Mn sites with +2/+3 oxidation states
- **BiOx+2**: Bidentate oxalate-bound Mn
- **Nterm_only**: N-terminal domain only configuration
- **empty+2, empty+3**: Empty active sites with +2/+3 Mn

Key system properties are tracked in `overview.md` and `analysis_parent/overview.csv`.

## Directory Structure Per System

Each system directory contains:
- **Topology/coordinates**: `5vg3_solv.prmtop`, `5vg3_solv.inpcrd` (solvated system)
- **mdin_templates/**: AMBER input files for equilibration stages (eq1a-d, eq2a-b, eq3a_mttk)
- **slurm/**: SBATCH scripts for HPC submission
- **analysis/**: Topology summaries, Mn site analysis, restraint masks
- **tools/**: QC scripts (`qc_check.py`, `qc.sh`)
- **RUN_PLAN.md**: System-specific run strategy and QC gates

## Equilibration Protocol

Two equilibration strategies based on Mn site flags:

1. **gpu-chunked**: Direct GPU equilibration for well-behaved Mn sites
   - Submit: `sbatch slurm/run_eq1_chunked_gpu.sbatch`

2. **cpu-bridge-then-gpu**: CPU bridge (100 ps) then GPU for flagged Mn sites (SHORT/SPARSE coordination)
   - Submit: `sbatch slurm/run_eq1_bridge_cpu.sbatch`
   - Then: `sbatch slurm/run_eq2_to_mttk_gpu.sbatch`

Equilibration stages: heat → eq1a-d (NPT, decreasing restraints) → eq2a-b (Berendsen) → eq3a (MTTK production-ready)

## Running QC Checks

From within a system directory:
```bash
python tools/qc_check.py
```

Outputs `analysis/qc_summary.json` with:
- Density statistics (target: 0.99 ± 0.02 g/cc)
- Overflow detection ('***' lines)
- CA-RMSD vs reference (target: ≤ 2.0 Å at eq1d & eq2b)

## Key File Types (Git LFS tracked)

Large binary files use Git LFS: `.prmtop`, `.parm7`, `.top`, `.inpcrd`, `.rst7`, `.nc`, `.mol2`, `.pdb`, `.chk`, `.fchk`

## Python Environment

A virtual environment exists at `.venv/` with parmed and numpy for topology analysis.

```bash
source .venv/bin/activate
```

## AMBER Module Loading (HPC)

For CPU runs:
```bash
module purge; module load gcc/14.2.0; module load openmpi/5.0.7; module load amber/25
```

For GPU runs:
```bash
module purge; module load cuda/12.8.1; module load gcc/14.2.0; module load openmpi/5.0.7; module load amber/25
```
