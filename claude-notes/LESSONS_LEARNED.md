# Lessons Learned: OxDC MD Simulation Project

**Date:** January 2026
**Context:** Winter break sprint to complete BiOx+2 production run
**Platform:** HiPerGator HPC (UF)

---

## Executive Summary

This document captures critical lessons from setting up and running metalloenzyme MD simulations with MCPB.py-parameterized Mn centers. These insights will save significant debugging time for future projects.

---

## 1. Equilibration: CPU vs GPU

### The Problem

GPU equilibration of metalloenzyme systems consistently failed with numerical instability errors (vlimit exceeded, coordinate resetting failures), while CPU runs succeeded.

### Root Cause

GPU implementations of AMBER (pmemd.cuda) use single-precision floating-point arithmetic by default for most calculations. Metal centers with high force constants (especially Mn-ligand bonds) require the higher numerical precision of CPU calculations.

### Evidence

| Run Type | Outcome | Error Type |
|----------|---------|------------|
| pmemd.cuda (GPU) | Failed | vlimit exceeded |
| pmemd (CPU serial) | Success | Clean completion |
| pmemd.MPI (CPU parallel) | Failed | Segfault/hang |

### Solution

**Use CPU-only equilibration for metalloenzyme systems**, especially:
- Any system with MCPB.py-derived parameters
- Mn, Fe, Cu, or other transition metal centers
- Systems with force constants > 50 kcal/mol·Å²

### SLURM Template for CPU Equilibration

```bash
#!/bin/bash
#SBATCH --job-name=eq_cpu
#SBATCH --output=eq_cpu_%j.out
#SBATCH --error=eq_cpu_%j.err
#SBATCH --ntasks=1                  # Single task - serial pmemd
#SBATCH --cpus-per-task=1           # One CPU
#SBATCH --mem=4gb
#SBATCH --time=48:00:00
#SBATCH --qos=ax-edr                # PI's QOS

module load amber/25

pmemd -O -i heat.in -o heat.out -p system.prmtop -c system.inpcrd -r heat.rst7 -ref system.inpcrd
```

### Key Takeaway

> **CPU equilibration is not a workaround—it's a requirement for metalloenzymes.**

---

## 2. MPI pmemd: Why It Fails

### The Problem

`pmemd.MPI` consistently failed with cryptic errors (segfaults, hangs, MPI errors) even when serial `pmemd` worked fine.

### Likely Causes

1. **OpenMPI/SLURM incompatibility**: The AMBER module's MPI build may conflict with SLURM's MPI environment
2. **Memory allocation**: MPI requires careful memory management across ranks
3. **Metal center handling**: Bonded model interactions may not parallelize correctly

### Attempted Solutions That Failed

- Using `srun pmemd.MPI` (still failed)
- Setting `--ntasks=4 --cpus-per-task=1` (still failed)
- Using `mpirun -np 4 pmemd.MPI` (still failed)

### Working Solution

**Use serial pmemd for equilibration.** For production runs, GPU is usually fine after equilibration is complete.

### Lesson

> **Don't fight MPI issues for equilibration. Serial CPU is reliable and completes overnight.**

---

## 3. Storage: /blue vs /home

### The Problem

Jobs mysteriously failed when trying to write large trajectory files to the wrong filesystem.

### HiPerGator Storage Hierarchy

| Location | Size Limit | Purge Policy | Best For |
|----------|-----------|--------------|----------|
| `/home/<user>/` | 40 GB | None | Scripts, small files |
| `/blue/<group>/<user>/` | Allocation | None | Active project data |
| `/orange/<group>/` | Allocation | None | Long-term storage |
| `/red/` | Scratch | 30 days | Temporary large files |

### Key Rules

1. **Always run jobs from /blue** - sufficient space for trajectories
2. **Check quota before production**: `home-quota` or `blue-quota`
3. **Trajectory files are LARGE**: ~500 MB per 10 ns segment
4. **Don't symlink from /home to /blue** - causes confusion

### Recommended Directory Structure

```
/blue/ax/<user>/
├── projects/
│   └── oxdc-md/
│       ├── systems/
│       │   └── BiOx+2/
│       │       ├── 5vg3.prmtop
│       │       ├── eq1.cpu.rst7
│       │       └── prod_seg001.nc  # Large files here
│       └── analysis/
└── backups/
```

### Lesson

> **Always work in /blue for MD projects. /home is only for tiny config files.**

---

## 4. MCP Server Configuration

### The Problem

Setting up an MCP server to connect Claude Code to HiPerGator was tricky due to SSH configuration mismatches.

### Configuration Gotchas

#### 1. controlPath Mismatch

The MCP server and local SSH must use the **same controlPath**:

```bash
# In ~/.ssh/config
Host hipergator
    HostName hpg.rc.ufl.edu
    User <gatorlink>
    IdentityFile ~/.ssh/id_rsa
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h:%p
    ControlPersist 10m
```

The MCP server must reference this exact path.

#### 2. IdentityFile Path Must Be Absolute

```json
// BAD - will fail
"identityFile": "~/.ssh/id_rsa"

// GOOD - works
"identityFile": "/Users/<username>/.ssh/id_rsa"
```

#### 3. SSH Key Must Be in ssh-agent

```bash
# Check if key is loaded
ssh-add -l

# If not, add it
ssh-add ~/.ssh/id_rsa
```

#### 4. Control Socket Directory Must Exist

```bash
mkdir -p ~/.ssh/sockets
chmod 700 ~/.ssh/sockets
```

### Working MCP Configuration

```json
{
  "mcpServers": {
    "hpc-ssh": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/claude-code-mcp-server-hpc-ssh",
        "--hostname", "hipergator",
        "--controlPath", "/Users/<user>/.ssh/sockets/%r@%h:%p",
        "--identityFile", "/Users/<user>/.ssh/id_rsa"
      ]
    }
  }
}
```

### Testing Connection

```bash
# First, establish the SSH connection manually
ssh hipergator

# Then, the MCP server can use the existing socket
```

### Lesson

> **Establish SSH connection manually first, then MCP server uses that socket.**

---

## 5. MCPB.py Parameterization Insights

### The Problem

Different systems showed dramatically different stability, traced to force field parameters.

### Key Findings

| Metric | Stable (BiOx+2) | Unstable (1Wat+3) |
|--------|-----------------|-------------------|
| Avg force constant | 29 kcal/mol·Å² | 97 kcal/mol·Å² |
| Mn-ligand distances | 2.08-2.41 Å | 1.86-2.03 Å |
| Outcome | Clean completion | vlimit exceeded |

### Force Constant Guidelines

```
STABLE ZONE:     k < 35 kcal/mol·Å²  (likely to equilibrate)
MARGINAL ZONE:   35 < k < 60         (may need tweaking)
DANGER ZONE:     k > 60              (likely to fail)
```

### QM Validation Checklist

Before running MD with MCPB.py parameters:

- [ ] Check `5vg3_small_opt.log` for "Stationary point found"
- [ ] Verify spin multiplicity matches expected (6 for high-spin Mn(II))
- [ ] Compare r₀ values in frcmod to QM-optimized distances
- [ ] Review force constants - flag any > 50 kcal/mol·Å²

### Lesson

> **Force field parameters, not restraint masks, determine metalloenzyme MD stability.**

---

## 6. Trajectory Analysis Gotchas

### cpptraj Path Issues

cpptraj input files use relative paths. Always:

1. Run cpptraj from a consistent directory
2. Use absolute paths in scripts
3. Check that topology and trajectory files exist before running

```bash
# Good practice
BASEDIR="/blue/ax/user/oxdc-md"
cpptraj -p ${BASEDIR}/system.prmtop -i analysis.in
```

### Atom Indices Change!

MCPB.py modifies the topology, so:
- Original PDB atom numbers ≠ topology atom indices
- Use `mn_bonds.csv` or `mn_contacts.csv` for correct indices
- Run `cpptraj resinfo` to verify residue mapping

### Lesson

> **Always verify atom indices match your topology, not the original PDB.**

---

## 7. Quick Reference: Commands That Work

### Start Equilibration

```bash
cd /blue/ax/<user>/oxdc-md/systems/BiOx+2
sbatch slurm/eq_cpu.sbatch
```

### Check Job Status

```bash
squeue -u $USER
squeue -j <jobid>
```

### Monitor Equilibration Progress

```bash
tail -f eq1.cpu.out | grep -E "NSTEP|Etot|TEMP"
```

### Check for Errors

```bash
grep -i "error\|fail\|exceeded" *.out *.err
```

### Quick Energy Check

```bash
tail -500 eq1.cpu.out | grep Etot | awk '{sum+=$3; count++} END {print "Avg Etot:", sum/count}'
```

---

## 8. What NOT To Do

### Don't

1. ❌ Use GPU for metalloenzyme equilibration
2. ❌ Fight with MPI for single-node jobs
3. ❌ Store trajectories in /home
4. ❌ Assume atom indices match PDB numbering
5. ❌ Skip checking force constants before running
6. ❌ Ignore vlimit warnings (they mean something is wrong)

### Do

1. ✅ Use CPU serial pmemd for equilibration
2. ✅ Work in /blue filesystem
3. ✅ Check MCPB.py parameters before running
4. ✅ Use MCP server with pre-established SSH connection
5. ✅ Monitor jobs with `tail -f`
6. ✅ Keep analysis scripts with absolute paths

---

## 9. Unresolved Questions

For future investigation:

1. **Why does MPI pmemd fail?** - Need to test with clean AMBER install
2. **Can GPU production work after CPU equilibration?** - Test pending
3. **Optimal force constant scaling for salvage?** - 0.7x proposed, needs testing
4. **1Wat+3 QM files location?** - Check HiPerGator /blue/ax/zbecerra/

---

## 10. Resources

### AMBER Documentation
- [AMBER Manual](https://ambermd.org/doc12/Amber24.pdf)
- [MCPB.py Tutorial](https://ambermd.org/tutorials/advanced/tutorial20/mcpbpy.htm)

### HiPerGator
- [Research Computing Help](https://help.rc.ufl.edu/)
- [SLURM Guide](https://help.rc.ufl.edu/doc/SLURM_Commands)

### Project Files
- Analysis scripts: `analysis/scripts/`
- cpptraj inputs: `analysis/cpptraj/`
- Force field data: `systems/*/analysis/mn_bonds.csv`

---

*Last updated: January 2026*
