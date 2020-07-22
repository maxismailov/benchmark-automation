# benchmark-automation
A small set of python scripts to automate the process of collecting benchmark data from LAMMPS running on AWS ParallelCluster. An easier way to spawn large numbers of jobs and capture their output in a tabular format.

## Dependencies:
    HPC package: LAMMPS 
    Scheduler: Slurm
    Benchmark: loop time

## Usage:

`python3 driver.py /path/to/working/directory --node_list 1 2 3 --task_list 4 5 6 --out_file name_of_outfile`
Example: `python3 driver.py /software/benchmarks/utah/AWS-EBS-c5n.18xlarge-EFA/ --node_list 2  --task_list 18 36 --out_file aggregated_perf_data8`

## Operation:

The `driver.py` script will launch the processes in the fashion you specified. The processes are created in a simple cartesian product fashion -- if your node list is [1, 2, 3] and your task list is [4, 5, 6], 9 jobs will be spawned; every possible combination of jobs and ntasks per job will be created. 

## Explanation of scripts: 
   1. `driver.py`: submits multiple identical slurm jobs (default job: get_perf_data.sh) with different variations of job parameters -- namely the number of compute nodes and ntasks per node
   
   2. `get_perf_data.sh`: This is the job script which is run. It runs 3 simulations: chain, EAM, and lj. It also creates a job-specific slurm-XXX.out file where XXX is the job number/id. Once the simulations are complete, perfparser.py is launched.
   
   3. `perfparser.py` seeks out the custom slurm out file associated with the job it was launched from and adds the relevant benchmarking data to a master benchmarking .
