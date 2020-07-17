import argparse
import os
import sys
import subprocess

def parse_all_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",help="Path to the directory that contains our lmp_mpi executable, bash script, and in.* files")
    parser.add_argument("--node_list",nargs="*",type=int,default=[])
    parser.add_argument("--task_list",nargs="*",type=int,default=[])
    #TODO: Make an option flag to possibly scale the size of the problem along with the number of clusters. Currently we keep the problem size the same always
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

    # TODO: Possibly write this output to our aggregated output file?
    print("LAMMPS Simulation started with parameters: dir=", args.input_dir, "nodes list=", node_list, "tasks=", task_list)
    print(args.input_dir)
    print(node_list)
    print(task_list)

    job_list = []
    
    # Launch all of the requested jobs, capture the job number of each 
    for nodes in node_list:
        for ntasks in task_list:
            node_command = "--nodes=" + str(nodes)
            tasks_command = "--ntasks-per-node=" + str(ntasks)
            proc = subprocess.Popen(["sbatch",node_command, tasks_command, "./jxu_auto.sh"],stdout=subprocess.PIPE,cwd=input_dir)
            job_str = str(proc.communicate()[0])
            job_num = job_str.split(' ')[3].replace("\n","").replace("'","").strip()
            job_list.append(job_num)
            
    # At this point job_list is populated with the job numbers of all of our submitted jobs
    # TODO: Make another python module that we pass off the job numbers to, and that actually parses our output files
            


if __name__ == "__main__":
    main(sys.argv)
