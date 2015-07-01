import bench.util
import hostlist
import logging
import os


logger = logging.getLogger(__name__)


def execute(directory, include_states=None, exclude_states=None, **kwargs):
    if not (include_states or exclude_states):
        exclude_states = ['down', 'draining', 'drained']

    node_list_filename = os.path.join(directory, 'node_list')
    logger.info('creating {0}'.format(node_list_filename))

    all_nodes = bench.util.get_nodes()
    node_list = bench.util.filter_node_list(all_nodes,
                                            include_states=include_states,
                                            exclude_states=exclude_states,
                                            **kwargs)
    logger.info('nodes to test: {0}'.format(len(node_list)))

    try:
        bench.util.write_node_list(node_list_filename, sorted(node_list))
    except IOError, ex:
        logger.error('unable to write {0}'.format(node_list_filename))
        logger.debug(ex, exc_info=True)

    not_tested_filename = os.path.join(directory, 'not_tested')
    not_tested_nodes = all_nodes - node_list
    if not_tested_nodes:
        logger.warn('not tested: {0} ({1} nodes)'.format(
            hostlist.collect_hostlist(not_tested_nodes),
            len(not_tested_nodes),
        ))
    try:
        bench.util.write_node_list(not_tested_filename, sorted(not_tested_nodes))
    except IOError, ex:
        logger.error('unable to write {0}'.format(not_tested_filename))
        logger.debug(ex, exc_info=True)
