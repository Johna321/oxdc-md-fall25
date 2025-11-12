#!/bin/bash
#SBATCH --job-name=eq1_chunked_gpu
#SBATCH --output=eq1_chunked_gpu.%j.out
#SBATCH --error=eq1_chunked_gpu.%j.err
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

echo "== eq1 chunked gpu =="
module purge; module load cuda/12.8.1; module load gcc/14.2.0; module load openmpi/5.0.7; module load amber/25
PRMTOP="./5vg3_solv.prmtop"
INPCRD="./5vg3_solv.inpcrd"
set -euo pipefail
# heat if missing
if [ ! -f heat.rst7 ]; then
  pmemd.cuda -O -i mdin_templates/heat.in -p "$PRMTOP" -c "$INPCRD" -o heat.out -r heat.rst7 -x heat.nc -inf heat.mdinfo
fi
run(){ pmemd.cuda -O -p "$PRMTOP" -c "$1" -i "mdin_templates/$2" -o "$3".out -x "$3".nc -r "$3".rst7 -inf "$3".mdinfo; grep -qE '\*{3,}' "$3".out && { echo "overflow in $3"; exit 42; } || true; }
run heat.rst7   eq1a.mdin eq1a
run eq1a.rst7   eq1b.mdin eq1b
run eq1b.rst7   eq1c.mdin eq1c
run eq1c.rst7   eq1d.mdin eq1d
