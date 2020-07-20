import argparse
import os
import sys
import subprocess

def parse_all_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",help="Path to the directory that contains our lmp_mpi executable, bash script, and in.* files")
    parser.add_argument("--node_list",nargs="*",type=int,default=[])
    parser.add_argument("--task_list",nargs="*",type=int,default=[])
    parser.add_argument("--out_file",type=str,default="",help="The name of the file that you want all of the timing data to be aggregated into")
    #TODO: Make an option flag to possibly scale the size of the problem along with the number of clusters. Currently we keep the problem size the same always
    return parser.parse_args()

# TODO: - Figure out the %j thing (jobID) in get_perf_data.sh
#   - Implement a parser to convert our aggregated timing file into tabular format
#   - Do something about scaling. Currently we never scale the problem, and we will need to either scale the problem proportionally to the cluster, or not (which is what we currently do)

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
    print("LAMMPS Simulation started with parameters: dir=", args.input_dir, "nodes list=", node_list, "tasks=", task_list)
    print(args.input_dir)
    print(node_list)
    print(task_list)

    ret = subprocess.call(["cp","get_perf_data.sh",input_dir])
    if ret != 0:
        print("Error with copying over our execution script")
        exit(-1)

    job_list = []
    
    # Launch all of the requested jobs, capture the job number of each 
    for nodes in node_list:
        for ntasks in task_list:
            node_command = "--nodes=" + str(nodes)
            tasks_command = "--ntasks-per-node=" + str(ntasks)
            # TODO: Add in a master aggregated file that all of our jobs will write into
            out_file_command = "--output="+out_file
            file_mode_command = "--open-mode=append"
            proc = subprocess.Popen(["sbatch",node_command, tasks_command, out_file_command, file_mode_command, "./get_perf_data.sh"],stdout=subprocess.PIPE,cwd=input_dir)
            job_str = str(proc.communicate()[0])
            job_num = job_str.split(' ')[3].replace("\\n","").replace("'","")
            job_list.append(job_num)

    # At this point we have all of the outputs being aggregated into our `out_file`
    
if __name__ == "__main__":
    main(sys.argv)
