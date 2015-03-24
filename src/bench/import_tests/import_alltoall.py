import os, sys
from datetime import datetime
from optparse import OptionParser

from bench.util import config
from bench.util import infiniband

appsdir = '/root/srv/www/benchmarks/apps/'
if not appsdir in sys.path:
    sys.path.insert(0,appsdir)

appsdir = '/root/srv/www/benchmarks/'
if not appsdir in sys.path:
    sys.path.insert(1,appsdir)

os.environ["DJANGO_SETTINGS_MODULE"] = "benchmarks_site.settings"
from django.db import models
from wire.models import Bandwidth
from django.db import IntegrityError



import logging
logger = logging.getLogger('Benchmarks')

def alltoall_data(in_file):

    value = (1. + float(config.alltoall_limits['percent'])/100.0)
    data = {'total':0, 'num':0, 'mean':0,'min':0,'max':0 }

    # First line is node_list
    line = in_file.readline()
    tmp_list = line.split(',')
    if tmp_list[-1] == '\n':
        del tmp_list[-1]
    data['node_list'] = []
    for n in tmp_list:
        n_tmp = n.strip()
        if n_tmp.startswith('node'):
            data['node_list'].append(n_tmp)

    num_nodes = len(data['node_list'])

    while in_file:
        line = in_file.readline()
        #print line
        split = line.split()
        if not split:
            break
        if split[0] == '#':
            continue
        try:
            data['num'] +=1
            data['total'] += float(split[1])
            if data['min'] > float(split[2]) or data['min']==0:
                data['min'] = float(split[2])
            if data['max'] < float(split[3]):
                data['max'] = float(split[3])
        except IndexError:
            logger.error("missing alltoall data")
        except ValueError, e:
            logger.error(e)
            logger.error(line)

    if data['num'] > 0:
        data['mean'] = data['total']/data['num']
        logger.debug(str(data['num']) + " " + str(data['mean']))
        data['percent'] = round(100*(config.alltoall_limits[num_nodes]- data['mean'])/config.alltoall_limits[num_nodes])

        if config.alltoall_limits[num_nodes]*value < data['mean']:
            data['effective'] = False
        else:
            data['effective'] = True
    else:
        data['effective'] = False
        data['percent'] = 100
    if data['effective'] == False:
        print num_nodes, data['mean'], config.alltoall_limits[num_nodes], data['effective']
    return data

def insert_bandwidth(data, subdirname, td, tr):
    node1 = subdirname[:8]
    node2 = subdirname[9:]
    tmp = datetime(year=td.year, month=td.month, day=td.day, hour=int(tr))

    bw = Bandwidth(test_date=tmp, name=node1, node1=node1, node2=node2, test1=data['65536'], test2=data['262144'], test3=data['1048576'], test4=data['4194304'], effective=True)
    try:
        bw.save()
    except IntegrityError as e:
        logger.error("Bandwidth import error: " + str(e))

def import_data(path, date, trial):
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            if subdirname.find("node") == 0:
                data_file = os.path.join(path,subdirname,"data_bw")
                print subdirname
                if os.path.exists(data_file):
                    in_file = open(data_file,"r")

                    b = bandwidth_data(in_file)
                    insert_bandwidth(b,subdirname,date, trial)

                    in_file.close()

def evaluate_alltoall_data(data, node_list, bad_nodes, good_nodes):

    print "--------------"
    print data

    if data['effective'] == False:
        bad_nodes.extend(node_list)
        print "bad nodes"
        for n in node_list:
            print n
        print ""
    else:
        good_nodes.extend(node_list)
        print "good nodes"
        for n in node_list:
            print n
        print ""



def read_all(node_path, subdirname, filename):

    node_dic = {}

    data_file = os.path.join(node_path,subdirname,filename)
    if os.path.exists(data_file):
        in_file = open(data_file,"r")
        b = alltoall_data(in_file)
        for n in b['node_list']:
            node_dic[n] = {}
        b['test'] = subdirname
        #print b
        for n in b['node_list']:
            node_dic[n]['all'] = b['effective']

        return node_dic
        #evaluate_alltoall_data(b,node_list,bad_nodes, good_nodes)
        in_file.close()
    return None

def read_pairs(node_path, subdirname, node_dic):

    filelist = os.listdir(os.path.join(node_path,subdirname))

    for file in filelist:
        if file.startswith("data_pair"):
            data_file = os.path.join(node_path,subdirname,file)
            if os.path.exists(data_file):
                #print data_file
                in_file = open(data_file,"r")
                b = alltoall_data(in_file)
                b['test'] = subdirname
                #print b
                try:
                    for n in b['node_list']:
                        node_dic[n]['pair'] = b['effective']
                except:
                    pass
                #evaluate_alltoall_data(b,node_list,bad_nodes, good_nodes)
                in_file.close()

    return node_dic

def read_singles(node_path, subdirname, node_dic):

    filelist = os.listdir(os.path.join(node_path,subdirname))

    for file in filelist:
        if file.startswith("data_single"):
            data_file = os.path.join(node_path,subdirname,file)
            if os.path.exists(data_file):
                #print data_file
                in_file = open(data_file,"r")
                b = alltoall_data(in_file)
                b['test'] = subdirname
                #print b
                try:
                    for n in b['node_list']:
                        node_dic[n]['single'] = b['effective']
                except:
                    pass
                #evaluate_alltoall_data(b,node_list,bad_nodes, good_nodes)
                in_file.close()

    return node_dic

def execute(dir_name, node_list):

    path = os.path.split(dir_name)

    node_path = os.path.join(dir_name,"alltoall")
    logger.info(node_path)

    bad_nodes = []
    good_nodes = []
    for dirname, dirnames, filenames in os.walk(node_path):
        for subdirname in dirnames:
            logger.debug(subdirname)
            if subdirname.find("test_") == 0:

                results = read_all(node_path,subdirname, "data")
                results = read_pairs(node_path, subdirname, results)
                results = read_singles(node_path, subdirname, results)

                #print results

                for k,v in results.items():
                    try:
                        logger.debug(results[k]['all'])
                        print k, results[k]['all'], results[k]['pair']
                        if results[k]['all'] == False:
                            bad_nodes.append(k)
                        # if results[k]['all'] == False and results[k]['pair'] == False:
             #                bad_nodes.append(k)
                        elif (results[k]['all'] == False or results[k]['all'] == True) and results[k]['pair'] == True:
                            good_nodes.append(k)
                        else:
                            logger.info("Passed the all test and failed the pair... this is weird")
                            bad_nodes.append(k)
                    except:
                        bad_nodes.append(k)

    tested = set(good_nodes).union(set(bad_nodes))
    not_tested = set(node_list).difference(tested)

    return {'not_tested': list(not_tested), 'bad_nodes': list(set(bad_nodes)), 'good_nodes': list(set(good_nodes).difference(set(bad_nodes)))}
