#!/bin/bash
#SBATCH --job-name=eq_cpu_mc
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

echo "cwd: $PWD"
module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25 # cpu build
export PATH="$AMBERHOME/bin:$PATH"

echo "AMBERHOME=$AMBERHOME"
which pmemd || {
  echo "pmemd not in PATH"
  exit 2
}

PRMTOP="5vg3_solv.prmtop"
INPCRD="5vg3_solv.inpcrd"
[[ -s "$PRMTOP" ]] || {
  echo "missing $PRMTOP"
  exit 3
}
[[ -s "$INPCRD" ]] || {
  echo "missing $INPCRD"
  exit 4
}
[[ -s mdin_templates/heat_nvt_1fs.in ]] || {
  echo "missing heat mdin"
  exit 5
}
[[ -s mdin_templates/eq1_mc_cpu_1fs.in ]] || {
  echo "missing eq1 mdin"
  exit 6
}
[[ -s mdin_templates/eq2_mc_cpu_1fs.in ]] || {
  echo "missing eq2 mdin"
  exit 7
}

run() {
  local in=$1 c=$2 out=$3 rst=$4 nc=$5 info=$6
  echo "=== running ${in} with -c ${c}"
  srun -n1 pmemd -O \
    -i "mdin_templates/${in}" \
    -p "$PRMTOP" -c "$c" \
    -o "${out}" -r "${rst}" -x "${nc}" -inf "${info}"
  [[ -s "${rst}" ]] || {
    echo "stage ${in} produced no ${rst}"
    exit 10
  }
}

# heat (NVT, 1 fs). only if not already present
if [[ ! -s heat.cpu.rst7 ]]; then
  run heat_nvt_1fs.in "$INPCRD" \
    heat.cpu.out heat.cpu.rst7 heat.cpu.nc heat.cpu.mdinfo
else
  echo "skip heat: heat.cpu.rst7 exists"
fi

# eq1 (NPT MC, 1 fs) — consume heat
run eq1_mc_cpu_1fs.in heat.cpu.rst7 \
  eq1.cpu.out eq1.cpu.rst7 eq1.cpu.nc eq1.cpu.mdinfo

# eq2 (NPT MC, 1 fs) — consume eq1
run eq2_mc_cpu_1fs.in eq1.cpu.rst7 \
  eq2.cpu.out eq2.cpu.rst7 eq2.cpu.nc eq2.cpu.mdinfo

echo "all stages done."
