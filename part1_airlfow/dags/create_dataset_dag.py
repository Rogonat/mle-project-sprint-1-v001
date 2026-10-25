"""Join buildings and flats into one table, flats_buildings."""

import pendulum
import pandas as pd
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

CONN_ID = "project_db"
TMP_DIR = "/opt/airflow/data/tmp"

MERGED_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS public.flats_buildings (
    id int8 PRIMARY KEY,
    building_id int8,
    floor int8,
    kitchen_area float8,
    living_area float8,
    rooms int8,
    is_apartment bool,
    studio bool,
    total_area float8,
    price int8,
    build_year int8,
    building_type_int int8,
    latitude float8,
    longitude float8,
    ceiling_height float8,
    flats_count int8,
    floors_total int8,
    has_elevator bool
);
"""


@dag(
    dag_id="create_dataset",
    schedule=None,
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["sprint", "stage-1"],
)
def create_dataset_dag():

    @task
    def create_table():
        PostgresHook(postgres_conn_id=CONN_ID).run(MERGED_TABLE_DDL)

    @task
    def extract() -> dict:
        hook = PostgresHook(postgres_conn_id=CONN_ID)
        buildings = hook.get_pandas_df("SELECT * FROM public.buildings;")
        flats = hook.get_pandas_df("SELECT * FROM public.flats;")
        buildings_path = f"{TMP_DIR}/buildings.csv"
        flats_path = f"{TMP_DIR}/flats.csv"
        buildings.to_csv(buildings_path, index=False)
        flats.to_csv(flats_path, index=False)
        return {"buildings_path": buildings_path, "flats_path": flats_path}

    @task
    def transform(paths: dict) -> str:
        buildings = pd.read_csv(paths["buildings_path"])
        flats = pd.read_csv(paths["flats_path"])
        merged = flats.merge(
            buildings, left_on="building_id", right_on="id", how="left", suffixes=("", "_building")
        )
        merged = merged.drop(columns=["id_building"])
        merged_path = f"{TMP_DIR}/merged.csv"
        merged.to_csv(merged_path, index=False)
        return merged_path

    @task
    def load(merged_path: str):
        hook = PostgresHook(postgres_conn_id=CONN_ID)
        merged = pd.read_csv(merged_path)
        engine = hook.get_sqlalchemy_engine()
        hook.run("TRUNCATE TABLE public.flats_buildings;")
        merged.to_sql("flats_buildings", engine, if_exists="append", index=False)

    created = create_table()
    extracted = extract()
    created >> extracted
    load(transform(extracted))


create_dataset_dag()
