# Non-BiOx+2 Systems: Salvageability Analysis

## Executive Summary

**Question**: Can the unstable systems (1Wat+2, 1Wat+3, empty+2) be salvaged for MD analysis?

**Answer**: **Partially salvageable**, but with significant effort. More importantly, the question of whether they are *necessary* for studying oxalate binding must be addressed.

---

## 1. Current System Status

| System | Stability | Force Constant (avg k) | Root Cause | Salvageability |
|--------|-----------|------------------------|------------|----------------|
| **BiOx+2** | ✓ STABLE | 29.3 | Optimal params | N/A - working |
| 1Wat+2 | ✗ Unstable | 40.2 | High k, bonded model | **MEDIUM** |
| 1Wat+3 | ✗ Unstable | 97.3 | JT distortion, very high k | **LOW** |
| empty+2 | ✗ Crashed | 44.0 | Under-coordinated (CN=4) | **VERY LOW** |

---

## 2. Detailed Salvage Assessment

### 2.1 System: 1Wat+2 (Water-coordinated Mn(II))

**Current Problem**:
- Force constants (33-46 kcal/mol·Å²) are ~40% higher than BiOx+2
- Bonded model at both Mn sites creates stiff connections
- vlimit exceeded during equilibration

**Salvage Strategy**:

| Approach | Effort | Success Probability | Notes |
|----------|--------|---------------------|-------|
| Scale force constants by 0.7x | Low | 50% | Simple frcmod edit |
| Re-parameterize with Seminario | Medium | 70% | New MCPB.py run |
| Hybrid ionic/bonded model | High | 80% | Major topology changes |
| Use SHAKE on Mn-ligand bonds | Low | 30% | May cause other issues |

**Recommended Approach**: Scale force constants by 0.7x (targeting k ≈ 30) and re-attempt equilibration.

```bash
# Example: Edit frcmod to scale force constants
# Original: M1-NE  46.0  2.19
# Modified: M1-NE  32.2  2.19  (46.0 × 0.7)
```

**Verdict**: **SALVAGEABLE** with moderate effort.

### 2.2 System: 1Wat+3 (Mn(III) oxidation state)

**Current Problem**:
- Force constants are 2-3× higher than Mn(II) systems (85-125 kcal/mol·Å²)
- Jahn-Teller distortion creates 1.86 Å axial Glu-Mn bond
- Classical harmonic potential cannot capture JT dynamics
- Literature gap: few successful Mn(III) classical MD studies

**Salvage Strategy**:

| Approach | Effort | Success Probability | Notes |
|----------|--------|---------------------|-------|
| Scale force constants | Low | 20% | May break geometry |
| QM/MM approach | Very High | 90% | Required for Mn(III) |
| Use Mn(II) params for Mn(III) | Low | 10% | Scientifically invalid |
| Constrain JT axis | Medium | 40% | Artificial but may work |

**Fundamental Issue**: Mn(III) has fundamentally different electronic structure (d⁴) that cannot be accurately captured by classical force fields.

**Verdict**: **NOT SALVAGEABLE** for production MD with current approach. Requires QM/MM.

### 2.3 System: empty+2 (No substrate/water at Mn)

**Current Problem**:
- Under-coordinated Mn (CN=4 vs expected CN=5-6)
- SHAKE failures due to extreme bond energy spikes (14,157 kcal/mol max)
- SPARSE flag indicates incomplete coordination sphere
- No stabilizing ligand to anchor Mn geometry

**Salvage Strategy**:

| Approach | Effort | Success Probability | Notes |
|----------|--------|---------------------|-------|
| Add explicit water to empty site | Medium | 60% | Would become 1Wat+2 |
| Use stronger restraints | Low | 20% | Masks problem, not scientific |
| Increase coordination number | High | 50% | Requires re-modeling |
| Use ionic Mn model entirely | High | 70% | Major topology change |

**Fundamental Issue**: Empty Mn sites are biologically unrealistic. In aqueous solution, Mn would be water-coordinated.

**Verdict**: **NOT SCIENTIFICALLY VALUABLE** - empty site is not a realistic state.

---

## 3. Are Non-BiOx+2 Systems Necessary?

### 3.1 Scientific Questions Requiring Each System

| System | Question It Addresses | Can BiOx+2 Answer? |
|--------|----------------------|-------------------|
| BiOx+2 | Substrate-bound enzyme dynamics | ✓ Yes |
| 1Wat+2 | Resting state dynamics | **No** |
| 1Wat+3 | Mn(III) intermediate state | **No** |
| empty+2 | Under-coordinated intermediate | **Not relevant** |

### 3.2 What We Can Learn from BiOx+2 Alone

**Directly Addressable**:
1. ✓ Substrate-Mn coordination geometry
2. ✓ Bidentate binding mode confirmation
3. ✓ Active site flexibility with substrate
4. ✓ Protein dynamics around catalytic Mn
5. ✓ W96/W274 electron transfer pathway structure

**Not Addressable**:
1. ✗ Substrate binding/unbinding dynamics
2. ✗ Comparison of resting vs. active states
3. ✗ Mn(II) → Mn(III) structural changes
4. ✗ Free energy of substrate binding

### 3.3 Comparison with Angerhofer Lab Needs

Based on their research focus:

| Angerhofer Lab Question | System Needed | BiOx+2 Sufficient? |
|------------------------|---------------|-------------------|
| Bidentate binding geometry | BiOx+2 | ✓ Yes |
| Mn(III) EPR correlation | 1Wat+3 or QM/MM | ✗ No |
| Electron hopping pathway | BiOx+2 + 1Wat+2 | Partial |
| Substrate on/off kinetics | All states | ✗ No |

---

## 4. Recommended Path Forward

### 4.1 Priority 1: Complete BiOx+2 Production (Current Plan)

This provides:
- 10 ns production trajectory
- Substrate coordination analysis
- Protein flexibility characterization
- Validation of MCPB.py parameters

### 4.2 Priority 2: Salvage 1Wat+2 (Future Work)

**Rationale**: Needed for substrate binding comparison.

**Protocol**:
1. Scale all Mn-ligand force constants by 0.7x
2. Extend equilibration time (2 ns instead of 500 ps)
3. Use weaker position restraints during equilibration
4. If successful, run 10 ns production

**Estimated Effort**: 1-2 days

### 4.3 Priority 3: QM/MM for Mn(III) States

**Rationale**: Classical MD cannot capture Jahn-Teller properly.

**Approach**:
- Use BiOx+2 or 1Wat+2 as starting structure
- QM region: Mn + first coordination sphere (~30-40 atoms)
- QM method: DFT (B3LYP or similar)
- MM: AMBER ff14SB

**Estimated Effort**: 1-2 weeks for setup + production

### 4.4 NOT Recommended: Empty Systems

**Rationale**: Biologically irrelevant - Mn sites are always coordinated by water or substrate in solution.

---

## 5. Substrate Binding Analysis Strategy

### 5.1 Without 1Wat+2 (BiOx+2 only)

**What We Can Do**:
1. Characterize bound-state structure thoroughly
2. Identify key substrate-protein contacts
3. Calculate binding site flexibility (RMSF)
4. Compare with crystallographic structures
5. Predict mutations affecting binding

**What We Cannot Do**:
1. Calculate binding free energy (ΔG)
2. Identify binding pathway
3. Compare bound vs. unbound dynamics

### 5.2 With Salvaged 1Wat+2

**Additional Analyses Possible**:
1. Endpoint binding free energy (MM-PBSA/GBSA)
2. Structural comparison of substrate vs. water coordination
3. Induced fit analysis upon substrate binding
4. Identification of conformational gating

### 5.3 Ultimate Goal: Full Binding Analysis

Would require:
- BiOx+2: Substrate-bound state (HAVE)
- 1Wat+2: Resting state (NEED TO SALVAGE)
- Enhanced sampling: Metadynamics or umbrella sampling
- Free energy: TI or FEP calculations

---

## 6. Conclusions

### 6.1 Salvageability Summary

| System | Salvageable? | Effort | Priority |
|--------|-------------|--------|----------|
| 1Wat+2 | Yes (likely) | Medium | High |
| 1Wat+3 | No (QM/MM needed) | Very High | Medium |
| empty+2 | No (irrelevant) | N/A | None |

### 6.2 Scientific Value Assessment

| Question | Required Systems | Current Capability |
|----------|-----------------|-------------------|
| What does substrate binding look like? | BiOx+2 | ✓ Full capability |
| How does Mn coordinate oxalate? | BiOx+2 | ✓ Full capability |
| What is binding affinity? | BiOx+2 + 1Wat+2 | ✗ Partial (need 1Wat+2) |
| How does Mn(III) differ from Mn(II)? | 1Wat+3 or QM/MM | ✗ Requires QM/MM |

### 6.3 Recommendation

**For the current project (Winter Break 2025)**:
1. Complete BiOx+2 production and analysis as planned
2. Document findings thoroughly

**For future work (Spring 2026)**:
1. Attempt 1Wat+2 salvage with scaled force constants
2. If successful, run comparative analysis
3. Consider QM/MM for Mn(III) studies

**Key Insight**: BiOx+2 alone provides substantial value for understanding substrate-bound OxDC dynamics. The other systems are not strictly *necessary* for initial publication-quality results, but would strengthen a comprehensive mechanistic study.
