# coding: utf-8

import json
import time
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

        self.services = ['grafana-server']

    def setup(self):
        data = self.init()
        self.install_packages()

        if filer.template('/etc/grafana/grafana.ini', data=data):
            self.handlers['restart_grafana-server'] = True

        self.enable_services().start_services()
        self.exec_handlers()
        time.sleep(10)

        for datasource in data['datasources']:
            option = json.dumps(datasource)
            self.curl_api(path="/datasources", option="-d '{0}'".format(option))

        filer.mkdir('/etc/grafana/dashboards')
        for dashboard in data['dashboards']:
            file_path = '/etc/grafana/dashboards/{0}.json'.format(dashboard)
            filer.template(file_path)
            self.curl_api(path="/dashboards/db", option='--data "@{0}"'.format(file_path))

    def curl_api(self, path, option):
        run('curl -k -i -XPOST -H "Accept: application/json" -H "Content-Type: application/json"'
            ' "http://admin:admin@localhost:3000/api{0}" {1}'.format(path, option))
