# OxDC MD Fall 2025: Complete Repository Guide

## Overview

This repository contains molecular dynamics simulation infrastructure and analysis for Oxalate Decarboxylase (OxDC) from *Bacillus subtilis*. The project investigates the relationship between MCPB.py force field parameterization and simulation stability across different Mn coordination environments.

**Key Finding**: Force field parameters (particularly Mn-ligand force constants) are the primary determinant of MD simulation stability, not equilibration protocol or restraint masks.

---

## Repository Structure

```
oxdc-md-fall25/
├── REPOSITORY_GUIDE.md          # This file
├── systems/                     # MD simulation systems (6 variants)
├── analysis/                    # Analysis scripts and results
├── claude-notes/                # Research documentation and journals
├── presentation/                # LaTeX presentation files
├── mcp-hipergator/             # MCP server for HiPerGator HPC access
└── figs_cpp/                   # Figure generation scripts
```

---

## Quick Start Guide

### For Production Runs (BiOx+2 only)

```bash
# 1. SSH to HiPerGator
ssh john.aitken@hpg.rc.ufl.edu

# 2. Navigate to BiOx+2
cd /home/john.aitken/oxdc-md-fall25/systems/BiOx+2

# 3. Submit equilibration (if not complete)
cd slurm && sbatch run_eq_cpu_mc.sbatch

# 4. After eq2 completes, submit production
sbatch run_prod_gpu_mc.sbatch
```

See `claude-notes/THREE_DAY_PLAN_FINAL.md` for detailed step-by-step commands.

---

## Directory Contents

### `/systems/` - MD Simulation Systems

| System | Description | Status | Force Constant (k) |
|--------|-------------|--------|-------------------|
| `BiOx+2/` | Substrate-bound Mn(II) | **STABLE** | 29.3 |
| `1Wat+2/` | Water-coordinated Mn(II) | Unstable | 40.2 |
| `1Wat+3/` | Water-coordinated Mn(III) | Unstable | 97.3 |
| `empty+2/` | Empty Mn(II) site | Crashed | 44.0 |
| `empty+3/` | Empty Mn(III) site | Not tested | - |
| `Nterm_only/` | N-terminal site only | Experimental | - |

Each system contains:
- `*.prmtop` - AMBER topology files
- `*.inpcrd`, `*.rst7` - Coordinate/restart files
- `slurm/` - SLURM batch scripts
- `mdin_templates/` - AMBER input files
- `tools/` - QC check scripts

### `/analysis/` - Analysis Scripts and Results

#### Scripts (`/analysis/scripts/`)
| Script | Purpose |
|--------|---------|
| `energy_analysis.py` | Bond energy extraction from mdout |
| `force_constant_analysis.py` | Compare Mn-ligand force constants |
| `comprehensive_mn_analysis.py` | Full coordination analysis |
| `project7_energy_landscape.py` | 3D parameter space visualization |
| `project8_vibrational_analysis.py` | Frequency analysis from k |
| `project9_thermal_fluctuations.py` | Thermal RMS predictions |
| `project10_parameterization_quality.py` | Literature comparison |
| `project11_coordination_geometry.py` | Geometry analysis |
| `exploratory_ml_stability.py` | ML stability prediction |

#### cpptraj Inputs (`/analysis/cpptraj/`)
| File | Analysis |
|------|----------|
| `rmsd_rmsf.in` | Backbone RMSD and per-residue RMSF |
| `mn_coordination.in` | Mn-ligand distance tracking |
| `lid_dynamics.in` | Lid domain motion analysis |
| `pca_prep.in` | Principal component preparation |
| `trp_pair.in` | W96/W274 stacking analysis |

#### Generated Figures (`/analysis/results/`)
- `bond_energy_distribution.png` - Energy violin plots
- `force_constant_analysis.png` - Force constant comparison
- `oxidation_state_analysis.png` - Mn(II) vs Mn(III)
- `substrate_coordination.png` - Bidentate oxalate
- `stability_predictor.png` - Stability zones
- `vibrational_analysis.png` - Frequency analysis
- `thermal_fluctuations.png` - RMS predictions
- `coordination_geometry.png` - Geometry analysis
- `ml_stability_analysis.png` - ML prediction results
- ... and more

### `/claude-notes/` - Research Documentation

#### Root Level
| File | Content |
|------|---------|
| `THREE_DAY_PLAN_FINAL.md` | **Production implementation guide** |
| `RESEARCH_CONCLUSIONS.md` | **10 key research conclusions** |
| `PROTOCOL_CRITIQUE_JOURNAL.md` | Protocol validation findings |
| `RIGOROUS_CRITIQUE.md` | Socratic examination of claims |
| `RESEARCH_JOURNAL.md` | Literature bookmarks and notes |
| `MCP_HIPERGATOR_RESEARCH.md` | MCP server design research |
| `NON_BIOX2_SALVAGEABILITY.md` | System salvage analysis |

#### `/claude-notes/audit/`
| File | Content |
|------|---------|
| `STRUCTURE.md` | Repository structure audit |
| `CONSISTENCY.md` | Cross-system consistency check |
| `PROTOCOL.md` | Equilibration protocol documentation |
| `ROOT_CAUSE_ANALYSIS.md` | **Why BiOx+2 is stable** |

#### `/claude-notes/literature/`
| File | Content |
|------|---------|
| `LITERATURE_REVIEW.md` | Initial literature survey |
| `LITERATURE_REVIEW_EXTENDED.md` | Comprehensive lit review |
| `ANGERHOFER_OXDC_REVIEW.md` | **Alex Angerhofer lab review** |

#### `/claude-notes/production/`
| File | Content |
|------|---------|
| `READINESS.md` | Production readiness assessment |
| `CORRECTED_PROTOCOL.md` | Fixed equilibration protocol |
| `prod_template.in` | Production mdin template |

### `/presentation/` - LaTeX Beamer Presentation

| File | Content |
|------|---------|
| `oxdc_md_analysis.tex` | Main presentation (placeholders) |
| `oxdc_md_analysis_with_figures.tex` | With embedded figures |
| `Makefile` | Build automation |
| `README.md` | Compilation guide |

### `/mcp-hipergator/` - HPC Access MCP Server

Complete TypeScript implementation for Claude Code HPC access:
```
mcp-hipergator/
├── src/
│   ├── index.ts              # Main server entry
│   ├── ssh-client.ts         # SSH connection handling
│   ├── slurm-tools.ts        # sbatch, squeue, sacct, scancel
│   ├── file-tools.ts         # ls, read, write, upload, download
│   ├── md-tools.ts           # AMBER-specific tools
│   ├── tool-definitions.ts   # MCP tool schemas
│   └── config.ts             # Configuration management
├── package.json
├── tsconfig.json
└── README.md                 # Installation guide
```

---

## Key Research Findings

### The 10 Research Conclusions

1. **Force field parameters determine stability** (HIGH confidence)
2. **Bidentate oxalate binding validated** (VERY HIGH - matches Angerhofer lab)
3. **Mn(III) shows Jahn-Teller distortion** (HIGH)
4. **Restraint mask hypothesis disproven** (HIGH)
5. **Coordination number correlates with stability** (MEDIUM)
6. **Only BiOx+2 is production-ready** (HIGH)
7. **Work aligns with Angerhofer research** (HIGH)
8. **Stability prediction possible but unvalidated** (LOW)
9. **MCPB.py parameters require validation** (MEDIUM)
10. **BiOx+2 production will provide valuable data** (HIGH)

### Force Constant Stability Thresholds
```
STABLE ZONE:     k_avg < 35 kcal/mol·Å²   (BiOx+2)
MARGINAL ZONE:   35 < k_avg < 60          (1Wat+2, empty+2)
UNSTABLE ZONE:   k_avg > 60               (1Wat+3)
```

---

## How to Use This Repository

### For Running Simulations
1. Read `claude-notes/THREE_DAY_PLAN_FINAL.md` for step-by-step commands
2. Focus on BiOx+2 system (only stable one)
3. Follow protocol: heat → eq1 → eq2 → production

### For Analysis
1. Scripts in `analysis/scripts/` generate figures
2. cpptraj inputs in `analysis/cpptraj/` for trajectory analysis
3. Results appear in `analysis/results/`

### For Understanding the Research
1. Start with `claude-notes/RESEARCH_CONCLUSIONS.md`
2. Read `analysis/FINDINGS_SUMMARY.md` for the 6 key findings
3. See `claude-notes/audit/ROOT_CAUSE_ANALYSIS.md` for mechanistic explanation
4. Review `claude-notes/literature/ANGERHOFER_OXDC_REVIEW.md` for experimental context

### For Presentation
1. Compile LaTeX in `presentation/` directory
2. Run `make` to generate PDF
3. Figures reference `analysis/results/`

### For HPC Access with Claude Code
1. Install MCP server from `mcp-hipergator/`
2. Configure SSH keys for HiPerGator
3. Add to Claude Code with `claude mcp add`

---

## Important Files Quick Reference

| Need | File |
|------|------|
| Run production | `claude-notes/THREE_DAY_PLAN_FINAL.md` |
| Understand findings | `claude-notes/RESEARCH_CONCLUSIONS.md` |
| See analysis results | `analysis/FINDINGS_SUMMARY.md` |
| Check stability cause | `claude-notes/audit/ROOT_CAUSE_ANALYSIS.md` |
| Literature context | `claude-notes/literature/ANGERHOFER_OXDC_REVIEW.md` |
| Salvage other systems? | `claude-notes/NON_BIOX2_SALVAGEABILITY.md` |
| Present findings | `presentation/oxdc_md_analysis_with_figures.tex` |
| Use Claude for HPC | `mcp-hipergator/README.md` |

---

## Author and Context

**Research conducted**: Fall 2025 - Winter 2026
**PI**: Angerhofer Lab, University of Florida

---

## Version History

- **January 2026**: Comprehensive documentation, MCP server, conclusions
- **Fall 2025**: Initial analysis, force constant findings
- **Earlier**: MCPB.py parameterization, system preparation
