# coding: utf-8

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

        filer.mkdir('/etc/grafana/dashboards')
        filer.template('/etc/grafana/dashboards/telegraf-system.json', data=data)

        self.enable_services().start_services()
        self.exec_handlers()
        time.sleep(10)

        run("""curl -k -i -XPOST -H "Accept: application/json" -H "Content-Type: application/json" "http://admin:admin@localhost:3000/api/datasources" -d '
        {
           "name": "influxdb-telegraf-datasource",
           "type": "influxdb",
           "access": "'"proxy"'",
           "url": "'"localhost:8086"'",
           "password": "'""'",
           "user": "'""'",
           "database": "'"telegraf"'"
         }'
         """)

        run("""
       for filename in /etc/grafana/dashboards/*.json; do
           echo "Importing ${filename} ..."
           curl -k -i -XPOST --data "@${filename}" -H "Accept: application/json" -H "Content-Type: application/json" "http://admin:admin@localhost:3000/api/dashboards/db"
       done
       """)
