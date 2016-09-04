# coding: utf-8

import os
from fabkit import env, Service, Package, sudo, filer, conf
from fablib import python


class GraphiteWeb():
    def __init__(self):
        self.data = {
            'user': 'nobody',
            'group': 'nobody',
            'secret_key': 'default',
            'time_zone': 'Asia/Tokyo',
            'storage_finders': [
                'graphite.finders.ceres.CeresFinder',
                # 'graphite.finders.standard.StandardFinder',
            ]
        }

    def setup(self):
        self.data.update(env.cluster['graphite_web'])
        is_updated = self.install_graphite_web()
        httpd = Service('httpd').enable().start()
        if is_updated:
            httpd.restart()

        return True

    def syncdb(self):
        sudo('sh -c "cd /opt/graphite/webapp/ && ./manage.py syncdb --noinput"')

    def install_graphite_web(self):
        data = self.data

        Package('pycairo').install()
        Package('cairo-devel').install()
        Package('bitmap-fonts-compat').install()
        Package('httpd').install()
        Package('mod_wsgi').install()
        Package('MySQL-python').install()

        python.setup()
        sudo('pip install django==1.6.8')
        python.install_from_git('graphite-web',
                                'https://github.com/graphite-project/graphite-web.git')

        log_dir = '/opt/graphite/storage/log/webapp/'
        owner = '{0[user]}:{0[group]}'.format(data)
        filer.mkdir(log_dir, owner=owner)
        log_files = ['access.log', 'error.log', 'exception.log', 'info.log']
        for log_file in log_files:
            log_file = os.path.join(log_dir, log_file)
            filer.touch(log_file, owner=owner)

        manage_py = os.path.join(conf.REMOTE_TMP_DIR, 'git/graphite-web.git/webapp/manage.py')
        sudo('cp {0} /opt/graphite/webapp/'.format(manage_py))

        is_updated = filer.template('/opt/graphite/webapp/graphite/local_settings.py',
                                    data=data)

        is_updated = filer.template('/opt/graphite/webapp/graphite/settings.py',
                                    data=data) or is_updated

        is_updated = filer.template('/opt/graphite/conf/graphite.wsgi') or is_updated

        is_updated = filer.template('/etc/httpd/conf.d/graphite-vhost.conf', data={
            'user': data['user'],
            'group': data['group'],
        }) or is_updated

        return is_updated
