# coding: utf-8

from fabkit import *  # noqa
from fablib.base import SimpleBase


class Influxdb(SimpleBase):
    def __init__(self, enable_services=['.*']):
        self.data_key = 'influxdb'
        self.data = {
        }

        self.packages = {
            'CentOS Linux 7.*': [
                'git',
                'wget',
                'vim',
                'influxdb-relay',
                {'name': 'influxdb', 'path': 'https://dl.influxdata.com/influxdb/releases/influxdb-1.6.0.x86_64.rpm'},  # noqa
                {'name': 'telegraf', 'path': 'https://dl.influxdata.com/telegraf/releases/telegraf-1.7.2-1.x86_64.rpm'}  # noqa
            ]
        }

        self.services = ['influxdb', 'influxdb-relay']

    def setup(self):
        data = self.init()
        filer.template('/etc/yum.repos.d/influxdb.repo')
        filer.template('/etc/yum.repos.d/sk.repo')

        data['hosts'] = env.cluster['node_map']['influxdb']['hosts']
        self.install_packages()
        if filer.template('/etc/influxdb/influxdb.conf', data=data):
            self.handlers['restart_influxdb'] = True

        if filer.template('/etc/influxdb-relay/relay.toml', data=data):
            self.handlers['restart_influxdb-relay'] = True

        self.enable_services().start_services()
        self.exec_handlers()

        run("influx -execute 'CREATE DATABASE telegraf'")
        # run("influx -execute 'CREATE USER root WITH PASSWORD \"root\" WITH ALL PRIVILEGES;'")
        # run("influx -execute 'CREATE RETENTION POLICY auto ON telegraf DURATION 10 REPLICATION 1 DEFAULT;'")
