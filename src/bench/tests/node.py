import bench.exc
import bench.util
import jinja2
import logging
import os
import pkg_resources
import re


TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'node.job'),
    keep_trailing_newline=True,
)

STREAM_P_T = r'^{0}: *([0-9\.]+) +([0-9\.]+) +([0-9\.]+) +([0-9\.]+) *$'
STREAM_COPY_P = re.compile(STREAM_P_T.format('Copy'), flags=re.MULTILINE)
STREAM_SCALE_P = re.compile(STREAM_P_T.format('Scale'), flags=re.MULTILINE)
STREAM_ADD_P = re.compile(STREAM_P_T.format('Add'), flags=re.MULTILINE)
STREAM_TRIAD_P = re.compile(STREAM_P_T.format('Triad'), flags=re.MULTILINE)


logger = logging.getLogger(__name__)


def generate(nodes, prefix, topology=None):
    if not topology:
        topology = {}
    for node in nodes:
        test_dir = os.path.join(prefix, node)
        bench.util.mkdir_p(test_dir)

        script_file = os.path.join(test_dir, '{0}.job'.format(node))
        with open(script_file, 'w') as fp:
            fp.write(TEMPLATE.render(
                job_name = 'bench-node-{0}'.format(node),
                node_name = node,
            ))

        node_list_file = os.path.join(test_dir, 'node_list')
        bench.util.write_node_list(node_list_file, [node])
    logger.info('node: add: {0}'.format(len(nodes)))


def process(nodes, prefix):
    fail_nodes = set()
    pass_nodes = set()
    for test in os.listdir(prefix):
        test_dir = os.path.join(prefix, test)
        test_nodes = set(bench.util.read_node_list(os.path.join(test_dir, 'node_list')))
        stream_out_path = os.path.join(test_dir, 'stream.out')
        try:
            with open(stream_out_path) as fp:
                stream_output = fp.read()
        except IOError as ex:
            logger.info('{0}: error nodes (unable to read {1})'.format(test, stream_out_path))
            logger.debug(ex, exc_info=True)
            continue
        try:
            stream_data = parse_stream(stream_output)
        except bench.exc.ParseError as ex:
            logger.warn('{0}: error nodes (unable to parse {1})'.format(test, stream_out_path))
            logger.debug(ex, exc_info=True)
            continue
        stream_passed = evaluate_stream(stream_data, test=test)

        try:
            linpack_out_path = os.path.join(test_dir, 'linpack.out')
            with open(linpack_out_path) as fp:
                linpack_output = fp.read()
        except IOError as ex:
            logger.info('{0}: error nodes (unable to read {1})'.format(test, linpack_out_path))
            logger.debug(ex, exc_info=True)
            continue
        try:
            linpack_data = parse_linpack(linpack_output)
        except bench.exc.ParseError as ex:
            logger.warn('{0}: error nodes (unable to parse {1})'.format(test, linpack_out_path))
            logger.debug(ex, exc_info=True)
            continue
        linpack_passed = evaluate_linpack(linpack_data, test=test)

        if stream_passed and linpack_passed:
            logger.info('{0}: pass'.format(test))
            pass_nodes |= test_nodes
        else:
            fail_nodes |= test_nodes
            if not stream_passed and not linpack_passed:
                logger.info('{0}: fail (stream, linpack)'.format(test))
            elif not stream_passed:
                logger.info('{0}: fail (stream)'.format(test))
            elif not linpack_passed:
                logger.info('{0}: fail (linpack)'.format(test))

    tested = pass_nodes | fail_nodes
    error_nodes = set(nodes) - tested

    return {
        'error_nodes': error_nodes,
        'fail_nodes': fail_nodes,
        'pass_nodes': pass_nodes,
    }


def parse_stream(output):
    copy_match = STREAM_COPY_P.search(output)
    if not copy_match:
        raise bench.exc.ParseError('stream: missing copy')
    copy = float(copy_match.group(1))

    scale_match = STREAM_SCALE_P.search(output)
    if not scale_match:
        raise bench.exc.ParseError('stream: missing scale')
    scale = float(scale_match.group(1))

    add_match = STREAM_ADD_P.search(output)
    if not add_match:
        raise bench.exc.ParseError('stream: missing add')
    add = float(add_match.group(1))

    triad_match = STREAM_TRIAD_P.search(output)
    if not triad_match:
        raise bench.exc.ParseError('stream: missing triad')
    triad = float(triad_match.group(1))

    return (copy, scale, add, triad)


def parse_linpack(output):
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
            size, lda, alignment, average, maximal = line.split()
            key = (int(size), int(lda), int(alignment))
            data[key] = float(average)
        else:
            break
    return data


def evaluate_stream(
        data,
        expected_copy = 23850.0,
        expected_scale = 36000.0,
        expected_add = 37350.0,
        expected_triad = 37800.0,
        test='unknown',
):
    copy, scale, add, triad = data

    if copy < expected_copy:
        logger.debug('stream: copy: expected {0}, found {1}'.format(
            expected_copy, copy))
        return False
    elif scale < expected_scale:
        logger.debug('stream: scale: expected {0}, found {1}'.format(
            expected_scale, scale))
        return False
    elif add < expected_add:
        logger.debug('stream: add: expected {0}, found {1}'.format(
            expected_add, add))
        return False
    elif triad < expected_triad:
        logger.debug('stream: triad: expected {0}, found {1}'.format(
            expected_triad, triad))
        return False
    else:
        return True


def evaluate_linpack(
        data,
        expected_averages = {
            (5000, 5000, 4): 94.5,
            (10000, 10000, 4): 102.6,
            (20000, 20000, 4): 108.9,
            (25000, 25000, 4): 109.8,
        },
        test='unknown',
):
    for key, expected_average in expected_averages.iteritems():
        if key not in data:
            logger.debug('linpack: {0}: {1}: expected {2}, not found'.format(
                test, key, expected_average))
            return False
        if data[key] < expected_average:
            logger.debug('linpack: {0}: {1}: expected {2}, found {3}'.format(
                test, key, expected_average, data[key]))
            return False
    else:
        return True
