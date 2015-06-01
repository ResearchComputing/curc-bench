
import bench.infiniband
import bench.util
import jinja2
import logging
import os
import pkg_resources


TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'bandwidth.job'),
    keep_trailing_newline=True,
)


logger = logging.getLogger(__name__)


def generate(nodes, topology, prefix):
    node_pairs = bench.infiniband.get_switch_node_pairs(nodes, topology)
    for pair_name, node_pair in node_pairs.iteritems():
        test_dir = os.path.join(prefix, pair_name)
        bench.util.mkdir_p(test_dir)
        script = os.path.join(test_dir, '{0}.job'.format(pair_name))
        with open(script, 'w') as fp:
            fp.write(TEMPLATE.render(
                job_name = 'bench-bandwidth-{0}'.format(pair_name),
                nodes = node_pair,
            ))
        bench.util.write_node_list(os.path.join(test_dir, 'node_list'), node_pair)
    logger.info('bandwidth: add: {0}'.format(len(node_pairs)))


def process(nodes, prefix):
    bad_nodes = set()
    good_nodes = set()
    for test in os.listdir(prefix):
        test_dir = os.path.join(prefix, test)
        test_nodes = set(bench.util.read_node_list(os.path.join(test_dir, 'node_list')))
        
        osu_bw_out_path = os.path.join(test_dir, 'osu_bw.out')
        try:
            with open(osu_bw_out_path) as fp:
                try:
                    data = parse_osu_bw(fp)
                except ValueError as ex:
                    logger.info('{0}: fail (malformed osu_bw)'.format(test))
                    logger.debug(ex, exc_info=True)
                    bad_nodes |= test_nodes
                    continue
        except IOError as ex:
            logger.info('{0}: not tested (unable to read {1})'.format(test, osu_bw_out_path))
            logger.debug(ex, exc_info=True)
            continue
        if evaluate_osu_bw(data, test=test):
            logger.info('{0}: pass'.format(test))
            good_nodes |= test_nodes
        else:
            logger.info('{0}: fail (osu_bw)'.format(test))
            bad_nodes |= test_nodes

    tested = good_nodes | bad_nodes
    not_tested = set(nodes) - tested

    return {
        'not_tested': not_tested,
        'bad_nodes': bad_nodes,
        'good_nodes': good_nodes,
    }


def parse_osu_bw(output):
    data = {}
    for line in output:
        if line.startswith('#'):
            continue
        size, bandwidth = line.strip().split()
        size = int(size)
        bandwidth = float(bandwidth)
        data[size] = bandwidth
    return data


def evaluate_osu_bw(
        data,
        expected_bandwidths = {
            4194304: 2720.0,
            1048576: 2720.0,
            262144: 2720.0,
            65536: 2720.0,
        },
        test='unknown',
):
    for size, bandwidth in expected_bandwidths.iteritems():
        if size not in data:
            logger.debug('bandwidth: {0}: {1}: expected {2}, not found'.format(
                test, size, expected_bandwidths[size]))
            return False
        if data[size] < expected_bandwidths[size]:
            logger.debug('bandwidth: {0}: {1}: expected {2}, found {3}'.format(
                test, size, expected_bandwidths[size], data[size]))
            return False
    return True
