# coding: utf-8

from fabkit import *  # noqa
from fablib.base import SimpleBase


class Graphite(SimpleBase):
    def __init__(self, enable_services=['.*']):
        self.data_key = 'graphite'
        self.data = {
        }

        self.packages = {
            'CentOS Linux 7.*': [
                'epel-release',
                'mariadb-server',
                'httpd',
                'graphite-web',
                'MySQL-python',
                {'name': 'go-carbon', 'path': 'https://github.com/lomik/go-carbon/releases/download/v0.7.3/go-carbon-0.7.3-1.el6.x86_64.rpm'},  # noqa
            ]
        }

        self.services = ['go-carbon', 'mariadb', 'httpd']

    def setup(self):
        data = self.init()

        if self.is_tag('package'):
            self.install_packages()
            filer.mkdir('/var/lib/carbon/whisper')
            filer.mkdir('/etc/graphite/graphite')

        if filer.template('/etc/graphite/schemas'):
            self.handlers['restart_go-carbon'] = True

        self.start_services().enable_services()
        sudo("mysql -uroot -e 'create database if not exists graphite'")

        if filer.template('/usr/local/etc/go-carbon.conf', data=data):
            self.handlers['restart_go-carbon'] = True
        if filer.template('/etc/graphite-web/local_settings.py', data=data):
            self.handlers['restart_httpd'] = True
        if filer.template('/etc/httpd/conf.d/graphite-web.conf', data=data):
            self.handlers['restart_httpd'] = True

        sudo('graphite-manage syncdb --noinput')
        self.exec_handlers()
