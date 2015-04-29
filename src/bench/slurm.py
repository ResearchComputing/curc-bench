import bench.exc
import subprocess


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

    if process.returncode != 0:
        stderr_message = stderr.strip().replace('\n', ':')
        raise bench.exc.SlurmError(stderr_message)
    else:
        return stdout
