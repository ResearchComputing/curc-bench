import bench.exc
import logging
import os
import subprocess
import time


if not hasattr(subprocess, 'check_output'):
    import bench.util
    bench.util.patch_subprocess_check_output()


logger = logging.getLogger('Benchmarks')


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

    logger.info('{0} jobs'.format(index-1))


def submit(prefix, index, pause, **kwargs):
    for test_basename in os.listdir(prefix):
        test_dir = os.path.join(prefix, test_basename)
        script = os.path.join(test_dir, '{0}.job'.format(test_basename))
        if pause:
            if index % pause == 0:
                logger.info('waiting 10 seconds...')
                time.sleep(10)
        try:
            sbatch(script, workdir=test_dir, **kwargs)
        except Exception as ex:
            logger.error('Cannot submit job {0}: {1}'.format(script, ex))
        index += 1
    return index


def sbatch (script, workdir=None, reservation=None, qos=None, account=None, output=None):
    command = ['sbatch']
    if reservation:
        command.extend(('--reservation', reservation))
    if qos:
        command.extend(('--qos', qos))
    if account:
        command.extend(('--account', account))
    if workdir:
        command.extend(('--workdir', workdir))
    command.append(script)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout_message = stdout.strip().replace('\n', ':')

    if stdout_message:
        logger.info(stdout_message)

    if process.returncode != 0:
        stderr_message = stderr.strip().replace('\n', ':')
        raise bench.exc.SlurmError(stderr_message)
