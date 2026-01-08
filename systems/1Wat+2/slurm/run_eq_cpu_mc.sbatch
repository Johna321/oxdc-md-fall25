#!/bin/bash
#SBATCH --job-name=1wat2_eq_cpu_mc
#SBATCH --output=eq_cpu_mc.%j.out
#SBATCH --error=eq_cpu_mc.%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=8gb
#SBATCH --time=06:00:00
#SBATCH --partition=hpg-milan
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --cpus-per-task=8

set -euo pipefail
echo "cwd: $PWD"

module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25   # cpu build
export PATH="$AMBERHOME/bin:$PATH"

echo "AMBERHOME=$AMBERHOME"
which pmemd || { echo "pmemd not in PATH"; exit 2; }

PRMTOP="5vg3_solv.prmtop"
INPCRD="5vg3_solv.inpcrd"

# existence checks
[[ -s "$PRMTOP" ]] || { echo "missing $PRMTOP"; exit 3; }
[[ -s "$INPCRD" ]] || { echo "missing $INPCRD"; exit 4; }
[[ -s mdin_templates/heat_nvt_1fs.in ]]   || { echo "missing heat mdin"; exit 5; }
[[ -s mdin_templates/eq1_mc_cpu_1fs.in ]] || { echo "missing eq1 mdin"; exit 6; }
[[ -s mdin_templates/eq2_mc_cpu_1fs.in ]] || { echo "missing eq2 mdin"; exit 7; }

# detect whether mdin uses positional restraints (ntr=1); ignore comments
needs_ref() {
  local mdin="mdin_templates/$1"
  sed 's/!.*$//' "$mdin" | tr -d '[:space:]' | grep -qi 'ntr=1'
}

run_stage() {
  local in_mdin="$1" c_in="$2" out_prefix="$3" rst_out="$4" nc_out="$5" info_out="$6"
  echo "=== running ${in_mdin} with -c ${c_in}"

  # add -ref only if ntr=1, and when present set -ref to the SAME coords as -c
  local ref_opt=()
  if needs_ref "$in_mdin"; then
    echo ">>> detected ntr=1 in ${in_mdin} → using -ref ${c_in}"
    ref_opt=( -ref "$c_in" )
  fi

  srun -n1 pmemd -O \
    -i "mdin_templates/${in_mdin}" \
    -p "$PRMTOP" -c "$c_in" "${ref_opt[@]}" \
    -o "${out_prefix}.out" -r "${rst_out}" -x "${nc_out}" -inf "${info_out}"

  [[ -s "${rst_out}" ]] || { echo "stage ${in_mdin} produced no ${rst_out}"; exit 10; }
}

# heat (NVT, 1 fs) — usually ntr=0; if your heat mdin has ntr=1, -ref will auto attach = INPCRD
if [[ ! -s heat.cpu.rst7 ]]; then
  run_stage heat_nvt_1fs.in "$INPCRD" \
            heat.cpu heat.cpu.rst7 heat.cpu.nc heat.cpu.mdinfo
else
  echo "skip heat: heat.cpu.rst7 exists"
fi

# eq1a (NPT Monte Carlo, 1 fs) — reference = heat start if ntr=1
run_stage eq1a_mc_cpu_1fs.in heat.cpu.rst7 \
          eq1a.cpu eq1a.cpu.rst7 eq1a.cpu.nc eq1a.cpu.mdinfo

# eq1b (NPT Monte Carlo, 1 fs) — reference = heat start if ntr=1
run_stage eq1b_mc_cpu_1fs.in eq1a.cpu.rst7 \
          eq1b.cpu eq1b.cpu.rst7 eq1b.cpu.nc eq1b.cpu.mdinfo

# eq1c (NPT Monte Carlo, 1 fs) — reference = heat start if ntr=1
run_stage eq1c_mc_cpu_1fs.in eq1b.cpu.rst7 \
          eq1c.cpu eq1c.cpu.rst7 eq1c.cpu.nc eq1c.cpu.mdinfo

# eq2 (NPT Monte Carlo, 1 fs) — reference = eq1 start if ntr=1
run_stage eq2_mc_cpu_1fs.in eq1c.cpu.rst7 \
          eq2.cpu eq2.cpu.rst7 eq2.cpu.nc eq2.cpu.mdinfo

echo "all stages done."

