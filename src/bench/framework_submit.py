import bench
import os
import hostlist

class Submit(object):

    def __init__(self, logger, test_name):
        self.logger = logger
        self.test_name = test_name
        self.nodelist = None
        self.prefix = None
        self.pause = None
        self.reservation = None
        self.qos = None
        self.account = None
        self.pass_nodes = None
        self.fail_nodes = None
        self.error_nodes = None


    def execute(self, directory, pause=None, nodelist=None, **kwargs):
        if nodelist:
            self.nodelist = hostlist.expand_hostlist(nodelist)
        prefix = os.path.join(directory, self.test_name)
        self.submit(prefix=prefix, **kwargs)
        self.logger.info('submitted {0} jobs'.format(self.test_name))

    def submit(self, prefix, index=0, pause=None,
               pass_nodes=None, fail_nodes=None, error_nodes=None,
               **kwargs
    ):
        tests_dir = os.path.join(prefix, 'tests')
        if not os.path.exists(tests_dir):
            return index

        if pass_nodes or fail_nodes or error_nodes:
            nodes = set()
            if pass_nodes:
                pass_nodes_file = os.path.join(prefix, 'pass_nodes')
                try:
                    nodes |= set(bench.util.read_node_list(pass_nodes_file))
                except IOError as ex:
                    self.logger.warn('unable to read {0}'.format(pass_nodes_file))
                    self.logger.debug(ex, exc_info=True)
            if fail_nodes:
                fail_nodes_file = os.path.join(prefix, 'fail_nodes')
                try:
                    nodes |= set(bench.util.read_node_list(fail_nodes_file))
                except IOError as ex:
                    self.logger.warn('unable to read {0}'.format(fail_nodes_file))
                    self.logger.debug(ex, exc_info=True)
            if error_nodes:
                error_nodes_file = os.path.join(prefix, 'error_nodes')
                try:
                    nodes |= set(bench.util.read_node_list(error_nodes_file))
                except IOError as ex:
                    self.logger.warn('unable to read {0}'.format(error_nodes_file))
                    self.logger.debug(ex, exc_info=True)
        else:
            nodes = None

        for test_basename in os.listdir(tests_dir):
            test_dir = os.path.join(tests_dir, test_basename)
            if nodes is not None:
                test_nodes = set(bench.util.read_node_list(
                    os.path.join(test_dir, 'node_list')))
                if not nodes & test_nodes:
                    continue
            script = os.path.join(test_dir, '{0}.job'.format(test_basename))
            if not os.path.exists(script):
                continue

            if pause:
                if index % pause == 0:
                    self.logger.info('pausing 10 seconds between {0} submissions'.format(pause))
                    time.sleep(10)

            # Only submit jobs where all nodes are in --nodelist
            if self.nodelist:
                test_nodes = set(bench.util.read_node_list(os.path.join(test_dir, 'node_list')))
                if not test_nodes.issubset(self.nodelist):
                    continue

            try:
                result = bench.slurm.sbatch(script, workdir=test_dir, **kwargs)
            except bench.exc.SlurmError as ex:
                self.logger.error('failed to submit job {0} ({1})'.format(script, ex))
                self.logger.debug(ex, exc_info=True)
            else:
                self.logger.info(': '.join(result.splitlines()))
            index += 1
        return index
