#!/curc/admin/benchmarks/bin/python

import os, sys
from datetime import datetime


from bench.util import config

# appsdir = '/home/molu8455/admin/benchmarks/django/benchmarks/apps/'
# if not appsdir in sys.path:
#     sys.path.insert(0,appsdir)

# appsdir = '/home/molu8455/admin/benchmarks/django/benchmarks/'
# if not appsdir in sys.path:
#     sys.path.insert(1,appsdir)

import logging
logger = logging.getLogger('Benchmarks')

# os.environ["DJANGO_SETTINGS_MODULE"] = "benchmarks_site.settings"
# from django.db import models
# from wire.models import Stream, Linpack
# from django.db import IntegrityError

def stream_data(in_file):
    test = in_file.readline().split()[0]
    data = in_file.readline().split()

    data_copy = 0
    data_scale = 0
    data_add = 0
    data_triad = 0

    if data:
        try:
            data_copy = data[0]
            data_scale = data[1]
            data_add = data[2]
            data_triad = data[3]
        except IndexError:
            logger.error("missing stream data")

    return {'t0': data_copy, 't1': data_scale, 't2': data_add, 't3': data_triad}

def evaluate_stream_data(data, subdirname, bad_nodes, good_nodes):

    value = (1-float(config.stream_limits['percent']/100.0))

    if float(data['t0']) < float(config.stream_limits['t0']*value):
        data['t0_effective'] = False
        bad_nodes.append(subdirname)
    else:
        data['t0_effective'] = True
        good_nodes.append(subdirname)

    if float(data['t1']) < float(config.stream_limits['t1']*value):
        data['t1_effective'] = False
        bad_nodes.append(subdirname)
    else:
        data['t1_effective'] = True
        good_nodes.append(subdirname)

    if float(data['t2']) < float(config.stream_limits['t2']*value):
        data['t2_effective'] = False
        bad_nodes.append(subdirname)
    else:
        data['t2_effective'] = True
        good_nodes.append(subdirname)

    if float(data['t3']) < float(config.stream_limits['t3']*value):
        data['t3_effective'] = False
        bad_nodes.append(subdirname)
    else:
        data['t3_effective'] = True
        good_nodes.append(subdirname)

def evaluate_linpack_data(data, subdirname, bad_nodes, good_nodes):

    value = (1-float(config.linpack_limits['percent']/100.0))

    if float(data['t0']) < float(config.linpack_limits['t0']*value):
        data['t0_effective'] = False
        bad_nodes.append(subdirname)
    else:
        data['t0_effective'] = True

    if float(data['t1']) < float(config.linpack_limits['t1']*value):
        data['t1_effective'] = False
        bad_nodes.append(subdirname)
    else:
        data['t1_effective'] = True

    if float(data['t2']) < float(config.linpack_limits['t2']*value):
        data['t2_effective'] = False
        bad_nodes.append(subdirname)
    else:
        data['t2_effective'] = True

    if float(data['t3']) < float(config.linpack_limits['t3']*value):
        data['t3_effective'] = False
        bad_nodes.append(subdirname)
    else:
        data['t3_effective'] = True



def linpack_data(in_file):
    for i in range(6):
        data = in_file.readline()
    data = in_file.readline().split()

    data_linpack = {'t0':0,'t1':0,'t2':0,'t3':0}
    for i in range(4):
        try:
            data_linpack['t'+str(i)] = (data[3])
        except IndexError:
            continue
        data = in_file.readline().split()

    return data_linpack

def insert_stream(data, node_name, td, tr):
    tmp = datetime(year=td.year, month=td.month, day=td.day, hour=int(tr))
    stream = Stream(test_date=tmp, name=node_name, node=node_name, test1=data['t0'], test2=data['t1'], test3=data['t2'], test4=data['t3'], effective=True)
    try:
        stream.save()
    except IntegrityError as e:
        logger.error("Stream import error: " + str(e))

def insert_linpack(data, node_name, td, tr):
    tmp = datetime(year=td.year, month=td.month, day=td.day, hour=int(tr))
    linpack = Linpack(test_date=tmp,  name=node_name, node=node_name, test1=data['t0'], test2=data['t1'], test3=data['t2'], test4=data['t3'], effective=True)
    try:
        linpack.save()
    except IntegrityError as e:
        logger.error("linpack import error: " + str(e))

def import_data(path, date, trial):
    logger.info("Importing Node level data")
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            if subdirname.find("node") == 0:
                data_file = os.path.join(path,subdirname,"data")
                if os.path.exists(data_file):
                    in_file = open(os.path.join(path,subdirname,"data"),"r")

                    # Stream data
                    s = stream_data(in_file)
                    insert_stream(s,subdirname,date, trial)

                    # Linpack
                    l = linpack_data(in_file)
                    insert_linpack(l,subdirname,date, trial)

                    in_file.close()

def execute(dir_name, node_list):

    path = os.path.split(dir_name)
    trial = path[-1].split('-')[-1]
    year = path[-1].split('-')[0]
    month = path[-1].split('-')[1]
    day = path[-1].split('-')[2]

    node_path = os.path.join(dir_name,"nodes")
    logger.info(node_path)

    bad_nodes = []
    good_nodes = []
    for dirname, dirnames, filenames in os.walk(node_path):
        for subdirname in dirnames:
            if subdirname.find("node") == 0:
                data_file = os.path.join(node_path,subdirname,"data")
                if os.path.exists(data_file):
                    in_file = open(os.path.join(node_path,subdirname,"data"),"r")
                    # Stream data
                    s = stream_data(in_file)
                    evaluate_stream_data(s, subdirname, bad_nodes, good_nodes)

                    #insert_stream(s,subdirname,date, trial)
                    # Linpack
                    l = linpack_data(in_file)
                    evaluate_linpack_data(l, subdirname, bad_nodes, good_nodes)
                    #insert_linpack(l,subdirname,date, trial)
                    in_file.close()

    tested = set(good_nodes).union(set(bad_nodes))
    not_tested = set(node_list).difference(tested)

    #logger.info("not tested  " + str(len(not_tested)))
    #logger.info("good nodes " + str(len(good_nodes)))

    return {'not_tested': list(not_tested), 'bad_nodes': list(set(bad_nodes)), 'good_nodes': list(set(good_nodes).difference(set(bad_nodes)))}
