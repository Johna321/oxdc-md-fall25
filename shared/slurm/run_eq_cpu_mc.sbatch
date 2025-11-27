#!/bin/bash
#SBATCH --job-name=eq_cpu_mc
#SBATCH --output=eq_cpu_mc.%j.out
#SBATCH --error=eq_cpu_mc.%j.err
#SBATCH --partition=hpg-milan
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8gb
#SBATCH --time=06:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu

set -euo pipefail
module purge
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25   # cpu build; no gpus requested

PRMTOP=5vg3_solv.prmtop
INPCRD=5vg3_solv.inpcrd

# heat (nvt, 1 fs)
if [ ! -f heat.cpu.rst7 ]; then
  sander -O -i mdin_templates/heat_nvt_1fs.in \
         -p "$PRMTOP" -c "$INPCRD" \
         -o heat.cpu.out -r heat.cpu.rst7 -x heat.cpu.nc -inf heat.cpu.mdinfo
fi

# eq1 (npt mc, 1 fs)
sander -O -i mdin_templates/eq1_mc_cpu_1fs.in \
       -p "$PRMTOP" -c heat.cpu.rst7 \
       -o eq1.cpu.out -r eq1.cpu.rst7 -x eq1.cpu.nc -inf eq1.cpu.mdinfo

# eq2 (npt mc, 1 fs)
sander -O -i mdin_templates/eq2_mc_cpu_1fs.in \
       -p "$PRMTOP" -c eq1.cpu.rst7 \
       -o eq2.cpu.out -r eq2.cpu.rst7 -x eq2.cpu.nc -inf eq2.cpu.mdinfo

