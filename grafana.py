# coding: utf-8

from fabkit import *  # noqa
from fablib.base import SimpleBase


class Grafana(SimpleBase):
    def __init__(self, enable_services=['.*']):
        self.data_key = 'grafana'
        self.data = {
        }

        self.packages = {
            'CentOS Linux 7.*': [
                {'name': 'grafana', 'path': 'https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-4.6.1-1.x86_64.rpm'}  # noqa
            ]
        }

        self.services = ['grafana']

    def setup(self):
        data = self.init()
        self.install_packages()

        if filer.template('/etc/grafana/grafana.ini', data=data):
            self.handlers['restart_grafana-server'] = True

        self.enable_services().start_services()
        self.exec_handlers()
