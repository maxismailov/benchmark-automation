import argparse
import os
import sys
import subprocess
import perfparser

# Authors: Max Ismailov and Caleb Grode
# Description: A script to launch a series of LAMMPS jobs with various numbers of nodes and ntasks 
#              Creates a file that associates spawned jobs with their job number, so that the subsequent
#              spawned job can parse its output file. 
#
#
# GPU Support: This version of the scripts is designed for automation support on a single GPU instance.
#              If you are looking for automation support for a cluster, grab the "cluster_automation.zip" file
#


def parse_all_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",help="Path to the directory that contains our lmp_mpi executable, bash script, and in.* files")
    parser.add_argument("--gpu_num",type=int,default=0)
    parser.add_argument("--out_file",type=str,default="",help="The name of the file that you want all of the timing data to be aggregated into")
    parser.add_argument("--task_num",type=int,default=0)
    return parser.parse_args()

def main(argv):
    # Get the core arguments necessary for this to run
    args = parse_all_args()
    gpu_num = args.gpu_num
    input_dir = args.input_dir
    out_file = args.out_file
    task_num = args.task_num

    # A few sanity checks
    if not os.path.exists(input_dir):
        print("Error: the input directory you specified doesn't exist")
        exit(-1)

    if (not gpu_num or not out_file or task_num==0):
        print("Error: One of the essential parameters (gpu_num, task_num, or out_file) were not provided. Please provide a list of values to proceed")
        exit(-1)

    print(" *** LAMMPS Simulation (GPU support) started with parameters: dir=", args.input_dir, "gpu num=", gpu_num, "tasks=", sequence[0])

    # Copy over execution script to working directory
    ret = subprocess.call(["cp","get_perf_data.sh",input_dir])
    if ret != 0:
        print("Error with copying over our execution script")
        exit(-1)

    print("Launching your GPU job, waiting for completion...")
    proc = subprocess.Popen(["./get_perf_data.sh",str(gpu_num),task_num,cwd=input_dir,stdout=job_file)
    ret = proc.wait()
    print("Done! Launching perfparser.py...")
    perfparser.parse_out_file(out_file)
    print("Parsing completed! Look for your specified output file")


if __name__ == "__main__":
    main(sys.argv)
