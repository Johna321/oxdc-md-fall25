#!/usr/bin/env python3
"""
Force Constant Analysis - Comparing MCPB.py parameters across OxDC systems
"""

import matplotlib.pyplot as plt
import numpy as np

# Data from mn_bonds.csv files
systems = ['BiOx+2', '1Wat+2', '1Wat+3', 'empty+2']

# Force constants (k, kcal/mol·Å²) for Site 1 Mn-ligand bonds
# Format: [His1, His2, Glu, His3]
force_constants = {
    'BiOx+2': [14.0, 31.7, 38.7, 32.9],
    '1Wat+2': [33.0, 46.0, 36.5, 45.3],
    '1Wat+3': [92.8, 85.1, 125.3, 85.9],
    'empty+2': [52.9, 43.3, 27.1, 52.6]
}

# Equilibrium distances (r0, Å)
eq_distances = {
    'BiOx+2': [2.406, 2.259, 2.084, 2.249],
    '1Wat+2': [2.249, 2.189, 2.108, 2.196],
    '1Wat+3': [2.019, 2.030, 1.862, 2.033],
    'empty+2': [2.162, 2.197, 2.153, 2.161]
}

# Stability metrics (from energy analysis)
stability = {
    'BiOx+2': {'std': 28.9, 'max': 1210, 'status': 'STABLE'},
    '1Wat+2': {'std': 1254, 'max': 8571, 'status': 'UNSTABLE'},
    '1Wat+3': {'std': 446, 'max': 4310, 'status': 'UNSTABLE'},
    'empty+2': {'std': 3726, 'max': 14157, 'status': 'CRASHED'}
}

colors = {'BiOx+2': '#2ecc71', '1Wat+2': '#3498db',
          '1Wat+3': '#9b59b6', 'empty+2': '#e74c3c'}

ligands = ['Mn-His1', 'Mn-His2', 'Mn-Glu', 'Mn-His3']

# Figure 1: Force Constants Comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Bar chart of force constants
x = np.arange(len(ligands))
width = 0.2
for i, sys in enumerate(systems):
    axes[0].bar(x + i*width, force_constants[sys], width,
                label=sys, color=colors[sys], alpha=0.8)

axes[0].set_xlabel('Bond Type', fontsize=12)
axes[0].set_ylabel('Force Constant (kcal/mol·Å²)', fontsize=12)
axes[0].set_title('Mn-Ligand Force Constants by System', fontsize=14, fontweight='bold')
axes[0].set_xticks(x + width*1.5)
axes[0].set_xticklabels(ligands)
axes[0].legend()
axes[0].axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='_nolegend_')
axes[0].annotate('Stability threshold (~50)', xy=(3, 55), fontsize=10, color='gray')

# Scatter: Force constant vs stability
avg_k = [np.mean(force_constants[sys]) for sys in systems]
std_energy = [stability[sys]['std'] for sys in systems]

axes[1].scatter(avg_k, std_energy, c=[colors[sys] for sys in systems],
                s=200, alpha=0.8, edgecolors='black', linewidths=2)
for i, sys in enumerate(systems):
    axes[1].annotate(sys, (avg_k[i], std_energy[i]),
                     xytext=(10, 10), textcoords='offset points',
                     fontsize=12, fontweight='bold')

axes[1].set_xlabel('Average Force Constant (kcal/mol·Å²)', fontsize=12)
axes[1].set_ylabel('Bond Energy Std Dev (kcal/mol)', fontsize=12)
axes[1].set_title('Force Constant vs Simulation Stability', fontsize=14, fontweight='bold')
axes[1].set_yscale('log')

# Add trend annotation
axes[1].annotate('Higher k → Less stable',
                xy=(70, 1000), fontsize=11, fontstyle='italic',
                arrowprops=dict(arrowstyle='->', color='gray'),
                xytext=(40, 200))

plt.tight_layout()
plt.savefig('../results/force_constant_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: force_constant_analysis.png")

# Figure 2: Equilibrium Distance vs Force Constant
fig, ax = plt.subplots(figsize=(10, 8))

for sys in systems:
    ax.scatter(eq_distances[sys], force_constants[sys],
               c=colors[sys], s=150, alpha=0.8, label=sys,
               edgecolors='black', linewidths=1)

ax.set_xlabel('Equilibrium Distance (Å)', fontsize=12)
ax.set_ylabel('Force Constant (kcal/mol·Å²)', fontsize=12)
ax.set_title('Mn-Ligand Force Constants vs Equilibrium Distances\n(Each point is one Mn-ligand bond)',
             fontsize=14, fontweight='bold')
ax.legend(title='System')

# Highlight the short-bond/high-k region
ax.axvspan(1.8, 2.1, alpha=0.1, color='red')
ax.annotate('Mn(III) region\n(short bonds, high k)',
           xy=(1.95, 110), fontsize=10, ha='center', color='darkred')

ax.axvspan(2.2, 2.5, alpha=0.1, color='green')
ax.annotate('BiOx+2 region\n(longer bonds, low k)',
           xy=(2.35, 20), fontsize=10, ha='center', color='darkgreen')

plt.tight_layout()
plt.savefig('../results/distance_vs_forceconstant.png', dpi=150, bbox_inches='tight')
print("Saved: distance_vs_forceconstant.png")

# Print summary
print("\n" + "="*70)
print("FORCE CONSTANT SUMMARY")
print("="*70)
print(f"{'System':<10} {'Avg k':>10} {'Min r0':>10} {'Max r0':>10} {'Status':<12}")
print("-"*70)
for sys in systems:
    avg_k = np.mean(force_constants[sys])
    min_r = min(eq_distances[sys])
    max_r = max(eq_distances[sys])
    status = stability[sys]['status']
    print(f"{sys:<10} {avg_k:>10.1f} {min_r:>10.3f} {max_r:>10.3f} {status:<12}")
print("="*70)
print("\nKey insight: BiOx+2 has lowest average force constant AND is only stable system")
