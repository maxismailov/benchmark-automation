#!/bin/bash
# Shell script which runs chain, eam, and lj lammps simulations with and without EFA

CPU=$SLURM_NTASKS
export RUNMAX=1
#export WORKDIR=/software/benchmarks/utah/AWS-EBS-c5n.18xlarge-EFA
export OMPI_MCA_mtl_base_verbose=100


#cd $WORKDIR
#export EXE=./lmp_spack_openmp
export EXE=./lmp_mpi
export OMP_NUM_THREADS=1
module purge
module load openmpi
#module load intelmpi
module load libfabric-aws

echo "  LAMMPS Simulation on AWS started on `date +%H:%M:%S--%m/%d/%y`"
echo "        Nodes: $SLURM_NODELIST"
echo "        mpirun: `which mpirun`"
echo "        EXE: `which $EXE`"
echo "        #Threads: $OMP_NUM_THREADS" 
echo "        UUID: $uuid "
echo "        working_dir: $parse_dir "	
#remove previous output files (if present)
rm -rf log.lammps

# patch alinux for a bug
mpirun sudo bash -c 'echo 5128 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages'

echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

for((RUN=1; RUN<=$RUNMAX; RUN++))
do
        for TYPE in chain.scaled eam.scaled lj.scaled 
        do
            echo "With EFA          Iter.: $RUN   #MPI Proc.: $CPU   TYPE: $TYPE "      
# run without efa 
#            mpirun -mca mtl_ofi_provider_exclude efa -mca mtl ^ofi $EXE -in in.$TYPE >& $TYPE.$CPU.$OMP_NUM_THREADS.$RUN.out
# run with tcp
#            mpirun -mca btl_tcp_if_include ens5 $EXE -in in.$TYPE >& $TYPE.$CPU.$OMP_NUM_THREADS.$RUN.out
            mpirun $EXE -in in.$TYPE >& $TYPE.$CPU.$OMP_NUM_THREADS.$RUN.out
            line=`cat $TYPE.$CPU.$OMP_NUM_THREADS.$RUN.out | grep 'Loop time'` 
            echo "$line"
            echo ""
            sleep 5
        done
	sleep 10
        for TYPE in chain.scaled eam.scaled lj.scaled 
        do
            echo " NO EFA:          Iter.: $RUN   #MPI Proc.: $CPU   TYPE: $TYPE "      
            mpirun -mca mtl_ofi_provider_exclude efa -mca mtl ^ofi $EXE -in in.$TYPE >& $TYPE.$CPU.$OMP_NUM_THREADS.$RUN.out
            line=`cat $TYPE.$CPU.$OMP_NUM_THREADS.$RUN.out | grep 'Loop time'` 
            echo "$line"
            echo ""
            sleep 5
        done
done

echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# Maybe make this conditional on whether or not python has already been installed
#sudo yum install -y python3
#python3 $parse_dir/perfparser.py $uuid
# We should just fire off the parser at this point in the script since the job will be done!

echo  "     LAMMPS Simulation on AWS done on `date +%H:%M:%S--%m/%d/%y`"
echo  "----------------------------------------------------------------"



