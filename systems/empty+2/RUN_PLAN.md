# RUN_PLAN — empty+2

## integrity

- top: `5vg3.prmtop`  crd: `5vg3.inpcrd`  atoms: 63283  residues: 19473  charge: 0.0

- detected waters: ['WAT', 'WTR']  ions: ['Cl-', 'MN1', 'MN2']

- mn atoms: 2

## mn site

- flags: {
  "6030": {
    "CN": 4,
    "MEAN": 2.236,
    "MIN": 2.04,
    "SHORT": false,
    "SPARSE": true
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

`'(!:WAT,WTR,Cl-,MN1,MN2,GU,HD)&!@H='`

## strategy

- eq1: **cpu-bridge-then-gpu** — mn site flagged (SHORT/SPARSE): using 100 ps cpu bridge then gpu chunks

## submit order

- `sbatch slurm/run_eq1_bridge_cpu.sbatch`

- `sbatch slurm/run_eq2_to_mttk_gpu.sbatch`

## qc gates
- density 0.99±0.02 g/cc (last 20 ps)
- no '*****' lines
- CA-RMSD ≤ 2.0 Å at eq1d & eq2b
