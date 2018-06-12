import argparse
import bench.create
import bench.framework
import bench.framework_add
import bench.framework_submit
import bench.framework_process
import bench.framework_reserve
import bench.tests.node_test
import bench.tests.bandwidth_test
import bench.tests.alltoall_tests
import bench.tests.ior
import bench.log
import bench.update_nodes
import datetime
import glob
import logging
import os
import sys


logger = logging.getLogger(__name__)

def parser(*args, **kwargs):
    parser = argparse.ArgumentParser(*args, **kwargs)
    parser.add_argument('-v', '--verbose', action='store_true', help='INFO logging')
    parser.add_argument('-P', '--directory-prefix', help='test directory prefix')
    parser.add_argument('-d', '--directory', help='test directory')
    parser.set_defaults(directory_prefix='.', verbose=False)

    subparsers = parser.add_subparsers(dest='command')

    create = subparsers.add_parser(
        'create', help='create test directory')
    parser_add_filter_arguments(create)

    add = subparsers.add_parser('add', help='add tests for submission')
    parser_add_test_arguments(add)
    parser_add_filter_arguments(add)

    submit = subparsers.add_parser('submit', help='submit jobs for scheduling')
    parser_add_test_arguments(submit)
    submit.add_argument('--pause', type=int, metavar='N',
                        help='pause between N job submissions')
    submit.add_argument('--nodelist', help='only submit jobs nodes in nodelist')
    submit.add_argument('--reservation', help='submission reservation')
    submit.add_argument('-q', '--qos', help='submission qos')
    submit.add_argument('-a', '--account', help='submission account')
    submit.add_argument('--error-nodes', action='store_true',
                        help='submit jobs for nodes with previous errors')
    submit.add_argument('--fail-nodes', action='store_true',
                        help='submit jobs for nodes with previous failures')
    submit.add_argument('--pass-nodes', action='store_true',
                        help='submit jobs for nodes with previous passes')
    submit.set_defaults(pause=0)

    process = subparsers.add_parser(
        'process', help='process test output')
    parser_add_test_arguments(process)

    reserve = subparsers.add_parser(
        'reserve', help='reserve nodes based on process results')
    parser_add_test_arguments(reserve)
    reserve.add_argument('--reservation-name', help='name of the created reservation')
    reserve.add_argument('--fail-nodes', action='store_true',
                         help='reserve nodes with failures')
    reserve.add_argument('--error-nodes', action='store_true',
                         help='reserve nodes with errors')
    reserve.add_argument('-a', '--account', help='reservation account')

    update_nodes = subparsers.add_parser(
        'update-nodes', help='configure nodes down based on process results')
    update_nodes.add_argument('--down',
                              help='set nodes down (default: drain)', action='store_true')
    parser_add_test_arguments(update_nodes)
    update_nodes.add_argument('--fail-nodes', action='store_true',
                              help='configure nodes with failures')
    update_nodes.add_argument('--error-nodes', action='store_true',
                              help='configure nodes with errors')
    update_nodes.set_defaults(down=False)

    return parser


def parser_add_test_arguments (parser):
    parser.add_argument('--test', required=True, action='store', dest='test',
                            choices=['alltoall-rack',
                                     'alltoall-switch',
                                     'alltoall-pair',
                                     'bandwidth',
                                     'node',
                                     'ior'],
                            help='''alltoall-rack = test osu_alltoall on a rack of nodes,
                                    alltoall-switch = test osu_alltoall on nodes connected to a switch
                                    alltoall-pair = test osu_alltoall on node pairs
                                    bandwidth = test osu_bibw on node pairs
                                    node = test linpack and stream on individual nodes
                                    ior = test scratch filesystem''')




def parser_add_filter_arguments (parser):
    parser.add_argument('--include-nodes', action='append',
                        help='include specific nodes')
    parser.add_argument('--exclude-nodes', action='append',
                        help='exclude specific nodes')
    parser.add_argument('--include-reservation', action='append', dest='include_reservations',
                        help='include nodes from an existing reservation')
    parser.add_argument('--exclude-reservation', action='append', dest='exclude_reservations',
                        help='exclude nodes in an existing reservation')
    parser.add_argument('--include-state', metavar='STATE',
                        action='append', dest='include_states',
                        help='include nodes with the given STATE')
    parser.add_argument('--exclude-state', metavar='STATE',
                        action='append', dest='exclude_states',
                        help='exclude nodes with the given STATE')
    parser.add_argument('--include-file', metavar='FILE',
                        action='append', dest='include_files',
                        help='include nodes from a given FILE')
    parser.add_argument('--exclude-file', metavar='FILE',
                        action='append', dest='exclude_files',
                        help='exclude nodes in a given FILE')


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


def driver(argv=None):
    if argv is None:
        argv = sys.argv

    bench.log.configure_package_logger()

    args = parser(prog=argv[0]).parse_args(args=argv[1:])

    if args.verbose:
        bench.log.configure_stderr_logging(level=logging.INFO)
    else:
        bench.log.configure_stderr_logging(level=logging.WARNING)

    directory = args.directory
    if directory is None:
        if args.command == 'create':
            try:
                directory = get_directory(args.directory_prefix, new=True)
            except (OSError, IOError) as ex:
                logger.error('unable to create session directory')
                logger.debug(ex, exc_info=True)
                sys.exit(-1)
        else:
            directory = get_directory(args.directory_prefix, new=False)
    else:
        if args.command == 'create':
            try:
                os.makedirs(directory)
            except (OSError, IOError) as ex:
                logger.error('unable to create session directory')
                logger.debug(ex, exc_info=True)
                sys.exit(-1)

    bench.log.configure_file_logging(directory)

    #Dictionary of possible commands
    commandDictionary = {}
    commandDictionary['node'] = bench.tests.node_test.NodeTest("node")
    commandDictionary['bandwidth'] = bench.tests.bandwidth_test.BandwidthTest("bandwidth")
    commandDictionary['alltoall-pair'] = bench.tests.alltoall_tests.AllToAllTest("alltoall-pair")
    commandDictionary['alltoall-switch'] = bench.tests.alltoall_tests.AllToAllTest("alltoall-switch")
    commandDictionary['alltoall-rack'] = bench.tests.alltoall_tests.AllToAllTest("alltoall-rack")
    commandDictionary['ior'] = bench.tests.ior.IorTest("ior")

    if args.command == 'create':
        bench.create.execute(
            directory,
            include_nodes = args.include_nodes,
            exclude_nodes = args.exclude_nodes,
            include_reservations = args.include_reservations,
            exclude_reservations = args.exclude_reservations,
            include_states = args.include_states,
            exclude_states = args.exclude_states,
            include_files = args.include_files,
            exclude_files = args.exclude_files,
        )

    elif args.command == 'add':
        currentTest = commandDictionary[args.test]

        currentTest.Add.execute(
            directory,
            include_nodes = args.include_nodes,
            exclude_nodes = args.exclude_nodes,
            include_reservations = args.include_reservations,
            exclude_reservations = args.exclude_reservations,
            include_states = args.include_states,
            exclude_states = args.exclude_states,
            include_files = args.include_files,
            exclude_files = args.exclude_files,
        )

    elif args.command == 'submit':
        currentTest = commandDictionary[args.test]
        currentTest.Submit.execute(
            directory,
            pause = args.pause,
            nodelist = args.nodelist,
            reservation = args.reservation or os.environ.get('BENCH_RESERVATION'),
            qos = args.qos or os.environ.get('BENCH_QOS'),
            account = args.account or os.environ.get('BENCH_ACCOUNT'),
            pass_nodes = args.pass_nodes,
            fail_nodes = args.fail_nodes,
            error_nodes = args.error_nodes,
        )

    elif args.command == 'process':
        currentTest = commandDictionary[args.test]
        currentTest.Process.results_logger = bench.log.setup_logger('results_logger', directory, 'results.log')
        currentTest.Process.execute(
            directory,
        )

    elif args.command == 'reserve':
        currentTest = commandDictionary[args.test]
        currentTest.Reserve.execute(
            directory,
        )

    elif args.command == 'update-nodes':
        bench.update_nodes.update_nodes(
            directory,
            alltoall_rack_tests = args.alltoall_rack_tests,
            alltoall_switch_tests = args.alltoall_switch_tests,
            alltoall_pair_tests = args.alltoall_pair_tests,
            node_tests = args.node_tests,
            bandwidth_tests = args.bandwidth_tests,
            fail_nodes = args.fail_nodes,
            error_nodes = args.error_nodes,
            down = args.down,
        )
