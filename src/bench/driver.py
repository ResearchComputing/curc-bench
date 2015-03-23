import argparse
import os
import datetime
import sys

#from create import execute
import bench.create as create
import bench.submit as submit

import bench.showq as showq
import bench.process as process
import bench.reserve as reserve
import bench.nodelist as nodelist
import bench.add as add
#import bench.scaling as scaling
import bench.nodes

import automation
import status

import logging
import shutil


def get_args(argv):

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help=None, dest='command')

    # Create
    create = subparsers.add_parser('create', help='Create the benchmark test scripts.  For options, type bench create -h for help.\n')
    create.add_argument('-d','--dir', help='directory', dest='directory')
    create.set_defaults(directory=None)
    #create.add_argument('-r','--retest', help='retest benchmarks', action='store_true')
    create.add_argument('-l','--nodelist', help='node_list for test')
    create.add_argument('-r','--reservation', help='node_list from reservation')
    create.set_defaults(nodelist=None)
    create.add_argument('-e','--exclude', help='exclude these nodes.  For example, --exclude node[01][01-80]')
    #create.set_defaults(exclude='node[01][01-80],node[00][01-04],node[02][01-08], node0773')
    create.set_defaults(exclude='node[00][01-04], node0773')

    add = subparsers.add_parser('add', help='Add a benchmark test.  For options, type bench add -h for help.\n')
    add.add_argument('-d','--dir', help='directory', dest='directory')
    add.set_defaults(directory=None)
    add.add_argument('-r','--allrack', help='alltoall rack level', action='store_true')
    add.add_argument('-s','--allswitch', help='alltoall switch level', action='store_true')
    add.add_argument('-p','--allpair', help='alltoall pair level', action='store_true')
    add.add_argument('-n','--nodes', help='nodes', action='store_true')
    add.add_argument('-b','--bandwidth', help='bandwidth', action='store_true')

    # Submit
    sumbit = subparsers.add_parser('submit', help='Submit all the jobs from create to the scheduler. For options, type bench submit -h for help.\n')
    sumbit.add_argument('-d','--dir', help='directory', dest='directory')
    sumbit.set_defaults(directory=None)
    sumbit.add_argument('-r','--allrack', help='alltoall rack level', action='store_true')
    sumbit.add_argument('-s','--allswitch', help='alltoall switch level', action='store_true')
    sumbit.add_argument('-p','--allpair', help='alltoall pair level', action='store_true')
    sumbit.add_argument('-n','--nodes', help='nodes', action='store_true')
    sumbit.add_argument('-b','--bandwidth', help='bandwidth', action='store_true')

    # Process
    process = subparsers.add_parser('process', help='Process the jobs when they are finished. For process options, type bench submit -h for help.\n')
    process.add_argument('-d','--dir', help='directory', dest='directory')
    process.set_defaults(directory=None)
    process.add_argument('-r','--allrack', help='alltoall rack level', action='store_true')
    process.add_argument('-s','--allswitch', help='alltoall switch level', action='store_true')
    process.add_argument('-p','--allpair', help='alltoall pair level', action='store_true')
    process.add_argument('-n','--nodes', help='nodes', action='store_true')
    process.add_argument('-b','--bandwidth', help='bandwidth', action='store_true')

    # Reserve
    reserve = subparsers.add_parser('reserve', help='Create the necessary reservations: For options, type bench reserve -h.\n')
    reserve.add_argument('-d','--dir', help='directory', dest='directory')
    reserve.set_defaults(directory=None)
    reserve.add_argument('-r','--allrack', help='alltoall rack level', action='store_true')
    reserve.add_argument('-s','--allswitch', help='alltoall switch level', action='store_true')
    reserve.add_argument('-p','--allpair', help='alltoall pair level', action='store_true')
    reserve.add_argument('-n','--nodes', help='nodes', action='store_true')
    reserve.add_argument('-b','--bandwidth', help='bandwidth', action='store_true')

    # Showq info
    showq = subparsers.add_parser('q', help='Checks the status of running jobs.  For additional information, type bench q -v or bench q --verbose.\n')
    showq.add_argument('-v','--verbose', help='verbose', action='store_true')

    # Node information
    nodes = subparsers.add_parser('nodes', help='Checks the status of nodes.')

    # Automation
    automation = subparsers.add_parser('execute', help='An automation of the entire process.  To specify a directory, type bench execute -d <DIR_NAME>.\n')
    automation.add_argument('-d','--dir', help='directory', dest='directory')
    automation.set_defaults(directory=None)
    automation.add_argument('-r','--retest', help='retest benchmarks', action='store_true')

    # Status
    status = subparsers.add_parser('status', help='Concatentates the log file of the current directory.  To specify a directory, type bench status -d <DIR_NAME>.\n')
    status.add_argument('-d','--dir', help='directory', dest='directory')
    status.set_defaults(directory=None)

#    scaling = subparsers.add_parser('scaling', help='Add scaling studies.  To specify a directory, type bench status -d <DIR_NAME>.\n')
#    scaling.add_argument('-d','--dir', help='directory', dest='directory')
#    scaling.set_defaults(directory=None)

    return parser.parse_args(argv)

def get_directory(dir_name=None):

    directory = '/curc/admin/benchmarks/data'
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not dir_name:
        folder = datetime.date.today()
        index = 1
        while index < 100:
            folder_name = os.path.join(directory,str(folder)+"-"+str(index))
            if not os.path.exists(folder_name):
                break
            index+=1
        folder_name = os.path.join(directory,str(folder)+"-"+str(index-1))
        return folder_name
    else:
        if dir_name.startswith('/curc/admin/benchmarks/data'):
            return dir_name
        else:
            return os.path.join('/curc/admin/benchmarks/data',dir_name)

def get_new_directory():

    directory = '/curc/admin/benchmarks/data'
    if not os.path.exists(directory):
        os.makedirs(directory)

    folder = datetime.date.today()
    index = 1
    while index < 100:
        folder_name = os.path.join(directory,str(folder)+"-"+str(index))
        if not os.path.exists(folder_name):
            break
        index+=1
    folder_name = os.path.join(directory,str(folder)+"-"+str(index))
    return folder_name

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

def create_directory(directory_name):

    if os.path.exists(directory_name):
        shutil.rmtree(directory_name)

    os.makedirs(directory_name)

def driver():

    # Get the working directory
    args = get_args(sys.argv[1:])

    # Create the working directory
    directory = None
    try:
        if not args.directory and (args.command == 'create' or args.command=='execute'):
            directory = get_new_directory()
        elif args.directory:
            directory = get_directory(args.directory)
        else:
            directory = get_directory()
    except:
        directory = get_directory()

    if args.command == 'create' or args.command == 'execute':
        create_directory(directory)

    # Create the logger
    logger = get_logger(directory)

    if args.command == 'create':
        create.execute(directory, args.nodelist, args.exclude, args.reservation)


    if args.command == 'add':
        add.execute(directory, args)

    if args.command == 'submit':
        submit.execute(directory, args)

    if args.command == 'process':
        process.execute(directory, args)

    if args.command == 'reserve':
        reserve.execute(directory, args)

    # if args.command == 'l':
        #TODO: run tests on a set of nodes specified by nodelist in filename

    # if args.command == 'createCustom':
        #TODO: user specified reservation instead of PM

    if args.command == 'q':
        showq.execute(args.verbose)

    if args.command == 'execute':
        #automation.execute(directory, args.retest)
        logger.error("This function is disabled at the moment")

    if args.command == 'status':
        status.execute(directory)

#    if args.command == 'scaling':
#        scaling.execute(directory)

    if args.command == 'nodes':
        nodes.execute()
