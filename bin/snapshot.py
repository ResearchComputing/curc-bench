#!/usr/bin/env /curc/tools/x_86_64/rh6/anaconda/1.4/bin/python

import glob
import os

stream_pass = [35000, 35000, 35000, 35000]
linpack_pass = [100, 110]

all_nodes = []
bad_nodes = []

files = glob.glob(os.path.join('/curc/torque/scripts/data/', '*'))


def write_initial(out_file, data):
    #output_file.write('jobid,node,time,test,case,value,result')
    out_file.write(data['jobid'] + ',')
    out_file.write(data['node'] + ',')
    out_file.write(data['timestamp'] + ',')


def parse_stream(input_file, data, out_file):
    line = input_file.readline().split()
    if len(line) == 7:
        data['timestamp'] = line[2]
           
        data['x1'] = line[3]
        data['x2'] = line[4]
        data['x3'] = line[5]
        data['x4'] = line[6]

        # x1
        write_initial(out_file, data)
        out_file.write('stream,')
        out_file.write('s1,' + str(data['x1'])+',')
        if int(data['x1']) < stream_pass[0]:
            out_file.write('0')
        else:
            out_file.write('1')
        out_file.write('\n')

        # x2
        write_initial(out_file, data)
        out_file.write('stream,')
        out_file.write('s2,' + str(data['x2'])+',')
        if int(data['x2']) < stream_pass[1]:
            out_file.write('0')
        else:
            out_file.write('1')
        out_file.write('\n')

        # x3
        write_initial(out_file, data)
        out_file.write('stream,')
        out_file.write('s3,' + str(data['x3'])+',')
        if int(data['x3']) < stream_pass[2]:
            out_file.write('0')
        else:
            out_file.write('1')
        out_file.write('\n')

        # x4
        write_initial(out_file, data)
        out_file.write('stream,')
        out_file.write('s4,' + str(data['x4'])+',')
        if int(data['x4']) < stream_pass[3]:
            out_file.write('0')
        else:
            out_file.write('1')
    out_file.write('\n')


def parse_linpack(input_file, data, out_file):
    line = input_file.readline().split()
    if len(line) == 5:
        data['timestamp'] = line[2]
        data['x1'] = line[3]
        data['x2'] = line[4]

        #x1
        write_initial(out_file, data)
        out_file.write('linpack,')
        out_file.write('l1,' + str(data['x1'])+',')
        if int(data['x1']) < linpack_pass[0]:
            out_file.write('0')
        else:
            out_file.write('1')
        out_file.write('\n')

        #x2
        write_initial(out_file, data)
        out_file.write('linpack,')
        out_file.write('l2,' + str(data['x2'])+',')
        if int(data['x2']) < linpack_pass[1]:
            out_file.write('0')
        else:
            out_file.write('1')
        out_file.write('\n')


def parse_ipmi(input_file, data, out_file):
    line = input_file.readline()  # jobid
    while line:
        linesplit = line.split('|')
        lab = linesplit[0].strip()
        if lab == 'date':
            data['timestamp'] = linesplit[1].strip()
        elif lab == 'FCB FAN1':
            data['f1'] = linesplit[1].strip()
        elif lab == 'FCB FAN2':
            data['f2'] = linesplit[1].strip()
        elif lab == 'FCB FAN3':
            data['f3'] = linesplit[1].strip()
        elif lab == 'FCB FAN4':
            data['f4'] = linesplit[1].strip()
        elif lab == 'Processor 1 Temp':
            data['p1'] = linesplit[1].strip()
        elif lab == 'Processor 2 Temp':
            data['p2'] = linesplit[1].strip()

        line = input_file.readline()

    if 'f1' in data and 'f2' in data and 'f3' in data and 'f4' in data:
        #f1
        write_initial(out_file, data)
        out_file.write('ipmi,')
        out_file.write('f1,' + str(data['f1'])+',1')
        out_file.write('\n')
        #f1
        write_initial(out_file, data)
        out_file.write('ipmi,')
        out_file.write('f2,' + str(data['f2'])+',1')
        out_file.write('\n')
        #f1
        write_initial(out_file, data)
        out_file.write('ipmi,')
        out_file.write('f3,' + str(data['f3'])+',1')
        out_file.write('\n')
        #f1
        write_initial(out_file, data)
        out_file.write('ipmi,')
        out_file.write('f4,' + str(data['f4'])+',1')
        out_file.write('\n')
        #f1
        write_initial(out_file, data)
        out_file.write('ipmi,')
        out_file.write('p1,' + str(data['p1'])+',1')
        out_file.write('\n')
        #f1
        write_initial(out_file, data)
        out_file.write('ipmi,')
        out_file.write('p2,' + str(data['p2'])+',1')
        out_file.write('\n')


def execute():
    with open(os.path.join(os.getcwd(), 'snapshot.csv'), 'w') as output_file:
        output_file.write('jobid,node,time,test,case,value,result')
        output_file.write('\n')
        for f in files:
            basename = os.path.basename(f).split('.')
            data = {}
            data['node'] = basename[0]
            data['jobid'] = basename[1]
            data['test'] = basename[6]

            with open(f, 'r') as input_file:
                if data['test'] == 'stream':
                    parse_stream(input_file, data, output_file)
                elif data['test'] == 'linpack':
                    parse_linpack(input_file, data, output_file)
                elif data['test'] == 'ipmi':
                    parse_ipmi(input_file, data, output_file)


if __name__ == '__main__':

    execute()
