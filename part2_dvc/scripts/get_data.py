import os
from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy import create_engine


def main():
    with open("params.yaml") as f:
        params = yaml.safe_load(f)["data"]

    user = os.environ.get("POSTGRES_USER", "mle_user")
    password = os.environ.get("POSTGRES_PASSWORD", "mle_password")
    host = os.environ.get("POSTGRES_HOST", "project-db")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "buildings_flats")

    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")
    df = pd.read_sql(f"SELECT * FROM public.{params['table_name']};", engine)

    out_path = Path(params["output_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()
