# Corrected Equilibration Protocol

## Critical Fix: Restraint Masks

The current equilibration is failing because the restraint masks don't properly exclude system-specific residues.

### System-Specific Masks

Copy these into the appropriate mdin files:

#### BiOx+2
```
restraintmask='(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H=',
```

#### 1Wat+2
```
restraintmask='(!:WAT,WT1,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=',
```

#### 1Wat+3
```
restraintmask='(!:WAT,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H=',
```

#### empty+2
```
restraintmask='(!:WAT,WTR,Cl-,MN1,MN2,GU,HD)&!@H=',
```

---

## Corrected Heat Input (heat_nvt_1fs_restrained.in)

```
Heating NVT 50 ps (1 fs, SHAKE) with restraints
 &cntrl
  imin=0, irest=0, ntx=1,
  nstlim=50000, dt=0.001,
  ntc=2, ntf=2,
  ntb=1,
  ntt=3, gamma_ln=2.0, tempi=0.0, temp0=300.0,
  ntr=1, restraint_wt=5.0,
  restraintmask='<SYSTEM_SPECIFIC_MASK>',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
 &wt TYPE='TEMP0', istep1=0, istep2=50000, value1=0.0, value2=300.0 /
 &wt TYPE='END' /
```

---

## Corrected Equilibration Pipeline

### Stage 1: Heat (50 ps, NVT)
- Restraint: 5.0 kcal/mol·Å²
- Timestep: 1 fs
- Temperature: 0 → 300 K ramp

### Stage 2: EQ1a (100 ps, NPT)
- Restraint: 5.0 kcal/mol·Å²
- Barostat: MC
- Check: Density approaching 1.0 g/cc

### Stage 3: EQ1b (100 ps, NPT)
- Restraint: 2.0 kcal/mol·Å²
- Check: No vlimit warnings

### Stage 4: EQ1c (100 ps, NPT)
- Restraint: 1.0 kcal/mol·Å²
- Check: RMSD < 2.0 Å

### Stage 5: EQ2 (250 ps, NPT)
- Restraint: 0.5 kcal/mol·Å²
- Check: Energy plateau

### Stage 6: EQ3 (500 ps, NPT)
- Restraint: None
- Timestep: 2 fs
- Final equilibration check

### Stage 7: Production
- 10 ns segments
- Monitor for stability

---

## BiOx+2 Quick Fix Script

```bash
#!/bin/bash
# fix_biox2_equilibration.sh

cd /home/user/oxdc-md-fall25/systems/BiOx+2

# Create corrected heat input
cat > mdin_templates/heat_nvt_1fs_fixed.in << 'EOF'
Heating NVT 50 ps (1 fs, SHAKE) with restraints
 &cntrl
  imin=0, irest=0, ntx=1,
  nstlim=50000, dt=0.001,
  ntc=2, ntf=2,
  ntb=1,
  ntt=3, gamma_ln=2.0, tempi=0.0, temp0=300.0,
  ntr=1, restraint_wt=5.0,
  restraintmask='(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
 &wt TYPE='TEMP0', istep1=0, istep2=50000, value1=0.0, value2=300.0 /
 &wt TYPE='END' /
EOF

# Create corrected eq1 input
cat > mdin_templates/eq1_mc_cpu_1fs_fixed.in << 'EOF'
EQ1 NPT MC (1 fs) with system-specific restraints
 &cntrl
  imin=0, irest=1, ntx=5,
  nstlim=250000, dt=0.001,
  ntc=2, ntf=2,
  ntb=2, ntp=1, barostat=2, pres0=1.0,
  ntt=3, gamma_ln=2.0,
  ntr=1, restraint_wt=2.0,
  restraintmask='(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
EOF

# Create corrected eq2 input
cat > mdin_templates/eq2_mc_cpu_1fs_fixed.in << 'EOF'
EQ2 NPT MC (1 fs) reduced restraints
 &cntrl
  imin=0, irest=1, ntx=5,
  nstlim=250000, dt=0.001,
  ntc=2, ntf=2,
  ntb=2, ntp=1, barostat=2, pres0=1.0,
  ntt=3, gamma_ln=2.0,
  ntr=1, restraint_wt=0.5,
  restraintmask='(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H=',
  ntpr=1000, ntwx=1000, ntwr=5000, ioutfm=1, iwrap=1
 /
EOF

echo "Corrected mdin files created."
echo "Update slurm script to use *_fixed.in files."
```

---

## Why BiOx+2 Works Without Fix

BiOx+2 shows zero vlimit warnings despite using the wrong mask. Possible reasons:

1. **Mn parameters are well-optimized:** MCPB.py generated stable parameters
2. **Oxalate provides additional stability:** Bidentate binding constrains geometry
3. **Fortunate initial conditions:** Starting geometry close to equilibrium

However, the mask should still be fixed for:
- Consistency across systems
- Reproducibility
- Correct physical behavior

---

## Validation Checklist

Before proceeding to production, verify:

- [ ] Heat completed with restraints
- [ ] EQ1-3 completed with correct masks
- [ ] Density: 0.99 ± 0.02 g/cc
- [ ] No vlimit warnings in EQ2-3
- [ ] CA RMSD < 2.0 Å from start
- [ ] Mn-ligand distances stable
- [ ] Total energy shows no drift
- [ ] Box volume stable (< 1% fluctuation)

---

## Suggested Production Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Total time | 100 ns minimum | Loop dynamics sampling |
| Segment length | 10 ns | Manageable file sizes |
| Save frequency | 10 ps | 10,000 frames per 100 ns |
| Replicas | 3-5 | Statistical significance |
| Random seeds | Different per replica | Independent sampling |

**Total data:** 100 ns × 3 replicas × 4 systems = 1.2 μs aggregate
