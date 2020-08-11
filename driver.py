import argparse
import os
import sys
import subprocess
import uuid

# Authors: Max Ismailov and Caleb Grode
# Description: A script to launch a series of slurm jobs with various numbers of nodes and ntasks 
#              Creates a file that associates spawned jobs with their job number, so that the subsequent
#              spawned job can parse its output file. Effectively just performs a cartesian product of 
#              permutations for the node_list and task_list parameters that you provide. 
#
# Cluster Support: This version of the script launches a series of jobs using the slurm scheduler. Because of this
#                  it is assumed that you are running this on a cluster initialized with AWS' ParallelCluster. If
#                  you want to run this automation framework on a GPU instance, switch to the 'gpu' branch.
#
#

def parse_all_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",help="Path to the directory that contains our lmp_mpi executable, bash script, and in.* files")
    parser.add_argument("--node_list",nargs="*",type=int,default=[])
    parser.add_argument("--task_list",nargs="*",type=int,default=[])
    parser.add_argument("--out_file",type=str,default="",help="The name of the file that you want all of the timing data to be aggregated into")
    parser.add_argument("--parse_dir",type=str,default=os.getcwd())
    parser.add_argument("--task_sequence",type=str,default="0,0")
    return parser.parse_args()


def main(argv):
    args = parse_all_args()
    node_list = args.node_list
    task_list = args.task_list
    input_dir = args.input_dir
    out_file = args.out_file
    parse_dir = args.parse_dir
    sequence = args.task_sequence.split(",")
    
    # A few sanity checks before starting the actual logic
    if int(sequence[0]) > int(sequence[1]):
        exit(1)

    if not input_dir[-1] == '/':
        input_dir = input_dir + "/"

    if not parse_dir[-1] == '/':
        parse_dir = parse_dir + "/"
        
    if not os.path.exists(input_dir):
        print("Error: the input directory you specified doesn't exist")
        exit(-1)

    if (not node_list or not task_list or not out_file) and (sequence[1]=="0"):
        print("Error: One of the essential lists (node_list or task_list) were not provided. Please provide a list of values to proceed")
        exit(-1)

    print(" *** Batch of LAMMPS Simulations started with parameters: dir=", args.input_dir, "nodes list=", node_list, "tasks=", task_list, " ***")

    # Things only need to be copied over if we are launching jobs in a batch
    if sequence[1] == "0":
        ret = subprocess.call(["cp","get_perf_data.sh",input_dir])
        if ret != 0:
            print("Error with copying over our execution script")
            exit(-1)

    # Make a temporary file in the input_dir, and in that file store the name of the master-out-file
    temp_file_out_name = input_dir+".temp-bench-auto.txt"
    temp_file_out = open(temp_file_out_name,"w")
    temp_file_out.write(out_file + "\n")

    # Launch all of the requested jobs, capture the job number of each, append it to the temp file
    if int(sequence[0]) == 0:
        print("Launching jobs in a batch...")
        for nodes in node_list:
            for ntasks in task_list:
                node_command = "--nodes=" + str(nodes)
                tasks_command = "--ntasks-per-node=" + str(ntasks)
                ticket = str(uuid.uuid1())
                params_command = "--export=ALL,uuid="+ticket+",parse_dir="+os.getcwd()+",seq_curr=0,input_dir="+input_dir
                proc = subprocess.Popen(["sbatch",node_command, tasks_command, params_command, "./get_perf_data.sh"],stdout=subprocess.PIPE,cwd=input_dir)
                job_str = str(proc.communicate()[0])
                job_num = job_str.split(' ')[3].replace("\\n","").replace("'","")
                # Write to file <ticket, job_num>
                temp_file_out.write(ticket + " " + job_num + "\n")
        print("Done! Keep an eye on the status of your jobs in the slurm queue")

    # Launch the current job in the sequence
    else:
        print("Launching jobs sequentially... ")
        node_command = "--nodes=1"
        tasks_command = "--ntasks-per-node=" + sequence[0]
        ticket = str(uuid.uuid1())
        params_command = "--export=ALL,uuid="+ticket+",parse_dir="+args.parse_dir+",seq_curr="+str(int(sequence[0])+1)+",seq_max="+sequence[1]
        proc = subprocess.Popen(["sbatch",node_command, tasks_command, params_command, "./get_perf_data.sh"],stdout=subprocess.PIPE,cwd=input_dir)
        job_str = str(proc.communicate()[0])
        job_num = job_str.split(' ')[3].replace("\\n","").replace("'","")
        # Write to file <ticket, job_num>
        temp_file_out.write(ticket + " " + job_num + "\n")
        print("Launched the first job in the sequence. Keep an eye on the status of sequential jobs in the slurm queue")


if __name__ == "__main__":
    main(sys.argv)
