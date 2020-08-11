import os
import sys
import subprocess
import csv
import numpy as np

# Authors: Max Ismailov, Caleb Grode
# Description: A script which gets information from the job's associated slurm-XXX.out files. 
#              Taking in a uuid as an input, script searches for the slurm-XXX.out file with the matching uuid
#              and grabs data from the lammps simulations.
#              Collected data: Nodes, Tasks, Atoms, Type, Time, Has_EFA, Steps, Iteration, Job ID
#              Data is stored in tabular format using a 2d array.
# 
# perfparser.py is fired from the shell script get_perf_data.sh after it finishes the lammps simulations
#
# Cluster support: This version of perfparser.py parses data for slurm output files. If you are looking to parse
#                  data from the output of a GPU run, switch to the 'gpu' branch and rerun the automation scripts


def main(argv):
    # Get the job file from the uuid given as argv[1]
    ticket = argv[1]
    input_dir = argv[2]

    temp_file_path = input_dir+".temp-bench-auto.txt"
    temp_file = open(temp_file_path,"r")

    # Find the job number from the uuid we were given, and open it
    job_num = -1
    out_file_name = ""
    for line in temp_file:
        if not out_file_name:
            out_file_name = line
        tokens = line.split()
        if tokens[0] == ticket:
            job_num = int(tokens[1])
            break
            
    job_file_name = "slurm-"+str(job_num)+".out"
    job_file = open(job_file_name,"r")

    slurm_out_lines = []
    for line in job_file:
        slurm_out_lines.append(line)

    # Get our index in the right spot by looking for our special sentinel value
    index_line = 0
    for line in slurm_out_lines:
        index_line += 1
        if line.count("~") != 0:
            break
    
    # At this point index_line will be set to the begining of the relevant data
    # Schema for tabular_data:
    #   Nodes, Tasks, Atoms, Type, Time, Has_EFA, Steps, Iteration, Job ID

    # Sets up the header for our tabular_data
    tabular_data = np.empty((1,9),dtype='object') 
    new_row = np.empty((1,9),dtype='object')
    index_data = 0

    # Get the number of nodes from the slurm.out file with a simple fencepost calculation
    nodes = slurm_out_lines[1][slurm_out_lines[1].find("["):].count(",") + slurm_out_lines[1][slurm_out_lines[1].find("["):].count("-") + 1
    ntasks = slurm_out_lines[index_line].split()[6] 
    index_line += 1
    num_atoms = slurm_out_lines[index_line].split()[11] 
    index_line -= 1 

    # The '~' character is the sentinel character for the end of our run
    while slurm_out_lines[index_line].count("~") == 0: 

       # Constants for all runs: num_nodes, num_tasks, num_atoms, job id
        tabular_data = np.append(tabular_data, new_row, axis = 0)
        
        # Insert constant values
        tabular_data[index_data,0] = nodes 
        tabular_data[index_data,1] = ntasks 
        tabular_data[index_data,2] = num_atoms 
        tabular_data[index_data,8] = job_num

        # Variables from data line 1: iter, type, EFA 
        tabular_data[index_data,7] = slurm_out_lines[index_line].split()[3] 
        tabular_data[index_data,3] = slurm_out_lines[index_line].split()[8] 
        tabular_data[index_data,5] = slurm_out_lines[index_line].split()[0] 

        index_line += 1 

        # Variables from data line 2: loop time, steps
        tabular_data[index_data,4] = slurm_out_lines[index_line].split()[3] 
        tabular_data[index_data,6] = slurm_out_lines[index_line].split()[8] 

        new_row = np.empty((1,9),dtype='object')
        index_data += 1 
        index_line += 2 

    # A hacky way to get rid of an unnecessary line...
    tabular_data = np.delete(tabular_data,index_data,0)

    # Write our current jobs' data to this specific output file
    with open(out_file_name, "ab") as out_file:
        np.savetxt(out_file, tabular_data, delimiter=",", fmt="%s", header = "Nodes,Tasks,Atoms,Type,Time,Has_EFA,Steps,Iteration,Job_ID", comments="")
        

if __name__ == "__main__":
    main(sys.argv)


        

            

