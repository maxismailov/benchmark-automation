# benchmark-automation
A small set of python scripts to automate the process of collecting benchmark data from LAMMPS running on AWS ParallelCluster

Meta Data:
    HPC package: LAMMPS 
    Scheduler: Slurm
    Benchmark: loop time

Command: python3 driver.py /path_to_working_directory --node_list X --task_list Y --out_file name_of_outfile
X = number of nodes desired, Y = number of tasks for the simulation (can be multiple if more inputs given here)

Example: python3 driver.py /software/benchmarks/utah/AWS-EBS-c5n.18xlarge-EFA/ --node_list 2  --task_list 18 36 --out_file aggregated_perf_data8

General process: 
   1. driver.py: submits multiple identical slurm jobs (default job: get_perf_data.sh) with different variations of slurm/hardware configurations such as number of compute nodes, ntasks/vCPUs.
   
   2. get_perf_data.sh: This is the job script which is run. It runs 3 simulations: chain, EAM, and lj. It also creates a custom slurm-XXX.out file where XXX is the job number/id. Once the simulations are complete, perfparser.py is launched.
   
   3. perfparser.py seeks out the custom slurm out file associated with the job it was launched from and adds the relevant benchmarking data to a master benchmarking dataset.
