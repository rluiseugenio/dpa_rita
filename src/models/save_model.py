
from src.utils.s3_utils import upload_file_to_bucket

import os
import zipfile
import json
from datetime import date
import shutil

#https://linuxhint.com/python_zip_file_directory/
#Declare the function to return all file paths of the particular directory
def retrieve_file_paths(dirName):
    # setup file paths variable
    filePaths = []
    # Read all directory, subdirectories and file lists
    for root, directories, files in os.walk(dirName):
        for filename in files:
            # Create the full filepath by using os module.
            filePath = os.path.join(root, filename)
            filePaths.append(filePath)
    # return all paths
    return filePaths

def zip_model(dir_name):
    # Call the function to retrieve all files and folders of the assigned directory
    filePaths = retrieve_file_paths(dir_name)
    # writing files to a zipfile
    zip_file = zipfile.ZipFile(dir_name+'.zip', 'w')
    with zip_file:
        # writing each file one by one
        for file in filePaths:
            zip_file.write(file)
    print(dir_name+'.zip file is created successfully!')


def parse_filename(objetivo, model_name, hyperparams):
    para_string = json.dumps(hyperparams)
    para_string = para_string.replace(" ", "%")
    para_string = para_string.replace('"', "#")
    para_string = para_string.replace('}', "&")
    para_string = para_string.replace('{', "=")
    para_string = para_string.replace(':', "-")
    para_string = para_string.replace(',', "$")

    today = date.today()
    d1 = today.strftime("%d%m%Y")

    saved_model_name = "./" + d1 + "_" + objetivo + "_" + model_name + "_" + para_string

    return saved_model_name

def clean(new_saved_model):
    os.remove(new_saved_model)

    folder = new_saved_model[:-4]
    shutil.rmtree(folder, ignore_errors=True)


def save_upload(cvModel, objetivo, model_name, hyperparams,bucket_name = "models-dpa"):
    trained_model = cvModel.stages[-1]

    saved_model_name = parse_filename(objetivo, model_name, hyperparams) + ".model"
    key_name = saved_model_name[2:]

    # Save model
    trained_model.save(saved_model_name)

    # Zip model
    zip_model(key_name)

    new_saved_model = saved_model_name +".zip"
    new_key_name = new_saved_model[2:]

    # Upload file
    upload_file_to_bucket(new_saved_model, bucket_name, new_key_name)

    # delete local files
    clean(new_saved_model)
