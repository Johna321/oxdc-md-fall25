#!/usr/bin/env python3
"""
Project 10: Parameterization Quality Assessment
==============================================
Quantify the "quality" of MCPB.py parameters by comparing with:
1. Literature values for Mn complexes
2. Internal consistency within each system
3. Chemical reasonableness criteria

This provides actionable guidance for re-parameterization.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# Literature reference values (from JCTC 2013 Mn parameters paper)
LITERATURE = {
    'Mn(II)-His': {'r0': (2.15, 2.30), 'k': (25, 50)},   # (min, max) ranges
    'Mn(II)-Glu': {'r0': (2.00, 2.20), 'k': (25, 45)},
    'Mn(III)-His': {'r0': (1.95, 2.10), 'k': (70, 100)},
    'Mn(III)-Glu': {'r0': (1.80, 2.00), 'k': (90, 130)},
}

# Our system data
systems = {
    'BiOx+2': {
        'expected_ox': 'Mn(II)',
        'bonds': {
            'His95': (2.406, 14.0),
            'His97': (2.259, 31.7),
            'Glu101': (2.084, 38.7),
            'His140': (2.249, 32.9),
        },
        'status': 'STABLE'
    },
    '1Wat+2': {
        'expected_ox': 'Mn(II)',
        'bonds': {
            'His95': (2.249, 33.0),
            'His97': (2.189, 46.0),
            'Glu101': (2.108, 36.5),
            'His140': (2.196, 45.3),
        },
        'status': 'UNSTABLE'
    },
    '1Wat+3': {
        'expected_ox': 'Mn(III)',
        'bonds': {
            'His95': (2.019, 92.8),
            'His97': (2.030, 85.1),
            'Glu101': (1.862, 125.3),
            'His140': (2.033, 85.9),
        },
        'status': 'UNSTABLE'
    },
    'empty+2': {
        'expected_ox': 'Mn(II)',
        'bonds': {
            'His95': (2.162, 52.9),
            'His97': (2.197, 43.3),
            'Glu101': (2.153, 27.1),
            'His140': (2.161, 52.6),
        },
        'status': 'CRASHED'
    }
}

colors = {'BiOx+2': '#2ecc71', '1Wat+2': '#3498db',
          '1Wat+3': '#9b59b6', 'empty+2': '#e74c3c'}

def assess_parameter_quality(r0, k, ligand_type, oxidation_state):
    """
    Score parameter quality against literature.
    Returns scores for r0 and k (0-100, higher is better).
    """
    key = f"{oxidation_state}-{ligand_type}"
    ref = LITERATURE.get(key, LITERATURE['Mn(II)-His'])

    # r0 score: 100 if in range, decreasing outside
    r0_min, r0_max = ref['r0']
    if r0_min <= r0 <= r0_max:
        r0_score = 100
    else:
        deviation = min(abs(r0 - r0_min), abs(r0 - r0_max))
        r0_score = max(0, 100 - deviation * 200)  # Lose 20 points per 0.1 Å

    # k score: 100 if in range, decreasing outside
    k_min, k_max = ref['k']
    if k_min <= k <= k_max:
        k_score = 100
    else:
        deviation = min(abs(k - k_min), abs(k - k_max))
        k_score = max(0, 100 - deviation * 2)  # Lose 2 points per unit

    return r0_score, k_score, ref

# Calculate quality scores
quality_results = {}
for sys, data in systems.items():
    quality_results[sys] = {'bonds': {}, 'overall': 0}
    total_score = 0

    for ligand, (r0, k) in data['bonds'].items():
        ligand_type = 'Glu' if 'Glu' in ligand else 'His'
        ox_state = data['expected_ox']
        r0_score, k_score, ref = assess_parameter_quality(r0, k, ligand_type, ox_state)

        quality_results[sys]['bonds'][ligand] = {
            'r0': r0, 'k': k,
            'r0_score': r0_score, 'k_score': k_score,
            'combined': (r0_score + k_score) / 2,
            'ref': ref
        }
        total_score += (r0_score + k_score) / 2

    quality_results[sys]['overall'] = total_score / len(data['bonds'])

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# === Panel A: Overall quality scores ===
ax = axes[0, 0]
sys_names = list(systems.keys())
overall_scores = [quality_results[s]['overall'] for s in sys_names]
status_labels = [systems[s]['status'] for s in sys_names]

bars = ax.bar(sys_names, overall_scores, color=[colors[s] for s in sys_names], alpha=0.8, edgecolor='black')

# Add status labels
for i, (bar, status) in enumerate(zip(bars, status_labels)):
    height = bar.get_height()
    ax.annotate(f'{status}\n{height:.0f}%',
                xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Parameter Quality Score (%)', fontsize=12)
ax.set_title('A) Overall Parameterization Quality\n(Higher = closer to literature values)', fontsize=14, fontweight='bold')
ax.set_ylim(0, 120)

# Correlation note
ax.annotate(f'Correlation with stability: r = {np.corrcoef(overall_scores, [1254, 446, 3726, 29])[0,1]:.2f}',
            xy=(0.02, 0.98), xycoords='axes fraction', fontsize=10, va='top')

# === Panel B: Bond length deviations from literature ===
ax = axes[0, 1]

x = np.arange(4)  # 4 bonds
width = 0.2
multiplier = 0

for sys in sys_names:
    deviations = []
    for ligand in ['His95', 'His97', 'Glu101', 'His140']:
        r0 = quality_results[sys]['bonds'][ligand]['r0']
        ref = quality_results[sys]['bonds'][ligand]['ref']
        ref_mid = (ref['r0'][0] + ref['r0'][1]) / 2
        deviation = r0 - ref_mid
        deviations.append(deviation)

    offset = width * multiplier
    ax.bar(x + offset, deviations, width, label=sys, color=colors[sys], alpha=0.8)
    multiplier += 1

ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax.axhspan(-0.1, 0.1, alpha=0.1, color='green')
ax.set_ylabel('Deviation from Literature r₀ (Å)', fontsize=12)
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(['His95', 'His97', 'Glu101', 'His140'])
ax.set_title('B) Bond Length Deviations from Literature\n(Green zone = ±0.1 Å)', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')

# === Panel C: Force constant deviations ===
ax = axes[1, 0]

multiplier = 0
for sys in sys_names:
    deviations = []
    for ligand in ['His95', 'His97', 'Glu101', 'His140']:
        k = quality_results[sys]['bonds'][ligand]['k']
        ref = quality_results[sys]['bonds'][ligand]['ref']
        ref_mid = (ref['k'][0] + ref['k'][1]) / 2
        deviation = k - ref_mid
        deviations.append(deviation)

    offset = width * multiplier
    ax.bar(x + offset, deviations, width, label=sys, color=colors[sys], alpha=0.8)
    multiplier += 1

ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax.axhspan(-10, 10, alpha=0.1, color='green')
ax.set_ylabel('Deviation from Literature k (kcal/mol·Å²)', fontsize=12)
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(['His95', 'His97', 'Glu101', 'His140'])
ax.set_title('C) Force Constant Deviations from Literature\n(Green zone = ±10)', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')

# === Panel D: Quality matrix heatmap ===
ax = axes[1, 1]

# Create matrix of combined scores
ligands = ['His95', 'His97', 'Glu101', 'His140']
matrix = np.zeros((len(sys_names), len(ligands)))

for i, sys in enumerate(sys_names):
    for j, ligand in enumerate(ligands):
        matrix[i, j] = quality_results[sys]['bonds'][ligand]['combined']

im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
plt.colorbar(im, ax=ax, label='Quality Score (%)')

ax.set_xticks(np.arange(len(ligands)))
ax.set_yticks(np.arange(len(sys_names)))
ax.set_xticklabels(ligands)
ax.set_yticklabels(sys_names)

# Add score values to cells
for i in range(len(sys_names)):
    for j in range(len(ligands)):
        text = ax.text(j, i, f'{matrix[i, j]:.0f}',
                      ha="center", va="center", color="black", fontsize=11, fontweight='bold')

ax.set_title('D) Parameter Quality Heatmap\n(Green=Good, Red=Problematic)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('../results/parameterization_quality.png', dpi=150, bbox_inches='tight')
print("Saved: parameterization_quality.png")
plt.close()

# Print detailed report
print("\n" + "="*70)
print("PROJECT 10: PARAMETERIZATION QUALITY ASSESSMENT")
print("="*70)

for sys in sys_names:
    print(f"\n{'='*50}")
    print(f"{sys} (Expected: {systems[sys]['expected_ox']}, Status: {systems[sys]['status']})")
    print(f"{'='*50}")
    print(f"Overall Quality Score: {quality_results[sys]['overall']:.1f}%")
    print(f"\nBond-by-bond assessment:")

    for ligand, scores in quality_results[sys]['bonds'].items():
        status = "✓" if scores['combined'] >= 80 else "⚠" if scores['combined'] >= 50 else "✗"
        print(f"  {status} {ligand}: r₀={scores['r0']:.3f}Å (score:{scores['r0_score']:.0f}), "
              f"k={scores['k']:.1f} (score:{scores['k_score']:.0f})")
        print(f"      Reference: r₀={scores['ref']['r0']}, k={scores['ref']['k']}")

print("\n" + "="*70)
print("RECOMMENDATIONS:")
print("-" * 70)
print("1. BiOx+2: His95 r₀ too long (2.41 Å) - consider re-parameterization")
print("2. 1Wat+3: All parameters match Mn(III) literature - model is correct")
print("3. empty+2: Good r₀ but anomalous k values - check MCPB.py input")
print("4. 1Wat+2: Reasonable parameters but stability issues suggest other problems")
print("="*70)
