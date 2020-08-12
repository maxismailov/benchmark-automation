# benchmark-automation
A small set of python scripts to automate the process of collecting benchmark data from LAMMPS running on AWS ParallelCluster. An easier way to spawn large numbers of jobs and capture their output in a tabular format.

## Required Dependencies:
    OpenMPI: absolutely essential since this script fires off mpi tasks
    HPC package: LAMMPS. You can manually change the executable that is fired off, but this program runs LAMMPS as the HPC workload.
    Scheduler: Slurm
    

## Usage:

`python3 driver.py /path/to/working/directory/ --node_list 1 2 3 --task_list 4 5 6 --out_file super-cool-output-file.out`
Example: `python3 driver.py /software/benchmarks/utah/AWS-EBS-c5n.18xlarge-EFA/ --node_list 2  --task_list 18 36 --out_file aggregated_perf_data.out`

## Operation:

The `driver.py` script will launch the processes in the fashion you specified. The processes are created in a simple cartesian product fashion -- if your node list is [1, 2, 3] and your task list is [4, 5, 6], 9 jobs will be spawned; every possible combination of jobs and ntasks per job will be created. 

## What each script does: 
   1. `driver.py`: submits multiple identical slurm jobs (default job: get_perf_data.sh) with different variations of job parameters -- namely the number of compute nodes and ntasks per node
   
   2. `get_perf_data.sh`: This is the job script which actually does the computation. It runs 3 simulations: chain, EAM, and lj. It also creates a job-specific slurm-XXX.out file where XXX is the job number. Once the simulations are complete, perfparser.py is launched from this script.
   
   3. `perfparser.py` seeks out the slurm out file associated with the job it was launched from (through a ticket-based system with the temporary file) and adds the relevant timing data from this run to our master aggregated file.

## GPU Support

If you want to run this on GPU-enabled EC2 instances, checkout the 'gpu' branch and make sure to do work in there. 

## GPU Usage

The syntax for interacting with the GPU-specific set of the automation scripts is not identical to the cluster-specific set of automation scripts, and requires a slightly different approach. Note: it is assumed that you are running this on an EC2 instance that has GPUs available to it (hopefully this was obvious). 

An example run looks something like this:
`python3 driver.py /path/to/working/directory/ --gpu_num 8 --task_num 32 --out_file my-super-cool-output-file.out`
This will launch 32 tasks which share 8 GPU's, a total of 4 tasks per GPU. The EC2 p* instances use NVIDIA Tesla V-100 GPU's, which have a maximum of 4 tasks per individual GPU. 
