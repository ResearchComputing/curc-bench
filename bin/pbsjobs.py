#!/usr/bin/env python
import argparse
import glob
import datetime
from lxml import etree
import re

import os


job_logs = '/curc/torque/4.2.3-redhat_6_x86_64/job_logs/'

def job_owner(tag):
    start_index = tag.find('<Job_Owner>') + 11
    end_index = tag.find('@')
    return tag[start_index:end_index]

def job_name(tag):
    start_index = tag.find('<Job_Name>') + 10
    end_index = tag.find('</Job_Name>')
    return tag[start_index:end_index]    

def job_id(tag):
    start_index = tag.find('<JobId>') + 10
    end_index = tag.find('.moab')
    return tag[start_index:end_index]        

def convert_date(date):

    tmp = str(date).replace('-','')
    return os.path.join(job_logs,tmp)

def write_data_to_file(data):
    print data
    try:
        with open(os.path.join(output_dir,'hostlist_' + data['job_owner'] \
                          + '_' + data['job_id']), 'w') as outfile:
            for host in data['host']:
                outfile.write(host)
                outfile.write('\n')
    except:
        print 'could not write file'


if __name__ == '__main__':  
    
    parser = argparse.ArgumentParser()            
    parser.add_argument('-u','--username', help='username', dest='username')
    parser.add_argument('-j','--jobid', help='jobid', dest='jobid')
    
    args = parser.parse_args()
    output_dir = os.getcwd()
    
    files = glob.glob(job_logs)

    files = []
    files.append(convert_date(datetime.date.today()))
    files.append(convert_date(datetime.date.today() - datetime.timedelta(days=1)))
    files.append(convert_date(datetime.date.today() - datetime.timedelta(days=2)))
    files.append(convert_date(datetime.date.today() - datetime.timedelta(days=3)))
    files.append(convert_date(datetime.date.today() - datetime.timedelta(days=4)))
    files.append(convert_date(datetime.date.today() - datetime.timedelta(days=5)))
    files.append(convert_date(datetime.date.today() - datetime.timedelta(days=6)))
    files.append(convert_date(datetime.date.today() - datetime.timedelta(days=7)))
    files.append(convert_date(datetime.date.today() - datetime.timedelta(days=8)))

    for file in files:

        with open(file, 'r') as f:
            line = f.readline()
            while line:
                data = {}
                if line.find('<Jobinfo>') >= 0:
                    data['job_id'] = job_id(f.readline())
                    data['job_name'] = job_name(f.readline())
                    data['job_owner'] = job_owner(f.readline())
                    
                    if args.username is not None:
                        if data['job_owner'].find(args.username) >= 0:
                            line = f.readline()
                            #print line
                            while line.find('</Jobinfo>') < 0:
                                line = f.readline()
                                if line.find('<exec_host>') >= 0:
                                    host_list = []
                                    nodes = re.findall('node\w+', line)
                                    for node in nodes:
                                        if node not in host_list:
                                            host_list.append(node)
                                    data['host'] = host_list
                    
                            write_data_to_file(data)

                    if args.jobid is not None:
                        if data['job_id'].find(args.jobid) >= 0:
                            line = f.readline()
                            #print line
                            while line.find('</Jobinfo>') < 0:
                                line = f.readline()
                                if line.find('<exec_host>') >= 0:
                                    host_list = []
                                    nodes = re.findall('node\w+', line)
                                    for node in nodes:
                                        if node not in host_list:
                                            host_list.append(node)
                                    data['host'] = host_list
                    
                            write_data_to_file(data)


                        

                line = f.readline()


