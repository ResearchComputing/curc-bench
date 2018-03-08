import bench.util
import bench.tests.node_test
# import bench.tests.bandwidth
# import bench.tests.alltoall
import hostlist
import logging
import os

class Process(object):

    def __init__(self, logger, parse_data, evaluate_data, test_name, subtests=None):
        self.logger = logger
        self.test_name = test_name
        self.parse_data = parse_data
        self.evaluate_data = evaluate_data
        self.subtests = subtests


    def execute(self, prefix):
        self.test_prefix = os.path.join(prefix, self.test_name)
        self.process_tests(self.test_prefix)

    def write_result_files(self, prefix, pass_nodes, fail_nodes, error_nodes):
        bench.util.write_node_list(
            os.path.join(prefix, 'pass_nodes'),
            pass_nodes,
        )

        bench.util.write_node_list(
            os.path.join(prefix, 'fail_nodes'),
            fail_nodes,
        )

        bench.util.write_node_list(
            os.path.join(prefix, 'error_nodes'),
            error_nodes,
        )

    def remove_previous_results(self, prefix):
        '''Remove old fail and error results files so that rerun tests
        with results that are now passing will be placed into the
        pass_nodes file'''

        try:
            os.remove(os.path.join(prefix, "fail_nodes"))
        except OSError:
            pass
        try:
            os.remove(os.path.join(prefix, "error_nodes"))
        except OSError:
            pass


    def process_tests (self, prefix):
        prefix_ = os.path.join(prefix, 'tests')
        if not os.path.exists(prefix_):
            self.logger.warn('{0}: not found'.format(prefix))
            return

        self.remove_previous_results(prefix)

        node_list = bench.util.read_node_list(os.path.join(prefix, 'node_list'))
        fail_nodes = set()
        pass_nodes = set()

        for test in os.listdir(prefix_):
            test_dir = os.path.join(prefix_, test)
            test_nodes = set(bench.util.read_node_list(os.path.join(test_dir, 'node_list')))

            for subtest in self.subtests:
                path = os.path.join(test_dir, subtest+'.out')
                self.process(path, test, subtest, fail_nodes, pass_nodes, test_nodes)

        tested = pass_nodes | fail_nodes
        error_nodes = set(node_list) - tested

        self.logger.info('{0}: fail nodes: {1} / {2}'.format(
            prefix, len(fail_nodes), len(node_list)))
        self.logger.info('{0}: pass nodes: {1} / {2}'.format(
            prefix, len(pass_nodes), len(node_list)))
        self.logger.info('{0}: error nodes: {1} / {2}'.format(
            prefix, len(error_nodes), len(node_list)))
        self.write_result_files(
            prefix,
            pass_nodes,
            fail_nodes,
            error_nodes,
        )

    def process(self, path, test, subtest, fail_nodes, pass_nodes, test_nodes):
        ''' Inputs
        test - directory containing test results, ex: node001, rack4
        subtest - name of subtest, curc-bench looks for a file called {subtest_name}.out
        (some tests contain multiple subtests, for example, a "node test" might run
        both stream and linpack.)
        '''
        try:
            with open(path) as fp:
                output = fp.read()
            data = self.parse_data(output, subtest)
        except IOError as ex:
            self.logger.warn('{0}: error (unable to read {1})'.format(test, path))
            self.logger.debug(ex, exc_info=True)
            return
        except bench.exc.ParseError as ex:
            self.logger.warn('{0}: error (unable to parse {1})'.format(test, path))
            self.logger.debug(ex, exc_info=True)
            return
        passed = self.evaluate_data(data, subtest, test_nodes)

        if passed:
            self.logger.info('{0}: pass'.format(test))
            if not test in fail_nodes:
                pass_nodes |= test_nodes
        else:
            pass_nodes.discard(test)
            fail_nodes |= test_nodes
            self.logger.info('{test}: fail {subtest}'.format(test=test,
                                                            subtest=subtest))
        return




        #
