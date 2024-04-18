import argparse
import os
import subprocess
from datetime import datetime as dt
from sys import exit
from typing import List

from ant.fwd_model.template import APPTAINER_TEMPLATE, MODULES, SLURM_TEMPLATE


def get_parser() -> argparse.ArgumentParser:
    """
    Get parser for command line arguments.

    Returns:
        parser for command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Hyperparameters and parameters"
    )
    parser.add_argument(
        "--experiment_name",
        type=str,
        default="dgp",
        help="Name of the experiment.",
    )
    parser.add_argument(
        "--max_freq",
        type=float,
        default=2,
        help="Maximum frequency of dispersion curves.",
    )
    parser.add_argument(
        "--min_freq",
        type=float,
        default=0.2,
        help="Minimum frequency of dispersion curves.",
    )
    parser.add_argument(
        "--num_runs",
        type=int,
        default=200,
        help="Number of times the script `generate_data.py` is run.",
    )
    parser.add_argument(
        "--num_samples",
        "-n",
        type=int,
        default=int(1e3),
        help="Number of samples from the prior.",
    )

    return parser


def submit_job(args_list: List) -> int:
    """
    Submit job and retrieve the job ID scheduled on SLURM.

    Args:
        args_list: List with arguments to submit job.

    Returns:
        Job ID.
    """

    # submit job
    result = subprocess.run(args_list, stdout=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to submit job '{submit_file}'")

    # retrieve job ID from output
    job_id = result.stdout.strip().split()[-1]

    return job_id


if __name__ == "__main__":
    # get command line arguments and parse them
    parser = get_parser()
    args = parser.parse_args()

    # Retrieve current time and day
    date_time = dt.now().strftime("%dp%mp%y_%Hp%Mp%S")
    day = date_time[:8]
    time = date_time[-8:-3]

    # Define saving path for data, slurm and submit files and create folders
    current_dir = os.getcwd()

    dir_tensor = os.path.join(current_dir, "data", day, time)
    saving_path__slurm = os.path.join(
        current_dir, "slurm", args.experiment_name, day, time
    )
    saving_path__submit = os.path.join(
        current_dir, "submit_files", args.experiment_name, day, time
    )

    os.makedirs(dir_tensor, exist_ok=True)
    os.makedirs(saving_path__slurm, exist_ok=True)
    os.makedirs(saving_path__submit, exist_ok=True)

    # create list where all job IDs will be stored
    job_ids = []

    # run DGP script `args.num_runs` times
    for run_id in range(args.num_runs):
        # Define submit file
        submit_file = os.path.join(saving_path__submit, f"run_dgp_{run_id}.sh")

        # Define output and error file names
        log_file = os.path.join(
            saving_path__slurm,
            f"run_%j_{run_id}.log",
        )

        launch_command = (
            f"/opt/conda/bin/python -m ant.fwd_model.generate_data "
            f"--dir__input_output_bounds {dir_tensor} "
            f"-i {run_id} --min_freq {args.min_freq} --max_freq "
            f"{args.max_freq} -s -n {args.num_samples} -u -t {dir_tensor}"
        )

        apptainer_command = APPTAINER_TEMPLATE.format(
            singularity_file="migrate_v004.sif",
            path2code=os.getcwd(),
            command=launch_command,
        )

        SLURM_CMD = SLURM_TEMPLATE.format(
            partition="shared-cpu",
            time="0-00:30:00",
            job_name=f"{args.experiment_name}_{run_id}",
            log_file=log_file,
            mem_per_cpu__gb=8,
            extra_params="",
            modules=MODULES,
            command=apptainer_command,
        )

        with open(submit_file, "w") as f:
            f.write(SLURM_CMD)

        try:
            job_id = submit_job(["sbatch", submit_file])
            job_ids.append(job_id)
        except Exception as e:
            print(e)

    if len(job_ids) != args.num_runs:
        print(f"{len(job_ids)} instead of {args.num_runs} jobs were submitted")
        exit()

    # Concatenation script
    submit_file = os.path.join(
        saving_path__submit, f"run_concat__{date_time[-8:]}.sh"
    )
    log_file = os.path.join(
        saving_path__slurm,
        f"run_concat__{date_time[-8:]}.log",
    )

    launch_command = (
        f"/opt/conda/bin/python -m ant.fwd_model.concat_data "
        f"--num_samples {args.num_samples} --tensor_dir {dir_tensor}"
    )

    apptainer_command = APPTAINER_TEMPLATE.format(
        singularity_file="migrate_v004.sif",
        path2code=os.getcwd(),
        command=launch_command,
    )

    SLURM_CMD = SLURM_TEMPLATE.format(
        partition="shared-cpu",
        time="0-00:30:00",
        job_name="concat",
        log_file=log_file,
        mem_per_cpu__gb=8,
        extra_params="",
        modules=MODULES,
        command=apptainer_command,
    )

    with open(submit_file, "w") as f:
        f.write(SLURM_CMD)

    dependency = ":".join(job_ids)
    submit_job(["sbatch", f"--dependency=afterok:{dependency}", submit_file])

    # TODO: Automatically upload the file on a S3 bucket repo? if an S3 is provided or configured. Can be implemented in concat_data
