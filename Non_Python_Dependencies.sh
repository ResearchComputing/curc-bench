#!/bin/bash
#Bash script to download, unpack and install non-python dependencies
#Should be run in top directory /curc-bench/

#osu micro benchmarks 3.8
wget https://www.nersc.gov/assets/Trinity--NERSC-8-RFP/Benchmarks/July12/osu-micro-benchmarks-3.8-July12.tar 
tar xf osu-micro-benchmarks-3.8-July12.tar
rm osu-micro-benchmarks-3.8-July12.tar
mv ./osu-micro-benchmarks-3.8-July12 ./lib/osu-micro-benchmarks-3.8

# cd ./lib/osu-micro-benchmarks-3.8/
# ./configure
# make
# make install
# cd ..


# IOR-2.10.3
wget http://colocrossing.dl.sourceforge.net/project/ior-sio/IOR%20latest/IOR-2.10.3/IOR-2.10.3.tgz
tar zxvf IOR-2.10.3.tgz
rm IOR-2.10.3.tgz
mv ./IOR ./lib/IOR

# cd ./lib/IOR/
# make [posix|mpiio|hdf5|ncmpi|all]
# cd ..


#HPL 2.0
wget http://www.netlib.org/benchmark/hpl/hpl-2.0.tar.gz
tar zxvf hpl-2.0.tar.gz
rm hpl-2.0.tar.gz
mv ./hpl-2.0 ./lib/hpl-2.0


# hpcc-1.4.2
wget http://icl.cs.utk.edu/projectsfiles/hpcc/download/hpcc-1.4.2.tar.gz
tar zxvf hpcc-1.4.2.tar.gz
rm hpcc-1.4.2.tar.gz
mv ./hpcc-1.4.2 ./lib/hpcc-1.4.2


#stream.c v5.9
wget http://www.cs.virginia.edu/stream/FTP/Code/stream.c
mkdir ./lib/stream/
mv ./stream.c ./lib/stream/stream.c
