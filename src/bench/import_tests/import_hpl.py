import os
import logging
logger = logging.getLogger(__name__)
from bench.util import infiniband

def parse(node_path, subdirname, node_dic):
    node_list = None
    data_file = os.path.join(node_path,subdirname,'info')
    if os.path.exists(data_file):
        in_file = open(data_file,"r")
        node_list = infiniband.read_info_file(in_file)
        in_file.close()

    data_file = os.path.join(node_path,subdirname,'time_data')
    if os.path.exists(data_file):

        in_file = open(data_file,"r")
        tmp = in_file.readline().split()
        value = 0
        if len(tmp)>0:
            value = int(tmp[0])
        in_file.close()
    #print len(node_list), node_list
    for n in node_list:
        if node_dic.has_key(n):
            node_dic[n][len(node_list)] = value
        else:
            node_dic[n] = {}
            node_dic[n][len(node_list)] = value

    return node_dic

def execute(node_list, dir_name):

    path = os.path.split(dir_name)
    #trial = path[-1].split('-')[-1]
    #year = path[-1].split('-')[0]
    #month = path[-1].split('-')[1]
    #day = path[-1].split('-')[2]

    node_path = os.path.join(dir_name,"hpl")
    logger.info(node_path)

    bad_nodes = []
    good_nodes = []

    results = {}
    for dirname, dirnames, filenames in os.walk(node_path):
        for subdirname in dirnames:
            #logger.debug(subdirname)
            if subdirname.find("test_") == 0:
                #rint subdirname
                results = parse(node_path, subdirname, results)

    for k,v in results.iteritems():
        print k,v

    #
    #                 results = read_all(node_path,subdirname, "data")
    #                 results = read_pairs(node_path, subdirname, results)
    #                 results = read_singles(node_path, subdirname, results)
    #
    #                 for k,v in results.items():
    #                     print k, results[k]
    #                     if results[k]['all'] == False and results[k]['pair'] == False:
    #                         bad_nodes.append(k)
    #                     elif (results[k]['all'] == False or results[k]['all'] == True) and results[k]['pair'] == True:
    #                         good_nodes.append(k)
    #                     else:
    #                         logger.info("Passed the all test and failed the pair... this is weird")
    #                         bad_nodes.append(k)

    logger.info("bad nodes  " + str(len(bad_nodes)))
    logger.info("good nodes " + str(len(good_nodes)))

    return {'bad_nodes': list(set(bad_nodes)), 'good_nodes': list(set(good_nodes).difference(set(bad_nodes)))}
