#!/usr/bin/env python3
"""
Scale force constants in AMBER frcmod file.

This script is designed to modify MCPB.py-generated frcmod files to reduce
force constants for metalloenzyme simulations that show numerical instability.

Usage:
    python scale_frcmod.py --input file.frcmod --output scaled.frcmod --scale 0.7

Background:
    High force constants (k > 50 kcal/mol·Å²) in metal-ligand bonds can cause
    numerical instability during MD equilibration. Scaling these by 0.7x brings
    them into the stable range while maintaining reasonable geometry.

Created: January 2026
For: OxDC MD Simulation Project - 1Wat+2 Salvage Experiment
"""

import argparse
import re
import sys
from pathlib import Path


def parse_bond_line(line):
    """
    Parse a BOND section line from frcmod.

    Format: XX-YY  k  r0  [comment]
    Example: M1-NE  46.0  2.19

    Returns:
        tuple: (atom_types, k, r0, rest_of_line) or None if not a bond line
    """
    # Match pattern: atom-atom  force_const  eq_dist  [anything else]
    pattern = r'^(\S{2}-\S{2})\s+(\d+\.?\d*)\s+(\d+\.?\d*)(.*)$'
    match = re.match(pattern, line)
    if match:
        return (
            match.group(1),  # atom types (e.g., "M1-NE")
            float(match.group(2)),  # force constant
            match.group(3),  # equilibrium distance (as string to preserve formatting)
            match.group(4)   # rest of line (comments, etc.)
        )
    return None


def parse_angle_line(line):
    """
    Parse an ANGLE section line from frcmod.

    Format: XX-YY-ZZ  k  theta0  [comment]
    """
    pattern = r'^(\S{2}-\S{2}-\S{2})\s+(\d+\.?\d*)\s+(\d+\.?\d*)(.*)$'
    match = re.match(pattern, line)
    if match:
        return (
            match.group(1),
            float(match.group(2)),
            match.group(3),
            match.group(4)
        )
    return None


def scale_frcmod(input_file, output_file, scale_factor,
                 scale_bonds=True, scale_angles=False, metal_only=True):
    """
    Scale force constants in frcmod file.

    Args:
        input_file: Path to original frcmod
        output_file: Path to write scaled frcmod
        scale_factor: Multiplier for force constants (e.g., 0.7)
        scale_bonds: Scale BOND section force constants
        scale_angles: Scale ANGLE section force constants
        metal_only: Only scale lines containing metal atom types (M1, M2, MN, etc.)
    """
    # Metal atom type patterns
    metal_patterns = ['M1', 'M2', 'MN', 'FE', 'ZN', 'CU', 'CO', 'NI']

    def is_metal_line(atom_types):
        """Check if atom types contain a metal."""
        return any(metal in atom_types.upper() for metal in metal_patterns)

    with open(input_file, 'r') as f:
        lines = f.readlines()

    output_lines = []
    current_section = None
    stats = {
        'bonds_scaled': 0,
        'bonds_skipped': 0,
        'angles_scaled': 0,
        'angles_skipped': 0,
    }

    print(f"\nProcessing: {input_file}")
    print(f"Scale factor: {scale_factor}")
    print(f"Metal-only mode: {metal_only}")
    print("-" * 60)

    for line in lines:
        stripped = line.strip()

        # Detect section headers
        if stripped in ['BOND', 'ANGLE', 'DIHE', 'IMPROPER', 'NONBON', 'MASS']:
            current_section = stripped
            output_lines.append(line)
            if stripped in ['BOND', 'ANGLE']:
                print(f"\n[{stripped} section]")
            continue

        # Empty line or section end
        if stripped == '' or stripped.startswith('END'):
            current_section = None
            output_lines.append(line)
            continue

        # Process BOND section
        if current_section == 'BOND' and scale_bonds:
            parsed = parse_bond_line(line)
            if parsed:
                atom_types, k, r0, rest = parsed

                # Check if we should scale this line
                should_scale = not metal_only or is_metal_line(atom_types)

                if should_scale:
                    k_scaled = k * scale_factor
                    new_line = f"{atom_types:<6s} {k_scaled:5.1f}  {r0}{rest}\n"
                    output_lines.append(new_line)
                    stats['bonds_scaled'] += 1
                    print(f"  {atom_types}: k = {k:5.1f} -> {k_scaled:5.1f}")
                else:
                    output_lines.append(line)
                    stats['bonds_skipped'] += 1
                continue

        # Process ANGLE section
        if current_section == 'ANGLE' and scale_angles:
            parsed = parse_angle_line(line)
            if parsed:
                atom_types, k, theta0, rest = parsed

                should_scale = not metal_only or is_metal_line(atom_types)

                if should_scale:
                    k_scaled = k * scale_factor
                    new_line = f"{atom_types:<9s} {k_scaled:5.1f}  {theta0}{rest}\n"
                    output_lines.append(new_line)
                    stats['angles_scaled'] += 1
                    print(f"  {atom_types}: k = {k:5.1f} -> {k_scaled:5.1f}")
                else:
                    output_lines.append(line)
                    stats['angles_skipped'] += 1
                continue

        # Pass through unchanged
        output_lines.append(line)

    # Write output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.writelines(output_lines)

    # Print summary
    print("-" * 60)
    print("\nSummary:")
    print(f"  Bonds scaled:  {stats['bonds_scaled']}")
    print(f"  Bonds skipped: {stats['bonds_skipped']}")
    if scale_angles:
        print(f"  Angles scaled:  {stats['angles_scaled']}")
        print(f"  Angles skipped: {stats['angles_skipped']}")
    print(f"\nOutput written to: {output_file}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Scale force constants in AMBER frcmod file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scale all metal-ligand bonds by 0.7x
  python scale_frcmod.py -i system.frcmod -o scaled.frcmod -s 0.7

  # Scale ALL bonds (not just metal-ligand)
  python scale_frcmod.py -i system.frcmod -o scaled.frcmod -s 0.7 --all-bonds

  # Scale bonds and angles
  python scale_frcmod.py -i system.frcmod -o scaled.frcmod -s 0.7 --include-angles
        """
    )

    parser.add_argument('-i', '--input', required=True,
                       help='Input frcmod file')
    parser.add_argument('-o', '--output', required=True,
                       help='Output frcmod file')
    parser.add_argument('-s', '--scale', type=float, default=0.7,
                       help='Scale factor for force constants (default: 0.7)')
    parser.add_argument('--all-bonds', action='store_true',
                       help='Scale all bonds, not just metal-ligand')
    parser.add_argument('--include-angles', action='store_true',
                       help='Also scale angle force constants')
    parser.add_argument('--no-bonds', action='store_true',
                       help='Do not scale bonds (use with --include-angles)')

    args = parser.parse_args()

    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Run scaling
    scale_frcmod(
        input_file=args.input,
        output_file=args.output,
        scale_factor=args.scale,
        scale_bonds=not args.no_bonds,
        scale_angles=args.include_angles,
        metal_only=not args.all_bonds
    )


if __name__ == '__main__':
    main()
