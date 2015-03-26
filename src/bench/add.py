import bench.tests.alltoall
import bench.tests.bandwidth
import bench.tests.node
import bench.util
from bench.util import util as util
import datetime
import logging
import re
import os
import subprocess


logger = logging.getLogger('Benchmarks')


RESERVATION_P = re.compile(r'ReservationName=([0-9]+.[0-9]+PM-janus) StartTime=([0-9]+-[0-9]+-[0-9]+)')


def get_first_pm_reservation ():
    pid = subprocess.Popen('scontrol show reservation', shell=True,
                           stdout=subprocess.PIPE)
    pid.wait()
    output, error = pid.communicate()
    tmp = RESERVATION_P.findall(output)

    reservation_name = tmp[0][0]
    reservation_time = datetime.datetime.strptime(tmp[0][1], "%Y-%m-%d")

    if len(tmp) > 1:
        for i in tmp[1:]:
            i_name = i[0]
            i_time = i[1]
            i_var = datetime.datetime.strptime(i_time, "%Y-%m-%d")
            if (i_var - reservation_time).days < 0:
                reservation_name = i_name
                reservation_time = i_var
    return reservation_name


def execute(prefix, alltoall_rack, alltoall_switch, alltoall_pair, bandwidth, nodes):
    reservation_name = get_first_pm_reservation()
    logger.info('reservation: {0}'.format(reservation_name))

    node_list = util.read_node_list(os.path.join(prefix, 'node_list'))
    logger.info('nodes: {0}'.format(len(node_list)))

    if not (alltoall_rack or alltoall_switch or alltoall_pair or bandwidth or nodes):
        add_node_tests(node_list, reservation_name, prefix)
        add_bandwidth_tests(node_list, reservation_name, prefix)
        add_allrack_tests(node_list, reservation_name, prefix)
        add_allswitch_tests(node_list, reservation_name, prefix)
        add_allpair_tests(node_list, reservation_name, prefix)

    else:
        if alltoall_rack:
            add_allrack_tests(node_list, reservation_name, prefix)
        if alltoall_switch:
            add_allswitch_tests(node_list, reservation_name, prefix)
        if alltoall_pair:
            add_allpair_tests(node_list, reservation_name, prefix)
        if bandwidth:
            add_bandwidth_tests(node_list, reservation_name, prefix)
        if nodes:
            add_node_tests(node_list, reservation_name, prefix)


def add_node_tests (node_list, reservation_name, prefix):
    node_prefix = os.path.join(prefix, 'node')
    logger.info('adding node tests to {0}'.format(node_prefix))
    bench.util.mkdir_p(prefix)
    bench.tests.node.generate(node_list, reservation_name, node_prefix)


def add_bandwidth_tests (node_list, reservation_name, prefix):
    bandwidth_prefix = os.path.join(prefix, 'bandwidth')
    logger.info('adding bandwidth tests to {0}'.format(prefix))
    bench.util.mkdir_p(bandwidth_prefix)
    bench.tests.bandwidth.generate(node_list, reservation_name, bandwidth_prefix)


def add_allrack_tests (node_list, reservation_name, prefix):
    allrack_prefix = os.path.join(prefix, 'allrack')
    logger.info('adding allrack tests to {0}'.format(prefix))
    bench.util.mkdir_p(allrack_prefix)
    bench.tests.alltoall.generate_allrack(node_list, reservation_name, allrack_prefix)


def add_allswitch_tests (node_list, reservation_name, prefix):
    allswitch_prefix = os.path.join(prefix, 'allswitch')
    logger.info('adding allswitch tests to {0}'.format(prefix))
    bench.util.mkdir_p(allswitch_prefix)
    bench.tests.alltoall.generate_allswitch(node_list, reservation_name, allswitch_prefix)


def add_allpair_tests (node_list, reservation_name, prefix):
    allpair_prefix = os.path.join(prefix, 'allpair')
    logger.info('adding allpair tests to {0}'.format(prefix))
    bench.util.mkdir_p(allpair_prefix)
    bench.tests.alltoall.generate_allpair(node_list, reservation_name, allpair_prefix)
