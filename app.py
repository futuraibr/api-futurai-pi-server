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
)


# set timezone for PIMS System
PI.PIConfig.DEFAULT_TIMEZONE = "America/Sao_Paulo"


def main():

    futurai_api_key, futurai_url_api, futurai_company_id, server_name = init_variables()

    all_process = get_list_process()

    # connect with PIMS System
    with PI.PIServer(server=server_name) as server:

        # loop by process
        for process in all_process:

            process_name = process
            process_id = all_process[process]

            all_periods = get_periods(
                company_id=futurai_company_id,
                process_id=process,
                url=futurai_url_api,
                futurai_api_key=futurai_api_key,
            )

            for period in all_periods:

                # init dataframe master of process
                df_master = pd.DataFrame([])
                df_master = get_values_by_tag(
                    server, tags[0], period["start_time"], period["end_time"]
                )
                df_master.reset_index(inplace=True)
                df_master.columns = ["TIMESTAMP", tags[0]]
                tags.pop(0)

                tags = get_list_tags(process_name)

                # loop by tag
                for tag in tags:

                    # get values by tag
                    df_aux = get_values_by_tag(
                        server, tag, period["start_time"], period["end_time"]
                    )
                    df_aux.reset_index(inplace=True)
                    df_aux.columns = ["TIMESTAMP", tag]
                    df_aux.drop("TIMESTAMP", axis=1, inplace=True)

                    # merge dataframe master with dataframe aux
                    df_master = df_master.merge(
                        df_aux, left_index=True, right_index=True
                    )

                df_master.set_index("TIMESTAMP", inplace=True)

                file_name, data_json = prepare_data(df_master, process_id=process_id)

                response = send_data(
                    company_id=futurai_company_id,
                    process_id=process_id,
                    url=futurai_url_api,
                    futurai_api_key=futurai_api_key,
                    file_name=file_name,
                    data_json=data_json,
                )

                print(response)


if __name__ == "__main__":
    main()
