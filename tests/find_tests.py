import inspect
import os
import subprocess
import sys
import time
import numpy as np
from pyiron_base.core.settings.generic import convert_path

# We would like to use:
#     python -m unittest discover -s tests -p 'test*.py'
# But that is not possible, as PyCharm expects the tests to be executed in the directory where they are located.

# create .pyiron config if it does not exist to enable non modal jobs
config_file = os.path.expanduser(os.path.join("~", ".pyiron"))
if not os.path.exists(config_file):
    with open(config_file, 'w') as cf:
        if os.name == 'nt':
            cf.writelines(['[DEFAULT]\n',
                           'PROJECT_PATHS = ' + convert_path(__file__).split('/pyiron-atomistics')[0] + '\n',
                           'RESOURCE_PATHS = ' + convert_path(__file__).split('/pyiron-atomistics')[0]
                           + '/pyiron-atomistics/tests/static\n'])
        else:
            cf.writelines(['[DEFAULT]\n',
                           'PROJECT_PATHS = ' + convert_path(__file__).split('/pyiron_atomistics')[0] + '\n',
                           'RESOURCE_PATHS = ' + convert_path(__file__).split('/pyiron_atomistics')[0]
                           + '/pyiron_atomistics/tests/static\n'])

import pyiron_atomistics
current_file_name = inspect.getfile(inspect.currentframe()).split('/')[-1]
pyrion_path = os.path.dirname(pyiron_atomistics.__file__)

if len(sys.argv) == 2:
    pythonversion = sys.argv[1]
    if 'coverage' in pythonversion:
        command_lst = [pythonversion, 'run', '--source', pyrion_path]
    else:
        command_lst = [pythonversion]
else:
    try:
        import coverage
        command_lst = ['coverage', 'run', '--source', pyrion_path]
    except ImportError:
        command_lst = ['python']

failed = False

with open('test_times.dat', mode='w') as f:
    dir_tree = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py") and file not in ['__init__.py', current_file_name]:
                time_start = time.time()
                if os.name == 'nt':
                    process = subprocess.Popen(command_lst + [file],
                                               cwd=os.path.abspath(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               universal_newlines=True, shell=True)
                else:
                    process = subprocess.Popen(command_lst + [file],
                                               cwd=os.path.abspath(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               universal_newlines=True, shell=False)
                output, error = process.communicate()
                time_tot = time.time() - time_start
                if process.returncode != 0:
                    print(file)
                    print(output)
                    print(error)
                    failed = True
                else:
                    print('{} OK: time(s) {}'.format(file, np.round(time_tot, 3)))
                    f.write('{} OK: time(s) {} \n'.format(file, np.round(time_tot, 3)))
                if root + '/.coverage' not in dir_tree:
                    dir_tree.append(root + '/.coverage')

if len(command_lst) > 1:
    command = ' '.join([command_lst[0], 'combine'] + dir_tree)
    command += '\n' + ' '.join([command_lst[0], 'report', '-m', '--omit', '*old*'])
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = process.communicate()
    print(error)
    print(output)
print(sys.version)

if failed:
    sys.exit(1)
