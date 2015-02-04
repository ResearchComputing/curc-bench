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
    maybe = tag[start_index:end_index]  
    return  maybe.split('[')[0] 

def convert_date(date):
    tmp = str(date).replace('-','')
    return os.path.join(job_logs,tmp)

def datetimetostring(data):
    return data.strftime("%Y%m%d%H%M")

def start_time(tag):
    start_index = tag.find('<start_time>') + 12
    end_index = tag.find('</start_time>')
    dt = datetime.datetime.fromtimestamp(float(tag[start_index:end_index]))  
    return dt
 
def end_time(tag):
    start_index = tag.find('<comp_time>') + 11
    end_index = tag.find('</comp_time>')
    dt = datetime.datetime.fromtimestamp(float(tag[start_index:end_index]))  
    return dt

def duration(start_time, end_time):
    dur = end_time - start_time
    return dur.days*60*60*24 + dur.seconds

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

def execute(days=0):
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
    #files.append(convert_date(datetime.date.today() - datetime.timedelta(days=8)))

    with open('users.csv', 'w') as outfile:
        outfile.write('jobid,owner,starttime,endtime,duration,numnodes\n')
        for file in files:
            with open(file, 'r') as f:
                line = f.readline()
                while line:
                    data = {}
                    if line.find('<Jobinfo>') >= 0:
                        data['job_id'] = job_id(f.readline())
                        data['job_name'] = job_name(f.readline())
                        data['job_owner'] = job_owner(f.readline())
                     
                        line = f.readline()
                                
                        while line.find('</Jobinfo>') < 0:
                            line = f.readline()
                            
                            if line.find('<exec_host>') >= 0:
                                host_list = []
                                nodes = re.findall('node\w+', line)
                                for node in nodes:
                                    if node not in host_list:
                                        host_list.append(node)
                                data['host'] = host_list
                            if line.find('<start_time>') >= 0:
                                data['start_time'] = start_time(line)
                                #print data['start_time']
                            if line.find('<comp_time>') >= 0:
                                data['end_time'] = end_time(line)

                        try:
                            data['duration'] = duration(data['start_time'], data['end_time'])
                            data['start_time'] = datetimetostring(data['start_time'] )
                            data['end_time'] = datetimetostring(data['end_time'] )
                            data['num_nodes'] = len(data['host'])

                            #Write to file
                            outfile.write(data['job_id'] + ',')
                            outfile.write(data['job_owner'] + ',')
                            outfile.write(data['start_time'] + ',')
                            outfile.write(data['end_time'] + ',')
                            outfile.write(str(data['duration'])+',')
                            outfile.write(str(data['num_nodes']))
                            outfile.write('\n')
                        except:
                            pass
                        
                    line = f.readline()

if __name__ == '__main__':  
    
    parser = argparse.ArgumentParser()            
    parser.add_argument('-d','--days', help='days prior', dest='days')
    
    args = parser.parse_args()
    execute()
    

