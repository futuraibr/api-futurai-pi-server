from integration import integration
from extraction import extraction
from time import sleep
import yaml
import os
import cronitor


# current directory
cwd = os.getcwd()

# get api key for conitor.io
with open(cwd + "/config/config.yaml") as file:
    documents = yaml.full_load(file)
    api_key_monitor = documents["monitor-api-key"]
    server_name = documents["server-historiador"]

cronitor.api_key = api_key_monitor
monitor = cronitor.Monitor("bopaper")

print("Realizando extração...")
monitor.ping(state="run")
extraction(monitor,server_name)
sleep(1)
print("Realizando envio dos arquivos...")
integration(monitor)
monitor.ping(state="complete")
