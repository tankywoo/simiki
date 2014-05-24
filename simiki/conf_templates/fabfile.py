#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
from fabric.api import env, local, run
from fabric.colors import blue
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


def update_simiki():
    print(blue("Old Version: "))
    run("simiki -V")
    run("pip install -U simiki")
    print(blue("New Version: "))
    run("simiki -V")

def deploy():
    project.rsync_project(
        local_dir = env.local_output,
        remote_dir = env.remote_output.rstrip("/") + "/",
        delete =True
    )

def g():
    local("simiki generate")

def p():
    local("simiki preview")

def gp():
    g()
    p()
