#!/usr/bin/env python3
"""
Production Analysis Visualization for BiOx+2 OxDC MD Simulations
Generates publication-quality figures from cpptraj output.

Usage: python3 plot_production_analysis.py [--results-dir PATH]

Created: January 2026
For: OxDC MD Simulation Project
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Style settings for publication-quality figures
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'sans-serif',
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Color scheme
COLORS = {
    'rmsd': '#1f77b4',
    'rmsf': '#2ca02c',
    'mn_coord': '#d62728',
    'lid': '#9467bd',
    'trp': '#ff7f0e',
}


def load_cpptraj_data(filepath):
    """Load cpptraj output file (space-separated, first column is frame number)."""
    try:
        data = np.loadtxt(filepath, comments='#')
        if data.ndim == 1:
            return np.arange(len(data)), data
        return data[:, 0], data[:, 1:]
    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}")
        return None, None


def plot_rmsd(results_dir, output_dir):
    """Plot RMSD time series."""
    fig, ax = plt.subplots(figsize=(8, 4))

    # Load backbone RMSD
    frames, rmsd = load_cpptraj_data(results_dir / 'rmsd' / 'rmsd_backbone.dat')
    if frames is not None:
        # Convert frames to time (assuming 2 fs timestep, 500 frame output interval = 1 ps)
        time_ns = frames * 0.001  # Adjust based on actual output frequency
        ax.plot(time_ns, rmsd, color=COLORS['rmsd'], linewidth=0.8, alpha=0.8)
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel('Backbone RMSD (Å)')
        ax.set_title('BiOx+2 Production: Backbone RMSD')

        # Add running average
        window = min(100, len(rmsd) // 10)
        if window > 1:
            running_avg = np.convolve(rmsd.flatten(), np.ones(window)/window, mode='valid')
            ax.plot(time_ns[window-1:], running_avg, 'k-', linewidth=2, label='Running avg')
            ax.legend()

        # Add statistics
        avg = np.mean(rmsd)
        std = np.std(rmsd)
        ax.axhline(avg, color='gray', linestyle='--', alpha=0.5)
        ax.text(0.95, 0.95, f'Mean: {avg:.2f} ± {std:.2f} Å',
                transform=ax.transAxes, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_dir / 'rmsd_timeseries.png')
    plt.savefig(output_dir / 'rmsd_timeseries.pdf')
    plt.close()
    print(f"Saved: rmsd_timeseries.png/pdf")


def plot_rmsf(results_dir, output_dir):
    """Plot per-residue RMSF with lid region highlighted."""
    fig, ax = plt.subplots(figsize=(10, 4))

    resnum, rmsf = load_cpptraj_data(results_dir / 'rmsf' / 'rmsf_ca.dat')
    if resnum is not None:
        ax.fill_between(resnum.flatten(), 0, rmsf.flatten(), color=COLORS['rmsf'], alpha=0.6)
        ax.plot(resnum, rmsf, color=COLORS['rmsf'], linewidth=1)

        # Highlight lid region (residues 160-166)
        lid_mask = (resnum >= 160) & (resnum <= 166)
        if np.any(lid_mask):
            ax.fill_between(resnum[lid_mask].flatten(), 0, rmsf[lid_mask].flatten(),
                          color=COLORS['lid'], alpha=0.8, label='Lid (160-166)')

        # Mark Mn-coordinating residues
        mn_residues = [95, 97, 101, 140]  # His95, His97, Glu101, His140
        for res in mn_residues:
            idx = np.where(resnum == res)[0]
            if len(idx) > 0:
                ax.axvline(res, color=COLORS['mn_coord'], linestyle=':', alpha=0.5)

        ax.set_xlabel('Residue Number')
        ax.set_ylabel('RMSF (Å)')
        ax.set_title('BiOx+2: Per-Residue RMSF')
        ax.legend()
        ax.set_xlim(resnum.min(), resnum.max())

    plt.tight_layout()
    plt.savefig(output_dir / 'rmsf_per_residue.png')
    plt.savefig(output_dir / 'rmsf_per_residue.pdf')
    plt.close()
    print(f"Saved: rmsf_per_residue.png/pdf")


def plot_mn_coordination(results_dir, output_dir):
    """Plot Mn coordination distances."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # Panel A: Mn-His distances
    ax = axes[0, 0]
    frames, his_data = load_cpptraj_data(results_dir / 'mn_coordination' / 'mn1_his.dat')
    if frames is not None and his_data is not None:
        time_ns = frames * 0.001
        labels = ['His95', 'His97', 'His140']
        for i, label in enumerate(labels[:his_data.shape[1] if his_data.ndim > 1 else 1]):
            col_data = his_data[:, i] if his_data.ndim > 1 else his_data
            ax.plot(time_ns, col_data, label=label, linewidth=0.8, alpha=0.8)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Distance (Å)')
    ax.set_title('Mn1-His Distances')
    ax.axhline(2.2, color='gray', linestyle='--', alpha=0.5, label='Expected')
    ax.legend(fontsize=8)
    ax.set_ylim(1.5, 3.0)

    # Panel B: Mn-Glu distance
    ax = axes[0, 1]
    frames, glu_data = load_cpptraj_data(results_dir / 'mn_coordination' / 'mn1_glu.dat')
    if frames is not None:
        time_ns = frames * 0.001
        ax.plot(time_ns, glu_data, color=COLORS['mn_coord'], linewidth=0.8)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Distance (Å)')
    ax.set_title('Mn1-Glu101 Distance')
    ax.axhline(2.08, color='gray', linestyle='--', alpha=0.5, label='r₀ = 2.08 Å')
    ax.legend(fontsize=8)
    ax.set_ylim(1.5, 3.0)

    # Panel C: Mn-Oxalate distances
    ax = axes[1, 0]
    frames, ox_data = load_cpptraj_data(results_dir / 'mn_coordination' / 'mn1_oxalate.dat')
    if frames is not None and ox_data is not None:
        time_ns = frames * 0.001
        if ox_data.ndim > 1:
            ax.plot(time_ns, ox_data[:, 0], label='Ox-O1 (tight)', linewidth=0.8)
            if ox_data.shape[1] > 1:
                ax.plot(time_ns, ox_data[:, 1], label='Ox-O2 (loose)', linewidth=0.8)
        else:
            ax.plot(time_ns, ox_data, linewidth=0.8)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Distance (Å)')
    ax.set_title('Mn1-Oxalate Distances (Bidentate)')
    ax.axhline(2.11, color='blue', linestyle='--', alpha=0.5, label='r₀(O1) = 2.11 Å')
    ax.axhline(2.42, color='orange', linestyle='--', alpha=0.5, label='r₀(O2) = 2.42 Å')
    ax.legend(fontsize=8)
    ax.set_ylim(1.5, 3.5)

    # Panel D: Mn-Mn distance
    ax = axes[1, 1]
    frames, mn_mn = load_cpptraj_data(results_dir / 'mn_coordination' / 'mn_mn.dat')
    if frames is not None:
        time_ns = frames * 0.001
        ax.plot(time_ns, mn_mn, color='purple', linewidth=0.8)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Distance (Å)')
    ax.set_title('Mn1-Mn2 Distance (Intra-subunit)')

    plt.tight_layout()
    plt.savefig(output_dir / 'mn_coordination.png')
    plt.savefig(output_dir / 'mn_coordination.pdf')
    plt.close()
    print(f"Saved: mn_coordination.png/pdf")


def plot_lid_dynamics(results_dir, output_dir):
    """Plot lid dynamics analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # Panel A: Lid RMSD
    ax = axes[0, 0]
    frames, lid_rmsd = load_cpptraj_data(results_dir / 'lid_dynamics' / 'lid_rmsd.dat')
    if frames is not None:
        time_ns = frames * 0.001
        ax.plot(time_ns, lid_rmsd, color=COLORS['lid'], linewidth=0.8)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('RMSD (Å)')
    ax.set_title('Lid RMSD (Res 160-166)')

    # Panel B: Glu162-Mn distance
    ax = axes[0, 1]
    frames, glu_mn = load_cpptraj_data(results_dir / 'lid_dynamics' / 'glu162_mn.dat')
    if frames is not None:
        time_ns = frames * 0.001
        ax.plot(time_ns, glu_mn, color=COLORS['lid'], linewidth=0.8)
        ax.hist(glu_mn.flatten(), bins=50, orientation='horizontal', alpha=0.3,
               color=COLORS['lid'], density=True)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Glu162-Mn Distance (Å)')
    ax.set_title('Lid-Mn Interaction')

    # Panel C: Lid SASA
    ax = axes[1, 0]
    frames, sasa = load_cpptraj_data(results_dir / 'lid_dynamics' / 'lid_sasa.dat')
    if frames is not None:
        time_ns = frames * 0.001
        ax.plot(time_ns, sasa, color=COLORS['lid'], linewidth=0.8)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('SASA (Å²)')
    ax.set_title('Lid Solvent Accessible Surface Area')

    # Panel D: Placeholder for H-bond analysis
    ax = axes[1, 1]
    ax.text(0.5, 0.5, 'H-bond analysis\n(see lid_hbonds.dat)',
            transform=ax.transAxes, ha='center', va='center', fontsize=12)
    ax.set_title('Lid H-bonds')

    plt.tight_layout()
    plt.savefig(output_dir / 'lid_dynamics.png')
    plt.savefig(output_dir / 'lid_dynamics.pdf')
    plt.close()
    print(f"Saved: lid_dynamics.png/pdf")


def plot_summary_dashboard(results_dir, output_dir):
    """Create a summary dashboard with all key metrics."""
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

    # Title
    fig.suptitle('BiOx+2 Production Analysis Summary', fontsize=14, fontweight='bold')

    # 1. RMSD
    ax = fig.add_subplot(gs[0, 0])
    frames, rmsd = load_cpptraj_data(results_dir / 'rmsd' / 'rmsd_backbone.dat')
    if frames is not None:
        time_ns = frames * 0.001
        ax.plot(time_ns, rmsd, color=COLORS['rmsd'], linewidth=0.5, alpha=0.7)
        ax.set_title(f'Backbone RMSD\nMean: {np.mean(rmsd):.2f} ± {np.std(rmsd):.2f} Å')
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel('RMSD (Å)')

    # 2. RMSF
    ax = fig.add_subplot(gs[0, 1])
    resnum, rmsf = load_cpptraj_data(results_dir / 'rmsf' / 'rmsf_ca.dat')
    if resnum is not None:
        ax.fill_between(resnum.flatten(), 0, rmsf.flatten(), color=COLORS['rmsf'], alpha=0.6)
        ax.set_title('Per-Residue RMSF')
        ax.set_xlabel('Residue')
        ax.set_ylabel('RMSF (Å)')

    # 3. Mn1-His coordination
    ax = fig.add_subplot(gs[0, 2])
    frames, his_data = load_cpptraj_data(results_dir / 'mn_coordination' / 'mn1_his.dat')
    if frames is not None and his_data is not None:
        if his_data.ndim > 1:
            for i in range(his_data.shape[1]):
                ax.hist(his_data[:, i].flatten(), bins=30, alpha=0.5, label=f'His{i+1}')
        else:
            ax.hist(his_data.flatten(), bins=30, alpha=0.7)
        ax.set_title('Mn1-His Distances')
        ax.set_xlabel('Distance (Å)')
        ax.set_ylabel('Count')
        ax.axvline(2.2, color='red', linestyle='--', label='Expected')

    # 4. Mn1-Oxalate
    ax = fig.add_subplot(gs[1, 0])
    frames, ox_data = load_cpptraj_data(results_dir / 'mn_coordination' / 'mn1_oxalate.dat')
    if frames is not None and ox_data is not None:
        if ox_data.ndim > 1:
            ax.hist(ox_data[:, 0].flatten(), bins=30, alpha=0.7, label='O1 (tight)', color='blue')
            if ox_data.shape[1] > 1:
                ax.hist(ox_data[:, 1].flatten(), bins=30, alpha=0.7, label='O2 (loose)', color='orange')
        ax.set_title('Mn1-Oxalate (Bidentate)')
        ax.set_xlabel('Distance (Å)')
        ax.legend(fontsize=8)

    # 5. Lid RMSD
    ax = fig.add_subplot(gs[1, 1])
    frames, lid_rmsd = load_cpptraj_data(results_dir / 'lid_dynamics' / 'lid_rmsd.dat')
    if frames is not None:
        time_ns = frames * 0.001
        ax.plot(time_ns, lid_rmsd, color=COLORS['lid'], linewidth=0.5)
        ax.set_title(f'Lid RMSD\nMean: {np.mean(lid_rmsd):.2f} Å')
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel('RMSD (Å)')

    # 6. Glu162-Mn histogram
    ax = fig.add_subplot(gs[1, 2])
    frames, glu_mn = load_cpptraj_data(results_dir / 'lid_dynamics' / 'glu162_mn.dat')
    if frames is not None:
        ax.hist(glu_mn.flatten(), bins=50, color=COLORS['lid'], alpha=0.7)
        ax.set_title(f'Glu162-Mn Distance\nMean: {np.mean(glu_mn):.2f} Å')
        ax.set_xlabel('Distance (Å)')

    # 7-9: Statistics summary table
    ax = fig.add_subplot(gs[2, :])
    ax.axis('off')

    # Collect statistics
    stats = []
    stats.append(['Metric', 'Mean', 'Std', 'Min', 'Max'])

    for name, path in [
        ('Backbone RMSD (Å)', 'rmsd/rmsd_backbone.dat'),
        ('Lid RMSD (Å)', 'lid_dynamics/lid_rmsd.dat'),
        ('Glu162-Mn (Å)', 'lid_dynamics/glu162_mn.dat'),
    ]:
        frames, data = load_cpptraj_data(results_dir / path)
        if data is not None:
            data = data.flatten()
            stats.append([name, f'{np.mean(data):.3f}', f'{np.std(data):.3f}',
                         f'{np.min(data):.3f}', f'{np.max(data):.3f}'])

    table = ax.table(cellText=stats, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    plt.savefig(output_dir / 'analysis_dashboard.png')
    plt.savefig(output_dir / 'analysis_dashboard.pdf')
    plt.close()
    print(f"Saved: analysis_dashboard.png/pdf")


def main():
    parser = argparse.ArgumentParser(description='Plot production analysis results')
    parser.add_argument('--results-dir', type=Path,
                       default=Path('analysis/results/BiOx+2'),
                       help='Directory containing cpptraj results')
    args = parser.parse_args()

    # Find results directory
    results_dir = args.results_dir
    if not results_dir.is_absolute():
        # Try relative to script location
        script_dir = Path(__file__).parent.parent.parent
        results_dir = script_dir / results_dir

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        print("Run the analysis pipeline first: ./run_full_analysis.sh")
        sys.exit(1)

    output_dir = results_dir / 'figures'
    output_dir.mkdir(exist_ok=True)

    print(f"Loading results from: {results_dir}")
    print(f"Saving figures to: {output_dir}")
    print()

    # Generate all plots
    plot_rmsd(results_dir, output_dir)
    plot_rmsf(results_dir, output_dir)
    plot_mn_coordination(results_dir, output_dir)
    plot_lid_dynamics(results_dir, output_dir)
    plot_summary_dashboard(results_dir, output_dir)

    print()
    print("All figures generated successfully!")
    print(f"Check {output_dir} for output files.")


if __name__ == '__main__':
    main()
