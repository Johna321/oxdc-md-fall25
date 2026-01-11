# BiOx+2 Topology Reference

## System Overview

| Property | Value |
|----------|-------|
| Topology File | 5vg3_solv.prmtop |
| Total Atoms | 63,287 |
| Residues | 19,473 |
| Molecules | 19,090 |
| Solvent Molecules | 19,079 (TIP3P) |
| Box Type | Orthorhombic |

## Protein Chain (Residues 1-385)

### Key Active Site Residues

| Residue | Name | Atoms | Role |
|---------|------|-------|------|
| 95 | HD1 (His) | 1508-1524 | Mn1 ligand |
| 96 | TRP | 1525-1548 | Electron transfer (W96) |
| 97 | HD2 (His) | 1549-1565 | Mn1 ligand |
| 101 | GU1 (Glu) | 1613-1627 | Mn1 ligand |
| 140 | HD3 (His) | 2219-2235 | Mn1 ligand |
| 160-166 | Lid | 2512-2617 | Flexible lid |
| 162 | GLH (Glu) | 2543-2558 | Proton donor, lid key residue |
| 273 | HID (His) | 4268-4284 | Near Mn2 |
| 274 | TRP | 4285-4308 | Electron transfer (W274) |
| 280 | GLU | 4369-4386 | Mn2 ligand |

### Mn Centers

| Site | Residue | Atom | Type | Charge | Role |
|------|---------|------|------|--------|------|
| Mn1 | MN1 (383) | 6033 | M1 | -0.15 | Catalytic (MCPB.py) |
| Mn2 | MN (384) | 6034 | Mn2+ | +2.0 | Structural |

### Oxalate Substrate

| Residue | Name | Atoms | Description |
|---------|------|-------|-------------|
| 385 | OX1 | 6035-6041 | Bidentate oxalate |

Oxalate atom details:
- CZ (6035): Carbon
- CX (6036): Carbon
- OZ (6037): Oxygen (coordinating)
- OY (6038): Oxygen (non-coordinating, ~4 A from Mn1)
- OX (6039): Oxygen (coordinating)
- OV (6040): Oxygen
- H7 (6041): Hydrogen

## Flexible Lid (160-166)

| Residue | Name | Atoms | RMSF (A) |
|---------|------|-------|----------|
| 160 | PHE | 2512-2531 | 0.40 |
| 161 | SER | 2532-2542 | 0.31 |
| 162 | GLH | 2543-2558 | 0.34 |
| 163 | ASN | 2559-2572 | 0.31 |
| 164 | SER | 2573-2583 | 0.51 |
| 165 | THR | 2584-2597 | 0.31 |
| 166 | PHE | 2598-2617 | 0.39 |

## Solvent/Ions

| Component | Count | Residues |
|-----------|-------|----------|
| TIP3P Water | 19,079 | 386-19464 |
| Cl- ions | 9 | 19465-19473 |

## Atom Selection Masks (cpptraj syntax)

```
# Protein backbone
@CA,C,N

# Mn1 catalytic site
@6033

# Mn2 structural site
@6034

# Flexible lid
:160-166

# Lid CA atoms
:160-166@CA

# Mn1 coordination sphere
:95,97,101,140@NE2,OE1

# Oxalate
:385

# W96-W274 pair (intra-subunit)
:96,274

# Strip waters and ions
:WAT,Cl-,Na+
```

## Notes

1. **Histidine naming**: HD1, HD2, HD3 = doubly protonated His (HIP equivalent)
2. **GLH vs GLU**: GLH = protonated Glu (Glu162 is protonated for catalysis)
3. **GU1**: Special MCPB.py naming for Glu101 coordinating Mn1
4. **Molecule segments**: Warning about non-contiguous segments (atoms 1-6033, 6035-6041) is expected due to Mn1 being separate from oxalate
