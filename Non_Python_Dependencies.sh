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