import bench.framework_add
import logging

class TestFramework(object):

    def __init__(self, test_name=None):
        # Todo: Make a configuration file and get topology_file from there
        # Todo: move topology file into individual tests so that different topologies may be specified
        self.test_name = test_name
        self.logger = logging.getLogger(__name__)

        #Classes for adding, submitting, processing, and reserving.
        self.Add = None
        self.Submit = None
        self.Process = None
        self.Reserve = None
