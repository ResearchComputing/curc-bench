import bench.util
import jinja2
import logging
import os
import pkg_resources


logger = logging.getLogger(__name__)


# additional latency above the specified limit allowed
LATENCY_MAX_PERCENT = 55

# expected average osu_alltoall latency for each node count
LIMITS = { 2:13613.5219632,  3:28375.5187868,  4:43137.5156105,
           5:57899.5124341,  6:72661.5092577,  7:87423.5060814,
           8:102185.502905,  9:116947.499729,  10:131709.496552,
           11:146471.493376, 12:161233.4902,   13:175995.487023,
           14:190757.483847, 15:205519.480671, 16:220281.477494,
           17:235043.474318, 18:249805.471141, 19:264567.467965,
           20:279329.464789, 21:294091.461612, 22:308853.458436,
           23:323615.45526,  24:338377.452083, 25:353139.448907,
           26:367901.445731, 27:382663.442554, 28:397425.439378,
           29:412187.436202, 30:426949.433025, 31:441711.429849,
           32:456473.426672, 33:471235.423496, 34:753806.42032,
           35:753806.417143, 36:753806.413967, 37:753806.410791,
           38:753806.407614, 39:753806.404438, 40:753806.401262,
           50:456062.014488, 51:522754.035136, 52:589446.055784,
           53:656138.076432, 54:722830.09708,  55:789522.117728,
           56:856214.138376, 57:922906.159024, 58:989598.179672,
           59:1056290.20032, 60:1122982.22097, 61:1189674.24162,
           62:1256366.26226, 63:1323058.28291, 64:1389750.30356,
           65:1456442.32421, 66:1523134.34486, 67:1589826.3655,
           68:1656518.38615, 69:1723210.4068,  70:1789902.42745,
           71:1856594.4481,  72:1923286.46874, 73:1989978.48939,
           74:2056670.51004, 75:2123362.53069, 76:2190054.55134,
           77:2256746.57198, 78:2323438.59263, 79:2390130.61328,
           80:2456822.63393, }

TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'alltoall.job'),
    keep_trailing_newline=True,
)


def generate_alltoall_rack(nodes, prefix):
    rack_nodes = bench.util.infiniband.get_rack_nodes(nodes)
    for rack_name, rack_nodes in rack_nodes.iteritems():
        if rack_nodes:
            test_dir = os.path.join(prefix, rack_name)
            render(test_dir, rack_nodes, rack_name)


def generate_alltoall_switch(nodes, topology, prefix):
    switch_nodes = bench.util.infiniband.get_switch_nodes(nodes, topology)
    for switch_name, switch_nodes in switch_nodes.iteritems():
        if switch_nodes:
            test_dir = os.path.join(prefix, switch_name)
            render(test_dir, switch_nodes, switch_name)


def generate_alltoall_pair(nodes, topology, prefix):
    node_pairs = bench.util.infiniband.get_switch_node_pairs(nodes, topology)
    for pair_name, name_list in node_pairs.iteritems():
        if name_list:
            test_dir = os.path.join(prefix, pair_name)
            render(test_dir, name_list, pair_name)


def render(prefix, nodes, node_list_name):
    bench.util.mkdir_p(prefix)
    script_file = os.path.join(prefix, '{0}.job'.format(node_list_name))
    with open(script_file, 'w') as fp:
        fp.write(TEMPLATE.render(
            job_name = 'bench-alltoall-{0}'.format(node_list_name),
            nodes = list(sorted(nodes)),
        ))

    node_list_file = os.path.join(prefix, 'node_list')
    bench.util.write_node_list(node_list_file, nodes)


def process(nodes, prefix):
    bad_nodes = set()
    good_nodes = set()
    for test in os.listdir(prefix):
        test_dir = os.path.join(prefix, test)
        test_nodes = set(bench.util.read_node_list(os.path.join(test_dir, 'node_list')))
        osu_alltoall_out_path = os.path.join(test_dir, 'osu_alltoall.out')
        try:
            with open(osu_alltoall_out_path) as fp:
                data = parse_osu_alltoall(fp.read())
        except IOError as ex:
            logger.info('unable to read {0}'.format(osu_alltoall_out_path))
            logger.debug(ex, exc_info=True)
            continue
        if evaluate_osu_alltoall(data, len(test_nodes)):
            logger.info('{0}: pass'.format(test))
            good_nodes |= test_nodes
        else:
            logger.info('{0}: fail (osu_alltoall)'.format(test))
            bad_nodes |= test_nodes

    tested = good_nodes | bad_nodes
    not_tested = set(nodes) - tested

    return {
        'not_tested': not_tested,
        'bad_nodes': bad_nodes,
        'good_nodes': good_nodes,
    }


def parse_osu_alltoall(output):
    for line in output.splitlines():
        if not line or line.startswith('#'):
            continue

        size, average, min_, max_, iterations = line.split()
        size = int(size)
        average = float(average)
        min_ = float(min_)
        max_ = float(max_)
        iterations = int(iterations)

        yield size, average, min_, max_, iterations


def evaluate_osu_alltoall (data, num_nodes):
    data = list(data)
    average_latency = 1.0 * sum(datum[1] for datum in data) / len(data)
    expected_average_latency = LIMITS[num_nodes]
    logger.debug('expected: {0} measured: {1}'.format(
        expected_average_latency,
        average_latency,
    ))

    percent_worse = (
        100 * (average_latency - expected_average_latency)
        / expected_average_latency
    )

    return percent_worse < LATENCY_MAX_PERCENT
