#!/bin/bash
#SBATCH --job-name=Bi-newlarge_2
#SBATCH --output=mcpy.out
#SBATCH --error=mcpy.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=zbecerra@ufl.edu
#SBATCH --time=4-00:00:00
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8    
#SBATCH --mem-per-cpu=4000
#SBATCH --account=ax
#SBATCH --qos=ax


module load cuda/12.2.2  gcc/12.2.0  openmpi/4.1.5  amber/22

module load gaussian/16

g16 < 5vg3_large_mk.com > 5vg3_large_mk.log


