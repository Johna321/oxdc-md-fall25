#!/usr/bin/env python3
"""
Comprehensive Mn Coordination Analysis - OxDC Systems
Comparing oxidation states, coordination geometry, and stability predictors
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches

# Complete data from mn_bonds.csv files
# Site 1 (catalytic site) parameters
site1_data = {
    'BiOx+2': {
        'ligands': ['His95', 'His97', 'Glu101', 'His140', 'Oxalate-O1', 'Oxalate-O2'],
        'r0': [2.406, 2.259, 2.084, 2.249, 2.112, 2.424],
        'k': [14.0, 31.7, 38.7, 32.9, 49.4, 11.6],
        'oxidation': 'Mn(II)',
        'substrate': 'Bicyclic oxalate'
    },
    '1Wat+2': {
        'ligands': ['His95', 'His97', 'Glu101', 'His140', 'Water'],
        'r0': [2.249, 2.189, 2.108, 2.196, 2.165],
        'k': [33.0, 46.0, 36.5, 45.3, 48.6],
        'oxidation': 'Mn(II)',
        'substrate': 'Water'
    },
    '1Wat+3': {
        'ligands': ['His95', 'His97', 'Glu101', 'His140'],
        'r0': [2.019, 2.030, 1.862, 2.033],
        'k': [92.8, 85.1, 125.3, 85.9],
        'oxidation': 'Mn(III)',
        'substrate': 'None (resting)'
    },
    'empty+2': {
        'ligands': ['His95', 'His97', 'Glu101', 'His140'],
        'r0': [2.162, 2.197, 2.153, 2.161],
        'k': [52.9, 43.3, 27.1, 52.6],
        'oxidation': 'Mn(II)',
        'substrate': 'None (empty)'
    }
}

# Site 2 parameters (same for 1Wat+2, 1Wat+3, empty+2; not present in BiOx+2)
site2_data = {
    '1Wat+2': {'r0': [2.206, 2.213, 2.250, 2.235], 'k': [42.6, 39.6, 15.4, 35.0]},
    '1Wat+3': {'r0': [2.206, 2.213, 2.250, 2.235], 'k': [42.6, 39.6, 15.4, 35.0]},
    'empty+2': {'r0': [2.206, 2.213, 2.250, 2.235], 'k': [42.6, 39.6, 15.4, 35.0]}
}

# Stability from energy analysis
stability = {
    'BiOx+2': {'std': 29, 'max': 1210, 'status': 'STABLE'},
    '1Wat+2': {'std': 1254, 'max': 8571, 'status': 'UNSTABLE'},
    '1Wat+3': {'std': 446, 'max': 4310, 'status': 'UNSTABLE'},
    'empty+2': {'std': 3726, 'max': 14157, 'status': 'CRASHED'}
}

systems = ['BiOx+2', '1Wat+2', '1Wat+3', 'empty+2']
colors = {'BiOx+2': '#2ecc71', '1Wat+2': '#3498db',
          '1Wat+3': '#9b59b6', 'empty+2': '#e74c3c'}

# Figure 1: Mn(II) vs Mn(III) Oxidation State Comparison
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Panel A: Bond length distributions by oxidation state
ax = axes[0]
mn2_r0 = []
mn3_r0 = []
for sys in systems:
    if site1_data[sys]['oxidation'] == 'Mn(II)':
        mn2_r0.extend(site1_data[sys]['r0'][:4])  # First 4 protein ligands
    else:
        mn3_r0.extend(site1_data[sys]['r0'][:4])

ax.hist(mn2_r0, bins=10, alpha=0.7, label=f'Mn(II) (n={len(mn2_r0)})', color='#3498db', edgecolor='black')
ax.hist(mn3_r0, bins=6, alpha=0.7, label=f'Mn(III) (n={len(mn3_r0)})', color='#9b59b6', edgecolor='black')
ax.axvline(x=2.2, color='gray', linestyle='--', label='Mn(II) typical')
ax.axvline(x=2.0, color='purple', linestyle='--', alpha=0.7, label='Mn(III) typical')
ax.set_xlabel('Equilibrium Bond Length (Å)', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('A) Mn-Ligand Bond Lengths\nby Oxidation State', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)

# Panel B: Force constant distributions
ax = axes[1]
mn2_k = []
mn3_k = []
for sys in systems:
    if site1_data[sys]['oxidation'] == 'Mn(II)':
        mn2_k.extend(site1_data[sys]['k'][:4])
    else:
        mn3_k.extend(site1_data[sys]['k'][:4])

ax.hist(mn2_k, bins=10, alpha=0.7, label=f'Mn(II) (n={len(mn2_k)})', color='#3498db', edgecolor='black')
ax.hist(mn3_k, bins=6, alpha=0.7, label=f'Mn(III) (n={len(mn3_k)})', color='#9b59b6', edgecolor='black')
ax.axvline(x=40, color='gray', linestyle='--', label='Mn(II) typical')
ax.axvline(x=95, color='purple', linestyle='--', alpha=0.7, label='Mn(III) typical')
ax.set_xlabel('Force Constant (kcal/mol·Å²)', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('B) Mn-Ligand Force Constants\nby Oxidation State', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)

# Panel C: Jahn-Teller signature
ax = axes[2]
# Show Glu bond (axial) vs His average (equatorial)
for sys in systems:
    glu_r0 = site1_data[sys]['r0'][2]  # Glu101
    his_avg_r0 = np.mean([site1_data[sys]['r0'][i] for i in [0, 1, 3]])
    marker = 'o' if site1_data[sys]['oxidation'] == 'Mn(II)' else 's'
    ax.scatter(his_avg_r0, glu_r0, c=colors[sys], s=200, marker=marker,
               edgecolors='black', linewidths=2, label=f"{sys} ({site1_data[sys]['oxidation']})")

# Jahn-Teller line (compressed = axial shorter than equatorial)
ax.plot([1.9, 2.5], [1.9, 2.5], 'k--', alpha=0.3, label='_nolegend_')
ax.fill_between([1.9, 2.5], [1.9, 2.5], [1.5, 2.1], alpha=0.1, color='red')
ax.annotate('Jahn-Teller\ncompression', xy=(2.1, 1.75), fontsize=10, ha='center', color='darkred')

ax.set_xlabel('Average His Bond Length (Å)', fontsize=12)
ax.set_ylabel('Glu Bond Length (Å)', fontsize=12)
ax.set_title('C) Jahn-Teller Distortion Analysis\n(Glu vs His coordination)', fontsize=14, fontweight='bold')
ax.legend(fontsize=9, loc='upper left')
ax.set_xlim(1.95, 2.45)
ax.set_ylim(1.75, 2.25)

plt.tight_layout()
plt.savefig('../results/oxidation_state_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: oxidation_state_analysis.png")
plt.close()

# Figure 2: BiOx+2 Substrate Coordination (unique feature)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Coordination sphere schematic
ax = axes[0]
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_aspect('equal')
ax.axis('off')

# Draw Mn center
mn = plt.Circle((0, 0), 0.3, color='#8B4513', zorder=10)
ax.add_patch(mn)
ax.annotate('Mn', (0, 0), ha='center', va='center', fontsize=14, fontweight='bold', color='white', zorder=11)

# Draw ligands
ligand_positions = {
    'His95': (-1.8, 1.5),
    'His97': (1.8, 1.5),
    'Glu101': (0, -2.0),
    'His140': (0, 2.2),
    'Oxalate': (-1.5, -1.0)
}

ligand_colors = {
    'His95': '#4169E1',
    'His97': '#4169E1',
    'Glu101': '#DC143C',
    'His140': '#4169E1',
    'Oxalate': '#228B22'
}

for lig, pos in ligand_positions.items():
    color = ligand_colors[lig]
    if lig == 'Oxalate':
        # Draw bidentate oxalate
        rect = FancyBboxPatch((pos[0]-0.6, pos[1]-0.3), 1.2, 0.6,
                              boxstyle="round,pad=0.1", facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.annotate('Oxalate\n(bidentate)', pos, ha='center', va='center', fontsize=10, fontweight='bold', color='white')
        # Two bonds to Mn
        ax.plot([pos[0]-0.2, -0.15], [pos[1]+0.3, -0.2], 'k-', linewidth=2)
        ax.plot([pos[0]+0.2, 0.15], [pos[1]+0.3, -0.2], 'k-', linewidth=2)
        ax.annotate('2.11Å', (pos[0]-0.5, pos[1]+0.7), fontsize=9, color='darkgreen')
        ax.annotate('2.42Å', (pos[0]+0.5, pos[1]+0.7), fontsize=9, color='darkgreen')
    else:
        circle = plt.Circle(pos, 0.35, color=color, zorder=5)
        ax.add_patch(circle)
        ax.annotate(lig.replace('His', 'H').replace('Glu', 'E'), pos,
                   ha='center', va='center', fontsize=10, fontweight='bold', color='white', zorder=6)
        ax.plot([0, pos[0]*0.85], [0, pos[1]*0.85], 'k-', linewidth=2)

ax.set_title('BiOx+2 Coordination Sphere\n(6-coordinate with substrate)', fontsize=14, fontweight='bold')

# Legend
legend_elements = [
    mpatches.Patch(facecolor='#4169E1', label='Histidine'),
    mpatches.Patch(facecolor='#DC143C', label='Glutamate'),
    mpatches.Patch(facecolor='#228B22', label='Oxalate (substrate)'),
    mpatches.Patch(facecolor='#8B4513', label='Mn(II)')]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

# Panel B: Asymmetric bidentate coordination
ax = axes[1]
systems_with_sub = ['BiOx+2']
# Show the asymmetry in oxalate binding
r0_values = site1_data['BiOx+2']['r0']
k_values = site1_data['BiOx+2']['k']
ligand_names = site1_data['BiOx+2']['ligands']

x = np.arange(len(ligand_names))
width = 0.35

bars1 = ax.bar(x - width/2, r0_values, width, label='Bond Length (Å)', color='#3498db', alpha=0.8)
ax2 = ax.twinx()
bars2 = ax2.bar(x + width/2, k_values, width, label='Force Constant', color='#e74c3c', alpha=0.8)

ax.set_ylabel('Equilibrium Distance (Å)', color='#3498db', fontsize=12)
ax2.set_ylabel('Force Constant (kcal/mol·Å²)', color='#e74c3c', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(ligand_names, rotation=45, ha='right')
ax.set_title('BiOx+2: Asymmetric Oxalate Coordination\n(Substrate provides flexible binding)', fontsize=14, fontweight='bold')

# Highlight the oxalate asymmetry
ax.annotate('Tight\nbinding', xy=(4, 2.112), xytext=(4.5, 2.3),
            arrowprops=dict(arrowstyle='->', color='green'), fontsize=10, color='darkgreen')
ax.annotate('Loose\nbinding', xy=(5, 2.424), xytext=(5.5, 2.6),
            arrowprops=dict(arrowstyle='->', color='green'), fontsize=10, color='darkgreen')

# Combined legend
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
plt.savefig('../results/substrate_coordination.png', dpi=150, bbox_inches='tight')
print("Saved: substrate_coordination.png")
plt.close()

# Figure 3: Stability Predictor Model
fig, ax = plt.subplots(figsize=(12, 8))

# Create a stability score based on multiple factors
for sys in systems:
    # Factors contributing to stability
    avg_k = np.mean(site1_data[sys]['k'][:4])  # Average force constant
    max_k = max(site1_data[sys]['k'][:4])       # Maximum force constant
    r0_range = max(site1_data[sys]['r0'][:4]) - min(site1_data[sys]['r0'][:4])  # Bond length range

    # Log stability metric
    log_std = np.log10(stability[sys]['std'] + 1)

    # Size based on max energy spike
    size = 100 + stability[sys]['max'] / 20

    # Plot
    sc = ax.scatter(avg_k, r0_range, s=size, c=colors[sys],
                    alpha=0.8, edgecolors='black', linewidths=2)

    # Label with stability status
    status = stability[sys]['status']
    ax.annotate(f'{sys}\n({status})',
                xy=(avg_k, r0_range),
                xytext=(10, 10), textcoords='offset points',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Define stability regions
ax.axvspan(0, 35, alpha=0.1, color='green')
ax.axvspan(35, 60, alpha=0.1, color='yellow')
ax.axvspan(60, 130, alpha=0.1, color='red')

ax.annotate('STABLE ZONE', xy=(17, 0.1), fontsize=12, color='darkgreen', fontweight='bold')
ax.annotate('MARGINAL', xy=(45, 0.1), fontsize=12, color='olive', fontweight='bold')
ax.annotate('UNSTABLE', xy=(85, 0.1), fontsize=12, color='darkred', fontweight='bold')

ax.set_xlabel('Average Force Constant (kcal/mol·Å²)', fontsize=14)
ax.set_ylabel('Bond Length Range (Å)', fontsize=14)
ax.set_title('MD Stability Predictor: Force Field Parameter Space\n(Bubble size = peak energy spike)',
             fontsize=14, fontweight='bold')

# Add trend line annotation
ax.annotate('Lower k + tighter coordination\n= more stable simulations',
            xy=(25, 0.35), fontsize=11, fontstyle='italic',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.tight_layout()
plt.savefig('../results/stability_predictor.png', dpi=150, bbox_inches='tight')
print("Saved: stability_predictor.png")
plt.close()

# Print comprehensive summary
print("\n" + "="*80)
print("COMPREHENSIVE Mn COORDINATION ANALYSIS")
print("="*80)

print("\n--- SITE 1 (Catalytic Site) ---")
print(f"{'System':<10} {'Oxidation':<8} {'Substrate':<15} {'Avg r0':>8} {'Avg k':>8} {'Stability':<10}")
print("-"*80)
for sys in systems:
    avg_r0 = np.mean(site1_data[sys]['r0'][:4])
    avg_k = np.mean(site1_data[sys]['k'][:4])
    ox = site1_data[sys]['oxidation']
    sub = site1_data[sys]['substrate'][:12]
    status = stability[sys]['status']
    print(f"{sys:<10} {ox:<8} {sub:<15} {avg_r0:>8.3f} {avg_k:>8.1f} {status:<10}")

print("\n--- KEY FINDINGS ---")
print("1. Mn(III) in 1Wat+3 shows Jahn-Teller compression: Glu-Mn = 1.86Å (axial)")
print("2. BiOx+2 has asymmetric bidentate oxalate: tight O (2.11Å) + loose O (2.42Å)")
print("3. Force constants correlate with oxidation state: Mn(III) ~95, Mn(II) ~35")
print("4. BiOx+2's low force constants (avg 29) enable stable MD trajectories")
print("5. Empty sites without substrate show intermediate instability")
print("="*80)
