import bench.conf.general as bc
import bench.exc
import bench.slurm
import bench.util
import os
import time

class Reserve(object):

    def __init__(self, logger, test_name, fail_nodes=None, error_nodes=None, reservation_name=None,
                    account=None, users=None):
        self.logger = logger
        self.test_name = test_name
        self.fail_nodes = fail_nodes
        self.error_nodes = error_nodes
        self.reservation_name = reservation_name

        #Defaults vs passed in
        self.account = bc.config['reserve']['account']
        self.users = ",".join(bc.config['reserve']['users'])
        if account:
            self.account = account
        if users:
            self.users = users



    def execute(self, prefix):
        if not self.reservation_name:
            self.reservation_name = 'bench-{0}'.format(self.test_name)

        self.test_prefix = os.path.join(prefix, self.test_name)

        fail_nodes_path = os.path.join(self.test_prefix, 'fail_nodes')
        try:
            fail_nodes_ = set(bench.util.read_node_list(fail_nodes_path))
        except IOError as ex:
            self.logger.info('unable to read {0}'.format(fail_nodes_path))
            self.logger.debug(ex, exc_info=True)
            fail_nodes_ = set()

        error_nodes_path = os.path.join(self.test_prefix, 'error_nodes')
        try:
            error_nodes_ = set(bench.util.read_node_list(error_nodes_path))
        except IOError as ex:
            self.logger.info('unable to read {0}'.format(error_nodes_path))
            self.logger.debug(ex, exc_info=True)
            error_nodes_ = set()

        # by default, reserve fail_nodes and error_nodes
        if not (self.fail_nodes or self.error_nodes):
            reserve_nodes_ = fail_nodes_ | error_nodes_
        else:
            reserve_nodes_ = set()
            if self.fail_nodes:
                reserve_nodes_ |= fail_nodes_
            if self.error_nodes:
                reserve_nodes_ |= error_nodes_

        if reserve_nodes_:

            # Check for existing reservation, create new one by default
            subcommand = 'create'
            try:
                output = bench.slurm.scontrol(subcommand='show', reservation=self.reservation_name)
                output = bench.util.string_to_bytes(output)

                # If reservation found, update old reservation
                if b"ReservationName=" in output:
                    subcommand = 'update'

            except bench.exc.SlurmError as ex:
                self.logger.error(ex)
                self.logger.debug(ex, exc_info=True)

            try:
                nodes=','.join(sorted(reserve_nodes_))
                # print("RESERVATION NAME ", self.reservation_name)
                # print("NODES = ", nodes)

                if subcommand == 'update':
                    bench.slurm.scontrol(
                        subcommand = subcommand,
                        accounts = self.account,
                        nodes=nodes,
                        reservation=self.reservation_name,
                        users=self.users,
                    )
                else:
                    bench.slurm.scontrol(
                        subcommand = subcommand,
                        accounts = self.account,
                        duration='UNLIMITED',
                        flags='overlap',
                        nodes=nodes,
                        reservation=self.reservation_name,
                        starttime='now',
                        users=self.users,
                    )
            except bench.exc.SlurmError as ex:
                self.logger.error(ex)
                self.logger.debug(ex, exc_info=True)
            else:
                self.logger.info('{0}: {1}'.format(self.reservation_name, len(reserve_nodes_)))
