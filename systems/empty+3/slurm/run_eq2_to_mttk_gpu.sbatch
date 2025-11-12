#!/bin/bash
#SBATCH --job-name=eq2_to_mttk
#SBATCH --output=eq2_to_mttk.%j.out
#SBATCH --error=eq2_to_mttk.%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --partition=hpg-turin
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --cpus-per-gpu=2
#SBATCH --gpus-per-task=1

echo "== eq2 (berendsen) -> mttk =="
module purge; module load cuda/12.8.1; module load gcc/14.2.0; module load openmpi/5.0.7; module load amber/25
PRMTOP="./5vg3.prmtop"
set -euo pipefail
pmemd.cuda -O -p "$PRMTOP" -c eq1d.rst7 -i mdin_templates/eq2a.mdin      -o eq2a.out -x eq2a.nc -r eq2a.rst7 -inf eq2a.mdinfo
grep -qE '\*{3,}' eq2a.out && { echo "overflow in eq2a"; exit 43; } || true
pmemd.cuda -O -p "$PRMTOP" -c eq2a.rst7 -i mdin_templates/eq2b.mdin      -o eq2b.out -x eq2b.nc -r eq2b.rst7 -inf eq2b.mdinfo
grep -qE '\*{3,}' eq2b.out && { echo "overflow in eq2b"; exit 44; } || true
pmemd.cuda -O -p "$PRMTOP" -c eq2b.rst7 -i mdin_templates/eq3a_mttk.mdin -o eq3a.out -x eq3a.nc -r eq3a.rst7 -inf eq3a.mdinfo
