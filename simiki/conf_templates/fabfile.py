#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, with_statement

import os
import sys
import ftplib
import getpass
from fabric.api import env, local, task, settings
from fabric.colors import blue, red
import fabric.contrib.project as project
from simiki import config
from simiki.compat import raw_input

# XXX must run fab in root path of wiki
configs = config.parse_config('_config.yml')

env.colorize_errors = True
SUPPORTED_DEPLOY_TYPES = ('rsync', 'git', 'ftp')


def do_exit(msg):
    print(red(msg))
    print(blue('Exit!'))
    sys.exit()


def get_rsync_configs():
    if 'deploy' in configs:
        for item in configs['deploy']:
            if item['type'] == 'rsync':
                return item
    return None


# cannot put this block in deploy_rsync() for env.hosts
rsync_configs = get_rsync_configs()
if rsync_configs:
    env.user = rsync_configs.get('user', 'root')
    # Remote host and username
    if 'host' not in rsync_configs:
        do_exit('Warning: rsync host not set in _config.yml!')
    env.hosts = [rsync_configs['host'], ]

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


def deploy_rsync(deploy_configs):
    """for rsync"""
    project.rsync_project(
        local_dir=env.local_output.rstrip("/") + "/",
        remote_dir=env.remote_output.rstrip("/") + "/",
        delete=env.rsync_delete
    )


def deploy_git(deploy_configs):
    """for pages service of such as github/gitcafe ..."""
    with settings(warn_only=True):
        res = local('which ghp-import > /dev/null 2>&1; echo $?', capture=True)
        if int(res.strip()):
            do_exit('Warning: ghp-import not installed! '
                    'run: `pip install ghp-import`')
    output_dir = configs['destination']
    remote = deploy_configs.get('remote', 'origin')
    branch = deploy_configs.get('branch', 'gh-pages')
    # commit gh-pages branch and push to remote
    _mesg = 'Update output documentation'
    local('ghp-import -p -m "{0}" -r {1} -b {2} {3}'
          .format(_mesg, remote, branch, output_dir))


def deploy_ftp(deploy_configs):
    """for ftp"""
    conn_kwargs = {'host': deploy_configs['host']}
    login_kwargs = {}
    if 'port' in deploy_configs:
        conn_kwargs.update({'port': deploy_configs['port']})
    if 'user' in deploy_configs:
        login_kwargs.update({'user': deploy_configs['user']})
    if 'password' in deploy_configs:
        passwd = deploy_configs['password']
        # when set password key with no value, get None by yaml
        if passwd is None:
            passwd = getpass.getpass('Input your ftp password: ')
        login_kwargs.update({'passwd': passwd})

    ftp_dir = deploy_configs.get('dir', '/')
    output_dir = configs['destination']

    ftp = ftplib.FTP()
    ftp.connect(**conn_kwargs)
    ftp.login(**login_kwargs)

    for root, dirs, files in os.walk(output_dir):
        rel_root = os.path.relpath(root, output_dir)
        for fn in files:
            store_fn = os.path.join(ftp_dir, rel_root, fn)
            ftp.storbinary('STOR %s' % store_fn,
                           open(os.path.join(root, fn), 'rb'))

    ftp.close()


@task
def deploy(type=None):
    """deploy your site, support rsync / ftp / github pages

    run deploy:
        $ fab deploy

    run deploy with specific type(not supported specify multiple types):
        $ fab deploy:type=rsync

    """
    if 'deploy' not in configs or not isinstance(configs['deploy'], list):
        do_exit('Warning: deploy not set right in _config.yml')
    if type and type not in SUPPORTED_DEPLOY_TYPES:
        do_exit('Warning: supported deploy type: {0}'
                .format(', '.join(SUPPORTED_DEPLOY_TYPES)))

    deploy_configs = configs['deploy']

    done = False

    for deploy_item in deploy_configs:
        deploy_type = deploy_item.pop('type')
        if type and deploy_type != type:
            continue
        func_name = 'deploy_{0}'.format(deploy_type)
        func = globals().get(func_name)
        if not func:
            do_exit('Warning: not supprt {0} deploy method'
                    .format(deploy_type))
        func(deploy_item)
        done = True

    if not done:
        if type:
            do_exit('Warning: specific deploy type not configured yet')
        else:
            print(blue('do nothing...'))


@task
def commit():
    """git commit source changes from all tracked files

    include:

      - add all tracked files in the work tree, include modified(M), deleted(D)
      - commit all files in the index, include added(A), modified(M),
        renamed(R), deleted(D)
      - untracked files should be manually added to the index before
        run this task

    before do commit, it requires to confirm the files to be committed; and
    the requirement before do add is a future feature, it is currently
    disabled.
    """
    message = 'Update Documentation'
    yes_ans = ('y', 'yes')

    with settings(warn_only=True):
        # Changes in the work tree to add
        add_file = '--update .'  # include tracked files
        # hack of res.return_code without warning info
        res = local('git diff --quiet --exit-code; echo $?', capture=True)
        if int(res.strip()):
            if False:  # future feature?
                # TODO: there use diff to uniform with below, and the
                # output can be formatted like `git add --dry-run --update .`
                test_res = local('git diff --name-status', capture=True)
                try:
                    _ans = raw_input('\n{0}\nAdd these files to index? (y/N) '
                                     .format(test_res.strip()))
                    if _ans.lower() in yes_ans:
                        local("git add {0}".format(add_file))
                except (KeyboardInterrupt, SystemExit):
                    pass
            else:
                local("git add {0}".format(add_file))

        # Changes in the index to commit
        res = local('git diff --cached --quiet --exit-code; echo $?',
                    capture=True)
        if int(res.strip()):
            test_res = local('git diff --cached --name-status', capture=True)
            try:
                _ans = raw_input('\n{0}\nCommit these files? (y/N) '
                                 .format(test_res.strip()))
                if _ans.lower() in yes_ans:
                    local("git commit -m '{0}'".format(message))
            except (KeyboardInterrupt, SystemExit):
                pass
        else:
            print('Nothing to commit.')
