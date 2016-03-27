import colorama
import glob
import os
import shutil
import subprocess
import sys
import unittest

"""Script to automate update procedure. Checks for PEP8 compliance, runs
unit tests, generates documentation using Sphinx, updates GIT repository.

As well as Sphinx, this script requires autoPEP8 and the colorama module.

.. todo: implement GIT repo manipulation"""

colorama.init()

# Get all the requirred paths
auto_update_full_filepath = os.path.abspath(__file__)

# base_dir is the main project directory
base_dir = auto_update_full_filepath[
    :auto_update_full_filepath.find('scripts')]

python_executable = sys.executable
if '.exe' in python_executable:
    python_executable = python_executable[:-3]

# python_dir is the directory of the python executable
python_dir = python_executable[:python_executable.rfind(os.sep) + 1]

# script_dir is the directory python scripts such as pep8, autopep8, and
# the Sphinx executables are
script_dir = os.path.join(python_dir, "Scripts")

# unit_test_dir is the path to the unit tests
unit_test_dir = os.path.join(base_dir, "unit_tests")

# doc_dir is the path for project docmentation
doc_dir = os.path.join(base_dir, "docs")

sys.path.insert(0, base_dir)
sys.path.insert(0, script_dir)
sys.path.insert(0, unit_test_dir)
sys.path.insert(0, doc_dir)


def check_pep8():
    """Runs the PEP8 style checker.

    :return: True if no formatting problems, else False"""
    pep8_result =\
        subprocess.run(
            "%s%s" % (os.path.join(script_dir, "pep8 "),
                      os.path.join(os.curdir, '')))

    pep8_pass = (pep8_result.returncode == 0)

    return pep8_pass


def auto_update():

    os.chdir(base_dir)

    # check for PEP8 violations
    print("%s%s\r\nChecking for PEP8 formatting ...\r\n" %
          (colorama.Fore.BLUE, colorama.Style.BRIGHT))
    print(colorama.Style.RESET_ALL)

    pep8_pass = check_pep8()

    # If there are PEP8 Viloations, try fixing them
    if not pep8_pass:
        pep8_pass = False

        print("%s%s\r\nPEP8 Violations found, running autoPEP8, %s" %
              ("may take 5-10 minutes \r\n",
               colorama.Fore.YELLOW, colorama.Style.BRIGHT))
        print(colorama.Style.RESET_ALL)

        # Attempt to fix PEP8 issues using autopep8
        os.system("%s%s%s" %
                  (os.path.join(script_dir, "autopep8 "),
                   os.path.join(os.curdir, ''),
                   " --recursive --in-place --pep8-passes 100 --verbose"))
        # Recheck for PEP8 viloations

        print("%s%s\r\nRe-checking for PEP8 formatting ...\r\n" %
              (colorama.Fore.BLUE, colorama.Style.BRIGHT))
        print(colorama.Style.RESET_ALL)

        pep8_pass = check_pep8()

    if not pep8_pass:
        return "\r\nCode is not PEP8 formatted.\r\n"
    else:
        print(("%s%s\r\nPEP8 format check successful. \r\n ") %
              (colorama.Fore.GREEN, colorama.Style.BRIGHT))

    # Run unit tests

    print("%s%s\r\nRunning unit tests ...\r\n" %
          (colorama.Fore.BLUE, colorama.Style.BRIGHT))
    print(colorama.Style.RESET_ALL)

    suite = unittest.TestLoader().discover('unit_tests\\')
    unit_test_result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not unit_test_result.wasSuccessful():
        return "\r\nUnit tests failed.\r\n"
    else:
        print(("%s%s\r\nUnit tests ran successfully. \r\n ") %
              (colorama.Fore.GREEN, colorama.Style.BRIGHT))

    # Generate documentation
    print("%s%s\r\nGenerating documentation ...\r\n" %
          (colorama.Fore.BLUE, colorama.Style.BRIGHT))
    print(colorama.Style.RESET_ALL)

    # Copy Sphinx executables
    print("Copying Sphinx executables to project documentation directory ...")
    sphinx_files = glob.glob(os.path.join(script_dir, "sphinx*"))
    for file in sphinx_files:
        shutil.copy(file, doc_dir)

    # Remove former .rst files
    print("Removing previous .rst files ...")
    rst_files = glob.glob(os.path.join(doc_dir, "docs", "*.rst"))
    for file in rst_files:
        os.remove(file)

    print("Running sphinx-apidoc to generate fresh .rst files ...\r\n")
    os.chdir(doc_dir)
    sphinx_apidoc_result = subprocess.run("sphinx-apidoc -o %s %s" %
                                          (os.path.join("docs", ""),
                                           os.path.join(os.pardir, "")))
    # os.remove(os.path.join(doc_dir, 'docs', 'modules.rst'))
    # os.remove(os.path.join(doc_dir, 'source', 'index.rst'))
    if sphinx_apidoc_result.returncode == 1:
        return "Sphinx documentation build error"

    print("\r\nRunning sphinx-build to generate HTML documentation ...\r\n")
    sphinx_build_result = \
        subprocess.run(
            "sphinx-build -b html .\\ -c source\\ build\\html\\")

    if sphinx_build_result.returncode == 1:
        return "Sphinx documentation build error"

    print("Removing Sphinx executables to project documentation directory ...")
    copied_sphinx_files = glob.glob(os.path.join(doc_dir, "sphinx*"))
    for file in copied_sphinx_files:
        os.remove(file)

    os.chdir(base_dir)

    # Send to GitHub
    return True

if __name__ == '__main__':
    result = auto_update()
    if result is not True:
        print("%s%s\r\n%s\r\n" %
              (colorama.Fore.RED, colorama.Style.BRIGHT, result))
        print(colorama.Style.RESET_ALL)
        sys.exit(1)
    else:
        sys.exit(0)
