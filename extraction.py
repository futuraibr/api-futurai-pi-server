import PIconnect as PI
import pandas as pd
import yaml
import os
from datetime import datetime, timedelta
from collections import ChainMap

PI.PIConfig.DEFAULT_TIMEZONE = "America/Sao_Paulo"
# current directory
cwd = os.getcwd()


def get_date():
    with open(cwd + "/config/setup.yaml") as file:
        documents = yaml.full_load(file)

    data_ini = documents["START-DATE"]
    data_fin = documents["END-DATE"]

    return data_ini, data_fin


def get_list_process():
    """Get the list of process in yaml configuration file
    Params: none
    Retunrs: List of process"""

    with open(cwd + "/config/aws.yaml") as file:
        documents = yaml.full_load(file)
        documents = documents["process"]
        documents = dict(ChainMap(*documents))
        process = list(documents.keys())

    return process


def get_list_tags(process):
    """Get the list of tag by process
    Params: process
    Retunrs: List of tags"""

    with open(cwd + "/config/tags.yaml") as file:
        documents = yaml.full_load(file)
        tags = list(documents[process])

    return tags


def get_values_by_tag(server, tag, data_ini, data_fin):

    # setup of tag
    point = server.search(tag)[0]

    # get de values with interpolated of 1 minute of interval
    data = point.interpolated_values(data_ini, data_fin, "1m")

    return pd.DataFrame(data)


def extraction(monitor, server_name):
    with PI.PIServer(server=server_name) as server:
        data_ini, data_fin = get_date()

        for process in get_list_process():
            try:
                df_master = pd.DataFrame([])
                tags = get_list_tags(process)

                df_master = get_values_by_tag(server, tags[0], data_ini, data_fin)
                df_master.reset_index(inplace=True)
                df_master.columns = ["TIMESTAMP", tags[0]]

                tags.pop(0)

                for tag in tags:
                    df_aux = get_values_by_tag(server, tag, data_ini, data_fin)
                    df_aux.reset_index(inplace=True)
                    df_aux.columns = ["TIMESTAMP", tag]
                    df_aux.drop("TIMESTAMP", axis=1, inplace=True)
                    df_master = df_master.merge(
                        df_aux, left_index=True, right_index=True
                    )

                print(df_master)
                df_master.set_index("TIMESTAMP", inplace=True)
                now = datetime.now()
                dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
                file_name = cwd + "/data/queue/" + process + "_" + dt_string + ".csv"

                df_master.to_csv(file_name, sep=";")

            except Exception as e:
                monitor.ping(state="fail", message=e)
                raise

            monitor.ping(state="ok", message=("Arquivo csv gerado: " + file_name))

        data_ini = datetime.strptime(data_ini, "%Y-%m-%d %H:%M:%S")
        data_fin = datetime.strptime(data_fin, "%Y-%m-%d %H:%M:%S")

        data_ini = data_ini + timedelta(minutes=120)
        data_fin = data_fin + timedelta(minutes=120)

        data_ini = data_ini.strftime("%Y-%m-%d %H:%M:%S")
        data_fin = data_fin.strftime("%Y-%m-%d %H:%M:%S")

        new_dates = {"START-DATE": data_ini, "END-DATE": data_fin}

        with open(cwd + "/config/setup.yaml", "w") as file:
            documents = yaml.dump(new_dates, file, sort_keys=False)
