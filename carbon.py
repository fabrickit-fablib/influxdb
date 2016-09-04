# coding: utf-8

from fabkit import *  # noqa
from fablib import python


class Carbon():
    def __init__(self, role=None):
        self.data = {
            'user': 'nobody',
            'group': 'nobody',
            'initscript': {
                'wait_interval': 5,
                'wait_interval_time': 1,
            },
            'daemons': {
                # 'carbon_relay0': {
                #
                # }
            }
        }

        self.role = role

    def init_data(self):
        self.data.update(env.cluster.get('carbon', {}))
        if self.role is not None:
            self.data.update(self.data[self.role])

    def setup(self):
        self.init_data()
        is_updated = self.install_carbon()
        for name in self.data['daemons']:
            carbon = Service('carbon-' + name).enable().start(pty=False)
            if is_updated:
                carbon.restart(pty=False)

        return 0

    def install_carbon(self):
        data = self.data
        python.setup()
        python.install_from_git('carbon',
                                'https://github.com/graphite-project/carbon.git -b megacarbon')

        graphite_dir = '/opt/graphite'
        storage_dir = os.path.join(graphite_dir, 'storage')
        storage_files = os.path.join(storage_dir, '*')
        sudo('chown {0}:{1} {2}'.format(data['user'], data['group'], storage_dir))
        sudo('chown {0}:{1} {2}'.format(data['user'], data['group'], storage_files))

        daemons_dir = '/opt/graphite/conf/carbon-daemons/'
        daemon_confs = [
            'daemon.conf',
            'relay.conf',
            'aggregation.conf',
            'amqp.conf',
            'filter-rules.conf',
            'relay.conf',
            'storage-rules.conf',
            'aggregation-filters.conf',
            'daemon.conf',
            'listeners.conf',
            'relay-rules.conf',
            'writer.conf',
            'aggregation-rules.conf',
            'db.conf',
            'management.conf',
            'rewrite-rules.conf',
        ]

        is_updated = False
        for name, daemon in data['daemons'].items():
            daemon_dir = os.path.join(daemons_dir, name)
            filer.mkdir(daemon_dir)

            for daemon_conf in daemon_confs:
                is_updated = filer.template(os.path.join(daemon_dir, daemon_conf), data={
                    'user': data['user'],
                    'daemon': daemon,
                }, src_target=daemon_conf) or is_updated

            is_updated = filer.template('/etc/init.d/carbon-{0}'.format(name), '755', data={
                'description': 'Carbon Daemon: {0}'.format(name),
                'name': name,
                'user': data['user'],
                'exec': os.path.join(graphite_dir, 'bin/carbon-daemon.py'),
                'initscript': data['initscript'],
            }, src_target='carbon-initscript') or is_updated

        return is_updated
