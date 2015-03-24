import bench.create_tests.create_alltoall as create_alltoall
import bench.create_tests.create_bandwidth_test as create_bandwidth_test
import bench.create_tests.create_node_test as create_node_test
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


def execute(directory, allrack, allswitch, bandwidth, nodes, allpair):
    reservation_name = get_first_pm_reservation()
    logger.info('reservation: {0}'.format(reservation_name))

    node_list = util.read_node_list(os.path.join(directory,'node_list'))
    logger.info('nodes: {0}'.format(len(node_list)))

    if not (allrack or allswitch or bandwidth or nodes or allpair):
        logger.info('adding all tests to {0}'.format(directory))
        create_node_test.create(node_list, reservation_name, directory)
        create_bandwidth_test.create(node_list, reservation_name, directory)
        create_alltoall.create(
            node_list, reservation_name, directory,
            allrack = True,
            allswitch = True,
            allpair = True,
        )

    else:
        if allrack or allswitch or allpair:
            logger.info('adding alltoall tests to {0}'.format(directory))
            create_alltoall.create(
                node_list, reservation_name, directory,
                allrack = allrack,
                allswitch = allswitch,
                allpair = allpair,
            )

        if args.bandwidth:
            logger.info('adding bandwidth tests to {0}'.format(directory))
            create_bandwidth_test.create(node_list, reservation_name, directory)

        if args.nodes:
            logger.info('adding nodes tests to {0}'.format(directory))
            create_node_test.create(node_list, reservation_name, directory)
