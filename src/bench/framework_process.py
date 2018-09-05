import bench.log
import bench.util
import datetime
import hostlist
import logging
import os
import tabulate

class Process(object):

    def __init__(self, logger, parse_data, evaluate_data, test_name, subtests=None):
        self.logger = logger
        self.test_name = test_name
        self.parse_data = parse_data
        self.evaluate_data = evaluate_data
        self.subtests = subtests
        self.node_list = None

        # Storing pass, fail, and error tests/nodes
        self.results = {}
        self.results['p_tests'] = set()
        self.results['p_nodes'] = set()
        self.results['f_tests'] = set()
        self.results['f_nodes'] = set()
        self.results['e_tests'] = set()
        self.results['e_nodes'] = set()

        # Additional dicts for displaying data
        self.results['fail'] = {}
        self.results['error'] = {}
        self.results['error']['not_found'] = set()
        self.results['error']['not_parsable'] = set()


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
        self.node_list = bench.util.read_node_list(os.path.join(prefix, 'node_list'))

        for test in os.listdir(prefix_):
            test_dir = os.path.join(prefix_, test)
            test_nodes = set(bench.util.read_node_list(os.path.join(test_dir, 'node_list')))

            for subtest in self.subtests:
                path = os.path.join(test_dir, subtest+'.out')
                self.process(path, test, subtest, self.results['f_nodes'], self.results['p_nodes'], test_nodes)

        tested = self.results['p_nodes'] | self.results['f_nodes']
        self.results['e_nodes'] = set(self.node_list) - tested

        #Write summary to file
        self.write_result_files(
            prefix,
            self.results['p_nodes'],
            self.results['f_nodes'],
            self.results['e_nodes'],
        )

        #Show user fail and error tables
        #log results tables, including passing results to file
        self.display_results()


    def process(self, path, test, subtest, fail_nodes, pass_nodes, test_nodes):
        ''' Inputs
        test - directory containing test results, ex: node001, rack4
        subtest - name of subtest, curc-bench looks for a file called {subtest_name}.out
        (some tests contain multiple subtests, for example, a "node test" might run
        both stream and linpack.)
        '''

        parsed_data = None
        passed = False
        data = None # Data for display in table

        try:
            with open(path) as fp:
                output = fp.read()
                parsed_data = self.parse_data(output, subtest)
                passed, data = self.evaluate_data(parsed_data, subtest, test_nodes)
        except IOError as ex:
            self.logger.debug(ex, exc_info=True)
            for ii in test.split(','):
                self.results['error']['not_found'].add(ii)
            self.update_sets(test, option='add_error', reason='not_found')
            return
        except (ValueError, bench.exc.ParseError) as ex:
            self.logger.debug(ex, exc_info=True)
            for ii in test.split(','):
                self.results['error']['not_parsable'].add(ii)
            self.update_sets(test, option='add_error', reason='not_parsable')
            return

        if passed:
            self.update_sets(test, option='add_pass')
        else:
            self.update_sets(test, option='add_fail')

            #results['fail'][HARDWARE] = ['Test', 'Result', 'Expected', 'Res/Exp']]
            self.results['fail'][hostlist.collect_hostlist(test_nodes)] = [data]


        return

    def display_results(self):
        error_table = []
        fail_table = []
        # for key, result in self.results['fail'].items():
        for key, result in list(self.results['fail'].items()):
            if result == []:
                self.results['fail'].pop(key, None)
                self.results['f_tests'].remove(key)
                for ii in key.split(','):
                    self.results['error']['not_parsable'].add(ii)
                continue
            fail_table.append([key] + result)

        # for key, result in self.results['error'].items():
        for key, result in list(self.results['error'].items()):
            if result:
                error_table.append([hostlist.collect_hostlist(result), key])

        self.log_results(fail_table, error_table)

        #print("FAIL TABLE :", fail_table)


        #Summary
        print("### Summary ###")
        print('passing nodes: {passed} / {total}'.format(passed=len(self.results['p_nodes']), total=len(self.node_list)))
        print('failing nodes: {passed} / {total}'.format(passed=len(self.results['f_nodes']), total=len(self.node_list)))
        print('error nodes: {passed} / {total}'.format(passed=len(self.results['e_nodes']), total=len(self.node_list)))

        if self.results['p_tests']:
            self.results_logger.info("\n### Passing Tests ###")
            self.results_logger.info(sorted(list(self.results['p_tests'])))

        if fail_table:
            print("\n### Failing Tests ###")
            print(tabulate.tabulate(fail_table, headers=['Hardware', 'Test', 'Result', 'Expected', 'Res/Exp'], floatfmt=".2f"))

        if error_table:
            print("\n### Missing/Error Tests ###")
            print(tabulate.tabulate(error_table, headers=['Hardware', 'Reason']))


    def log_results(self, fail_table, error_table):

        # Print results to results log
        self.results_logger.info("\n######## Summary - {test} - {time} ########".format(
            test=self.test_name, time=datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")))
        self.results_logger.info('passing nodes: {passed} / {total}'.format(passed=len(self.results['p_nodes']), total=len(self.node_list)))
        self.results_logger.info('failing nodes: {passed} / {total}'.format(passed=len(self.results['f_nodes']), total=len(self.node_list)))
        self.results_logger.info('error nodes: {passed} / {total}'.format(passed=len(self.results['e_nodes']), total=len(self.node_list)))

        self.results_logger.info("\n### Failing Tests ###")
        self.results_logger.info(tabulate.tabulate(fail_table, headers=['Hardware', 'Test', 'Result', 'Expected', 'Res/Exp'], floatfmt=".2f"))

        self.results_logger.info("\n### Missing/Error Tests ###")
        self.results_logger.info(tabulate.tabulate(error_table, headers=['Hardware', 'Reason']))

    def update_sets(self, test, option=None, reason=None):
        '''Updates all sets when a change is needed'''

        if option == 'add_pass':
            if test not in self.results['f_tests']:
                for ii in test.split(','):
                    self.results['p_nodes'].add(ii)
                    self.results['f_nodes'].discard(ii)
                    self.results['e_nodes'].discard(ii)
                self.results['p_tests'].add(test)
                self.results['f_tests'].discard(test)
                self.results['e_tests'].discard(test)
        elif option == 'add_fail':
            for ii in test.split(','):
                self.results['f_nodes'].add(ii)
                self.results['p_nodes'].discard(ii)
                self.results['e_nodes'].discard(ii)
            self.results['f_tests'].add(test)
            self.results['p_tests'].discard(test)
            self.results['e_tests'].discard(test)
        elif option == 'add_error':
            for ii in test.split(','):
                self.results['e_nodes'].add(ii)
                self.results['p_nodes'].discard(ii)
                self.results['f_nodes'].discard(ii)
            self.results['e_tests'].add(test)
            self.results['p_tests'].discard(test)
            self.results['f_tests'].discard(test)


        #
