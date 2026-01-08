#!/bin/bash
#SBATCH --job-name=1wat2_eq1_stab_cpu
#SBATCH --output=eq1_stab_cpu.%j.out
#SBATCH --error=eq1_stab_cpu.%j.err
#SBATCH --partition=hpg-milan
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem=8gb
#SBATCH --time=08:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu

echo "cwd: $PWD"

module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25   # CPU build
export OMP_NUM_THREADS=1

# pick topology
PRMTOP=""
for f in 5vg3_solv.prmtop 5vg3.prmtop top.parm7; do
  [[ -s "$f" ]] && PRMTOP="$f" && break
done
[[ -n "$PRMTOP" ]] || { echo "no prmtop found"; exit 2; }

# require completed heating
START="heat.cpu.rst7"
[[ -s "$START" ]] || { echo "missing $START (run heat first)"; exit 3; }

need() { [[ -s "$1" ]] || { echo "missing $1"; exit 4; }; }
need mdin_templates/eq1a_mc_cpu_1fs.in
need mdin_templates/eq1b_mc_cpu_1fs.in
need mdin_templates/eq1c_mc_cpu_1fs.in

run() {
  local label=$1 in=$2 cin=$3 out=$4 rst=$5 nc=$6 info=$7 ref=$8
  echo "=== $label: $in  -c $cin  -ref $ref"
  srun -n $SLURM_NTASKS pmemd.MPI -O \
    -i "mdin_templates/$in" \
    -p "$PRMTOP" -c "$cin" -ref "$ref" \
    -o "$out" -r "$rst" -x "$nc" -inf "$info"
  [[ -s "$rst" ]] || { echo "stage $label produced no $rst"; exit 10; }
  # quick sanity check: no overflows/vlimit in last chunk
  if grep -q 'vlimit exceeded' "$out"; then
    echo "warning: vlimit exceeded in $out"; fi
  if grep -q '\*\*\*\*\*' "$out"; then
    echo "error: overflow (***** ) in $out"; exit 11; fi
}

# eq1a (50 ps): stronger damping + restraints
run "eq1a"  "eq1a_mc_cpu_1fs.in" "$START" \
    "eq1a.cpu.out" "eq1a.cpu.rst7" "eq1a.cpu.nc" "eq1a.cpu.mdinfo" "$START"

# eq1b (50 ps): relax a bit
run "eq1b"  "eq1b_mc_cpu_1fs.in" "eq1a.cpu.rst7" \
    "eq1b.cpu.out" "eq1b.cpu.rst7" "eq1b.cpu.nc" "eq1b.cpu.mdinfo" "eq1a.cpu.rst7"

# eq1c (50 ps): light damping/restraints; often good handoff point
run "eq1c"  "eq1c_mc_cpu_1fs.in" "eq1b.cpu.rst7" \
    "eq1c.cpu.out" "eq1c.cpu.rst7" "eq1c.cpu.nc" "eq1c.cpu.mdinfo" "eq1b.cpu.rst7"

echo "eq1 stabilizer complete (eq1a/b/c). next: eq2 or transition to mttk/gpu."

