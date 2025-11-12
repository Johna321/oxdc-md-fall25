# RUN_PLAN — Nterm_only

## integrity

- top: `5vg3_solv.prmtop`  crd: `5vg3_solv.inpcrd`  atoms: 63287  residues: 19473  charge: 0.0

- detected waters: ['WAT']  ions: ['Cl-']

- mn atoms: 2

## mn site

- flags: {
  "6032": {
    "CN": 6,
    "MEAN": 2.0,
    "MIN": 1.306,
    "SHORT": true,
    "SPARSE": false
  },
  "6033": {
    "CN": 4,
    "MEAN": 2.177,
    "MIN": 2.051,
    "SHORT": false,
    "SPARSE": true
  }
}

## restraint mask

`'(!:WAT,Cl-,GLU,GU,HD,HID,HIP,OX)&!@H='`

## strategy

- eq1: **cpu-bridge-then-gpu** — mn site flagged (SHORT/SPARSE): using 100 ps cpu bridge then gpu chunks

## submit order

- `sbatch slurm/run_eq1_bridge_cpu.sbatch`

- `sbatch slurm/run_eq2_to_mttk_gpu.sbatch`

## qc gates
- density 0.99±0.02 g/cc (last 20 ps)
- no '*****' lines
- CA-RMSD ≤ 2.0 Å at eq1d & eq2b
