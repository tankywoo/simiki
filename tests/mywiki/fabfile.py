#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import os.path
from sys import exit
from fabric.api import env, local, run
from fabric.colors import blue, red
import fabric.contrib.project as project

# Remote host and username
env.hosts = []
env.user = ""
env.colorize_errors = True

# Local output path
env.local_output = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "output/")
# Remote path to deploy output
env.remote_output = ""

# Other options
env.rsync_delete = False


def update_simiki():
    print(blue("Old Version: "))
    run("simiki -V")
    run("pip install -U simiki")
    print(blue("New Version: "))
    run("simiki -V")


def deploy():
    if not env.remote_output:
        if env.rsync_delete:
            print(red("You can't enable env.rsync_delete option "
                      "if env.remote_output is not set!!!"))
            print(blue("Exit"))
            exit()

        print(red("Warning: env.remote_output directory is not set!\n"
                  "This will cause some problems!!!"))
        ans = raw_input(red("Do you want to continue? (y/N) "))
        if ans != "y":
            print(blue("Exit"))
            exit()

    project.rsync_project(
        local_dir=env.local_output,
        remote_dir=env.remote_output.rstrip("/") + "/",
        delete=env.rsync_delete
    )


def g():
    local("simiki generate")


def p():
    local("simiki preview")


def gp():
    g()
    p()
