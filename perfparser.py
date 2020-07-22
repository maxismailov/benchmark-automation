import os
import sys
import subprocess
import csv
import numpy as np

# perfparser.py
# Authors: Max Ismailov, Caleb Grode
# Description: This file is a script which gets information from our custom slurm-XXX.out files. 
#              Taking in a uuid as an input, script searches for the slurm-XXX.out file with the matching uuid
#              and grabs data from the lammps simulations.
#              Collected data: Nodes, Tasks, Atoms, Type, Time, Has_EFA, Steps, Iteration, Job ID
#              Data is stored in tabular format using a 2d array.
# 
# File Dependencies: perfparser.py is fired from the shell script get_perf_data.sh after it finishes the lammps simulations


# TODO: Write data to master CSV file --> probably where we would need to write lock
# - WE NEED TO INCLUDE A SETUP.PY TO INSTALL ALL DEPENDENCIES


# Possibly use portalocker package if we need to implement locks
def main(argv):
    # Get the job file from the uuid given as argv[1]
    ticket = argv[1]

    # We will eventually want to make this a non hardcoded-value

    temp_file = open("/software/benchmarks/utah/AWS-EBS-c5n.18xlarge-EFA/temp-bench-auto.txt","r")
    

    # Find the job number from the uuid we were given
    job_num = -1
    out_file_name = ""

    for line in temp_file:
        if not out_file_name:
            out_file_name = line
        tokens = line.split()
        if tokens[0] == ticket:
            job_num = int(tokens[1])
            break
    
    print("I am uuid: ", ticket , " and my job number is: ", job_num)
        
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

    print("First line index: ", index_line , " First line: " , slurm_out_lines[index_line] , "\n")
    
    # At this point index_line will be set to the begining of the relevant data
    # *** Schema for tabular_data:
    #   Nodes, Tasks, Atoms, Type, Time, Has_EFA, Steps, Iteration, Job ID

    # Sets up the header for our tabular_data
    tabular_data = np.empty((1,9),dtype='object') 
    tabular_data[0,:] = ["Nodes", "Tasks", "Atoms", "Type", "Time", "Has_EFA", "Steps", "Iteration", "Job_ID"]
    new_row = np.empty((1,9),dtype='object')
    tabular_data = np.append(tabular_data, new_row,axis=0)
    index_data = 1
    nodes = slurm_out_lines[1].count(",") + 1 
    print(slurm_out_lines[index_line].split())
    ntasks = slurm_out_lines[index_line].split()[6] 
    index_line += 1
    num_atoms = slurm_out_lines[index_line].split()[11] 


    index_line -= 1 # move back up before we start the while loop

    # The '~' character is the sentinel character for the end of our run
    while slurm_out_lines[index_line].count("~") == 0: 
       # Constants for all runs: num_nodes, num_tasks, num_atoms, job id
        print("Current line: ", slurm_out_lines[index_line])
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

        print(tabular_data)
        print("###################")
        new_row = np.empty((1,9),dtype='object')

        tabular_data = np.append(tabular_data, new_row, axis = 0)
        
        # Increment row pointer and line pointer 
        index_data += 1 
        index_line += 2 # move to next simulation

    #dbg_file = open("debug-slurm-"+job_num+".out")

    np.savetxt(out_file_name, tabular_data, delimiter=",") 
    # Actually write this data out to our master file
    # with open(out_file_name, 'wb') as master_file:
    #     np.savetxt(master_file, tabular_data, delimiter=",") 

if __name__ == "__main__":
    main(sys.argv)


        

            

