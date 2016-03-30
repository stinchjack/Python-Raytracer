import glob
import os
import shutil


#quick package update
python_executable = sys.executable
if '.exe' in python_executable:
    python_executable = python_executable[:-3]
 
# Get all the required paths
pkg_update_full_filepath = os.path.abspath(__file__)

# base_dir is the main project directory
base_dir = pkg_update_full_filepath [
    :auto_update_full_filepath.find('scripts')] 
 
dest_path = os.path.join (python_executable, 'Lib',
                             'site-packages', 'raytracer' )

print("Copying raytracer .py files to %s ..." % (copy_to_path)
files = glob.glob(os.path.join(base_dir, "*.py"))
for file in files:
    shutil.copy(file, dest_path)

