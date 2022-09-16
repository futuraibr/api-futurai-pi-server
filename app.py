from integration import integration
from extraction import extraction
from time import sleep
import yaml
import os
import cronitor

def main():
    
    # current directory
    cwd = os.getcwd()

    # get tags configuration for conitor.io and PIMS systems
    with open(cwd + "/config/config.yaml") as file:
        documents = yaml.full_load(file)
        api_key_monitor = documents["monitor-api-key"]
        server_name = documents["server-historiador"]
        monitor_client = documents["monitor-client"]

    # set cronitor.io
    cronitor.api_key = api_key_monitor
    monitor = cronitor.Monitor(monitor_client)

    # start extraction
    monitor.ping(state="run",message="Iniciando extração...")
    extraction(monitor,server_name)

    sleep(1)

    # start Integration
    integration(monitor)
    monitor.ping(state="complete",message="Finalizando integração...")


if __name__ == '__main__':
   main()