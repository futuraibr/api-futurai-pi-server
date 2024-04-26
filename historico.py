import PIconnect as PI
import pandas as pd
import os
from datetime import datetime

from libs import (
    get_list_process,
    get_values_by_tag,
    get_list_tags,
    init_variables,
    get_date,
)


PI.PIConfig.DEFAULT_TIMEZONE = "America/Sao_Paulo"
# current directory
cwd = os.getcwd()

_, _, _, server_name, _, _ = init_variables()


def extraction():
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
                file_name = process + "_" + dt_string + ".csv"

                df_master.to_csv(file_name, sep=";")

            except Exception as e:
                print(e)
                raise


if __name__ == "__main__":
    extraction()
