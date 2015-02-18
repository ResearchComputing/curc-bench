#!/bin/bash
#Bash script to download, unpack and install non-python dependencies

#osu micro benchmarks 3.8
wget https://www.nersc.gov/assets/Trinity--NERSC-8-RFP/Benchmarks/July12/osu-micro-benchmarks-3.8-July12.tar 
tar xf osu-micro-benchmarks-3.8-July12.tar
# mv /home/aaron/Documents/curc-bench/osu-micro-benchmarks-3.8-July12 /home/aaron/Documents/curc-bench/lib/osu-micro-benchmarks-3.8
mv ./osu-micro-benchmarks-3.8-July12 ./lib/osu-micro-benchmarks-3.8
rm osu-micro-benchmarks-3.8-July12.tar

cd ./lib/osu-micro-benchmarks-3.8/
./configure
make
make install