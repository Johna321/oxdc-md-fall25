#!/usr/bin/env python3
"""
BiOx+2 Equilibration Analysis Script

Analyzes the available equilibration data (~200 ps) to assess:
1. RMSD convergence
2. Per-residue RMSF
3. Energy stability (from mdout parsing)
4. Equilibration quality assessment

IMPORTANT: This is equilibration data only. Biological conclusions
require production runs of 100+ ns.

Author: Claude (Research Assistant)
Date: January 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

# Configuration
BASEDIR = Path(__file__).parent.parent
FIGS_DIR = BASEDIR / "figs"
RESULTS_DIR = BASEDIR / "analysis_results"
FIGURES_DIR = RESULTS_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Style settings
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})


def load_cpptraj_data(filepath):
    """Load cpptraj ASCII output file."""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    data.append([float(x) for x in parts])
                except ValueError:
                    continue
    return np.array(data)


def parse_mdout_energies(filepath):
    """Parse AMBER mdout file for energy values."""
    energies = {
        'nstep': [],
        'time': [],
        'temp': [],
        'etot': [],
        'ektot': [],
        'eptot': [],
        'density': [],
    }

    with open(filepath, 'r') as f:
        content = f.read()

    # Parse energy blocks
    pattern = r'NSTEP\s*=\s*(\d+)\s+TIME.*?=\s*([\d.]+).*?TEMP.*?=\s*([\d.]+).*?Etot\s*=\s*([-\d.]+).*?EKtot\s*=\s*([\d.]+).*?EPtot\s*=\s*([-\d.]+)'

    for match in re.finditer(pattern, content, re.DOTALL):
        energies['nstep'].append(int(match.group(1)))
        energies['time'].append(float(match.group(2)))
        energies['temp'].append(float(match.group(3)))
        energies['etot'].append(float(match.group(4)))
        energies['ektot'].append(float(match.group(5)))
        energies['eptot'].append(float(match.group(6)))

    # Parse density
    density_pattern = r'Density\s*=\s*([\d.]+)'
    for match in re.finditer(density_pattern, content):
        energies['density'].append(float(match.group(1)))

    return {k: np.array(v) for k, v in energies.items()}


def plot_rmsd(rmsd_data, output_path):
    """Plot RMSD time series with equilibration assessment."""
    fig, ax = plt.subplots(figsize=(10, 5))

    frames = rmsd_data[:, 0]
    rmsd = rmsd_data[:, 1]

    # Assuming 1 ps per frame for equilibration
    time_ps = frames * 1.0  # Adjust if different

    ax.plot(time_ps, rmsd, 'b-', linewidth=0.8, alpha=0.8)

    # Running average
    window = min(20, len(rmsd) // 5)
    if window > 1:
        running_avg = np.convolve(rmsd, np.ones(window)/window, mode='valid')
        ax.plot(time_ps[window-1:], running_avg, 'r-', linewidth=2,
                label=f'Running avg (n={window})')

    # Statistics
    mean_rmsd = np.mean(rmsd)
    std_rmsd = np.std(rmsd)
    final_rmsd = np.mean(rmsd[-20:]) if len(rmsd) >= 20 else mean_rmsd

    ax.axhline(mean_rmsd, color='gray', linestyle='--', alpha=0.5)

    # Add text box
    textstr = f'Mean: {mean_rmsd:.3f} Å\nStd: {std_rmsd:.3f} Å\nFinal: {final_rmsd:.3f} Å'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)

    ax.set_xlabel('Time (ps)')
    ax.set_ylabel('RMSD (Å)')
    ax.set_title('BiOx+2 Equilibration: Cα RMSD\n(~200 ps equilibration only)')
    ax.legend(loc='upper left')

    # Add warning
    ax.text(0.5, -0.12,
            '⚠ EQUILIBRATION DATA ONLY - Not suitable for biological conclusions',
            transform=ax.transAxes, ha='center', fontsize=9, color='red')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.savefig(output_path.with_suffix('.pdf'))
    plt.close()

    return {'mean': mean_rmsd, 'std': std_rmsd, 'final': final_rmsd}


def plot_rmsf(rmsf_data, output_path):
    """Plot per-residue RMSF with lid region highlighted."""
    fig, ax = plt.subplots(figsize=(12, 5))

    residues = rmsf_data[:, 0]
    rmsf = rmsf_data[:, 1]

    # Plot RMSF
    ax.fill_between(residues, 0, rmsf, color='steelblue', alpha=0.6)
    ax.plot(residues, rmsf, 'steelblue', linewidth=1)

    # Highlight lid region (160-166)
    lid_mask = (residues >= 160) & (residues <= 166)
    if np.any(lid_mask):
        ax.fill_between(residues[lid_mask], 0, rmsf[lid_mask],
                       color='red', alpha=0.6, label='Lid (160-166)')

    # Mark key residues
    key_residues = {
        95: 'His95',
        97: 'His97',
        101: 'Glu101',
        140: 'His140',
        162: 'Glu162',
    }

    for res, label in key_residues.items():
        idx = np.where(residues == res)[0]
        if len(idx) > 0:
            ax.axvline(res, color='green', linestyle=':', alpha=0.5)

    ax.set_xlabel('Residue Number')
    ax.set_ylabel('RMSF (Å)')
    ax.set_title('BiOx+2 Equilibration: Per-Residue RMSF\n(~200 ps - NOT converged)')
    ax.legend()
    ax.set_xlim(residues.min(), residues.max())

    # Statistics
    mean_rmsf = np.mean(rmsf)
    lid_rmsf = np.mean(rmsf[lid_mask]) if np.any(lid_mask) else 0

    textstr = f'Global mean: {mean_rmsf:.3f} Å\nLid mean: {lid_rmsf:.3f} Å'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    # Warning
    ax.text(0.5, -0.12,
            '⚠ 200 ps insufficient for converged RMSF - Need 100+ ns',
            transform=ax.transAxes, ha='center', fontsize=9, color='red')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.savefig(output_path.with_suffix('.pdf'))
    plt.close()

    return {'mean': mean_rmsf, 'lid_mean': lid_rmsf}


def plot_energy(energies, output_path):
    """Plot energy time series from mdout."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    time = energies['time']

    # Total Energy
    ax = axes[0, 0]
    ax.plot(time, energies['etot'], 'b-', linewidth=0.5)
    ax.set_xlabel('Time (ps)')
    ax.set_ylabel('Total Energy (kcal/mol)')
    ax.set_title('Total Energy')
    mean_e = np.mean(energies['etot'])
    std_e = np.std(energies['etot'])
    ax.axhline(mean_e, color='red', linestyle='--', alpha=0.5)
    ax.text(0.95, 0.95, f'Mean: {mean_e:.0f}\nStd: {std_e:.0f}',
            transform=ax.transAxes, ha='right', va='top', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Temperature
    ax = axes[0, 1]
    ax.plot(time, energies['temp'], 'r-', linewidth=0.5)
    ax.set_xlabel('Time (ps)')
    ax.set_ylabel('Temperature (K)')
    ax.set_title('Temperature')
    ax.axhline(300, color='gray', linestyle='--', alpha=0.5, label='Target (300 K)')
    mean_t = np.mean(energies['temp'])
    ax.text(0.95, 0.95, f'Mean: {mean_t:.1f} K',
            transform=ax.transAxes, ha='right', va='top', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Potential Energy
    ax = axes[1, 0]
    ax.plot(time, energies['eptot'], 'g-', linewidth=0.5)
    ax.set_xlabel('Time (ps)')
    ax.set_ylabel('Potential Energy (kcal/mol)')
    ax.set_title('Potential Energy')

    # Density
    ax = axes[1, 1]
    if len(energies['density']) > 0:
        # Density array may be shorter - use available data
        density_time = time[:len(energies['density'])]
        ax.plot(density_time, energies['density'], 'm-', linewidth=0.5)
        ax.axhline(1.0, color='gray', linestyle='--', alpha=0.5, label='Target (1.0 g/cc)')
        mean_d = np.mean(energies['density'])
        ax.text(0.95, 0.95, f'Mean: {mean_d:.4f} g/cc',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.set_xlabel('Time (ps)')
    ax.set_ylabel('Density (g/cc)')
    ax.set_title('Density')

    fig.suptitle('BiOx+2 Equilibration: Energy & Temperature', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.savefig(output_path.with_suffix('.pdf'))
    plt.close()

    return {
        'mean_etot': np.mean(energies['etot']),
        'std_etot': np.std(energies['etot']),
        'mean_temp': np.mean(energies['temp']),
        'mean_density': np.mean(energies['density']) if len(energies['density']) > 0 else None
    }


def main():
    print("=" * 60)
    print("BiOx+2 Equilibration Analysis")
    print("=" * 60)
    print()
    print("⚠  WARNING: Only equilibration data available (~200 ps)")
    print("   Biological conclusions require production runs (100+ ns)")
    print()

    results = {}

    # 1. RMSD Analysis
    print("1. Analyzing RMSD...")
    rmsd_file = FIGS_DIR / "eq1_rmsd_ca.dat"
    if rmsd_file.exists():
        rmsd_data = load_cpptraj_data(rmsd_file)
        results['rmsd'] = plot_rmsd(rmsd_data, FIGURES_DIR / "eq_rmsd_ca.png")
        print(f"   Mean RMSD: {results['rmsd']['mean']:.3f} ± {results['rmsd']['std']:.3f} Å")
    else:
        print(f"   ERROR: {rmsd_file} not found")

    # 2. RMSF Analysis
    print("\n2. Analyzing RMSF...")
    rmsf_file = FIGS_DIR / "eq1_rmsf_ca.dat"
    if rmsf_file.exists():
        rmsf_data = load_cpptraj_data(rmsf_file)
        results['rmsf'] = plot_rmsf(rmsf_data, FIGURES_DIR / "eq_rmsf_ca.png")
        print(f"   Mean RMSF: {results['rmsf']['mean']:.3f} Å")
        print(f"   Lid RMSF: {results['rmsf']['lid_mean']:.3f} Å")
    else:
        print(f"   ERROR: {rmsf_file} not found")

    # 3. Energy Analysis
    print("\n3. Analyzing Energies...")
    mdout_file = BASEDIR / "eq1.cpu.out"
    if mdout_file.exists():
        energies = parse_mdout_energies(mdout_file)
        results['energy'] = plot_energy(energies, FIGURES_DIR / "eq_energy.png")
        print(f"   Mean Etot: {results['energy']['mean_etot']:.0f} kcal/mol")
        print(f"   Mean Temp: {results['energy']['mean_temp']:.1f} K")
        if results['energy']['mean_density']:
            print(f"   Mean Density: {results['energy']['mean_density']:.4f} g/cc")
    else:
        print(f"   ERROR: {mdout_file} not found")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("Equilibration Assessment:")

    # Check convergence criteria
    issues = []
    if 'rmsd' in results:
        if results['rmsd']['std'] > 0.5:
            issues.append("RMSD variance high - may need longer equilibration")
        else:
            print("  ✓ RMSD appears stable")

    if 'energy' in results:
        if results['energy']['mean_temp'] < 295 or results['energy']['mean_temp'] > 305:
            issues.append(f"Temperature drift ({results['energy']['mean_temp']:.1f} K)")
        else:
            print("  ✓ Temperature stable around 300 K")

        if results['energy']['mean_density'] and abs(results['energy']['mean_density'] - 1.0) > 0.02:
            issues.append(f"Density deviation ({results['energy']['mean_density']:.4f} g/cc)")
        else:
            print("  ✓ Density near 1.0 g/cc")

    if issues:
        print("\nPotential Issues:")
        for issue in issues:
            print(f"  ⚠ {issue}")

    print("\n" + "-" * 60)
    print("CRITICAL LIMITATIONS")
    print("-" * 60)
    print("• Data: ~200 ps equilibration only")
    print("• Required for lid dynamics: 100-500 ns production")
    print("• Required for statistics: 3-5 replica trajectories")
    print("• Current data is ~500× shorter than minimum needed")
    print()
    print(f"Figures saved to: {FIGURES_DIR}")

    return results


if __name__ == '__main__':
    main()
