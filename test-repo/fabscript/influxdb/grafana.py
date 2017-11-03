# coding: utf-8

from fabkit import task
from fablib.influxdb import Grafana


@task
def setup():
    grafana = Grafana()
    grafana.setup()
