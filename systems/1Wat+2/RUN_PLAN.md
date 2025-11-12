# RUN_PLAN — 1Wat+2

## integrity

- top: `5vg3_solv.prmtop`  crd: `5vg3.inpcrd`  atoms: 63286  residues: 19474  charge: 0.0

- detected waters: ['WAT', 'WT1', 'WTR']  ions: ['Cl-', 'MN1', 'MN2']

- mn atoms: 2

## mn site

- flags: {
  "6030": {
    "CN": 5,
    "MEAN": 2.213,
    "MIN": 2.04,
    "SHORT": false,
    "SPARSE": false
  },
  "6031": {
    "CN": 5,
    "MEAN": 2.218,
    "MIN": 2.051,
    "SHORT": false,
    "SPARSE": false
  }
}

## restraint mask

`'(!:WAT,WT1,WTR,Cl-,MN1,MN2,GU,HD,WT)&!@H='`

## strategy

- eq1: **gpu-chunked** — mn site stable: using 4×50 ps gpu chunks

## submit order

- `sbatch slurm/run_eq1_chunked_gpu.sbatch`

- `sbatch slurm/run_eq2_to_mttk_gpu.sbatch`

## qc gates
- density 0.99±0.02 g/cc (last 20 ps)
- no '*****' lines
- CA-RMSD ≤ 2.0 Å at eq1d & eq2b
