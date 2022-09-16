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
    """ 
    Params: none
    Returns: 
        - access_key: string
        - secret_key: string
        - bucket_name: string"""
    
    with open(cwd+"/config/aws.yaml") as file:
        documents = yaml.full_load(file)
        documents = documents["aws"]
        documents = dict(ChainMap(*documents ))

    access_key = documents["ACCESS_KEY"]
    secret_key = documents["SECRET_KEY"]
    bucket_name = documents["BUCKET"]

    return access_key,secret_key,bucket_name
        
def upload_to_aws(local_file, process_name_futurai,monitor):
    """ 
    Uploading file to client bucket
    Params:
        - local_file: string
        - process_name_futurai: string
        - monitor: string
    Returns: 
        - True: upload successfully
        - False: error"""
    
    object_name = os.path.basename(local_file)

    s3_file = "raw-data/"+process_name_futurai+"/"+ object_name

    # set s3 client
    s3 = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )

    # try send file
    try:
        s3.upload_file(local_file, BUCKET_NAME, s3_file)
        monitor.ping(state='ok',message=("Arquivo csv enviado: "+object_name))
        return True
    except FileNotFoundError:
        monitor.ping(state='ok',message=("Arquivo não encontrado para envio: "+object_name))
        return False
    except NoCredentialsError:
        monitor.ping(state='ok',message=("Error ao acessar o bucket: "+object_name))
        return False

def get_list_process():
    """ Get the list of process in yaml configuration file
    Params: none
    Retunrs: 
         - process: List of process
         - documents: List with process name futurai""" 

    with open(cwd+"/config/aws.yaml") as file:
        documents = yaml.full_load(file)
        documents = documents["process"]
        documents = dict(ChainMap(*documents ))
        process = list(documents.keys())

    return process,documents

def get_filenames(process,cwd):
    """ Get the list of filenames to upload
    Params: 
        - process: strings
        - cwd: string
    Retunrs: 
        - List with filenames sorted by process""" 
    
    filenames_by_process = []
    
    f = []
    for (dirpath, dirnames, filenames) in walk(cwd+"/data/queue/"):
        f.extend(filenames)
        break

    for file in filenames:
        if(file.find(process)>=0):
            filenames_by_process.append(file)

    return sorted(filenames_by_process)

ACCESS_KEY,SECRET_KEY,BUCKET_NAME = get_credentials_and_bucket_name()

def integration(monitor):

    list_process,documents = get_list_process()

    # loop by process
    for process in list_process:
        
        try:
            
            # get file accordingly with process name
            filenames_by_process = get_filenames(process,cwd)
            
            # loop by file
            for file in filenames_by_process:
                
                local_file = cwd+"/data/queue/"+file
                process_name_futurai = documents[process]
                
                # send file to client bucket
                uploaded = upload_to_aws(local_file,process_name_futurai,monitor)

                # move file to successfully folder
                if uploaded:
                    local_file_destionation = cwd+"/data/successfully/"+file

                # move file to error folder
                else:
                    local_file_destionation = cwd+"/data/error/"+file

                os.rename(local_file,local_file_destionation)
             
        except Exception as e:
            monitor.ping(state='fail',message=("erro ao tentar fazer o upload do processo: "+process+" error:"+ str(e)))
            


        



        