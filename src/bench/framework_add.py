import bench.tests.node
import os

class Add:

    def __init__(self, logger):
        self.logger = logger
        self.prefix = None
        self.include_states = None
        self.exclude_states = None
        self.GENERATOR = bench.tests.node.generate

    def execute(self, prefix, topology_file,
              alltoall_rack_tests=None,
              alltoall_switch_tests=None,
              alltoall_pair_tests=None,
              bandwidth_tests=None,
              node_tests=None,
              include_states=None,
              exclude_states=None,
              **kwargs
    ):
        if not (include_states or exclude_states):
          exclude_states = ['down', 'draining', 'drained']

        global_node_list = set(bench.util.read_node_list(os.path.join(prefix, 'node_list')))
        node_list = bench.util.filter_node_list(global_node_list,
                                              include_states=include_states,
                                              exclude_states=exclude_states,
                                              **kwargs)

        if topology_file is not None:
            topology = bench.infiniband.get_topology(topology_file)
        else:
            topology = {}

        if alltoall_rack_tests:
            self.add_tests(node_list, prefix, 'alltoall-rack', topology)
        if alltoall_switch_tests:
            self.add_tests(node_list, prefix, 'alltoall-switch', topology)
        if alltoall_pair_tests:
            self.add_tests(node_list, prefix, 'alltoall-pair', topology)
        if bandwidth_tests:
            self.add_tests(node_list, prefix, 'bandwidth', topology)
        if node_tests:
            self.add_tests(node_list, prefix, 'node', topology)


    def add_tests(self, node_list, prefix, key, topology=None):
      tests_prefix = os.path.join(prefix, key, 'tests')
      self.logger.info('adding {0} tests to {1}'.format(key, tests_prefix))
      bench.util.mkdir_p(tests_prefix)
      self.GENERATOR(node_list, tests_prefix, topology)
      bench.util.write_node_list(
          os.path.join(prefix, key, 'node_list'),
          node_list)
