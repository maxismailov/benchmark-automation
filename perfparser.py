
import os

import sys

import subprocess

import asyncio

import numpy as np

# Possibly use portalocker package if we need to implement locks
def main(argv):
    # Get the job file from the uuid given as argv[1]

    ticket = argv[1]

​

    # We will eventually want to make this a non hardcoded-value

    temp_file = open("/tmp/temp-bench-auto.txt","r")

    

    # Find the job number from the uuid we were given

    job_num = -1

    for line in temp_file:

        tokens = line.split(" ")

        if tokens[0] == ticket:

            job_num = int(tokens[1])

            break

​

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
        

    

    # *** Schema for tabular_data:
    #   Nodes, Tasks, Atoms, Type, Time, Has_EFA, Steps, Iteration

    tabular_data = np.array((1,8)) # starting array   

    index_data = 0
    nodes = slurm_out_lines[1].count(",") + 1 # the nodes list is separated by commas. Number of nodes = num commas + 1
    ntasks = line[index_line].split(" ")[5] # get ntasks
    index_line += 1 # move down a line
    num_atoms = line[index_line].split(" ")[11] # get number of atoms


    index_line -= 1 # move back up before we start the while loop


    while slurm_out_lines.count("~") == 0: # while the ~ count is 0 (which denotes the location of the relevant data) fill our data table
        
        # constants: num_nodes, num_tasks, num_atoms
        tabular_data[index_data][0].append(nodes) #fill tasks
        tabular_data[index_data][1].append(ntasks) #fill tasks
        tabular_data[index_data][2].append(num_atoms) #fill num atoms

        # variables from data line 1: iter, type, EFA
        tabular_data[index_data][7].append(slurm_out_lines[index_line].split(" ")[3]) #grab iter number
        tabular_data[index_data][3].append(slurm_out_lines[index_line].split(" ")[8]) # grab the simulation type
        tabular_data[index_data][5].append(slurm_out_lines[index_line].split(" ")[0]) # Grab With or NO EFA

        index_line += 1 # move down a line

        # variables from data line 2: loop time, steps
        tabular_data[index_data][4].append(slurm_out_lines[index_line].split(" ")[3]) # grab loop time
        tabular_data[index_data][6].append(slurm_out_lines[index_line].split(" ")[8]) # grab number of steps
      

        #TODO add new row to tabular data
        
        index_data += 1 # move to next table row

        index_line += 2 # move to next simulation

        

            

