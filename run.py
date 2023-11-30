import os
import subprocess
from datetime import datetime as dt

# Parameter
num_runs = 200

# Hyperparameter
num_samples = 100  # int(1e3)

# Retrieve current time and day
date_time = dt.now().strftime("%dp%mp%y_%Hp%Mp%S")
day = date_time[:8]

# Define saving path for slurm files
saving_path__slurm = os.getcwd().split("/")
saving_path__slurm.pop(-1)
saving_path__slurm = "/".join(saving_path__slurm)
saving_path__slurm = os.path.join(saving_path__slurm, "slurm", "dgp", day)

# Create folder for slurm files
os.makedirs(saving_path__slurm, exist_ok=True)

# Define saving path for submit files
saving_path__submit = os.path.join(os.getcwd(), day)

# Create folder for submit files
os.makedirs(saving_path__submit, exist_ok=True)

# Write `num_runs` submit files
for run_id in range(num_runs):
    # Define submit file
    submit_file_name = f"run_dgp_{date_time[-8:]}_{run_id}.sh"

    # Define output and error file names
    output_file_name = os.path.join(
        saving_path__slurm,
        f"run_%j_{date_time[-8:]}_{run_id}.log",
    )
    error_file_name = os.path.join(
        saving_path__slurm,
        f"run_%j_{date_time[-8:]}_{run_id}.err",
    )

    with open(
        os.path.join(saving_path__submit, submit_file_name), "w"
    ) as file:
        file.write(f"#!/bin/bash\n")
        file.write(f"#SBATCH --partition=shared-cpu\n")
        file.write(f"#SBATCH --time=0-12:00:00\n")
        file.write(f"#SBATCH --cpus-per-task=1\n")
        file.write(f"#SBATCH --ntasks=1\n")
        file.write(
            "#SBATCH --chdir=/home/users/s/shekhza2/ant-migrate/git_repo/"
            "benchmarking\n"
        )
        file.write(f"#SBATCH --job-name=dgp_{run_id}\n")
        file.write(f"#SBATCH --output={output_file_name}\n")
        file.write(f"#SBATCH --error={output_file_name}\n")
        # file.write(f'#SBATCH --mail-type=END\n')
        # file.write(f'#SBATCH --mail-user=imahn.shekhzadeh@unige.ch\n')
        file.write(f"#SBATCH --mem-per-cpu=8G\n")  # minimum memory per CPU
        file.write(f"#SBATCH --wait-all-nodes=1\n\n")
        file.write(
            "module purge && module load GCC/11.3.0 OpenMPI/4.1.4 geopsy/3.4."
            "2\n"
        )
        file.write(
            "source activate /home/users/s/shekhza2/.conda/envs/"
            "ant-migrate-dev\n"
        )
        file.write(
            f"python -m scripts_python.fwd_model.generate_data -i {run_id} -s "
            f"-n {num_samples} -u\n"
        )

        subprocess.Popen(
            ["sbatch", os.path.join(saving_path__submit, submit_file_name)]
        )
