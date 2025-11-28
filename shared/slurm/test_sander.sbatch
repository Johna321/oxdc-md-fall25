#!/bin/bash -l
#SBATCH -p hpg-milan
#SBATCH -A ax
#SBATCH --qos=ax
#SBATCH -t 00:30:00
#SBATCH -c 4
#SBATCH --mem=8g
#SBATCH -J heat_cpu
#SBATCH -o heat_cpu.%j.out
#SBATCH -e heat_cpu.%j.err

# guarantee modules exist even if -l is stripped by site config
[ -f /etc/profile.d/modules.sh ] && source /etc/profile.d/modules.sh

module purge
module load gcc/14.2.0 openmpi/5.0.7 amber/25

# sanity
echo "AMBERHOME=${AMBERHOME:-unset}"
module list || true
export PATH="$AMBERHOME/bin:$PATH"

SANDER="$(command -v sander || command -v sander_serial || command -v sander.MPI || true)"
if [[ -z "${SANDER}" ]]; then
  echo "fatal: sander not found"; module show amber/25 || true; ls -l "$AMBERHOME/bin"; exit 2
fi

srun -n1 "${SANDER}" -O \
  -i mdin_templates/heat_nvt.in \
  -p 5vg3_solv.prmtop -c 5vg3_solv.inpcrd \
  -o heat.cpu.out -r heat.cpu.rst7 -x heat.cpu.nc -inf heat.cpu.mdinfo

