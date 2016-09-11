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
                'nmap-ncat',
                'influxdb-0.11.1',
                {'name': 'grafana', 'path': 'https://grafanarel.s3.amazonaws.com/builds/grafana-3.1.1-1470047149.x86_64.rpm'}
            ]
        }

        self.services = ['influxdb', 'carbon-relay-ng']

    def setup(self):
        data = self.init()
        filer.template('/etc/yum.repos.d/influxdb.repo')

        self.install_packages()
        if filer.template('/etc/influxdb/influxdb.conf'):
            self.handlers['restart_influxdb'] = True

        if filer.template('/etc/default/influxdb'):
            self.handlers['restart_influxdb'] = True

        with api.cd('/tmp'):
            run('[ -e go1.7.linux-amd64.tar.gz ] || wget https://storage.googleapis.com/golang/go1.7.linux-amd64.tar.gz')
            run('[ -e go ] || tar -xf go1.7.linux-amd64.tar.gz')
            sudo('[ -e /usr/local/go ] || cp go/bin/go /usr/local/')
        filer.mkdir('/opt/go')
        sudo('export GOROOT=/tmp/go/;'
             'export GOPATH=/opt/go/;'
             'export PATH=$PATH:$GOPATH/bin:$GOROOT/bin;'
             '/tmp/go/bin/go get -d github.com/graphite-ng/carbon-relay-ng;'
             '/tmp/go/bin/go get github.com/jteeuwen/go-bindata/...;'
             'cd "$GOPATH/src/github.com/graphite-ng/carbon-relay-ng";'
             'make;')

        if filer.template('/etc/carbon-relay-ng.ini'):
            self.handlers['restart_carbon-relay-ng'] = True

        filer.template('/etc/init.d/carbon-relay-ng', mode='755')

        self.start_services()
        self.exec_handlers()
