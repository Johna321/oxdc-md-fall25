#!/bin/bash
#SBATCH --job-name=prod_gpu_mc
#SBATCH --output=prod_gpu_mc.%j.out
#SBATCH --error=prod_gpu_mc.%j.err
#SBATCH --partition=hpg-turin
#SBATCH --account=ax
#SBATCH --qos=ax
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-gpu=2
#SBATCH --gpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=12:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu

module purge
module load cuda/12.8.1
module load gcc/14.2.0
module load openmpi/5.0.7
module load amber/25

PRMTOP=5vg3_solv.prmtop
START=eq2.cpu.rst7

pmemd.cuda -O -i mdin_templates/prod_mc_gpu_2fs.in \
  -p "$PRMTOP" -c "$START" \
  -o prod.out -r prod.rst7 -x prod.nc -inf prod.mdinfo
