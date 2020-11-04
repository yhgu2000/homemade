from subprocess import call

call("python -m pip install --upgrade pip")

from pip._internal.utils.misc import get_installed_distributions

for dist in get_installed_distributions():
    call("pip3 install --upgrade " + dist.project_name, shell=True)
