import bench.framework
import bench.framework_add
import bench.framework_submit
import bench.framework_process
import bench.framework_reserve
import bench.exc
import bench.util
import bench.conf.node_conf as bnc
import jinja2
import logging
import os
import pkg_resources
import re
import collections
import hostlist



class NodeTest(bench.framework.TestFramework):

    def __init__(self, test_name):
        bench.framework.TestFramework.__init__(self, test_name)

        self.subtests = ['stream', 'linpack']

        self.Add = bench.framework_add.Add(self.logger, self.generate, test_name, bnc.config['nodes'])
        self.Submit = bench.framework_submit.Submit(self.logger, test_name)
        self.Process = bench.framework_process.Process(self.logger, self.parse_data, self.evaluate_data, test_name, self.subtests)
        self.Reserve = bench.framework_reserve.Reserve(self.logger, test_name)

        self.TEMPLATE = jinja2.Template(
            pkg_resources.resource_string(__name__, 'node.job').decode('utf-8'),
            keep_trailing_newline=True,
        )

        self.STREAM_P_T = r'^{0}: *([0-9\.]+) +([0-9\.]+) +([0-9\.]+) +([0-9\.]+) *$'
        self.STREAM_COPY_P = re.compile(self.STREAM_P_T.format('Copy'), flags=re.MULTILINE)
        self.STREAM_SCALE_P = re.compile(self.STREAM_P_T.format('Scale'), flags=re.MULTILINE)
        self.STREAM_ADD_P = re.compile(self.STREAM_P_T.format('Add'), flags=re.MULTILINE)
        self.STREAM_TRIAD_P = re.compile(self.STREAM_P_T.format('Triad'), flags=re.MULTILINE)


    def generate(self, nodes, prefix, topology=None, test_name=None):

        if topology:
            self.logger.info('node: ignoring topology (not used)')

        node_set = collections.defaultdict(set)
        node_set = set(hostlist.expand_hostlist(bnc.config['nodes']))
        node_set &= set(nodes) #Don't include error/excluded nodes

        for node in node_set:
            test_dir = os.path.join(prefix, "tests", node)
            bench.util.mkdir_p(test_dir)

            script_file = os.path.join(test_dir, '{0}.job'.format(node))
            with open(script_file, 'w') as fp:
                fp.write(self.TEMPLATE.render(
                    job_name = 'bench-node-{0}'.format(node),
                    modules = " ".join(bnc.config['modules']),
                    node_name = node,
                    linpack_path = bnc.config['linpack_path'],
                    stream_path = bnc.config['stream_path'],
                ))

            node_list_file = os.path.join(test_dir, 'node_list')
            bench.util.write_node_list(node_list_file, [node])
        self.logger.info('node: add: {0}'.format(len(nodes)))

    def parse_data(self, output, subtest):
        if subtest == 'stream':
            copy_match = self.STREAM_COPY_P.search(output)
            if not copy_match:
                raise bench.exc.ParseError('stream: missing copy')
            copy = float(copy_match.group(1))

            scale_match = self.STREAM_SCALE_P.search(output)
            if not scale_match:
                raise bench.exc.ParseError('stream: missing scale')
            scale = float(scale_match.group(1))

            add_match = self.STREAM_ADD_P.search(output)
            if not add_match:
                raise bench.exc.ParseError('stream: missing add')
            add = float(add_match.group(1))

            triad_match = self.STREAM_TRIAD_P.search(output)
            if not triad_match:
                raise bench.exc.ParseError('stream: missing triad')
            triad = float(triad_match.group(1))

            return (copy, scale, add, triad)


        elif subtest == 'linpack':
            output = output.splitlines()

            # Find the start of the performance summary
            for i, line in enumerate(output):
                if line.startswith('Performance Summary'):
                    performance_summary = i
                    break
            else:
                raise bench.exc.ParseError('linpack: missing performance summary')

            # Find the performance summary header
            for i, line in enumerate(output[performance_summary+1:]):
                if line.startswith('Size'):
                    header = performance_summary + i + 1
                    break
            else:
                raise bench.exc.ParseError('linpack: missing performance summary header')

            data = {}
            for line in output[header+1:]:
                if line:
                    try:
                        size, lda, alignment, average, maximal = line.split()
                        key = (int(size), int(lda), int(alignment))
                        data[key] = float(average)
                    except:
                        raise bench.exc.ParseError('Unable to parse line')
                else:
                    break
            return data


    def evaluate_data(self, data, subtest, *args):
        passed = True
        results = []
        if subtest == 'stream':
            expected_copy = bnc.config['stream_copy']
            expected_scale = bnc.config['stream_scale']
            expected_add = bnc.config['stream_add']
            expected_triad = bnc.config['stream_triad']
            copy, scale, add, triad = data

            if copy < expected_copy:
                #self.logger.debug('stream: copy: expected {0}, found {1} ({2:.0%})'.format(
                #    expected_copy, copy, copy / expected_copy))
                return False, ['copy', copy, expected_copy, copy / expected_copy]
            elif scale < expected_scale:
                #self.logger.debug('stream: scale: expected {0}, found {1} ({2:.0%})'.format(
                #    expected_scale, scale, scale / expected_scale))
                return False, ['scale', scale, expected_scale, scale / expected_scale]
            elif add < expected_add:
                #self.logger.debug('stream: add: expected {0}, found {1} ({2:.0%})'.format(
                #    expected_add, add, add / expected_add))
                return False, ['add', add, expected_add, add / expected_add]
            elif triad < expected_triad:
                #self.logger.debug('stream: triad: expected {0}, found {1} ({2:.0%})'.format(
                #    expected_triad, triad, triad / expected_triad))
                return False, ['triad', triad, expected_triad, triad / expected_triad]
            else:
                return True, []

            return [passed, results]

        elif subtest == 'linpack':
            expected_averages = bnc.config['linpack_averages']

            for key, expected_average in expected_averages.items():
                if key not in data:
                    self.logger.debug('linpack: {0}: {1}: expected {2}, not found'.format(
                        subtest, key, expected_average))
                    return False, []
                if data[key] < expected_average:
                    self.logger.debug('linpack: {0}: {1}: expected {2}, found {3} ({4:.0%})'.format(
                        subtest, key, expected_average, data[key], data[key] / expected_average))
                    return False, [[subtest, key], data[key], expected_average, data[key]/expected_average]
            else:
                return True, []





#
