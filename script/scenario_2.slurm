#!/bin/bash
#SBATCH --account=COMP90024
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1
#SBATCH --output=scenario_2.txt
#SBATCH --time=0-06:00:00
module load python/3.7.4
module load gcccore/8.3.0
module load mpi4py/3.0.2-timed-pingpong

source ~/venvs/venv-3.7.4/bin/activate

mpirun python3 ../code/main.py --location /../../sal.json --data /../../bigTwitter.json
my-job-stats -a -n -s

