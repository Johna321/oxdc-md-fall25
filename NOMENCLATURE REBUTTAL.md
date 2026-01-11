Your **11–12 Å Glu162↔Mn1** is *not* inconsistent with something people label “closed” in OxDC. The literature has (at least) **three distinct “states”** that get conflated:

### 1) “Open-loop” (classic *open*) — **PDB 1J58**

* **Definition:** the **161–164 SENS loop** is swung away → solvent channel open. ([ORCA][1])
* From the **1J58 coordinates**, **Glu162(OE1/OE2)↔Mn(site1)** is **~15–16 Å** (i.e., *very far*). ([PDB Archive][2])
* So: *open* ≈ **~15 Å**, not ~11 Å.

### 2) “Closed-loop, Glu162-in” (classic *closed*) — **PDB 1UW8** (Just et al.)

* **Definition:** SENS loop “closed”; **Glu162 doesn’t ligate Mn**—it sits **second-sphere** and **H-bonds to an Mn-bound water**. ([ORCA][1])
* From the **1UW8 coordinates**, **Glu162(OE1/OE2)↔Mn(site1)** is **~4.6–5.1 Å** (NOT 2–4 Å; 2 Å would imply *direct coordination*, which is not what’s described). ([PDB Archive][3])
* The **“tight” metric** here is instead: **Glu162(OE*)↔O(water bound to Mn)** ≈ **~2.7–2.8 Å** (that’s the stabilizing H-bond the papers talk about). ([ORCA][1])

### 3) “Closed-loop backbone, Glu162-out” (this is the one you’re probably in) — **PDB 5VG3 @ pH 4.6**

* **Key fact:** there exists a **closed-like loop backbone** state where **Glu162 sidechain is displaced away** (replaced by water / small carboxylate occupancy patterns), *yet the loop is not the “open” channel state*. This is explicitly seen in mutational/structural work: **loop remains ‘closed’ but Glu162 sidechain is displaced**. ([PMC][4])
* In **5VG3 (pH 4.6; crystallized with acetate in conditions)**, **Glu162(OE*)↔Mn(site1)** from coordinates is **~10–12 Å** across chains. ([PDB Archive][5])

  * This **numerically matches your MD**:

    * you: **11.5 ± 0.5 Å**, **11.7 ± 0.7 Å**, **12.3 ± 0.6 Å**
    * 5VG3: **~10–12 Å** ([PDB Archive][5])

So: **your distances are very plausibly “closed-backbone / Glu162-out”**, not “open-loop”, and not “Glu162-in closed”.

---

## Why your “2–4 Å should be closed” intuition is off

* In OxDC, **Glu162 is not a first-shell Mn ligand** (first shell is the canonical 3 His + 1 Glu motif). Expecting **2–2.5 Å** to Mn would mean you’re making Glu162 a *metal ligand*—a different coordination model than the canonical structural description. ([PMC][6])
* The structurally emphasized “closed” contact is **Glu162 ↔ Mn-bound water**, not **Glu162 ↔ Mn**. ([ORCA][1])

---

## Substrate-bound Michaelis complex nuance: Glu162-in may be *sterically impossible*

This is the big mechanistic wrinkle you were already sensing:

* Zhu et al. show that the **Glu162 position in 1UW8** would **sterically clash** with substrate *if oxalate binds in the experimentally observed position in their ΔE162 complex*, and they explicitly say this **raises questions about the “true” Glu162 orientation** in the catalytically competent Michaelis complex. ([ORCA][1])
* They further argue the **1UW8 Glu162 pose** is plausibly a **substrate-absent stabilizing pose** (via H-bond to Mn-water), and may **not** represent the catalytic Michaelis geometry. ([ORCA][1])

Meaning: even if you start from something labeled “closed”, **substrate binding can force Glu162 out**—*without* implying the loop is “open” in the gating sense.

---

## Binding mode: monodentate vs bidentate is currently *live* (and it impacts “closed” semantics)

Two competing experimental narratives:

**Monodentate (“end-on”) oxalate**

* Supported structurally in the **ΔE162 Co(II) complex** work; argued to be consistent with **V/K isotope effects** and to leave room for the “dioxygen binds at Mn” picture. ([ORCA][1])

**Bidentate oxalate**

* **ENDOR (2024)** argues oxalate binds **bidentate (κO,κO′)** to Mn(II) in WT at high pH *and* in W96F at low pH, and they conclude **bidentate is energetically preferred** and that **dioxygen likely does not bind to Mn after substrate binds**. ([PMC][6])

If your model enforces **bidentate oxalate at Mn1**, it will tend to:

* **occupy coordination space / reorganize waters**, and
* plausibly favor **Glu162-out** (esp. if Glu162 is deprotonated and oxalate is highly anionic).

So your MD setup is not automatically “wrong”; it may be sampling a state aligned with the **bidentate-binding / non-Mn–O₂-binding** view. ([PMC][6])

---

## Practical: how to decide “open vs closed” in *your* trajectory (don’t use Glu162↔Mn alone)

Use **two orthogonal classifiers**:

### A) **Loop-gating (open/closed proper)**

Metrics that actually report the **SENS loop backbone position / channel**:

* **RMSD of residues 160–166** to reference **1J58(open)** vs **1UW8(closed)** (backbone-only).
* **Cα distance**: e.g. **CA(162)↔Mn1** (backbone proxy). In coordinate comparisons, this separates **open (~11–12 Å)** vs **closed-backbone (~7–9 Å)** even when the **sidechain** is out. (This is exactly why “closed-backbone/Glu-out” exists.) ([PMC][4])
* **Solvent access proxy**: count waters within e.g. **5 Å of Mn1** or compute a **tunnel radius** to bulk (HOLE/CAVER style).

### B) **“Glu162-in” catalytic pose (second-sphere chemistry)**

Metrics that report whether Glu162 is in the **1UW8-like** stabilizing pose:

* **min distance {Glu162(OE1/OE2) ↔ O(Mn-bound water)}** (expect ~2.7–3.0 Å in the 1UW8-like pose). ([ORCA][1])
* H-bond occupancy of **Glu162↔Mn-water**.

Your reported ~11–12 Å to Mn suggests: **not Glu162-in**, but it does *not* uniquely imply **open noting gating**.

---

## One sanity check you should do immediately

Make sure you’re measuring to the correct Mn:

* **Mn1 (N-terminal site)** should be coordinated by residues **His95/His97/Glu101/His140** (B. subtilis numbering used in many papers). ([PMC][4])
  If Mn naming got swapped in your topology, you can accidentally report nonsense distances.

---

## Bottom line

* **Your distances (~11–12 Å) are *compatible* with a “closed” OxDC system** (specifically the **closed-backbone / Glu162-out** family; 5VG3-like). ([PDB Archive][5])
* They are **incompatible with the “Glu162-in closed” 1UW8-like pose**, where Glu162 is **~5 Å from Mn** and **~2.7–2.8 Å from an Mn-bound water**. ([PDB Archive][3])
* And the literature itself warns that **1UW8’s Glu162 pose may not be the Michaelis complex** because of **steric clash with substrate** in an experimentally supported oxalate pose. ([ORCA][1])

If you want, paste: **(i)** which PDB you started from, **(ii)** your oxalate protonation state, **(iii)** Glu162 protonation state, and **(iv)** whether any acetate/formate/waters were retained at Mn1—then you can map your trajectory *cleanly* onto one of the above three state families.

[1]: https://orca.cardiff.ac.uk/id/eprint/88326/13/acs.biochem.6b00043.pdf "bi6b00043 1..11"
[2]: https://files.rcsb.org/download/1J58.pdb "files.rcsb.org"
[3]: https://files.rcsb.org/download/1UW8.pdb "files.rcsb.org"
[4]: https://pmc.ncbi.nlm.nih.gov/articles/PMC3319475/ "
            A Structural Element that Facilitates Proton-Coupled Electron Transfer in Oxalate Decarboxylase - PMC
        "
[5]: https://files.rcsb.org/download/5VG3.pdb "files.rcsb.org"
[6]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11433825/ "
            Bidentate Substrate Binding Mode in Oxalate Decarboxylase - PMC
        "
