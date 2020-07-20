import os
import sys
import subprocess
import asyncio
import numpy as np
# Possibly use portalocker package if we need to implement locks

def main(argv):

    # Get the job file from the uuid given as argv[1]
    ticket = argv[1]

    # We will eventually want to make this a non hardcoded-value
    temp_file = open("/tmp/temp-bench-auto.txt","r")
    
    # Find the job number from the uuid we were given
    job_num = -1
    for line in temp_file:
        tokens = line.split(" ")
        if tokens[0] == ticket:
            job_num = int(tokens[1])
            break

    job_file_name = "slurm-"+job_num+".out"
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
    nodes = lines[1].count(",") + 1 # the nodes list is separated by commas. Number of nodes = num commas + 1
    
    ntasks = line[8].split(" ")[5]
    num_atoms = line[8].split(" ")[11]
    steps = line[8].split(" ")[8]

   
    # *** Schema for tabular_data:
    #   Nodes, Tasks, Atoms, Type, Time, Has_EFA, Steps, Iteration
    tabular_data = np.array((1,8)) # starting array   

    # loop times from output
    
    # 
    # fill times
    index_data = 0
    while slurm_out_lines.count("~")
        tabular_data[index_data][7].append(slurm_out_lines[index_line].split(" ")[3]) #grab iter number
        tabular_data[index_data][3].append(slurm_out_lines[index_line].split(" ")[8])
        tabular_data[index_data][4].append(slurm_out_lines[index_line].split(" ")[3]) # grab loop time
        index_data += 2 # move to next simulation
        
            
        index_data +=1
        index_line += 1
        



    # TODO: remove top %j line from output
    # TODO: remove echo Job ID and echo $JOBID from bottome

    

    # - Get the name of the master output file from /tmp/temp-bench-auto.txt

    # - Lock the writer lock, so that you can have access to the file
 
 
    # Access to the shared resource goes in here
        
        
    # X Open the slurm-XXX.out file (given as argv[1])

    # - Parse through the file and add it to the master out file
    #   : This one is gonna be by and large the most work

    # - Optional: Do something with the job number stored in the master output file

    # - Relinquish the writer lock, let the next process in for writing!


if __name__ == "__main__":
    main(sys.argv)