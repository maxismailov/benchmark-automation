import argparse
import os
import sys
import subprocess
import uuid

# Authors: Max Ismailov and Caleb Grode
# Description: A script to launch a series of slurm jobs with various numbers of nodes and ntasks 
#              Creates a file that associates spawned jobs with their job number, so that the subsequent
#              spawned job can parse its output file. 
#



def parse_all_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",help="Path to the directory that contains our lmp_mpi executable, bash script, and in.* files")
    parser.add_argument("--node_list",nargs="*",type=int,default=[])
    parser.add_argument("--task_list",nargs="*",type=int,default=[])
    parser.add_argument("--out_file",type=str,default="",help="The name of the file that you want all of the timing data to be aggregated into")
    # TODO: Make an option flag to scale the size of the problem along with the number of clusters. something like --size [x y z]. Also number_iterations
    # TODO: Add the option to choose output file format: csv, tsv 
    return parser.parse_args()

# TODO: 
#   - Do something about scaling. Currently we never scale the problem, and we will need to either scale the problem proportionally to the cluster, or not (which is what we currently do)
#   - Add some nice print statements to the console so that things are more intelligible for the user
#   - Create a setup script to install any package dependencies

def main(argv):
    # Get the core arguments necessary for this to run
    args = parse_all_args()
    node_list = args.node_list
    task_list = args.task_list
    input_dir = args.input_dir
    out_file = args.out_file
    if not os.path.exists(input_dir):
        print("Error: the input directory you specified doesn't exist")
        exit(-1)

    if not node_list or not task_list or not out_file:
        print("Error: One of the essential lists (node_list or task_list) were not provided. Please provide a list of values to proceed")
        exit(-1)

    # TODO: Make another file that contains #node information for each job that gets run, so we can have that information in our ultimate aggregated file 
    print(" *** Batch LAMMPS Simulation started with parameters: dir=", args.input_dir, "nodes list=", node_list, "tasks=", task_list, " ***")

    ret = subprocess.call(["cp","get_perf_data.sh",input_dir])
    if ret != 0:
        print("Error with copying over our execution script")
        exit(-1)

    # Make a temporary file in /tmp using some uuid, and in that file store the name of the master-out-file
    temp_file_out_name = "/software/benchmarks/utah/AWS-EBS-c5n.18xlarge-EFA/.temp-bench-auto.txt"
    temp_file_out = open(temp_file_out_name,"w")
    temp_file_out.write(out_file + "\n")

    job_list = []
    
    # Launch all of the requested jobs, capture the job number of each, append it 
    for nodes in node_list:
        for ntasks in task_list:
            node_command = "--nodes=" + str(nodes)
            tasks_command = "--ntasks-per-node=" + str(ntasks)
            ticket = str(uuid.uuid1())
            params_command = "--export=ALL,uuid="+ticket+",parse_dir="+os.getcwd()
            proc = subprocess.Popen(["sbatch",node_command, tasks_command, params_command, "./get_perf_data.sh"],stdout=subprocess.PIPE,cwd=input_dir)
            job_str = str(proc.communicate()[0])
            job_num = job_str.split(' ')[3].replace("\\n","").replace("'","")
            # Write to file <ticket, job_num>
            job_list.append(job_num)
            temp_file_out.write(ticket + " " + job_num + "\n")


if __name__ == "__main__":
    main(sys.argv)
