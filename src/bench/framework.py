

class TestFramework:

    def __init__(self, test_name=None, topology_file=None):
        # Todo: Make a configuration file and get topology_file from there
        self.test_name = test_name
        self.topology_file = topology_file
        if self.topology_file is None:
            topology_file

        #Classes for adding, submitting, processing, and reserving.
        self.Add = None
        self.Submit = None
        self.Process = None
        self.Reserve = None
