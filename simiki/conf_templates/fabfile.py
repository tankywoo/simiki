import os
import os.path
from fabric.api import env
import fabric.contrib.project as project

env.hosts = []
env.user = ""

local_output = os.path.join(os.path.abspath(os.path.dirname(__file__)), "output")
dest_path = ""

def deploy():
    project.rsync_project(
        local_dir = local_output,
        remote_dir = dest_path,
        delete =True
    )
