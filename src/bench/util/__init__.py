import bench.exc
import errno
import logging
import os
import subprocess


logger = logging.getLogger(__name__)


def mkdir_p (path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    l = list(l)
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def read_node_list(node_list_path):
    nodes = []
    with open(node_list_path) as fp:
        for line in fp:
            node = line.strip()
            if node:
                nodes.append(node)
    return nodes


def write_node_list (path, nodes):
    with open(path, 'w') as fp:
        for node in sorted(nodes):
            fp.write('{0}\n'.format(node))
