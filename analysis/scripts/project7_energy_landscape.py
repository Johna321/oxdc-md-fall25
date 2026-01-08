#!/usr/bin/env python3
"""
Project 7: 3D Energy Landscape Visualization
============================================
Creates a 3D surface showing the relationship between:
- Force constant (k)
- Equilibrium distance (r0)
- Simulation stability (bond energy variance)

This demonstrates that stable simulations occupy a specific region
of parameter space: low k, longer r0.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap

# Data from analysis
systems = {
    'BiOx+2': {
        'k': [14.0, 31.7, 38.7, 32.9],
        'r0': [2.406, 2.259, 2.084, 2.249],
        'stability': 29,  # Bond energy std dev
        'status': 'STABLE'
    },
    '1Wat+2': {
        'k': [33.0, 46.0, 36.5, 45.3],
        'r0': [2.249, 2.189, 2.108, 2.196],
        'stability': 1254,
        'status': 'UNSTABLE'
    },
    '1Wat+3': {
        'k': [92.8, 85.1, 125.3, 85.9],
        'r0': [2.019, 2.030, 1.862, 2.033],
        'stability': 446,
        'status': 'UNSTABLE'
    },
    'empty+2': {
        'k': [52.9, 43.3, 27.1, 52.6],
        'r0': [2.162, 2.197, 2.153, 2.161],
        'stability': 3726,
        'status': 'CRASHED'
    }
}

colors = {'BiOx+2': '#2ecc71', '1Wat+2': '#3498db',
          '1Wat+3': '#9b59b6', 'empty+2': '#e74c3c'}

# Create figure with multiple views
fig = plt.figure(figsize=(16, 12))

# === Panel A: 3D scatter of individual bonds ===
ax1 = fig.add_subplot(2, 2, 1, projection='3d')

for sys, data in systems.items():
    for k, r0 in zip(data['k'], data['r0']):
        # Use log stability for z-axis
        z = np.log10(data['stability'] + 1)
        ax1.scatter(r0, k, z, c=colors[sys], s=100, alpha=0.8,
                   edgecolors='black', linewidths=1)

# Add system labels
for sys, data in systems.items():
    avg_r0 = np.mean(data['r0'])
    avg_k = np.mean(data['k'])
    z = np.log10(data['stability'] + 1)
    ax1.text(avg_r0, avg_k, z + 0.3, sys, fontsize=10, fontweight='bold')

ax1.set_xlabel('Equilibrium Distance r₀ (Å)', fontsize=11)
ax1.set_ylabel('Force Constant k (kcal/mol·Å²)', fontsize=11)
ax1.set_zlabel('log₁₀(Bond Energy σ)', fontsize=11)
ax1.set_title('A) 3D Parameter Space\n(Each point = one Mn-ligand bond)', fontsize=12, fontweight='bold')
ax1.view_init(elev=20, azim=45)

# === Panel B: Theoretical stability surface ===
ax2 = fig.add_subplot(2, 2, 2, projection='3d')

# Create meshgrid
r0_range = np.linspace(1.8, 2.5, 50)
k_range = np.linspace(10, 130, 50)
R0, K = np.meshgrid(r0_range, k_range)

# Theoretical model: instability increases with k and decreases with r0
# Based on harmonic oscillator: E_max ~ k * (displacement)^2
# And displacement tolerance increases with longer bonds
Z = np.log10(K * (2.2 / R0)**2 * 50 + 1)  # Empirical model

# Custom colormap: green (stable) to red (unstable)
cmap = LinearSegmentedColormap.from_list('stability',
    ['#2ecc71', '#f1c40f', '#e74c3c'])

surf = ax2.plot_surface(R0, K, Z, cmap=cmap, alpha=0.7, linewidth=0)

# Overlay actual data points
for sys, data in systems.items():
    avg_r0 = np.mean(data['r0'])
    avg_k = np.mean(data['k'])
    z = np.log10(data['stability'] + 1)
    ax2.scatter([avg_r0], [avg_k], [z], c='black', s=200, marker='o',
               edgecolors='white', linewidths=2, zorder=10)
    ax2.text(avg_r0, avg_k, z + 0.4, sys, fontsize=10, fontweight='bold')

ax2.set_xlabel('r₀ (Å)', fontsize=11)
ax2.set_ylabel('k (kcal/mol·Å²)', fontsize=11)
ax2.set_zlabel('Predicted Instability', fontsize=11)
ax2.set_title('B) Theoretical Stability Surface\n(Black dots = observed systems)', fontsize=12, fontweight='bold')
ax2.view_init(elev=25, azim=135)

# === Panel C: Top-down view with contours ===
ax3 = fig.add_subplot(2, 2, 3)

# Contour plot
contour = ax3.contourf(R0, K, Z, levels=20, cmap=cmap)
plt.colorbar(contour, ax=ax3, label='Predicted Instability (log scale)')

# Add stability boundaries
ax3.axhline(y=35, color='white', linestyle='--', linewidth=2, label='Stability threshold')
ax3.axhline(y=60, color='white', linestyle=':', linewidth=2)

# Plot actual systems
for sys, data in systems.items():
    avg_r0 = np.mean(data['r0'])
    avg_k = np.mean(data['k'])
    marker = 'o' if data['status'] == 'STABLE' else ('s' if data['status'] == 'UNSTABLE' else 'X')
    ax3.scatter(avg_r0, avg_k, c=colors[sys], s=300, marker=marker,
               edgecolors='black', linewidths=2, label=f"{sys} ({data['status']})")

ax3.set_xlabel('Equilibrium Distance r₀ (Å)', fontsize=12)
ax3.set_ylabel('Force Constant k (kcal/mol·Å²)', fontsize=12)
ax3.set_title('C) Stability Map (Top View)\nCircle=Stable, Square=Unstable, X=Crashed', fontsize=12, fontweight='bold')
ax3.legend(loc='upper right', fontsize=9)

# === Panel D: Stability score decomposition ===
ax4 = fig.add_subplot(2, 2, 4)

# Calculate stability scores for each system
def calc_stability_score(k_vals, r0_vals):
    """Lower score = more stable"""
    avg_k = np.mean(k_vals)
    avg_r0 = np.mean(r0_vals)
    k_range = max(k_vals) - min(k_vals)
    r0_range = max(r0_vals) - min(r0_vals)
    # Weighted score: high k bad, short r0 bad, high variance bad
    return avg_k / 30 + (2.2 - avg_r0) * 5 + k_range / 20

scores = {}
components = {}
for sys, data in systems.items():
    avg_k = np.mean(data['k'])
    avg_r0 = np.mean(data['r0'])
    k_range = max(data['k']) - min(data['k'])

    components[sys] = {
        'Force Constant': avg_k / 30,
        'Bond Length': (2.2 - avg_r0) * 5,
        'Heterogeneity': k_range / 20
    }
    scores[sys] = sum(components[sys].values())

# Stacked bar chart
x = np.arange(len(systems))
width = 0.6
bottom = np.zeros(len(systems))

comp_colors = ['#3498db', '#e74c3c', '#f39c12']
comp_names = ['Force Constant', 'Bond Length', 'Heterogeneity']

for i, comp in enumerate(comp_names):
    values = [components[sys][comp] for sys in systems.keys()]
    ax4.bar(x, values, width, bottom=bottom, label=comp, color=comp_colors[i], alpha=0.8)
    bottom += values

# Add stability status
for i, sys in enumerate(systems.keys()):
    status = systems[sys]['status']
    ax4.annotate(status, (i, scores[sys] + 0.3), ha='center', fontsize=10, fontweight='bold')

ax4.set_xticks(x)
ax4.set_xticklabels(systems.keys(), fontsize=11)
ax4.set_ylabel('Instability Score (decomposed)', fontsize=12)
ax4.set_title('D) Instability Score Breakdown\nLower = More Stable', fontsize=12, fontweight='bold')
ax4.legend(loc='upper left', fontsize=10)

plt.tight_layout()
plt.savefig('../results/energy_landscape_3d.png', dpi=150, bbox_inches='tight')
print("Saved: energy_landscape_3d.png")
plt.close()

# Print summary
print("\n" + "="*70)
print("PROJECT 7: ENERGY LANDSCAPE ANALYSIS")
print("="*70)
print("\nInstability Scores (lower = more stable):")
for sys in sorted(scores.keys(), key=lambda x: scores[x]):
    print(f"  {sys}: {scores[sys]:.2f} ({systems[sys]['status']})")
print("\nConclusion: BiOx+2 occupies the most favorable region of parameter space")
print("="*70)
