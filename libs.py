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
    """
    Classe para monitoramento via Cronitor.
    Implementa um método genérico de ping para evitar código repetitivo.
    """

    def __init__(self, api_key_monitor, monitor_client):
        self.monitor = cronitor.Monitor(monitor_client, api_key=api_key_monitor)

    def _ping(self, state, message):
        """Método interno para envio de pings ao monitoramento."""
        self.monitor.ping(state=state, message=message)

    def ping_start(self):
        self._ping("run", "Start")

    def ping_finish(self):
        self._ping("complete", "Finish")

    def ping_process(self, process):
        self._ping("ok", process)

    def ping_error(self, error):
        self._ping("fail", error)


def init_variables():
    """
    Lê as variáveis de configuração do arquivo YAML e as retorna em um dicionário.
    Inclui tratamento de erro para garantir que o sistema não falhe caso o arquivo esteja ausente ou mal formatado.
    """
    config_path = os.path.join(cwd, "config/config.yaml")

    try:
        with open(config_path, "r") as file:
            documents = yaml.full_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {config_path}"
        )
    except yaml.YAMLError as e:
        raise ValueError(f"Erro ao carregar o arquivo YAML: {str(e)}")

    return {
        "server_name": documents.get("SERVER-HISTORIADOR", ""),
        "futurai_api_key": documents.get("FUTURAI-API-KEY", ""),
        "futurai_url_api": documents.get("FUTURAI-URL-API", ""),
        "futurai_company_id": documents.get("FUTURAI-COMPANY-ID", ""),
        "monitor_client": documents.get("MONITOR-CLIENT", ""),
        "monitor_api_key": documents.get("MONITOR-API-KEY", ""),
    }


def get_periods(url, company_id, process_id, futurai_api_key):
    """
    Obtém os períodos a serem processados a partir da API Futurai.
    Implementa tratamento de erro para evitar falhas inesperadas.
    """
    url_path = f"{url}periods"
    params = {"company_id": company_id, "process_id": process_id}
    headers = {"x-api-key": futurai_api_key}

    try:
        response = requests.get(url_path, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao chamar API {url_path}: {str(e)}")
        return None


def get_list_process():
    """
    Obtém a lista de processos a partir do arquivo de configuração YAML.
    Implementa validação para garantir que os dados estejam corretamente formatados.
    """
    config_path = os.path.join(cwd, "config/config.yaml")

    try:
        with open(config_path, "r") as file:
            documents = yaml.full_load(file)
            return dict(ChainMap(*documents.get("PROCESS", [])))
    except FileNotFoundError:
        raise FileNotFoundError("Arquivo config.yaml não encontrado.")
    except yaml.YAMLError as e:
        raise ValueError(f"Erro ao carregar config.yaml: {str(e)}")


def get_list_tags(process):
    """
    Obtém a lista de tags associadas a um processo a partir do arquivo tags.yaml.
    Retorna uma lista vazia caso o processo não esteja configurado.
    """
    tags_path = os.path.join(cwd, "config/tags.yaml")

    try:
        with open(tags_path, "r") as file:
            documents = yaml.full_load(file)
        return list(documents.get(process, []))
    except FileNotFoundError:
        raise FileNotFoundError("Arquivo tags.yaml não encontrado.")
    except yaml.YAMLError as e:
        raise ValueError(f"Erro ao carregar tags.yaml: {str(e)}")


def get_values_by_tag(server, tag, data_ini, data_fin):
    """
    Obtém os valores históricos de uma tag específica do servidor PIMS.
    Implementa validação para garantir que a tag esteja presente.
    """
    points = server.search(tag)

    if not points:
        raise ValueError(f"Tag '{tag}' não encontrada no servidor.")

    point = points[0]  # Usa o primeiro resultado retornado
    data = point.interpolated_values(data_ini, data_fin, "1m")

    return pd.DataFrame(data)


def prepare_data(df_master, process_id):
    """
    Formata os dados extraídos para envio à API.
    Converte timestamps e gera um nome de arquivo único baseado no horário atual.
    """
    df_master.rename_axis("TIMESTAMP", inplace=True)
    df_master.reset_index(inplace=True)
    df_master["TIMESTAMP"] = df_master["TIMESTAMP"].dt.strftime("%Y-%m-%d %H:%M")

    dt_string = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    file_name = f"{process_id}_{dt_string}.csv"
    data_json = df_master.to_dict(orient="records")

    return file_name, data_json


def send_data(url, company_id, process_id, file_name, futurai_api_key, data_json):
    """
    Envia os dados processados para a API Futurai.
    Implementa tratamento de erro para falhas de conexão e resposta inesperada.
    """
    url_path = f"{url}send-data"
    payload = json.dumps(
        {
            "company_id": company_id,
            "process_id": process_id,
            "file_name": file_name,
            "file": data_json,
        }
    )

    headers = {"x-api-key": futurai_api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(url_path, data=payload, headers=headers)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar dados para {url_path}: {str(e)}")
        return None


def get_date():
    """
    Obtém a data de início e fim do processamento a partir do arquivo historico.yaml.
    Implementa tratamento de erro para evitar falhas ao carregar o YAML.
    """
    history_path = os.path.join(cwd, "config/historico.yaml")

    try:
        with open(history_path, "r") as file:
            documents = yaml.full_load(file)
        return documents.get("START-DATE"), documents.get("END-DATE")
    except FileNotFoundError:
        raise FileNotFoundError("Arquivo historico.yaml não encontrado.")
    except yaml.YAMLError as e:
        raise ValueError(f"Erro ao carregar historico.yaml: {str(e)}")
