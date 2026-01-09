# OxDC MD Analysis Presentation

LaTeX Beamer presentation summarizing force field parameter analysis findings.

## Files

- `oxdc_md_analysis.tex` - Main presentation with placeholder figures (for review/editing)
- `oxdc_md_analysis_with_figures.tex` - Version with embedded figure paths (for compilation)
- `Makefile` - Build automation

## Compilation

### Using Make
```bash
cd presentation
make            # Compile with figures
make clean      # Remove build artifacts
```

### Manual Compilation
```bash
pdflatex oxdc_md_analysis_with_figures.tex
pdflatex oxdc_md_analysis_with_figures.tex  # Run twice for TOC
```

## Required Figures

All figures are located in `../analysis/results/`:

| Figure | Description |
|--------|-------------|
| `bond_energy_distribution.png` | Finding 1 - Energy distribution violin plots |
| `force_constant_analysis.png` | Finding 2 - Force constant comparison |
| `oxidation_state_analysis.png` | Finding 3 - Mn(II) vs Mn(III) |
| `substrate_coordination.png` | Finding 4 - Bidentate oxalate |
| `distance_vs_forceconstant.png` | Finding 5 - r0 vs k correlation |
| `stability_predictor.png` | Finding 6 - Stability zones |
| `energy_landscape_3d.png` | Project 7 - 3D parameter space |
| `vibrational_analysis.png` | Project 8 - Frequency analysis |
| `thermal_fluctuations.png` | Project 9 - Thermal RMS |
| `parameterization_quality.png` | Project 10 - Literature comparison |
| `coordination_geometry.png` | Project 11 - Geometry analysis |
| `ml_stability_analysis.png` | Exploratory - ML prediction |

## Presentation Structure

1. **Introduction** - OxDC background and computational challenge
2. **Key Findings** (6 findings) - Core stability analysis results
3. **Extended Analysis** (Projects 7-11) - Additional computational investigations
4. **Exploratory Projects** - ML and web demo
5. **Conclusions** - Root cause revision and recommendations

## Dependencies

- LaTeX distribution (TeX Live recommended)
- Beamer package
- TikZ package
- Standard packages: graphicx, booktabs, amsmath, siunitx, hyperref

## Notes

- Presentation uses UF colors (blue #0021A5, orange #FA4616)
- 16:9 aspect ratio for modern displays
- All figures reference `../analysis/results/` directory
