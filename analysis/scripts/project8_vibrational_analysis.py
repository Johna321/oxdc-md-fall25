#!/usr/bin/env python3
"""
Project 8: Vibrational Frequency Analysis
=========================================
Calculate expected vibrational frequencies from force constants
and compare with typical MD timesteps to identify numerical instability risks.

Key insight: High force constants → high frequencies → potential timestep issues
"""

import matplotlib.pyplot as plt
import numpy as np

# Physical constants
# k in kcal/mol·Å² → convert to SI for frequency calculation
KCAL_TO_J = 4184  # J/kcal
ANGSTROM_TO_M = 1e-10  # m/Å
AMU_TO_KG = 1.66054e-27  # kg/amu

# Reduced masses (approximate)
# Mn-N (His): Mn=55, N=14 → μ = 55*14/(55+14) = 11.16 amu
# Mn-O (Glu): Mn=55, O=16 → μ = 55*16/(55+16) = 12.39 amu
REDUCED_MASS_MN_N = 11.16  # amu
REDUCED_MASS_MN_O = 12.39  # amu

def force_constant_to_frequency(k_kcal, reduced_mass_amu):
    """
    Convert force constant to vibrational frequency.

    k: force constant in kcal/mol·Å²
    reduced_mass: in amu

    Returns: frequency in cm⁻¹ (wavenumber)
    """
    # Convert k to SI: J/m²
    k_si = k_kcal * KCAL_TO_J / (ANGSTROM_TO_M**2) / 6.022e23  # per molecule

    # Convert mass to SI
    m_si = reduced_mass_amu * AMU_TO_KG

    # Angular frequency: ω = sqrt(k/m)
    omega = np.sqrt(k_si / m_si)

    # Frequency in Hz
    freq_hz = omega / (2 * np.pi)

    # Convert to wavenumber (cm⁻¹)
    c = 3e10  # cm/s
    wavenumber = freq_hz / c

    # Also get period for timestep comparison
    period_fs = 1e15 / freq_hz  # femtoseconds

    return wavenumber, period_fs

# System data
systems = {
    'BiOx+2': {
        'bonds': [
            ('Mn-His95', 14.0, 'N'),
            ('Mn-His97', 31.7, 'N'),
            ('Mn-Glu101', 38.7, 'O'),
            ('Mn-His140', 32.9, 'N'),
        ],
        'status': 'STABLE'
    },
    '1Wat+2': {
        'bonds': [
            ('Mn-His95', 33.0, 'N'),
            ('Mn-His97', 46.0, 'N'),
            ('Mn-Glu101', 36.5, 'O'),
            ('Mn-His140', 45.3, 'N'),
        ],
        'status': 'UNSTABLE'
    },
    '1Wat+3': {
        'bonds': [
            ('Mn-His95', 92.8, 'N'),
            ('Mn-His97', 85.1, 'N'),
            ('Mn-Glu101', 125.3, 'O'),
            ('Mn-His140', 85.9, 'N'),
        ],
        'status': 'UNSTABLE'
    },
    'empty+2': {
        'bonds': [
            ('Mn-His95', 52.9, 'N'),
            ('Mn-His97', 43.3, 'N'),
            ('Mn-Glu101', 27.1, 'O'),
            ('Mn-His140', 52.6, 'N'),
        ],
        'status': 'CRASHED'
    }
}

colors = {'BiOx+2': '#2ecc71', '1Wat+2': '#3498db',
          '1Wat+3': '#9b59b6', 'empty+2': '#e74c3c'}

# Calculate frequencies for all systems
results = {}
for sys, data in systems.items():
    results[sys] = []
    for bond_name, k, atom_type in data['bonds']:
        mu = REDUCED_MASS_MN_N if atom_type == 'N' else REDUCED_MASS_MN_O
        wavenumber, period = force_constant_to_frequency(k, mu)
        results[sys].append({
            'bond': bond_name,
            'k': k,
            'wavenumber': wavenumber,
            'period_fs': period
        })

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# === Panel A: Vibrational frequencies ===
ax = axes[0, 0]
x = np.arange(4)  # 4 bonds per system
width = 0.2
multiplier = 0

for sys in systems.keys():
    frequencies = [r['wavenumber'] for r in results[sys]]
    offset = width * multiplier
    bars = ax.bar(x + offset, frequencies, width, label=sys, color=colors[sys], alpha=0.8)
    multiplier += 1

ax.set_ylabel('Vibrational Frequency (cm⁻¹)', fontsize=12)
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(['His95', 'His97', 'Glu101', 'His140'])
ax.set_title('A) Calculated Mn-Ligand Vibrational Frequencies', fontsize=14, fontweight='bold')
ax.legend(loc='upper left')
ax.axhline(y=400, color='gray', linestyle='--', alpha=0.5)
ax.annotate('Typical metal-ligand\nstretching region', xy=(3, 420), fontsize=9, color='gray')

# === Panel B: Periods vs timestep ===
ax = axes[0, 1]

# Typical MD timestep
MD_TIMESTEP = 2.0  # fs (with SHAKE on H atoms)
SHAKE_RECOMMENDED = 10  # periods per timestep for safety

for i, sys in enumerate(systems.keys()):
    periods = [r['period_fs'] for r in results[sys]]
    y = [i] * len(periods)
    ax.scatter(periods, y, c=colors[sys], s=200, alpha=0.8,
              edgecolors='black', linewidths=2, label=sys)

# Safety threshold
ax.axvline(x=MD_TIMESTEP * SHAKE_RECOMMENDED, color='red', linestyle='--', linewidth=2)
ax.axvspan(0, MD_TIMESTEP * SHAKE_RECOMMENDED, alpha=0.1, color='red')
ax.annotate('DANGER ZONE\n(period < 10× timestep)', xy=(12, 3.5), fontsize=10, color='red')
ax.annotate('2 fs timestep\n× 10 = 20 fs', xy=(22, 2.5), fontsize=9, color='red')

ax.set_xlabel('Vibrational Period (fs)', fontsize=12)
ax.set_yticks(range(len(systems)))
ax.set_yticklabels(systems.keys())
ax.set_title('B) Period Safety Analysis\n(Red zone = potential timestep issues)', fontsize=14, fontweight='bold')
ax.set_xlim(0, 100)

# === Panel C: Frequency vs force constant ===
ax = axes[1, 0]

all_k = []
all_freq = []
all_colors = []
all_labels = []

for sys in systems.keys():
    for r in results[sys]:
        all_k.append(r['k'])
        all_freq.append(r['wavenumber'])
        all_colors.append(colors[sys])
        all_labels.append(sys)

ax.scatter(all_k, all_freq, c=all_colors, s=150, alpha=0.8, edgecolors='black')

# Fit line (ω ∝ √k)
k_fit = np.linspace(10, 130, 100)
# Theoretical: ν = (1/2π) * sqrt(k/μ), so ν ∝ √k
coef = np.mean([f/np.sqrt(k) for f, k in zip(all_freq, all_k)])
freq_fit = coef * np.sqrt(k_fit)
ax.plot(k_fit, freq_fit, 'k--', alpha=0.5, label=r'$\nu \propto \sqrt{k}$')

ax.set_xlabel('Force Constant k (kcal/mol·Å²)', fontsize=12)
ax.set_ylabel('Vibrational Frequency (cm⁻¹)', fontsize=12)
ax.set_title('C) Frequency-Force Constant Relationship\n(Confirms harmonic oscillator physics)', fontsize=14, fontweight='bold')
ax.legend()

# Add safety threshold
ax.axhline(y=500, color='orange', linestyle=':', alpha=0.7)
ax.annotate('High frequency\nwarning threshold', xy=(100, 520), fontsize=9, color='orange')

# === Panel D: Summary statistics ===
ax = axes[1, 1]
ax.axis('off')

# Create summary table
summary_text = """
╔══════════════════════════════════════════════════════════════════════╗
║              VIBRATIONAL ANALYSIS SUMMARY                            ║
╠══════════════════════════════════════════════════════════════════════╣
║ System    │ Avg ν (cm⁻¹) │ Min Period (fs) │ Status      │ Risk     ║
╠══════════════════════════════════════════════════════════════════════╣"""

risk_levels = {'BiOx+2': 'LOW', '1Wat+2': 'MEDIUM', '1Wat+3': 'HIGH', 'empty+2': 'MEDIUM'}

for sys in systems.keys():
    avg_freq = np.mean([r['wavenumber'] for r in results[sys]])
    min_period = min([r['period_fs'] for r in results[sys]])
    status = systems[sys]['status']
    risk = risk_levels[sys]
    summary_text += f"\n║ {sys:<9}│ {avg_freq:>12.0f} │ {min_period:>15.1f} │ {status:<11} │ {risk:<8}║"

summary_text += """
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║ KEY FINDINGS:                                                        ║
║ • 1Wat+3 has highest frequencies (shortest periods) → numerical risk ║
║ • BiOx+2 has lowest frequencies → most timestep-friendly             ║
║ • All periods > 20 fs, so 2 fs timestep should be safe              ║
║ • BUT: high frequencies amplify any force field errors               ║
║                                                                      ║
║ RECOMMENDATION: Consider 1 fs timestep for 1Wat+3 Mn(III) system    ║
╚══════════════════════════════════════════════════════════════════════╝
"""

ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=10,
        fontfamily='monospace', verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('../results/vibrational_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: vibrational_analysis.png")
plt.close()

# Print detailed results
print("\n" + "="*70)
print("PROJECT 8: VIBRATIONAL FREQUENCY ANALYSIS")
print("="*70)
print("\nDetailed Results:")
for sys in systems.keys():
    print(f"\n{sys} ({systems[sys]['status']}):")
    for r in results[sys]:
        print(f"  {r['bond']}: k={r['k']:.1f} → ν={r['wavenumber']:.0f} cm⁻¹, T={r['period_fs']:.1f} fs")
print("="*70)
