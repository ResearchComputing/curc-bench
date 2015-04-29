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
    return _run_command(command)


def scontrol (subcommand, reservation=None, accounts=None, flags=None,
              starttime=None, duration=None, nodes=None):
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
    return _run_command(command)
    


def _run_command (command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        stderr_message = stderr.strip().replace('\n', ':')
        raise bench.exc.SlurmError(stderr_message)
    else:
        return stdout
