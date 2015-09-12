#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os
import sys
from fabric.api import env, local, task
from fabric.colors import blue, red
import fabric.contrib.project as project
from simiki import config

# XXX must run fab in root path of wiki
configs = config.parse_config('_config.yml')

env.colorize_errors = True


def do_exit(msg):
    print(red(msg))
    print(blue('Exit!'))
    sys.exit()


if 'rsync' in configs:
    rsync_configs = configs['rsync']
    if not isinstance(rsync_configs, dict):
        do_exit('Warning: rsync not set right in _config.yml')

    env.user = rsync_configs.get('user', 'root')
    # Remote host and username
    if 'host' not in rsync_configs:
        do_exit('Warning: rsync host not set in _config.yml!')
    env.hosts = [rsync_configs['host'],]

    # Local output path
    env.local_output = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        configs['destination'])

    # Remote path to deploy output
    if 'dir' not in rsync_configs:
        do_exit('Warning: rsync dir not set in _config.yml!')
    env.remote_output = rsync_configs['dir']

    # Other options
    env.port = rsync_configs.get('port')
    env.rsync_delete = rsync_configs.get('delete', False)


def deploy_rsync():
    project.rsync_project(
        local_dir=env.local_output.rstrip("/")+"/",
        remote_dir=env.remote_output.rstrip("/")+"/",
        delete=env.rsync_delete
    )


@task
def deploy():
    if 'rsync' in configs:
        deploy_rsync()
    else:
        print(blue('do nothing...'))


@task
