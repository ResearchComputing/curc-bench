import bench.exc
import os
import subprocess


def sbatch (script, chdir=None, reservation=None, qos=None, account=None, output=None):
    command = ['sbatch']
    if reservation:
        command.extend(('--reservation', reservation))
    if qos:
        command.extend(('--qos', qos))
    if account:
        command.extend(('--account', account))
    if chdir:
        command.extend(('--chdir', chdir))
    command.append(script)
    return _run_command(command)


def scontrol (subcommand, sub_args=None, reservation=None, accounts=None, flags=None,
              starttime=None, duration=None, nodes=None, users=None):
    command = []
    if sub_args is not None:
        command = ['scontrol', subcommand, sub_args]
    else:
        command = ['scontrol', subcommand]
    if reservation is not None:
        command.append('reservation={0}'.format(reservation))
    if accounts is not None:
        command.append('accounts={0}'.format(accounts))
    if flags is not None:
        command.append('flags={0}'.format(flags))
    if starttime is not None:
        command.append('starttime={0}'.format(starttime))
    if duration is not None:
        command.append('duration={0}'.format(duration))
    if nodes is not None:
        command.append('nodes={0}'.format(nodes))
    if users is not None:
        command.append('users={0}'.format(users))
    return _run_command(command)



def _run_command (command):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as ex:
        message = 'slurm: {0}: {1}'.format(os.path.basename(command[0]), ex.strerror)
        raise bench.exc.SlurmError(message)

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        stderr_message = stderr.strip().replace(b'\n', b':')
        raise bench.exc.SlurmError(stderr_message)
    else:
        return stdout
