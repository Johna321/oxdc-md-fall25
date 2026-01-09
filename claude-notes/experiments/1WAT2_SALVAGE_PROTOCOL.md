# 1Wat+2 Salvage Experiment: Force Constant Scaling Protocol

## Objective

Test whether scaling Mn-ligand force constants by 0.7x can salvage the 1Wat+2 system for stable MD simulations.

## Background

### Current 1Wat+2 Parameters (Problem)

| Bond | Original k | Original r₀ |
|------|------------|-------------|
| Mn1-His95 | 33.0 | 2.25 |
| Mn1-His97 | 46.0 | 2.19 |
| Mn1-Glu101 | 36.5 | 2.11 |
| Mn1-His140 | 45.3 | 2.20 |
| Mn1-Water | 48.6 | 2.17 |
| **Average** | **41.9** | |

### Target Parameters (0.7x Scaling)

| Bond | Scaled k (0.7x) | r₀ (unchanged) |
|------|-----------------|----------------|
| Mn1-His95 | 23.1 | 2.25 |
| Mn1-His97 | 32.2 | 2.19 |
| Mn1-Glu101 | 25.6 | 2.11 |
| Mn1-His140 | 31.7 | 2.20 |
| Mn1-Water | 34.0 | 2.17 |
| **Average** | **29.3** | |

The scaled average (29.3) matches BiOx+2's average (29.7), which is the stable reference.

---

## Protocol

### Step 1: Locate Original frcmod File

```bash
cd /blue/ax/<user>/oxdc-md/systems/1Wat+2
ls -la *.frcmod
# Should find: 5vg3_mcpbpy.frcmod or 5vg3_mcpbpy_pre.frcmod
```

### Step 2: Create Modified frcmod

Use the script below to generate a scaled version:

```bash
# Run from systems/1Wat+2 directory
python3 ../../analysis/scripts/scale_frcmod.py \
    --input 5vg3_mcpbpy.frcmod \
    --output 5vg3_mcpbpy_scaled07.frcmod \
    --scale 0.7 \
    --bonds-only
```

### Step 3: Regenerate Topology

```bash
# Modify tleap input to use scaled frcmod
cp 5vg3_tleap.in 5vg3_tleap_scaled.in
# Edit to point to scaled frcmod

tleap -f 5vg3_tleap_scaled.in

# Should produce:
# - 5vg3_scaled.prmtop
# - 5vg3_scaled.inpcrd
```

### Step 4: Test Equilibration

```bash
# Submit test equilibration job
sbatch slurm/eq_scaled_test.sbatch
```

### Step 5: Evaluate Results

Check for:
1. No vlimit warnings
2. Stable bond energies (std < 100 kcal/mol)
3. Mn-ligand distances remain within 0.5 Å of r₀

---

## Implementation Scripts

### scale_frcmod.py

```python
#!/usr/bin/env python3
"""
Scale force constants in AMBER frcmod file.

Usage:
    python scale_frcmod.py --input file.frcmod --output scaled.frcmod --scale 0.7

This script modifies only the bond force constants (k values in BOND section),
leaving equilibrium distances (r0) and all other parameters unchanged.
"""

import argparse
import re
import sys


def scale_frcmod(input_file, output_file, scale_factor, bonds_only=True):
    """
    Scale force constants in frcmod file.

    Args:
        input_file: Path to original frcmod
        output_file: Path to write scaled frcmod
        scale_factor: Multiplier for force constants (e.g., 0.7)
        bonds_only: If True, only scale BOND section; if False, also scale ANGLE
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()

    output_lines = []
    current_section = None
    modified_count = 0

    for line in lines:
        # Detect section headers
        if line.strip() in ['BOND', 'ANGLE', 'DIHE', 'IMPROPER', 'NONBON', 'MASS']:
            current_section = line.strip()
            output_lines.append(line)
            continue

        # Empty line ends section
        if line.strip() == '':
            current_section = None
            output_lines.append(line)
            continue

        # Process BOND section
        if current_section == 'BOND':
            # Format: XX-YY  k    r0
            # Example: M1-NE  46.0  2.19
            match = re.match(r'^(\S+-\S+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)(.*)$', line)
            if match:
                atom_types = match.group(1)
                k = float(match.group(2))
                r0 = match.group(3)
                rest = match.group(4)

                # Scale k, keep r0
                k_scaled = k * scale_factor

                # Reconstruct line with same formatting
                new_line = f"{atom_types:<6s} {k_scaled:5.1f}  {r0}{rest}\n"
                output_lines.append(new_line)
                modified_count += 1
                print(f"  BOND {atom_types}: {k:.1f} -> {k_scaled:.1f}")
                continue

        # Process ANGLE section (optional)
        if current_section == 'ANGLE' and not bonds_only:
            # Format: XX-YY-ZZ  k    theta0
            match = re.match(r'^(\S+-\S+-\S+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)(.*)$', line)
            if match:
                atom_types = match.group(1)
                k = float(match.group(2))
                theta0 = match.group(3)
                rest = match.group(4)

                k_scaled = k * scale_factor
                new_line = f"{atom_types:<9s} {k_scaled:5.1f}  {theta0}{rest}\n"
                output_lines.append(new_line)
                modified_count += 1
                continue

        # Pass through unchanged
        output_lines.append(line)

    with open(output_file, 'w') as f:
        f.writelines(output_lines)

    print(f"\nModified {modified_count} force constants by factor {scale_factor}")
    print(f"Saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Scale frcmod force constants')
    parser.add_argument('--input', required=True, help='Input frcmod file')
    parser.add_argument('--output', required=True, help='Output frcmod file')
    parser.add_argument('--scale', type=float, default=0.7, help='Scale factor (default 0.7)')
    parser.add_argument('--bonds-only', action='store_true', default=True,
                       help='Only scale bonds (default: True)')
    parser.add_argument('--include-angles', action='store_true',
                       help='Also scale angle force constants')

    args = parser.parse_args()

    bonds_only = not args.include_angles

    print(f"Scaling force constants by {args.scale}")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Scaling bonds only: {bonds_only}")
    print()

    scale_frcmod(args.input, args.output, args.scale, bonds_only)


if __name__ == '__main__':
    main()
```

### eq_scaled_test.sbatch

```bash
#!/bin/bash
#SBATCH --job-name=1wat2_scaled
#SBATCH --output=eq_scaled_%j.out
#SBATCH --error=eq_scaled_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=24:00:00
#SBATCH --qos=ax-edr

# Test equilibration with scaled force constants

module load amber/25

WORKDIR="/blue/ax/$USER/oxdc-md/systems/1Wat+2"
cd $WORKDIR

PRMTOP="5vg3_scaled.prmtop"
INPCRD="5vg3_scaled.inpcrd"

echo "=== Testing scaled 1Wat+2 equilibration ==="
echo "Start time: $(date)"
echo "Using topology: $PRMTOP"

# Heat (short test)
pmemd -O \
    -i mdin_templates/heat_nvt_1fs.in \
    -o heat_scaled.out \
    -p $PRMTOP \
    -c $INPCRD \
    -r heat_scaled.rst7 \
    -x heat_scaled.nc \
    -ref $INPCRD

if [ $? -ne 0 ]; then
    echo "ERROR: Heating failed!"
    exit 1
fi

echo "Heating completed successfully"

# Check for vlimit warnings
if grep -q "vlimit exceeded" heat_scaled.out; then
    echo "WARNING: vlimit exceeded during heating"
    grep -c "vlimit exceeded" heat_scaled.out
else
    echo "No vlimit warnings during heating"
fi

# Short equilibration test (100 ps)
cat > eq_test_100ps.in << 'EOF'
Equilibration test (100 ps)
 &cntrl
  imin=0, ntx=5, irest=1,
  nstlim=50000, dt=0.002,
  ntc=2, ntf=2,
  ntpr=500, ntwx=500, ntwr=5000,
  cut=10.0,
  ntt=3, gamma_ln=2.0, temp0=300.0,
  ntp=1, barostat=2, pres0=1.0,
  iwrap=1,
  ntr=1, restraintmask='@CA', restraint_wt=1.0,
 /
EOF

pmemd -O \
    -i eq_test_100ps.in \
    -o eq_test_100ps.out \
    -p $PRMTOP \
    -c heat_scaled.rst7 \
    -r eq_test_100ps.rst7 \
    -x eq_test_100ps.nc \
    -ref heat_scaled.rst7

if [ $? -ne 0 ]; then
    echo "ERROR: Equilibration test failed!"
    exit 1
fi

echo "Equilibration test completed successfully"

# Check for vlimit warnings
if grep -q "vlimit exceeded" eq_test_100ps.out; then
    echo "WARNING: vlimit exceeded during equilibration"
    grep -c "vlimit exceeded" eq_test_100ps.out
else
    echo "SUCCESS: No vlimit warnings during equilibration"
fi

# Quick energy check
echo ""
echo "=== Energy Statistics ==="
grep "Etot" eq_test_100ps.out | tail -10

echo ""
echo "End time: $(date)"
```

---

## Success Criteria

### Pass Criteria

1. **No vlimit warnings** during heating or equilibration
2. **Bond energy std < 200 kcal/mol** (vs original 1254)
3. **Mn-ligand distances within 0.3 Å** of original r₀
4. **Temperature stable** at 300 ± 5 K
5. **Density stable** at 1.0 ± 0.02 g/cc

### Fail Criteria

1. Any SHAKE failure
2. vlimit warnings > 10
3. Bond energy std > 500 kcal/mol
4. Any Mn-ligand distance > 3.0 Å

---

## Analysis Script

```python
#!/usr/bin/env python3
"""
Analyze scaled 1Wat+2 test equilibration.
"""

import sys
import re
from pathlib import Path

def analyze_mdout(filepath):
    """Parse AMBER output file for key metrics."""
    vlimit_count = 0
    etot_values = []
    ebond_values = []

    with open(filepath) as f:
        for line in f:
            if 'vlimit exceeded' in line.lower():
                vlimit_count += 1
            if 'Etot' in line:
                match = re.search(r'Etot\s*=\s*([-\d.]+)', line)
                if match:
                    etot_values.append(float(match.group(1)))
            if 'BOND' in line and '=' in line:
                match = re.search(r'BOND\s*=\s*([\d.]+)', line)
                if match:
                    ebond_values.append(float(match.group(1)))

    return {
        'vlimit_count': vlimit_count,
        'etot_mean': sum(etot_values)/len(etot_values) if etot_values else 0,
        'etot_std': (sum((x - sum(etot_values)/len(etot_values))**2 for x in etot_values) / len(etot_values))**0.5 if len(etot_values) > 1 else 0,
        'ebond_mean': sum(ebond_values)/len(ebond_values) if ebond_values else 0,
        'ebond_std': (sum((x - sum(ebond_values)/len(ebond_values))**2 for x in ebond_values) / len(ebond_values))**0.5 if len(ebond_values) > 1 else 0,
    }

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'eq_test_100ps.out'

    results = analyze_mdout(filepath)

    print("=== Scaled 1Wat+2 Test Analysis ===")
    print(f"vlimit warnings: {results['vlimit_count']}")
    print(f"Etot: {results['etot_mean']:.1f} ± {results['etot_std']:.1f} kcal/mol")
    print(f"BOND: {results['ebond_mean']:.1f} ± {results['ebond_std']:.1f} kcal/mol")
    print()

    # Pass/Fail assessment
    passed = True
    if results['vlimit_count'] > 10:
        print("FAIL: Too many vlimit warnings")
        passed = False
    if results['ebond_std'] > 500:
        print("FAIL: Bond energy too unstable")
        passed = False

    if passed:
        print("PASS: System appears stable with scaled parameters")
        print("\nRecommendation: Proceed with full equilibration")
    else:
        print("\nRecommendation: Try different scaling factor or consider QM/MM")
```

---

## Timeline

| Day | Task |
|-----|------|
| 1 | Create scaled frcmod, regenerate topology |
| 1 | Submit test equilibration |
| 2 | Analyze results, iterate if needed |
| 3 | If successful, run full equilibration |

---

## Alternatives If 0.7x Fails

1. **Try 0.6x scaling** - More aggressive reduction
2. **Use ionic model at Site 1** - Like BiOx+2 Site 2
3. **Hybrid approach** - Scale only problematic bonds
4. **Conclude: Not salvageable** - Document as limitation

---

## Notes

- **Do not scale Site 2** - Those parameters are already within stable range
- **Keep r₀ unchanged** - Geometry should match QM optimization
- **Document all attempts** - Even failures are valuable data
- **Compare to BiOx+2** - Use as stability reference throughout

---

*Protocol prepared: January 2026*
*Status: Ready for execution after BiOx+2 production completes*
