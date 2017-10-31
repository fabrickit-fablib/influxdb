# coding: utf-8

from fabkit import task
from fablib.influxdb import Telegraf


@task
def setup():
    telegraf = Telegraf()
    telegraf.setup()
