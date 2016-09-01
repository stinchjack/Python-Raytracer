import glob
import os
import sys


def get_filepaths():
    # quick package update
    python_executable = sys.executable
    if '.exe' in python_executable:
        python_executable = python_executable[:-4]

    # Get all the required paths
    pkg_update_full_filepath = os.path.abspath(__file__)

# base_dir is the main project directory
    base_dir = pkg_update_full_filepath[
        :pkg_update_full_filepath.find('devutil')]
    return (python_executable, base_dir)


def setup():
    filepaths = get_filepaths()

    os.system("%s setup.py clean --user" % (filepaths[0]))
    os.system("%s setup.py install --user" % (filepaths[0]))


def run(py_file, dir=None):
    setup()

    filepaths = get_filepaths()

    if dir is not None:
        os.chdir(dir)
    os.system("%s %s" % (filepaths[0], py_file))
