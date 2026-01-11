#!/bin/bash
#SBATCH --job-name=biox2_analysis
#SBATCH --output=analysis.%j.out
#SBATCH --error=analysis.%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=john.aitken@ufl.edu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16gb
#SBATCH --time=02:00:00
#SBATCH --partition=hpg-default
#SBATCH --account=ax
#SBATCH --qos=ax

echo "============================================================"
echo "BiOx+2 Production Trajectory Analysis"
echo "Started: $(date)"
echo "Host: $(hostname)"
echo "============================================================"

cd /home/john.aitken/oxdc-md-fall25/systems/BiOx+2

# Load ambertools (has cpptraj)
module load ambertools/23

echo ""
echo "=== Environment ==="
echo "AMBERHOME: $AMBERHOME"
which cpptraj

# Verify files exist
echo ""
echo "=== Checking input files ==="
ls -lh 5vg3_solv.prmtop prod.nc prod.rst7

# Create output directory
mkdir -p analysis_results

echo ""
echo "=== Running Full Analysis (RMSD, RMSF, Mn coord, lid, Trp) ==="
cpptraj -p 5vg3_solv.prmtop -i cpptraj_ins/full_analysis.in

echo ""
echo "=== Running PCA Analysis ==="
cpptraj -p 5vg3_solv.prmtop -i cpptraj_ins/pca_analysis.in

echo ""
echo "=== Analysis Complete ==="
echo "Output files:"
ls -lh analysis_results/

echo ""
echo "=== Quick Summary ==="
echo "RMSD range:"
awk 'NR>1 {if(NR==2){min=max=$2}; if($2<min)min=$2; if($2>max)max=$2} END{printf "  Min: %.2f A, Max: %.2f A\n", min, max}' analysis_results/rmsd_ca.dat

echo "Glu162-Mn1 distance (open/closed indicator):"
awk 'NR>1 {sum+=$2; n++} END{printf "  Average: %.2f A\n", sum/n}' analysis_results/glu162_mn_distance.dat

echo "Mn-Mn distance:"
awk 'NR>1 {sum+=$2; n++} END{printf "  Average: %.2f A\n", sum/n}' analysis_results/mn_mn_distance.dat

echo ""
echo "Finished: $(date)"

