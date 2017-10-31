# coding: utf-8

from fabkit import *  # noqa
from fablib.base import SimpleBase


class Telegraf(SimpleBase):
    def __init__(self, enable_services=['.*']):
        self.data_key = 'telegraf'
        self.data = {
        }

        self.packages = {
            'CentOS Linux 7.*': [
                {'name': 'telegraf', 'path': 'https://dl.influxdata.com/telegraf/releases/telegraf-1.4.3-1.x86_64.rpm'}  # noqa
            ]
        }

        self.services = ['telegraf']

    def setup(self):
        data = self.init()
        self.install_packages()

        if filer.template('/etc/telegraf/telegraf.conf', data=data):
            self.handlers['restart_telegraf'] = True

        self.enable_services().start_services()
        self.exec_handlers()
