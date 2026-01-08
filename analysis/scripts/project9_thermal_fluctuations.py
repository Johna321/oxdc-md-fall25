#!/usr/bin/env python3
"""
Project 9: Thermal Fluctuation Analysis
=======================================
Calculate expected bond length fluctuations at 300K from force constants
and compare with actual simulation behavior.

Key insight: Lower k → larger thermal fluctuations → more forgiving MD
"""

import matplotlib.pyplot as plt
import numpy as np

# Physical constants
KB = 1.987e-3  # kcal/mol·K (Boltzmann constant)
TEMP = 300  # K

def expected_fluctuation(k, T=300):
    """
    Calculate expected RMS bond length fluctuation from harmonic approximation.

    For a harmonic oscillator at temperature T:
    <(Δr)²> = kT/k  (equipartition theorem)

    k: force constant in kcal/mol·Å²
    T: temperature in K

    Returns: RMS fluctuation in Å
    """
    # <Δr²> = kT/k
    variance = KB * T / k
    rms = np.sqrt(variance)
    return rms

# System data
systems = {
    'BiOx+2': {
        'bonds': [
            ('His95', 2.406, 14.0),
            ('His97', 2.259, 31.7),
            ('Glu101', 2.084, 38.7),
            ('His140', 2.249, 32.9),
        ],
        'stability': 29,
        'status': 'STABLE'
    },
    '1Wat+2': {
        'bonds': [
            ('His95', 2.249, 33.0),
            ('His97', 2.189, 46.0),
            ('Glu101', 2.108, 36.5),
            ('His140', 2.196, 45.3),
        ],
        'stability': 1254,
        'status': 'UNSTABLE'
    },
    '1Wat+3': {
        'bonds': [
            ('His95', 2.019, 92.8),
            ('His97', 2.030, 85.1),
            ('Glu101', 1.862, 125.3),
            ('His140', 2.033, 85.9),
        ],
        'stability': 446,
        'status': 'UNSTABLE'
    },
    'empty+2': {
        'bonds': [
            ('His95', 2.162, 52.9),
            ('His97', 2.197, 43.3),
            ('Glu101', 2.153, 27.1),
            ('His140', 2.161, 52.6),
        ],
        'stability': 3726,
        'status': 'CRASHED'
    }
}

colors = {'BiOx+2': '#2ecc71', '1Wat+2': '#3498db',
          '1Wat+3': '#9b59b6', 'empty+2': '#e74c3c'}

# Calculate fluctuations
results = {}
for sys, data in systems.items():
    results[sys] = []
    for ligand, r0, k in data['bonds']:
        rms = expected_fluctuation(k)
        rel_fluct = 100 * rms / r0  # Relative fluctuation as percentage
        results[sys].append({
            'ligand': ligand,
            'r0': r0,
            'k': k,
            'rms': rms,
            'rel_fluct': rel_fluct
        })

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# === Panel A: RMS fluctuations by bond ===
ax = axes[0, 0]
x = np.arange(4)
width = 0.2
multiplier = 0

for sys in systems.keys():
    rms_values = [r['rms'] for r in results[sys]]
    offset = width * multiplier
    bars = ax.bar(x + offset, rms_values, width, label=sys, color=colors[sys], alpha=0.8)
    multiplier += 1

ax.set_ylabel('RMS Fluctuation (Å)', fontsize=12)
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(['His95', 'His97', 'Glu101', 'His140'])
ax.set_title('A) Expected Thermal Fluctuations at 300K\n(From harmonic approximation)', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')

# Add harmonic limit annotation
ax.axhline(y=0.2, color='orange', linestyle='--', alpha=0.7)
ax.annotate('Harmonic approximation\nbreaks down above ~10%', xy=(2.5, 0.21), fontsize=9, color='orange')

# === Panel B: Fluctuation vs equilibrium distance ===
ax = axes[0, 1]

for sys in systems.keys():
    for r in results[sys]:
        ax.scatter(r['r0'], r['rms'], c=colors[sys], s=150, alpha=0.8,
                  edgecolors='black', linewidths=1)

# Show "safe zones"
ax.axhspan(0.1, 0.25, alpha=0.1, color='green')
ax.axhspan(0.05, 0.1, alpha=0.2, color='yellow')
ax.axhspan(0, 0.05, alpha=0.1, color='red')

ax.annotate('Flexible\n(forgiving)', xy=(2.35, 0.17), fontsize=10, color='darkgreen')
ax.annotate('Moderate', xy=(2.35, 0.075), fontsize=10, color='olive')
ax.annotate('Stiff\n(unforgiving)', xy=(2.35, 0.03), fontsize=10, color='darkred')

ax.set_xlabel('Equilibrium Bond Length r₀ (Å)', fontsize=12)
ax.set_ylabel('RMS Fluctuation (Å)', fontsize=12)
ax.set_title('B) Fluctuation vs Bond Length\n(BiOx+2 is most flexible)', fontsize=14, fontweight='bold')

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, label=s, alpha=0.8) for s, c in colors.items()]
ax.legend(handles=legend_elements, loc='lower right')

# === Panel C: Relative fluctuation (% of bond length) ===
ax = axes[1, 0]

x_pos = 0
for sys in systems.keys():
    for i, r in enumerate(results[sys]):
        ax.barh(x_pos, r['rel_fluct'], color=colors[sys], alpha=0.8, edgecolor='black')
        ax.text(r['rel_fluct'] + 0.5, x_pos, f"{r['rel_fluct']:.1f}%", va='center', fontsize=9)
        x_pos += 1
    x_pos += 0.5  # Space between systems

# Add system labels
ytick_positions = [1.5, 6, 10.5, 15]
ax.set_yticks(ytick_positions)
ax.set_yticklabels(systems.keys())

# Harmonic validity threshold
ax.axvline(x=10, color='red', linestyle='--', linewidth=2)
ax.annotate('Harmonic\nbreakdown\nlimit', xy=(10.5, 2), fontsize=9, color='red')

ax.set_xlabel('Relative Fluctuation (% of bond length)', fontsize=12)
ax.set_title('C) Relative Bond Length Fluctuations\n(Higher % = more flexible)', fontsize=14, fontweight='bold')

# === Panel D: Fluctuation energy budget ===
ax = axes[1, 1]

# At 300K, each harmonic DOF has kT/2 energy on average
# Total energy in bond stretching = number of bonds × kT/2
# When this energy is concentrated, max displacement = sqrt(n × kT / k)

systems_list = list(systems.keys())
n_systems = len(systems_list)

# Calculate energy-based metrics
total_stretch_energy = n_systems * [0]
max_energy_spike = n_systems * [0]

for i, sys in enumerate(systems_list):
    data = systems[sys]
    k_values = [b[2] for b in data['bonds']]
    avg_k = np.mean(k_values)

    # Thermal energy per bond at 300K
    thermal_energy_per_bond = KB * TEMP / 2  # kT/2 per DOF

    # If energy fluctuates, could all go to one bond temporarily
    # Max displacement when all energy (4 bonds) goes to one:
    max_displacement = np.sqrt(4 * KB * TEMP / min(k_values))

    total_stretch_energy[i] = 4 * thermal_energy_per_bond
    max_energy_spike[i] = 0.5 * min(k_values) * max_displacement**2

# Bar chart
x = np.arange(n_systems)
width = 0.35

bars1 = ax.bar(x - width/2, total_stretch_energy, width, label='Average thermal energy', color='#3498db')
bars2 = ax.bar(x + width/2, [systems[s]['stability']/1000 for s in systems_list], width,
               label='Observed σ/1000', color='#e74c3c')

ax.set_xticks(x)
ax.set_xticklabels(systems_list)
ax.set_ylabel('Energy (kcal/mol)', fontsize=12)
ax.set_title('D) Thermal Budget vs Observed Instability\n(Red >> Blue indicates force field problems)', fontsize=14, fontweight='bold')
ax.legend()

plt.tight_layout()
plt.savefig('../results/thermal_fluctuations.png', dpi=150, bbox_inches='tight')
print("Saved: thermal_fluctuations.png")
plt.close()

# Print summary
print("\n" + "="*70)
print("PROJECT 9: THERMAL FLUCTUATION ANALYSIS")
print("="*70)

for sys in systems.keys():
    avg_rms = np.mean([r['rms'] for r in results[sys]])
    avg_rel = np.mean([r['rel_fluct'] for r in results[sys]])
    print(f"\n{sys} ({systems[sys]['status']}):")
    print(f"  Average RMS fluctuation: {avg_rms:.3f} Å")
    print(f"  Average relative fluctuation: {avg_rel:.1f}%")
    print(f"  Range: {min([r['rms'] for r in results[sys]]):.3f} - {max([r['rms'] for r in results[sys]]):.3f} Å")

print("\n" + "="*70)
print("CONCLUSION: BiOx+2's larger allowed fluctuations provide a 'buffer'")
print("            against transient energy spikes that crash other systems.")
print("="*70)
