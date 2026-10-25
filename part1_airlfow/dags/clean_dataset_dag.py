"""Clean flats_buildings and write the result to flats_buildings_clean."""

import pendulum
import pandas as pd
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

from steps.cleaning import clean_dataset

CONN_ID = "project_db"
TMP_DIR = "/opt/airflow/data/tmp"


@dag(
    dag_id="clean_dataset",
    schedule=None,
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["sprint", "stage-2"],
)
def clean_dataset_dag():

    @task
    def extract() -> str:
        hook = PostgresHook(postgres_conn_id=CONN_ID)
        df = hook.get_pandas_df("SELECT * FROM public.flats_buildings;")
        path = f"{TMP_DIR}/flats_buildings.csv"
        df.to_csv(path, index=False)
        return path

    @task
    def transform(path: str) -> str:
        df = pd.read_csv(path)
        cleaned, report = clean_dataset(df)
        print(f"Cleaning report: {report}")
        out_path = f"{TMP_DIR}/flats_buildings_clean.csv"
        cleaned.to_csv(out_path, index=False)
        return out_path

    @task
    def load(path: str):
        hook = PostgresHook(postgres_conn_id=CONN_ID)
        cleaned = pd.read_csv(path)
        engine = hook.get_sqlalchemy_engine()
        cleaned.to_sql("flats_buildings_clean", engine, if_exists="replace", index=False)

    load(transform(extract()))


clean_dataset_dag()
