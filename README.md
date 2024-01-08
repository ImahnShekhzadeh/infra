# infra
Repository for sharing template Docker file, submit file, etc. 

## [`infra.pdf`](infra.pdf)

Useful instructions/information/commands for...
- ... bash \& Linux (**chapter 1**),
- ... Docker (**chapter 2**),
- ... AWS S3 (**chapter 3**),
- ... conda (**chapter 4**), 
- ... git (**chapter 5**), 
- ... remote development (**chapter 6**), 
- ... python (**chapter 7**), 
- ... Jax (**chapter 8**)

## Template Submit File

To simplify life when using an HPC cluster, I created [`run.py`](run.py).

It will likely be necessary to adapt the template file to i) the HPC, and ii) the script that is run, in particular L68 - L71.

## Template Docker Files

- [This](Dockerfile) template docker file installs both `PyTorch` and `Jax`, take into account that [L58](https://github.com/ImahnShekhzadeh/infra/blob/main/Dockerfile#L58) and 
[L61](https://github.com/ImahnShekhzadeh/infra/blob/main/Dockerfile#L61) assume there is a shell script `run_scripts.sh` that can be run. 
The script `run_scripts.sh` might look like this:
    ```bash
    #!/bin/sh
    isort /app/scripts/*.py  # if `isort` is in `pyproject.toml`
    black /app/scripts/*.py  # if `black` is in `pyproject.toml`

    python3 -B /app/scripts/test_script.py
    ```
    where you should adjust the name of the Python script you are running.

    Run the script as follows:
    ```
    docker build -f Dockerfile -t project-name:tag-name .
    docker run --rm -v $(pwd)/test_scripts_nbs:/app/scripts --gpus all -it project-name:tag-name
    ```
    where you should replace `project-name` and `tag-name` with whatever information you want to provide, and `test_scripts_nbs` is a local directory containing a script. 
    If this is not the case, please adjust the directory and script names.

    **NOTE**: The Dockerfile also assumes that there is a `setup.py` and `pyproject.toml` file ([L46-47](https://github.com/ImahnShekhzadeh/infra/blob/main/Dockerfile#L46-L47)).

- I also created a [Dockerfile for running a Jupyter NB inside a container](https://github.com/ImahnShekhzadeh/infra/blob/main/Dockerfile_nb), which should be run as follows:
    ```
    docker run -it --rm -v $(pwd)/test_scripts_nbs:/app/scripts -p 8888:8888 img-name:tag-name
    ```