import requests
import json
from datetime import datetime
from collections import ChainMap
import os
import yaml
import pandas as pd
import cronitor

cwd = os.getcwd()


class CronitorMonitor:
    def __init__(self, api_key_monitor, monitor_client):
        self.monitor = cronitor.Monitor(monitor_client, api_key=api_key_monitor)

    def ping_start(self):
        self.monitor.ping(state="run", message="Start")

    def ping_finish(self):
        self.monitor.ping(state="complete", message="Finish")

    def ping_process(self, process):
        self.monitor.ping(state="ok", message=process)

    def ping_error(self, error):
        self.monitor.ping(state="fail", message=error)


def init_variables():
    # get tags configuration for cronitor.io and PIMS systems
    with open(cwd + "/config/config.yaml") as file:
        documents = yaml.full_load(file)

        server_name = documents["SERVER-HISTORIADOR"]
        futurai_api_key = documents["FUTURAI-API-KEY"]
        futurai_url_api = documents["FUTURAI-URL-API"]
        futurai_company_id = documents["FUTURAI-COMPANY-ID"]
        monitor_client = documents["MONITOR-CLIENT"]
        monitor_api_key = documents["MONITOR-API-KEY"]

    return (
        futurai_api_key,
        futurai_url_api,
        futurai_company_id,
        server_name,
        monitor_client,
        monitor_api_key,
    )


def get_periods(url, company_id, process_id, futurai_api_key):
    url_path = url + "periods"
    params = {"company_id": company_id, "process_id": process_id}

    headers = {"x-api-key": futurai_api_key}

    response = requests.get(url_path, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Falha na chamada à API:", response.status_code)
        return None


def get_list_process():
    """Get the list of process in yaml configuration file
    Params: none
    Returns:
        - process: list of strings"""

    with open(cwd + "/config/config.yaml") as file:
        documents = yaml.full_load(file)
        documents = documents["PROCESS"]
        process = dict(ChainMap(*documents))

    return process


def get_list_tags(process):
    """Get the list of tag by process
    Params:
        - process: string
    Retunrs:
        - tags: list of strings"""

    with open(cwd + "/config/tags.yaml") as file:
        documents = yaml.full_load(file)
        tags = list(documents[process])

    return tags


def get_values_by_tag(server, tag, data_ini, data_fin):
    """Get values by tag
    Params:
        - server: string
        - tag: string
        - data_ini: string
        - data_fin: string
    Retunrs:
        - DataFrame"""

    # setup tag
    point = server.search(tag)[0]

    # get de values with interpolated of 1 minute of interval
    data = point.interpolated_values(data_ini, data_fin, "1m")

    return pd.DataFrame(data)


def prepare_data(df_master, process_id):
    df_master.rename_axis("TIMESTAMP", inplace=True)
    df_master.reset_index(inplace=True)
    df_master["TIMESTAMP"] = df_master["TIMESTAMP"].dt.strftime("%Y-%m-%d %H:%M")
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
    file_name = process_id + "_" + dt_string + ".csv"
    data_json = df_master.to_dict(orient="records")

    return file_name, data_json


def send_data(url, company_id, process_id, file_name, futurai_api_key, data_json):
    url_path = url + "send-data"
    payload = {
        "company_id": company_id,
        "process_id": process_id,
        "file_name": file_name,
        "file": data_json,
    }

    payload = json.dumps(payload)

    headers = {"x-api-key": futurai_api_key, "Content-Type": "application/json"}

    # Enviando a solicitação HTTP com o corpo contendo os parâmetros
    response = requests.post(url_path, data=payload, headers=headers)

    # Verificando a resposta da solicitação
    if response.status_code == 200:
        print("Solicitação enviada com sucesso!")
        return response.status_code
    else:
        print("Ocorreu um erro ao enviar a solicitação:", response.text)
        return None


def get_date():
    with open(cwd + "/config/historico.yaml") as file:
        documents = yaml.full_load(file)

    data_ini = documents["START-DATE"]
    data_fin = documents["END-DATE"]

    return data_ini, data_fin
