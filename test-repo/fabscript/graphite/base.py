# coding: utf-8

from fabkit import task
from fablib.graphite import Graphite

graphite = Graphite()


@task
def setup():
    graphite.setup()
