import PIconnect as PI
import pandas as pd

from libs import (
    get_list_process,
    get_periods,
    get_values_by_tag,
    get_list_tags,
    prepare_data,
    send_data,
    init_variables,
    CronitorMonitor,
)

# Configuração do fuso horário para garantir que os timestamps do sistema PIMS estejam corretos
PI.PIConfig.DEFAULT_TIMEZONE = "America/Sao_Paulo"


def main():
    """
    Função principal responsável por extrair dados do sistema PIMS, processá-los e enviá-los para a API FuturAI.
    Utiliza monitoramento via Cronitor para rastreamento do status da execução.
    """

    # Inicializa as variáveis de configuração a partir do arquivo YAML e as armazena em um dicionário
    config = init_variables()

    # Inicia o monitoramento utilizando um gerenciador de contexto, garantindo que os pings sejam finalizados corretamente
    with CronitorMonitor(
        config["monitor_client"], config["monitor_api_key"]
    ) as monitor:

        try:
            # Obtém a lista de processos a serem analisados
            all_process = get_list_process()

            # Estabelece conexão com o servidor PIMS dentro de um gerenciador de contexto
            with PI.PIServer(server=config["server_name"]) as server:

                # Itera sobre todos os processos cadastrados
                for process_name, process_id in all_process.items():

                    # Obtém os períodos de tempo para os quais os dados serão coletados
                    all_periods = get_periods(
                        company_id=config["futurai_company_id"],
                        process_id=process_id,
                        url=config["futurai_url_api"],
                        futurai_api_key=config["futurai_api_key"],
                    )

                    # Processa os dados para cada período identificado
                    for period in all_periods:
                        try:
                            # Recupera as tags associadas ao processo atual
                            tags = get_list_tags(process_name)

                            # Obtém os valores históricos das tags e armazena os DataFrames em uma lista
                            df_list = [
                                get_values_by_tag(
                                    server,
                                    tag,
                                    period["start_time"],
                                    period["end_time"],
                                ).rename(columns={tag: tag})
                                for tag in tags
                            ]

                            # Concatena os DataFrames em um único DataFrame mestre, garantindo alinhamento temporal dos dados
                            df_master = pd.concat(df_list, axis=1)
                            df_master.reset_index(inplace=True)
                            df_master.set_index("TIMESTAMP", inplace=True)

                            # Prepara os dados para envio à API, gerando arquivo e estrutura JSON
                            file_name, data_json = prepare_data(
                                df_master, process_id=process_id
                            )

                            # Realiza o envio dos dados para a API FuturAI
                            response = send_data(
                                company_id=config["futurai_company_id"],
                                process_id=process_id,
                                url=config["futurai_url_api"],
                                futurai_api_key=config["futurai_api_key"],
                                file_name=file_name,
                                data_json=data_json,
                            )

                            # Formata mensagem de monitoramento garantindo robustez na exibição dos períodos analisados
                            message_ping = "Process {} - {} - {}".format(
                                process_name,
                                period.get("start_time", "N/A"),
                                period.get("end_time", "N/A"),
                            )

                            # Registra um ping no monitoramento indicando que o processamento do período foi concluído
                            monitor.ping_process(message_ping)

                        except Exception as e:
                            # Captura erros individuais por período e os registra sem interromper a execução do restante dos períodos
                            monitor.ping_error(
                                f"Erro no período {period.get('start_time', 'N/A')} - {period.get('end_time', 'N/A')}: {str(e)}"
                            )

        except Exception as e:
            # Captura exceções globais da execução do script e registra no monitoramento
            monitor.ping_error(str(e))


if __name__ == "__main__":
    # Executa o script principal
    main()
