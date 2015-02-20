#!/bin/bash
#Bash script to download, unpack and install non-python dependencies
#Should be run in top directory /curc-bench/

#osu micro benchmarks 3.8
wget https://www.nersc.gov/assets/Trinity--NERSC-8-RFP/Benchmarks/July12/osu-micro-benchmarks-3.8-July12.tar 
tar xf osu-micro-benchmarks-3.8-July12.tar
rm osu-micro-benchmarks-3.8-July12.tar
mv ./osu-micro-benchmarks-3.8-July12 ./lib/osu-micro-benchmarks-3.8


# IOR-2.10.3
wget http://colocrossing.dl.sourceforge.net/project/ior-sio/IOR%20latest/IOR-2.10.3/IOR-2.10.3.tgz
tar zxvf IOR-2.10.3.tgz
rm IOR-2.10.3.tgz
mv ./IOR ./lib/IOR


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

# #Note:The version of stream.c included has numbers that have been changed
# #stream.c v5.9
# wget http://www.cs.virginia.edu/stream/FTP/Code/stream.c
# mkdir ./lib/stream/
# mv ./stream.c ./lib/stream/stream.c


#Note: The version originally used (10.3.9) is no longer available on the INTEL site
#This version may or may not produce consitant results (in theory it just adds support
#for the latest architecture along with some optimizations)
#Also, you may have to accept a license agreement to download
#linpack
wget http://registrationcenter.intel.com/irc_nas/5232/l_lpk_p_11.2.2.010.tgz
tar zxvf l_lpk_p_11.2.2.010.tgz
rm l_lpk_p_11.2.2.010.tgz
mv ./l_lpk_p_11.2.2.010 ./lib/linpack
