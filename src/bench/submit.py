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
        index = submit(os.path.join(directory, 'node', 'tests'), index, pause, **kwargs)
        index = submit(os.path.join(directory, 'bandwidth', 'tests'), index, pause, **kwargs)
        index = submit(os.path.join(directory, 'alltoall-rack', 'tests'), index, pause, **kwargs)
        index = submit(os.path.join(directory, 'alltoall-switch', 'tests'), index, pause, **kwargs)
        index = submit(os.path.join(directory, 'alltoall-pair', 'tests'), index, pause, **kwargs)
    else:
        if alltoall_rack_tests:
            index = submit(os.path.join(directory, 'alltoall-rack', 'tests'), index, pause, **kwargs)
        if alltoall_switch_tests:
            index = submit(os.path.join(directory, 'alltoall-switch', 'tests'), index, pause, **kwargs)
        if alltoall_pair_tests:
            index = submit(os.path.join(directory, 'alltoall-pair', 'tests'), index, pause, **kwargs)
        if bandwidth_tests:
            index = submit(os.path.join(directory, 'bandwidth', 'tests'), index, pause, **kwargs)
        if node_tests:
            index = submit(os.path.join(directory, 'node', 'tests'), index, pause, **kwargs)

    logger.info('submitted {0} jobs'.format(index-1))


def submit(prefix, index, pause, **kwargs):
    for test_basename in os.listdir(prefix):
        test_dir = os.path.join(prefix, test_basename)
        script = os.path.join(test_dir, '{0}.job'.format(test_basename))
        if pause:
            if index % pause == 0:
                logger.info('pausing 10 seconds between {0} submissions'.format(pause))
                time.sleep(10)
        try:
            bench.slurm.sbatch(script, workdir=test_dir, **kwargs)
        except bench.exc.SlurmError as ex:
            logger.error('failed to submit job {0}'.format(script))
            logger.debug(ex, exc_info=True)
        index += 1
    return index
