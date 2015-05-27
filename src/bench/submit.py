import bench.exc
import bench.slurm
import logging
import os
import time


logger = logging.getLogger(__name__)


def execute(
        directory,
        node_tests=None,
        bandwidth_tests=None,
        alltoall_rack_tests=None,
        alltoall_switch_tests=None,
        alltoall_pair_tests=None,
        pause=None, **kwargs):

    submit_any_tests_explicitly = (
        alltoall_rack_tests
        or alltoall_switch_tests
        or alltoall_pair_tests
        or bandwidth_tests
        or node_tests
    )

    index = 1
    if not submit_any_tests_explicitly:
        index = submit(os.path.join(directory, 'node'), index, pause, **kwargs)
        index = submit(os.path.join(directory, 'bandwidth'), index, pause, **kwargs)
        index = submit(os.path.join(directory, 'alltoall-rack'), index, pause, **kwargs)
        index = submit(os.path.join(directory, 'alltoall-switch'), index, pause, **kwargs)
        index = submit(os.path.join(directory, 'alltoall-pair'), index, pause, **kwargs)
    else:
        if alltoall_rack_tests:
            index = submit(os.path.join(directory, 'alltoall-rack'), index, pause, **kwargs)
        if alltoall_switch_tests:
            index = submit(os.path.join(directory, 'alltoall-switch'), index, pause, **kwargs)
        if alltoall_pair_tests:
            index = submit(os.path.join(directory, 'alltoall-pair'), index, pause, **kwargs)
        if bandwidth_tests:
            index = submit(os.path.join(directory, 'bandwidth'), index, pause, **kwargs)
        if node_tests:
            index = submit(os.path.join(directory, 'node'), index, pause, **kwargs)

    logger.info('submitted {0} jobs'.format(index-1))


def submit(prefix, index=0, pause=None,
           good_nodes=None, bad_nodes=None, not_tested=None,
           **kwargs
):
    tests_dir = os.path.join(prefix, 'tests')
    if not os.path.exists(tests_dir):
        return index

    if good_nodes or bad_nodes or not_tested:
        nodes = set()
        if good_nodes:
            good_nodes_file = os.path.join(prefix, 'good_nodes')
            try:
                nodes |= set(bench.util.read_node_list(good_nodes_file))
            except IOError as ex:
                logger.warn('unable to read {0}'.format(good_nodes_file))
                logger.debug(ex, exc_info=True)
        if bad_nodes:
            bad_nodes_file = os.path.join(prefix, 'bad_nodes')
            try:
                nodes |= set(bench.util.read_node_list(bad_nodes_file))
            except IOError as ex:
                logger.warn('unable to read {0}'.format(bad_nodes_file))
                logger.debug(ex, exc_info=True)
        if not_tested:
            not_tested_file = os.path.join(prefix, 'not_tested')
            try:
                nodes |= set(bench.util.read_node_list(not_tested_file))
            except IOError as ex:
                logger.warn('unable to read {0}'.format(not_tested_file))
                logger.debug(ex, exc_info=True)
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
                logger.info('pausing 10 seconds between {0} submissions'.format(pause))
                time.sleep(10)

        try:
            result = bench.slurm.sbatch(script, workdir=test_dir, **kwargs)
        except bench.exc.SlurmError as ex:
            logger.error('failed to submit job {0}'.format(script))
            logger.debug(ex, exc_info=True)
        else:
            logger.info(': '.join(result.splitlines()))
        index += 1
    return index
