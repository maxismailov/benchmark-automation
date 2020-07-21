# benchmark-automation
A small set of python scripts to automate the process of collecting benchmark data from LAMMPS running on AWS ParallelCluster

General process: 
   1. driver.py: submits multiple identical slurm jobs (usually shell script get_perf_data.sh) with different variations of slurm/hardware configurations such as number of compute nodes, ntasks/vCPUs.
   
   2. get_perf_data.sh: This is the job script which is run. It runs 3 simulations: chain, EAM, and lj. It also creates a custom slurm-XXX.out file where XXX is the job number/id. Once the simulations are complete, perfparser.py is launched.
   
   3. perfparser.py seeks out the custom slurm out file associated with the job it was launched from and adds the relevant benchmarking data to a master benchmarking dataset.
