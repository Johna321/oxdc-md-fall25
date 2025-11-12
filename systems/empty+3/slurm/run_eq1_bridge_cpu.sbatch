#!/bin/bash
#SBATCH --job-name=eq1_bridge_cpu
#SBATCH --output=eq1_bridge_cpu.%j.out
#SBATCH --error=eq1_bridge_cpu.%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=4gb
#SBATCH --time=08:00:00
#SBATCH --partition=hpg-turin
#SBATCH --account=ax
#SBATCH --qos=ax

echo "== eq1 bridge cpu->gpu =="
module purge; module load gcc/14.2.0; module load openmpi/5.0.7; module load amber/25
PRMTOP="./5vg3.prmtop"
INPCRD="./5vg3.inpcrd"
set -euo pipefail
mpirun -np 16 pmemd.MPI -O -p "$PRMTOP" -c "$INPCRD" -i mdin_templates/eq1a.mdin -o eq1_cpu.out -x eq1_cpu.nc -r eq1_cpu.rst7 -inf eq1_cpu.mdinfo
module purge; module load cuda/12.8.1; module load gcc/14.2.0; module load openmpi/5.0.7; module load amber/25
pmemd.cuda -O -p "$PRMTOP" -c eq1_cpu.rst7 -i mdin_templates/eq1b.mdin -o eq1b.out -x eq1b.nc -r eq1b.rst7 -inf eq1b.mdinfo
pmemd.cuda -O -p "$PRMTOP" -c eq1b.rst7   -i mdin_templates/eq1c.mdin -o eq1c.out -x eq1c.nc -r eq1c.rst7 -inf eq1c.mdinfo
pmemd.cuda -O -p "$PRMTOP" -c eq1c.rst7   -i mdin_templates/eq1d.mdin -o eq1d.out -x eq1d.nc -r eq1d.rst7 -inf eq1d.mdinfo
