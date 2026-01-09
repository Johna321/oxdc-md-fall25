#!/bin/bash
#SBATCH --job-name=Bi-new
#SBATCH --output=oxMonosmall.out
#SBATCH --error=oxMonosmall.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=zbecerra@ufl.edu
#SBATCH --time=7-00:00:00
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8    
#SBATCH --mem-per-cpu=4000
#SBATCH --account=ax
#SBATCH --qos=ax


module load cuda/12.2.2  gcc/12.2.0  openmpi/4.1.5  amber/22

module load gaussian/16

g16 < 5vg3_small_opt.com > 5vg3_small_opt.log
g16 < 5vg3_small_fc.com > 5vg3_small_fc.log

  
