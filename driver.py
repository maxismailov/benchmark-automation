import argparse
import os
import sys
import subprocess
import uuid
import perfparser

# Authors: Max Ismailov and Caleb Grode
# Description: A script to launch a series of slurm jobs with various numbers of nodes and ntasks 
#              Creates a file that associates spawned jobs with their job number, so that the subsequent
#              spawned job can parse its output file. 
#


def parse_all_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",help="Path to the directory that contains our lmp_mpi executable, bash script, and in.* files")
    parser.add_argument("--gpu_num",type=int,default=0)
    parser.add_argument("--out_file",type=str,default="",help="The name of the file that you want all of the timing data to be aggregated into")
    parser.add_argument("--task_sequence",type=str,default="0,0")
    
    return parser.parse_args()

# TODO: 
#   - Do something about scaling. Currently we never scale the problem, and we will need to either scale the problem proportionally to the cluster, or not (which is what we currently do)
#   - Add some nice print statements to the console so that things are more intelligible for the user
#   - Create a setup script to install any package dependencies

def main(argv):
    # Get the core arguments necessary for this to run
    args = parse_all_args()
    gpu_num = args.gpu_num
    input_dir = args.input_dir
    out_file = args.out_file
    sequence = args.task_sequence.split(",")
    if int(sequence[0]) > int(sequence[1]):
        exit(1)

    if not os.path.exists(input_dir):
        print("Error: the input directory you specified doesn't exist")
        exit(-1)

    if (not gpu_num or not out_file) and (sequence[1]=="0"):
        print("Error: One of the essential lists (gpu_num or task_list) were not provided. Please provide a list of values to proceed")
        exit(-1)

    # TODO: Make another file that contains #node information for each job that gets run, so we can have that information in our ultimate aggregated file 
    print(" *** Batch LAMMPS Simulation started with parameters: dir=", args.input_dir, "gpu num=", gpu_num, "tasks=", sequence[0])

    
    ret = subprocess.call(["cp","get_perf_data.sh",input_dir])
    if ret != 0:
        print("Error with copying over our execution script")
        exit(-1)

    # Make a temporary file in /tmp using some uuid, and in that file store the name of the master-out-file
    temp_file_out_name = "/mnt/efs/in-files/.temp-bench-auto.txt"
    temp_file_out = open(temp_file_out_name,"w")
    temp_file_out.write(out_file + "\n")

    # Export the necessary environment variables and call get_perf_data
    seq_curr_str = "seq_curr="+str(int(sequence[0])+1)
    seq_max_str = "seq_max="+sequence[1]
    ticket = str(uuid.uuid1())
    ticket_str = "uuid="+ticket
    # foo = subprocess.call(["export",seq_curr_str])
    # foo = subprocess.call(["export",seq_max_str])
    # foo = subprocess.call(["export",ticket_str])
    
    job_filename = "gpu_"+str(gpu_num)+"_"+str(sequence[0])+".out"
    job_file = open(job_filename,"w")
    temp_file_out.write(ticket + " " + job_filename+ "\n")

    #TODO: Use sstdout=*** to redirect this output to stdout, call proc.wait() and then you can manually fire off the parser in this script!
    print("Launching get_perf_data...")
    proc = subprocess.Popen(["./get_perf_data.sh",str(gpu_num),sequence[0],ticket,str(int(sequence[0])+1),sequence[1]],cwd=input_dir,stdout=job_file)
    ret = proc.wait()
    print("Done!")
    perfparser.parse_out_file(job_filename)
    print("Parsing completed!")
    # # Had to hacky-y hardcode the value of the parse_dir...
    # params_command = "--export=ALL,uuid="+ticket+",parse_dir=/software/benchmarks/benchmark-automation/"+",seq_curr="+str(int(sequence[0])+1)+",seq_max="+sequence[1]
    # proc = subprocess.Popen(["sbatch",node_command, tasks_command, params_command, "./get_perf_data.sh"],stdout=subprocess.PIPE,cwd=input_dir)
    # job_str = str(proc.communicate()[0])
    # job_num = job_str.split(' ')[3].replace("\\n","").replace("'","")
    # # Write to file <ticket, job_num>
    # job_list.append(job_num)
    # temp_file_out.write(ticket + " " + job_num + "\n")


if __name__ == "__main__":
    main(sys.argv)
