import bench.util.infiniband
import bench.util
import jinja2
import logging
import os
import pkg_resources


OSU_BW_PERCENT = 20

OSU_BW_LIMITS = {
    4194304: 3400,
    1048576: 3400,
    262144: 3400,
    65536: 3400,
}

TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'bandwidth.job'),
    keep_trailing_newline=True,
)


logger = logging.getLogger(__name__)


def generate(nodes, topology, prefix):
    node_pairs = bench.util.infiniband.get_switch_node_pairs(nodes, topology)
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


def process(nodes, prefix):
    bad_nodes = set()
    good_nodes = set()
    for test in os.listdir(prefix):
        test_dir = os.path.join(prefix, test)
        test_nodes = set(bench.util.read_node_list(os.path.join(test_dir, 'node_list')))
        try:
            osu_bw_out_path = os.path.join(test_dir, 'osu_bw.out')
            with open(osu_bw_out_path) as fp:
                data = parse_osu_bw(fp)
        except IOError as ex:
            logger.info('unable to read {0}'.format(osu_bw_out_path))
            logger.debug(ex, exc_info=True)
            continue
        if evaluate_osu_bw(data):
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


def evaluate_osu_bw(data):
    for size, bandwidth in OSU_BW_LIMITS.iteritems():
        threshold = bandwidth - (OSU_BW_PERCENT * bandwidth)
        if size not in data or data[size] < threshold:
            return False
    return True
