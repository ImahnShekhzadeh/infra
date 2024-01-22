import os
import subprocess
from datetime import datetime as dt
from typing import Optional


def write_skeleton(
    submit_file: str,
    job_name: str,
    log_file: str,
    partition: str = "shared-cpu",
    python_dir: str = "/home/users/s/shekhza2/ant-migrate/ml4ant",
    run_id: Optional[int] = None,
    mem_per_cpu__gb: int = 8,
) -> None:
    """
    Write skeleton for submit file.

    Args:
        submit_file: Name of the submit file.
        log_file: Name of the log file.
        partition: Name of the partition to use.
        python_dir: Path to the python directory.
        run_id: ID of the run.
        mem_per_cpu__gb: Memory per CPU in GB.
    """

    with open(submit_file, "w") as f:
        f.write(f"#!/bin/bash\n")
        f.write(f"#SBATCH --partition={partition}\n")
        f.write(f"#SBATCH --time=0-12:00:00\n")
        f.write(f"#SBATCH --cpus-per-task=1\n")
        f.write(f"#SBATCH --ntasks=1\n")
        f.write(f"#SBATCH --chdir={python_dir}\n")
        if run_id is None:
            f.write(f"#SBATCH --job-name={job_name}\n")
        else:
            f.write(f"#SBATCH --job-name={job_name}_{run_id}\n")
        f.write(f"#SBATCH --output={log_file}\n")
        f.write(f"#SBATCH --error={log_file}\n")
        # file.write(f'#SBATCH --mail-type=END\n')
        # file.write(f'#SBATCH --mail-user=imahn.shekhzadeh@unige.ch\n')
        # minimum memory per CPU
        f.write(f"#SBATCH --mem-per-cpu={mem_per_cpu__gb}G\n")
        f.write(f"#SBATCH --wait-all-nodes=1\n\n")


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

# Define saving path for submit files
saving_path__submit = os.path.join(os.getcwd(), day)

# Create folder for slurm and files
os.makedirs(saving_path__slurm, exist_ok=True)
os.makedirs(saving_path__submit, exist_ok=True)

# Write `num_runs` submit files
for run_id in range(num_runs):
    # Define submit file and log file
    submit_file_name = os.path.join(
        saving_path__submit, f"run_dgp_{date_time[-8:]}_{run_id}.sh"
    )
    log_file = os.path.join(
        saving_path__slurm,
        f"run_%j_{date_time[-8:]}_{run_id}.log",
    )

    # Write skeleton for submit file
    write_skeleton(
        submit_file=submit_file_name,
        job_name="dgp",
        log_file=log_file,
        partition="shared-cpu",
        python_dir="/home/users/s/shekhza2/ant-migrate/git_repo/benchmarking",
        run_id=run_id,
    )

    # append rest
    with open(submit_file_name, "a") as f:
        f.write(
            "module purge && module load GCC/11.3.0 OpenMPI/4.1.4 geopsy/3.4." "2\n"
        )
        f.write("source activate ant-migrate-dev\n")
        f.write(
            f"python -m scripts_python.fwd_model.generate_data -i {run_id} -s "
            f"-n {num_samples} -u\n"
        )

    subprocess.Popen(["sbatch", submit_file_name])
