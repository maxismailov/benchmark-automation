import argparse
import numpy
import os
import sys
import subprocess

def parse_all_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",help="Path to the directory that contains our lmp_mpi executable, bash script, and in.* files")
    parser.add_argument("--node_list",nargs="*",type=int,default=[])
    parser.add_argument("--task_list",nargs="*",type=int,default=[])
    return parser.parse_args()


def main(argv):
    # Get the core arguments necessary for this to run
    args = parse_all_args()
    node_list = args.node_list
    task_list = args.task_list
    input_dir = args.input_dir
    if not os.path.exists(input_dir):
        print("Error: the input directory you specified doesn't exist")
        exit(-1)

    if not node_list or not task_list:
        print("Error: One of the essential lists (node_list or task_list) were not provided. Please provide a list of values to proceed")
        exit(-1)
    print("LAMMPS Simulation started with parameters: dir=", args.input_dir, "nodes list=", node_list, "tasks=", task_list)
    print(args.input_dir)
    print(node_list)
    print(task_list)

    job_list = []
    # TODO: Wrap this all up inside of a "with redirectSTDout()" so we can capture standard out, populate job_list

    # Some kind of doubly-nested for loop
    #   Outer -- nodes, Inner -- tasks
    for nodes in node_list:
        for ntasks in task_list:
            # command line 
            # spawn job with our particular commands 
            node_command = "--nodes=" + str(nodes)
            tasks_command = "--ntasks-per-node=" + str(ntasks)
            proc = subprocess.Popen(["sbatch",node_command, tasks_command, "./jxu_auto.sh"],stdout=subprocess.PIPE,cwd=input_dir)
            job_num = proc.communicate()[0]
            print(job_num)
            #TODO: get job number
            

            # We've submitted a slurm job with our particular commands
            #   --> We need to know the job number, so we can get the timing info from that job we launched
            # Idea: redirect stdout so we capture all the input that is being created from slurm about our job numbers, pass off job numbers to the module respondible for processing output

            


if __name__ == "__main__":
    main(sys.argv)