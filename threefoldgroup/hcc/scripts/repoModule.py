
import os
#from werkzeug.utils import secure_filename
import zipfile

from os import listdir, path, unlink
import shutil
from datetime import datetime

def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_repo(repo):
    folder1 = os.getcwd()+repo

    for filename in listdir(folder1):
        file_path = path.join(folder1, filename)
        try:
            if path.isfile(file_path) or path.islink(file_path):
                unlink(file_path)
            elif path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
