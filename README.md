# infra
Repository for sharing template Docker file, submit file, etc.

## Template Submit File

To simplify life when using an HPC cluster, I created [`run.py`](run.py).

It will likely be necessary to adapt the template file to i) the HPC, and ii) the script that is run, in particular L68 - L71.

## Template Docker File

[This](Dockerfile) template docker file installs both `PyTorch` and `Jax`, take into account that L58 & L61 assume there is a shell script `run_scripts.sh` that can be run. 
The script `run_scripts.sh` might look like this:
```bash
#!/bin/sh
isort /app/scripts/*.py
black /app/scripts/*.py

python3 -B /app/scripts/test_script.py
```
where you should adjust the name of the Python script you are running.

Depending on your internet speed, building the docker image from the docker file will take some time. Personally, I run the script as follows:
```
docker build -f docker_img -t project-name:tag-name .
docker run --rm -v $(pwd)/test_scripts_nbs:/app/scripts --gpus all -it project-name:tag-name
```
where you should replace `project-name` and `tag-name` with whatever information you want to provide.