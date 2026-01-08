#!/usr/bin/env python3
"""
Energy Analysis for OxDC MD Simulations
Compares bond energy stability across systems

Run from analysis/scripts/ directory:
    python energy_analysis.py
"""

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configure matplotlib
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

def extract_energies(filepath, energy_type="BOND"):
    """Extract energy values from AMBER output file."""
    energies = []
    # Use word boundary to avoid matching EHBOND when looking for BOND
    pattern = rf"\b{energy_type}\s+=\s+([-\d.]+)"

    with open(filepath, 'r') as f:
        for line in f:
            # Skip lines with EHBOND when looking for BOND
            if energy_type == "BOND" and "EHBOND" in line:
                continue
            match = re.search(pattern, line)
            if match:
                energies.append(float(match.group(1)))

    return np.array(energies)

def extract_timesteps(filepath):
    """Extract timesteps from AMBER output."""
    times = []
    pattern = r"NSTEP\s+=\s+(\d+)"

    with open(filepath, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                times.append(int(match.group(1)))

    return np.array(times)

def main():
    # Setup paths
    systems_dir = Path(__file__).parent.parent.parent / "systems"
    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(exist_ok=True)

    systems = ["BiOx+2", "1Wat+2", "1Wat+3", "empty+2"]
    colors = {"BiOx+2": "#2ecc71", "1Wat+2": "#3498db",
              "1Wat+3": "#9b59b6", "empty+2": "#e74c3c"}

    # Extract data
    data = {}
    for sys in systems:
        eq1_path = systems_dir / sys / "eq1.cpu.out"
        if eq1_path.exists():
            bond = extract_energies(eq1_path, "BOND")
            steps = extract_timesteps(eq1_path)
            # Match lengths - use shorter
            n = min(len(bond), len(steps))
            data[sys] = {
                'bond': bond[:n],
                'angle': extract_energies(eq1_path, "ANGLE")[:n],
                'steps': steps[:n]
            }
            print(f"{sys}: {n} frames")

    # Figure 1: Bond Energy Time Series
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for i, sys in enumerate(systems):
        if sys in data and len(data[sys]['bond']) > 0:
            ax = axes[i]
            steps = data[sys]['steps'][:len(data[sys]['bond'])]
            ax.plot(steps/1000, data[sys]['bond'], color=colors[sys], alpha=0.7)
            ax.axhline(y=np.mean(data[sys]['bond']), color='black',
                      linestyle='--', label=f'Mean: {np.mean(data[sys]["bond"]):.0f}')
            ax.set_title(f'{sys}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Time (ps)')
            ax.set_ylabel('Bond Energy (kcal/mol)')
            ax.legend()

            # Mark instability region
            threshold = np.mean(data[sys]['bond']) + 3*np.std(data[sys]['bond'])
            spikes = data[sys]['bond'] > threshold
            if np.any(spikes):
                spike_times = steps[:len(data[sys]['bond'])][spikes]/1000
                ax.scatter(spike_times, data[sys]['bond'][spikes],
                          color='red', s=20, zorder=5, label='Energy spikes')

    plt.suptitle('Bond Energy Stability Comparison Across OxDC Systems',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'bond_energy_timeseries.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_dir / 'bond_energy_timeseries.png'}")
    plt.close()

    # Figure 2: Energy Distribution Comparison
    fig, ax = plt.subplots(figsize=(12, 6))

    positions = []
    for i, sys in enumerate(systems):
        if sys in data and len(data[sys]['bond']) > 0:
            positions.append(i)
            violin = ax.violinplot([data[sys]['bond']], positions=[i],
                                   showmeans=True, showmedians=True)
            for pc in violin['bodies']:
                pc.set_facecolor(colors[sys])
                pc.set_alpha(0.7)

    ax.set_xticks(range(len(systems)))
    ax.set_xticklabels(systems, fontsize=12)
    ax.set_ylabel('Bond Energy (kcal/mol)', fontsize=12)
    ax.set_title('Bond Energy Distribution by System\n(Wider = more variable = less stable)',
                fontsize=14, fontweight='bold')

    # Add statistics text
    for i, sys in enumerate(systems):
        if sys in data and len(data[sys]['bond']) > 0:
            stats = f"σ={np.std(data[sys]['bond']):.0f}"
            ax.annotate(stats, xy=(i, np.max(data[sys]['bond'])),
                       ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / 'bond_energy_distribution.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_dir / 'bond_energy_distribution.png'}")
    plt.close()

    # Figure 3: Summary Bar Chart
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Means
    means = [np.mean(data[sys]['bond']) if sys in data and len(data[sys]['bond']) > 0 else 0
             for sys in systems]
    axes[0].bar(systems, means, color=[colors[s] for s in systems])
    axes[0].set_ylabel('Mean Bond Energy (kcal/mol)')
    axes[0].set_title('Mean Bond Energy')

    # Std devs
    stds = [np.std(data[sys]['bond']) if sys in data and len(data[sys]['bond']) > 0 else 0
            for sys in systems]
    axes[1].bar(systems, stds, color=[colors[s] for s in systems])
    axes[1].set_ylabel('Std Dev (kcal/mol)')
    axes[1].set_title('Bond Energy Variability')
    axes[1].axhline(y=100, color='green', linestyle='--', label='Stable threshold')
    axes[1].legend()

    # Max spikes
    maxs = [np.max(data[sys]['bond']) if sys in data and len(data[sys]['bond']) > 0 else 0
            for sys in systems]
    axes[2].bar(systems, maxs, color=[colors[s] for s in systems])
    axes[2].set_ylabel('Max Bond Energy (kcal/mol)')
    axes[2].set_title('Peak Bond Energy Spikes')
    axes[2].axhline(y=2000, color='orange', linestyle='--', label='Warning threshold')
    axes[2].axhline(y=5000, color='red', linestyle='--', label='Critical threshold')
    axes[2].legend()

    plt.suptitle('Bond Energy Statistics Summary', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'energy_summary.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_dir / 'energy_summary.png'}")
    plt.close()

    # Print summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"{'System':<10} {'Mean':>10} {'Std':>10} {'Max':>10} {'Status':<15}")
    print("-"*60)
    for sys in systems:
        if sys in data and len(data[sys]['bond']) > 0:
            mean = np.mean(data[sys]['bond'])
            std = np.std(data[sys]['bond'])
            maxv = np.max(data[sys]['bond'])
            status = "STABLE" if std < 100 else ("UNSTABLE" if std < 2000 else "CRASHED")
            print(f"{sys:<10} {mean:>10.1f} {std:>10.1f} {maxv:>10.1f} {status:<15}")
    print("="*60)

if __name__ == "__main__":
    main()
