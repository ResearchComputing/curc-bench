import argparse
import bench.add as add
import bench.automation as automation
import bench.create as create
import bench.nodelist as nodelist
import bench.nodes
import bench.process as process
import bench.reserve as reserve
import bench.showq as showq
import bench.status as status
import bench.submit as submit
import datetime
import glob
import logging
import os


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-P', '--directory-prefix', dest='prefix')
    parser.add_argument('-d', '--directory', help='directory')
    parser.set_defaults(prefix='.')

    subparsers = parser.add_subparsers(dest='command')

    create = subparsers.add_parser('create', help='Create the benchmark test scripts')
    create.add_argument('-N', '--nodes',
                        help = 'explicit list of nodes to test')
    create.add_argument('-x', '--exclude-nodes',
                        help = 'explicit list of nodes to exclude from testing')
    create.add_argument('-r', '--reservation',
                        help = 'test a set of reserved nodes')
    create.add_argument('-X', '--exclude-reservation',
                        help = 'exclude nodes in a reservation from testing')

    add = subparsers.add_parser('add', help='Add a benchmark test')
    add.add_argument('-r', '--allrack',
                     help = 'alltoall rack level tests',
                     action = 'store_true')
    add.add_argument('-s', '--allswitch',
                     help = 'alltoall switch level tests',
                     action = 'store_true')
    add.add_argument('-p', '--allpair',
                     help = 'alltoall pair level tests',
                     action = 'store_true')
    add.add_argument('-n', '--nodes',
                     help = 'individual node tests',
                     action = 'store_true')
    add.add_argument('-b', '--bandwidth',
                     help = 'bandwidth tests',
                     action = 'store_true')

    sumbit = subparsers.add_parser('submit', help='Submit all the jobs from create to the scheduler.')
    sumbit.add_argument('-r','--allrack', help='alltoall rack level', action='store_true')
    sumbit.add_argument('-s','--allswitch', help='alltoall switch level', action='store_true')
    sumbit.add_argument('-p','--allpair', help='alltoall pair level', action='store_true')
    sumbit.add_argument('-n','--nodes', help='nodes', action='store_true')
    sumbit.add_argument('-b','--bandwidth', help='bandwidth', action='store_true')

    process = subparsers.add_parser('process', help='Process the jobs when they are finished.')
    process.add_argument('-r','--allrack', help='alltoall rack level', action='store_true')
    process.add_argument('-s','--allswitch', help='alltoall switch level', action='store_true')
    process.add_argument('-p','--allpair', help='alltoall pair level', action='store_true')
    process.add_argument('-n','--nodes', help='nodes', action='store_true')
    process.add_argument('-b','--bandwidth', help='bandwidth', action='store_true')

    reserve = subparsers.add_parser('reserve', help='Create the necessary reservations.')
    reserve.add_argument('-r','--allrack', help='alltoall rack level', action='store_true')
    reserve.add_argument('-s','--allswitch', help='alltoall switch level', action='store_true')
    reserve.add_argument('-p','--allpair', help='alltoall pair level', action='store_true')
    reserve.add_argument('-n','--nodes', help='nodes', action='store_true')
    reserve.add_argument('-b','--bandwidth', help='bandwidth', action='store_true')

    showq = subparsers.add_parser('q', help='Checks the status of running jobs.')
    showq.add_argument('-v','--verbose', help='verbose', action='store_true')

    nodes = subparsers.add_parser('nodes', help='Checks the status of nodes.')

    status = subparsers.add_parser('status', help='Concatentates the log file of the current directory.')

    return parser


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


class MyFormatter(logging.Formatter):

    def format(self, record):
        filename = record.filename.split('.')[0]

        a = "%s %s: %s  " % (datetime.date.today(), filename.rjust(20), str(record.lineno).rjust(4))
        return "%s %s" % (a, record.msg)


def get_logger(directory):

    logger = logging.getLogger('Benchmarks')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.FileHandler(os.path.join(directory,'bench.log'))
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:   %(message)s', datefmt='%I:%M:%S %p')
    formatter = MyFormatter()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = MyFormatter()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger


def driver():
    args = parser().parse_args()

    directory = args.directory
    if directory is None:
        if args.command == 'create':
            directory = get_directory(args.prefix, new=True)
        else:
            directory = get_directory(args.prefix, new=False)
    else:
        if args.command == 'create':
            os.makedirs(directory)

    logger = get_logger(directory)

    if args.command == 'create':
        create.execute(directory,
                       include_nodes = args.nodes,
                       include_reservation = args.reservation,
                       exclude_nodes = args.exclude_nodes,
                       exclude_reservation = args.exclude_reservation,
        )

    if args.command == 'add':
        add.execute(directory,
                    allrack = args.allrack,
                    allswitch = args.allswitch,
                    bandwidth = args.bandwidth,
                    nodes = args.nodes,
                    allpair = args.allpair,
        )

    if args.command == 'submit':
        submit.execute(directory, args)

    if args.command == 'process':
        process.execute(directory, args)

    if args.command == 'reserve':
        reserve.execute(directory, args)

    if args.command == 'q':
        showq.execute(args.verbose)

    if args.command == 'status':
        status.execute(directory)

    if args.command == 'nodes':
        nodes.execute()
