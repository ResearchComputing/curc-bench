import argparse
import os
import datetime
import sys
import subprocess

from hostlist import expand_hostlist
import bench.util

def get_args(argv):

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help=None, dest='command')

    # Create
    add = subparsers.add_parser('add', help='add nodes to reservation\n')
    sub = subparsers.add_parser('sub', help='sub nodes to reservation\n')
    newres = subparsers.add_parser('new', help='create a new reservation\n')

    parser.add_argument('-l','--nodelist', help='e.g. --nodelist=node[01][01-80], \
                                                 node[00][01-04],node[02][01-08],node0773 \
                                                 or --nodelist file, where file is a list of nodes')

    parser.add_argument('-r','--reservation', help='name of reservation')

    return parser.parse_args(argv)

def reservation():

    # Get the working directory
    args = get_args(sys.argv[1:])

    print args
    node_list = None
    if os.path.exists(args.nodelist):
        node_list = bench.util.read_node_list(args.nodelist)
    else:
        node_list = expand_hostlist(args.nodelist)

    if node_list is not None:
        node_string = "".join(["%s," % n for n in node_list])
        os.environ['NODE_LIST'] = node_string[:-1]

    cmd = None
    if args.command == 'add':
        cmd = "mrsvctl -m hostexp+=$NODE_LIST " + args.reservation
        #cmd_out = subprocess.check_output([cmd] , shell=True)

    elif args.command == 'sub':
        cmd = "mrsvctl -m hostexp-=$NODE_LIST " + args.reservation
        #cmd_out = subprocess.check_output([cmd] , shell=True)
    elif args.command == 'new':
        cmd = "mrsvctl -c -h $NODE_LIST -n " + args.reservation

    print cmd
    cmd_out = subprocess.check_output([cmd] , shell=True)
    # # Create the working directory
    # directory = None
    # try:
    #     if not args.directory and (args.command == 'create' or args.command=='execute'):
    #         directory = get_new_directory()
    #     elif args.directory:
    #         directory = get_directory(args.directory)
    #     else:
    #         directory = get_directory()
    # except:
    #     directory = get_directory()

    # if args.command == 'create' or args.command == 'execute':
    #     create_directory(directory)

    # # Create the logger
    # logger = get_logger(directory)

    # if args.command == 'create':
    #     create.execute(directory, args.retest, args.nodelist, args.exclude)

    # if args.command == 'add':
    #     add.execute(directory, args.hpl, args.alltoall, args.bandwidth, args.nodes)

    # if args.command == 'submit':
    #     submit.execute(directory, args.hpl, args.alltoall, args.bandwidth, args.nodes)

    # if args.command == 'process':
    #     process.execute(directory, args.hpl, args.alltoall, args.bandwidth, args.nodes)

    # if args.command == 'reserve':
    #     reserve.execute(directory, args.hpl, args.alltoall, args.bandwidth, args.nodes)

    # if args.command == 'q':
    #     showq.execute(args.verbose)

    # if args.command == 'execute':
    #     #automation.execute(directory, args.retest)
    #     logger.error("This function is disabled at the moment")

    # if args.command == 'status':
    #     status.execute(directory)

    # if args.command == 'scaling':
    #     scaling.execute(directory)

    # if args.command == 'nodes':
    #     nodes.execute()
