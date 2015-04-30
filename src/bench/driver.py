import argparse
import bench.add
import bench.create
import bench.log
import bench.process
import bench.reserve
import bench.submit
import bench.update_nodes
import datetime
import glob
import logging
import os
import sys


logger = logging.getLogger(__name__)


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-P', '--directory-prefix', dest='prefix')
    parser.add_argument('-d', '--directory', help='directory')
    parser.set_defaults(prefix='.', verbose=False)

    subparsers = parser.add_subparsers(dest='command')

    create = subparsers.add_parser(
        'create', help='Create the benchmark test scripts')
    create.add_argument('-N', '--nodes',
                        help = 'explicit list of nodes to test')
    create.add_argument('-x', '--exclude-nodes',
                        help = 'explicit list of nodes to exclude from testing')
    create.add_argument('-r', '--reservation',
                        help = 'test a set of reserved nodes')
    create.add_argument('-X', '--exclude-reservation',
                        help = 'exclude nodes in a reservation from testing')

    add = subparsers.add_parser('add', help='Add a benchmark test')
    parser_add_test_arguments(add)
    add.add_argument('-t', '--topology-file',
                     help = 'slurm topology.conf')  


    submit = subparsers.add_parser(
        'submit', help='Submit all the jobs from create to the scheduler.')
    parser_add_test_arguments(submit)
    submit.add_argument('--pause', type=int, help='number of jobs submitted before pause')
    submit.add_argument('--reservation', help='reservation to run jobs in')
    submit.add_argument('-q', '--qos', help='qos to associate with the jobs')
    submit.add_argument('-a', '--account', help='account to use with the jobs')
    submit.set_defaults(pause=0)

    process = subparsers.add_parser(
        'process', help='Process the test results')
    parser_add_test_arguments(process)

    reserve = subparsers.add_parser(
        'reserve', help='Reserve nodes based on processed results')
    parser_add_test_arguments(reserve)
    parser.add_argument('--bad-nodes', action='store_true')
    parser.add_argument('--not-tested', action='store_true')

    update_nodes = subparsers.add_parser(
        'update-nodes', help='Mark nodes down based on processed results')
    update_nodes.add_argument('--down',
                              help='set nodes down (default: drain)', action='store_true')
    parser_add_test_arguments(update_nodes)
    update_nodes.set_defaults(down=False)

    return parser


def parser_add_test_arguments (parser):
    parser.add_argument('-r', '--alltoall-rack-tests',
                     help = 'alltoall rack level tests',
                     action = 'store_true')
    parser.add_argument('-s', '--alltoall-switch-tests',
                     help = 'alltoall switch level tests',
                     action = 'store_true')
    parser.add_argument('-p', '--alltoall-pair-tests',
                     help = 'alltoall pair level tests',
                     action = 'store_true')
    parser.add_argument('-n', '--node-tests',
                     help = 'individual node tests',
                     action = 'store_true')
    parser.add_argument('-b', '--bandwidth-tests',
                     help = 'bandwidth tests',
                     action = 'store_true')


def get_directory(prefix, new=False):
    if not os.path.exists(prefix):
        os.makedirs(prefix)

    today = datetime.date.today()
    existing_directories = glob.glob(os.path.join(prefix, '{0}-*'.format(today)))
    existing_indexes = []
    for directory in existing_directories:
        try:
            existing_indexes.append(int(os.path.basename(directory).split('-')[-1]))
        except ValueError:
            continue

    if new:
        try:
            index = max(existing_indexes) + 1
        except ValueError:
            index = 1
        directory = os.path.join(prefix, '{0}-{1}'.format(today, index))
        os.makedirs(directory)
        return directory
    else:
        try:
            index = max(existing_indexes)
        except ValueError:
            raise IOError('test directory not found')
        directory = os.path.join(prefix, '{0}-{1}'.format(today, index))
        return directory


def driver():
    bench.log.configure_package_logger()

    args = parser().parse_args()

    if args.verbose:
        bench.log.configure_stderr_logging(level=logging.INFO)
    else:
        bench.log.configure_stderr_logging(level=logging.WARNING)

    directory = args.directory
    if directory is None:
        if args.command == 'create':
            try:
                directory = get_directory(args.prefix, new=True)
            except (OSError, IOError) as ex:
                logger.error('unable to create session directory')
                logger.debug(ex, exc_info=True)
                sys.exit(-1)
        else:
            directory = get_directory(args.prefix, new=False)
    else:
        if args.command == 'create':
            try:
                os.makedirs(directory)
            except (OSError, IOError) as ex:
                logger.error('unable to create session directory')
                logger.debug(ex, exc_info=True)
                sys.exit(-1)

    bench.log.configure_file_logging(directory)

    if args.command == 'create':
        bench.create.execute(
            directory,
            include_nodes = args.nodes,
            include_reservation = args.reservation,
            exclude_nodes = args.exclude_nodes,
            exclude_reservation = args.exclude_reservation,
        )

    elif args.command == 'add':
        bench.add.execute(
            directory, args.topology_file,
            alltoall_rack_tests = args.alltoall_rack_tests,
            alltoall_switch_tests = args.alltoall_switch_tests,
            alltoall_pair_tests = args.alltoall_pair_tests,
            bandwidth_tests = args.bandwidth_tests,
            node_tests = args.node_tests,
        )

    elif args.command == 'submit':
        bench.submit.execute(
            directory,
            alltoall_rack_tests = args.alltoall_rack_tests,
            alltoall_switch_tests = args.alltoall_switch_tests,
            alltoall_pair_tests = args.alltoall_pair_tests,
            node_tests = args.node_tests,
            bandwidth_tests = args.bandwidth_tests,
            pause = args.pause,
            reservation = args.reservation,
            qos = args.qos,
            account = args.account,
        )

    elif args.command == 'process':
        bench.process.execute(
            directory,
            alltoall_rack_tests = args.alltoall_rack_tests,
            alltoall_switch_tests = args.alltoall_switch_tests,
            alltoall_pair_tests = args.alltoall_pair_tests,
            node_tests = args.node_tests,
            bandwidth_tests = args.bandwidth_tests,
        )

    elif args.command == 'reserve':
        bench.reserve.execute(
            directory,
            alltoall_rack_tests = args.alltoall_rack_tests,
            alltoall_switch_tests = args.alltoall_switch_tests,
            alltoall_pair_tests = args.alltoall_pair_tests,
            node_tests = args.node_tests,
            bandwidth_tests = args.bandwidth_tests,
            not_tested = args.not_tested,
        )

    elif args.command == 'update-nodes':
        bench.update_nodes.update_nodes(
            directory,
            alltoall_rack_tests = args.alltoall_rack_tests,
            alltoall_switch_tests = args.alltoall_switch_tests,
            alltoall_pair_tests = args.alltoall_pair_tests,
            node_tests = args.node_tests,
            bandwidth_tests = args.bandwidth_tests,
            down = args.down,
        )
