# coding: utf-8

from fablib import python


class Ceres():
    def __init__(self):
        return

    def setup(self):
        python.setup()
        python.install_from_git('ceres',
                                'https://github.com/graphite-project/ceres.git')
