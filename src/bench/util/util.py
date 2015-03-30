import datetime
import os
import shutil


def read_node_list(node_list_name, dir=None):
    node_list = []
    if not dir:
        file_in = open(os.path.join(os.getcwd(), node_list_name),'r')
    else:
        file_in = open(os.path.join(dir, node_list_name),'r')

    node_name = file_in.readline()

    while node_name:
        if len(node_name.strip()) == 8:
            node_list.append(node_name.strip())
        node_name = file_in.readline()
    file_in.close()

    return node_list


def categorize(node_list):
    long_nodes = []
    special_nodes = []
    janus_nodes = []

    for x in node_list:
        if x[4:6] == "01":
            long_nodes.append(x)
        elif (x[4:6] == "02" or x == "node0301"):
            special_nodes.append(x)
        else:
            janus_nodes.append(x)

    return {'long':long_nodes, 'special':special_nodes, 'janus':janus_nodes}


def create_directory_structure(dir_name):
    if os.path.exists(dir_name):
        cmd = 'The directory {0} exists.\n Delete it? (y or n): '.format(dir_name)
        ans = raw_input(cmd)
        if ans == 'y':
            shutil.rmtree(dir_name)
            os.mkdir(dir_name)
    else:
        try:
            os.mkdir(dir_name)
        except os.error as e:
            print "ERROR: {0}".format(e.strerror)


def get_directory(directory_name):
    directory = '/curc/admin/benchmarks/data'
    if not os.path.exists(directory):
        os.makedirs(directory)

    folder = datetime.date.today()
    index = 1
    if not directory_name:
        while index < 100:
            folder_name = os.path.join(directory,str(folder)+"-"+str(index))
            if not os.path.exists(folder_name):
                break
            index+=1
    else:
        folder_name = os.path.join(directory,directory_name)
        return folder_name

    folder_name = os.path.join(directory,str(folder)+"-"+str(index-1))
    return folder_name
