import bench
import bench.configuration as bc
import os
import hostlist

class Add(object):

    def __init__(self, logger, generate, test_name):
        self.logger = logger
        self.add_tests = generate
        self.test_name = test_name
        self.prefix = None
        self.include_states = None
        self.exclude_states = None

    def execute(self, prefix,
              include_states=None,
              exclude_states=None,
              **kwargs
    ):
        if not (include_states or exclude_states):
          exclude_states = ['down', 'draining', 'drained']

        test_node_list = set(hostlist.expand_hostlist(bc.config[self.test_name]["nodes"]))
        node_list = bench.util.filter_node_list(test_node_list,
                                              include_states=include_states,
                                              exclude_states=exclude_states,
                                              **kwargs)

        #make the test directory and write the node list to it
        self.test_prefix = os.path.join(prefix, self.test_name)
        bench.util.mkdir_p(os.path.join(self.test_prefix))
        bench.util.write_node_list(
            os.path.join(self.test_prefix, 'node_list'),
            node_list)

        self.add_tests(node_list, self.test_prefix)
