#!/curc/admin/benchmarks/bin/python
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
    data['num_nodes'] = num_nodes
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
        #data['percent'] = round(100*(config.alltoall_limits[num_nodes]- data['mean'])/config.alltoall_limits[num_nodes])
        data['percent'] = 100

        # if config.alltoall_limits[num_nodes]*value < data['mean']:
 #            data['effective'] = False
 #        else:
 #            data['effective'] = True
    else:
        # data['effective'] = False
        data['percent'] = 100
    # if data['effective'] == False:
 #        print num_nodes, data['mean'], config.alltoall_limits[num_nodes], data['effective']

    data['effective'] = False
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
                #print subdirname
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



def read_all(node_path, subdirname, filename, keyname, bad_nodes, good_nodes):

    node_dic = {}

    data_file = os.path.join(node_path,subdirname,filename)
    if os.path.exists(data_file):
        in_file = open(data_file,"r")
        b = alltoall_data(in_file)

        # compute % difference
        try:
            pdiff = 100*(b['mean'] - config.alltoall_limits[b['num_nodes']] )/b['mean']
        except ZeroDivisionError, e:
            pdiff = 100
        except KeyError, e:
            pdiff = 100

        #print pdiff, config.alltoall_limits['percent']

        threshold = config.alltoall_limits['percent']
        # NOTE: CHANGE THRESHOLD
        threshold = 55
        if pdiff > threshold:
            b['effective'] = False
        else:
            b['effective'] = True

        b['test'] = subdirname

        # print b['test'], b['num_nodes'], b['mean'], config.alltoall_limits[b['num_nodes']], pdiff, b['effective']
  #
        for n in b['node_list']:
            if n not in node_dic:
                node_dic[n] = {}



        for n in b['node_list']:
            if b['effective'] == False:
                bad_nodes.append(n)
            else:
                good_nodes.append(n)

        in_file.close()

    return node_dic


def execute(dir_name, node_list):

    path = os.path.split(dir_name)

    bad_nodes_rack = []
    good_nodes_rack = []

    bad_nodes_switch = []
    good_nodes_switch = []

    bad_nodes_pair = []
    good_nodes_pair = []

    node_path = os.path.join(dir_name,"alltoall_rack")
    logger.info(node_path)
    for dirname, dirnames, filenames in os.walk(node_path):
        for subdirname in dirnames:
            logger.debug(subdirname)
            if subdirname.find("test_") == 0:
                results_rack = read_all(node_path,subdirname, "data",'rack',bad_nodes_rack,good_nodes_rack)

    node_path = os.path.join(dir_name,"alltoall_switch")
    logger.info(node_path)
    for dirname, dirnames, filenames in os.walk(node_path):
        for subdirname in dirnames:
            logger.debug(subdirname)
            if subdirname.find("test_") == 0:
                results_switch = read_all(node_path,subdirname, "data",'switch',bad_nodes_switch,good_nodes_switch)

    node_path = os.path.join(dir_name,"alltoall_pair")
    logger.info(node_path)
    for dirname, dirnames, filenames in os.walk(node_path):
        for subdirname in dirnames:
            logger.debug(subdirname)
            if subdirname.find("test_") == 0:
                results_pair = read_all(node_path,subdirname, "data",'pair',bad_nodes_pair,good_nodes_pair)

    print 'bad'
    print 'rack', len(bad_nodes_rack)
    print 'switch', len(bad_nodes_switch)
    print 'pair', len(bad_nodes_pair)

    print 'good'
    print 'rack', len(good_nodes_rack)
    print 'switch', len(good_nodes_switch)
    print 'pair', len(good_nodes_pair)

    print 'not tested'
    tested_r = set(good_nodes_rack).union(set(bad_nodes_rack))
    not_tested_r = set(node_list).difference(tested_r)
    print 'rack', len(not_tested_r)

    tested_s = set(good_nodes_switch).union(set(bad_nodes_switch))
    not_tested_s = set(node_list).difference(tested_s)
    print 'switch', len(not_tested_s)

    tested_p = set(good_nodes_pair).union(set(bad_nodes_pair))
    not_tested_p = set(node_list).difference(tested_p)
    print 'pair', len(not_tested_p)

    print 'node_list', len(node_list)
    bad_nodes = set(bad_nodes_rack).union(set(bad_nodes_switch)).union(set(bad_nodes_pair))
    print 'bad nodes', len(bad_nodes)
    not_tested = set(not_tested_r).union(set(not_tested_s)).union(set(not_tested_p))
    print 'not tested', len(not_tested)
    not_bad = set(bad_nodes).union(set(not_tested))
    print 'not bad', len(not_bad)
    good_nodes = set(node_list).difference(not_bad)
    print 'good nodes', len(good_nodes)


    return {'not_tested': list(not_tested), 'bad_nodes': list(set(bad_nodes)), 'good_nodes': list(good_nodes)}
#
def execute_rack(dir_name, node_list):

    path = os.path.split(dir_name)

    bad_nodes_rack = []
    good_nodes_rack = []

    node_path = os.path.join(dir_name,"alltoall_rack")
    logger.info(node_path)
    for dirname, dirnames, filenames in os.walk(node_path):
        for subdirname in dirnames:
            logger.debug(subdirname)
            if subdirname.find("test_") == 0:
                results_rack = read_all(node_path,subdirname, "data",'rack',bad_nodes_rack,good_nodes_rack)

    tested_r = set(good_nodes_rack).union(set(bad_nodes_rack))
    not_tested_r = set(node_list).difference(tested_r)


    return {'not_tested': list(not_tested_r), 'bad_nodes': list(set(bad_nodes_rack)), 'good_nodes': list(good_nodes_rack)}
#
def execute_switch(dir_name, node_list):
    path = os.path.split(dir_name)

    bad_nodes_switch = []
    good_nodes_switch = []

    node_path = os.path.join(dir_name,"alltoall_switch")
    logger.info(node_path)
    for dirname, dirnames, filenames in os.walk(node_path):
       for subdirname in dirnames:
           logger.debug(subdirname)
           if subdirname.find("test_") == 0:
               results_switch = read_all(node_path,subdirname, "data",'switch',bad_nodes_switch,good_nodes_switch)

    tested_r = set(good_nodes_switch).union(set(bad_nodes_switch))
    not_tested_r = set(node_list).difference(tested_r)


    return {'not_tested': list(not_tested_r), 'bad_nodes': list(set(bad_nodes_switch)), 'good_nodes': list(good_nodes_switch)}

def execute_pair(dir_name, node_list):
    path = os.path.split(dir_name)

    bad_nodes_switch = []
    good_nodes_switch = []

    node_path = os.path.join(dir_name,"alltoall_pair")
    logger.info(node_path)
    for dirname, dirnames, filenames in os.walk(node_path):
       for subdirname in dirnames:
           logger.debug(subdirname)
           if subdirname.find("test_") == 0:
               results_switch = read_all(node_path,subdirname, "data",'pair',bad_nodes_switch,good_nodes_switch)

    tested_r = set(good_nodes_switch).union(set(bad_nodes_switch))
    not_tested_r = set(node_list).difference(tested_r)

    A = set(not_tested_r).union(set(bad_nodes_switch))
    good_nodes_switch = set(node_list).difference(A)
    #good_nodes_switch = set(tested_r).union(set(bad_nodes_switch)).union(set(bad_nodes_switch))

    # print len(good_nodes_switch)
 #    print len(bad_nodes_switch)
 #    print len(tested_r)
 #    print len(not_tested_r)
 #
 #

    return {'not_tested': list(not_tested_r), 'bad_nodes': list(set(bad_nodes_switch)), 'good_nodes': list(good_nodes_switch)}
