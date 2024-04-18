SLURM_TEMPLATE = """#!/bin/bash

#SBATCH --partition={partition}
#SBATCH --time={time}
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --job-name={job_name}
#SBATCH --output={log_file}
#SBATCH --error={log_file}
##SBATCH --mail-type=END
##SBATCH --mail-user=imahn.shekhzadeh@unige.ch
#SBATCH --mem-per-cpu={mem_per_cpu__gb}G
#SBATCH --wait-all-nodes=1
{extra_params}

{modules}

srun {command}
"""

MODULES = "module purge && module load Anaconda3/2022.05"

APPTAINER_TEMPLATE = """apptainer run -B $HOME/scratch:/scratch \
  $HOME/docker/{singularity_file} \
  /bin/bash -c 'cd {path2code}; \
  {command}'
"""
