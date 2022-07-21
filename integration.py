import boto3
from botocore.exceptions import NoCredentialsError
import os
import yaml
from collections import ChainMap
from os import walk
from time import sleep

# current directory
cwd = os.getcwd()

def get_credentials_and_bucket_name():
    with open(cwd+"/config/aws.yaml") as file:
        documents = yaml.full_load(file)
        documents = documents["aws"]
        documents = dict(ChainMap(*documents ))

    access_key = documents["ACCESS_KEY"]
    secret_key = documents["SECRET_KEY"]
    bucket_name = documents["BUCKET"]

    return access_key,secret_key,bucket_name
        
def upload_to_aws(local_file, process_name_futurai,monitor):

    object_name = os.path.basename(local_file)

    s3_file = "raw-data/"+process_name_futurai+"/"+ object_name

    s3 = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )

    try:
        s3.upload_file(local_file, BUCKET_NAME, s3_file)
        print("Upload Successful: "+local_file )
        monitor.ping(state='ok',message=("Arquivo csv enviado: "+object_name))
        return True
    except FileNotFoundError:
        monitor.ping(state='ok',message=("Arquivo csv não foi enviado: "+object_name))
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        monitor.ping(state='ok',message=("Arquivo csv não foi enviado: "+object_name))
        return False

def get_list_process():
    """ Get the list of process in yaml configuration file
    Params: none
    Retunrs: List of process""" 

    with open(cwd+"/config/aws.yaml") as file:
        documents = yaml.full_load(file)
        documents = documents["process"]
        documents = dict(ChainMap(*documents ))
        process = list(documents.keys())

    return process,documents

def get_filenames(process,cwd):
    filenames_by_process = []
    
    f = []
    for (dirpath, dirnames, filenames) in walk(cwd+"/data/queue/"):
        f.extend(filenames)
        break

    for file in filenames:
        if(file.find(process)>=0):
            filenames_by_process.append(file)

    return sorted(filenames_by_process)

# main
ACCESS_KEY,SECRET_KEY,BUCKET_NAME = get_credentials_and_bucket_name()
def integration(monitor):

    list_process,documents = get_list_process()

    for process in list_process:
        try:
            filenames_by_process = get_filenames(process,cwd)
            print("**** Iniciando integração para o processo "+process)
            for file in filenames_by_process:
                local_file = cwd+"/data/queue/"+file

                process_name_futurai = documents[process]

                uploaded = upload_to_aws(local_file,process_name_futurai,monitor)

                if uploaded:
                    local_file_destionation = cwd+"/data/successfully/"+file

                else:
                    local_file_destionation = cwd+"/data/error/"+file

                os.rename(local_file,local_file_destionation)
                sleep(5)
        except Exception as e:
            print("erro ao tentar fazer o upload do processo: "+process)
            monitor.ping(state='fail',message=str(e))
            raise

    print("finished")

        



        