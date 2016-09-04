# coding: utf-8

from fabkit import task
from fablib.influxdb import Influxdb


@task
def setup():
    influxdb = Influxdb()
    influxdb.setup()
