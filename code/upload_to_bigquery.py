from google.cloud import bigquery
from google.oauth2 import service_account
from create_df_security import fct 

df = fct()


def upload_dataframe_to_bigquery(
    key_path: str,
    table_id: str,
    write_disposition: str = "WRITE_TRUNCATE"
) -> None:
    """Upload a DataFrame to BigQuery."""
    print(f"Loaded DataFrame: {len(df)} rows, {len(df.columns)} columns")
    
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    
    job_config = bigquery.LoadJobConfig(write_disposition=write_disposition)
    
    print(f"Uploading to {table_id}...")
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    
    table = client.get_table(table_id)
    print(f"Upload successful: {table.num_rows} rows, {len(table.schema)} columns")


if __name__ == "__main__":
    upload_dataframe_to_bigquery(
        key_path="key_group_5.json",
        table_id="ai-technologies-ur2.dataset_groupe_5.events"
    )