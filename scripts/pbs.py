
import string
from subprocess import check_output
import datetime
from xml2obj import xml2obj
from hostlist import expand_hostlist

def listPBSnodes(hostExpression):
    """ Create a list of nodes that are free to run jobs

    Example: freePBSnodes('node01[05-11],node02[01-80]')
    """

    nodeNames = expand_hostlist(hostExpression)
    nodeString = "".join(["%s " % n for n in nodeNames])
    pbsOut = check_output(["pbsnodes -x %s" % nodeString] , shell=True)
    nodes = xml2obj(pbsOut)

    freenodelist = []

    # find free nodes
    # state = free
    # no jobs are runing
    # no message
    for node in nodes["Node"]:
        status = {}
        messages = []
        jobs = []
        name = node["name"]
        state = node["state"]
        freenodelist.append(name)
        
    return freenodelist


def freePBSnodes(hostExpression):
    """ Create a list of nodes that are free to run jobs

    Example: freePBSnodes('node01[05-11],node02[01-80]')
    """

    nodeNames = expand_hostlist(hostExpression)
    nodeString = "".join(["%s " % n for n in nodeNames])
    pbsOut = check_output(["pbsnodes -x %s" % nodeString] , shell=True)
    nodes = xml2obj(pbsOut)

    freenodelist = []

    # find free nodes
    # state = free
    # no jobs are runing
    # no message
    for node in nodes["Node"]:
        status = {}
        messages = []
        jobs = []
        name = node["name"]
        state = node["state"]
        if state == "free":
            
            if node["jobs"]:
                # node has a job running
                jobs = node["jobs"].split(", ")
                continue
            if "status" in node:
                for item in node["status"].split(","):
                    (S, value) = item.split("=")
                    status[S] = value
                if status.has_key("message"):
                    continue
            #print "%s free" % name        
            freenodelist.append(name)
        
    return freenodelist

if __name__ == '__main__':
    import os, sys
    r = freePBSnodes("node10[01-80],node16[01-80]")
    print r
    


