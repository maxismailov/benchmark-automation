import os
import sys
import subprocess

def main(argv):

    # TODO: Make a writer lock so multiple simultaneous writes dont fuck shit up

    # - Get the name of the master output file from /tmp/temp-bench-auto.txt

    # - Lock the writer lock, so that you can have access to the file

    # - Open the slurm-XXX.out file (given as argv[1])

    # - Parse through the file and add it to the master out file
    #   : This one is gonna be by and large the most work

    # - Optional: Do something with the job number stored in the master output file

    # - Relinquish the writer lock, let the next process in for writing!


if __name__ == "__main__":
    main(sys.argv)