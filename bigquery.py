from google.oauth2 import service_account
import pandas_gbq
import pandas as pd

df = pd.read_csv("df_event.csv")
credentials = service_account.Credentials.from_service_account_file(
    "sa-key-group-5.json",
)
pandas_gbq.to_gbq(
    df,
    "dataset_group_5.my_table",
    project_id="ai-technologies-ur2",
    credentials=credentials,
)
