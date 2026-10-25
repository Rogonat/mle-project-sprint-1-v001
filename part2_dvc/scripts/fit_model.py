import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ID_COLS = ["id", "building_id"]
CATEGORICAL_COLS = ["building_type_int"]
BOOL_COLS = ["is_apartment", "studio", "has_elevator"]


def main():
    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    data_params = params["data"]
    split_params = params["split"]
    model_params = params["model"]
    target_col = params["target_col"]

    df = pd.read_csv(data_params["output_path"])
    for col in BOOL_COLS:
        df[col] = df[col].astype(int)

    feature_cols = [c for c in df.columns if c not in ID_COLS + [target_col]]
    numeric_cols = [c for c in feature_cols if c not in CATEGORICAL_COLS]

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=split_params["test_size"], random_state=split_params["random_state"]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLS),
            ("num", "passthrough", numeric_cols),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=model_params["n_estimators"],
        max_depth=model_params["max_depth"],
        random_state=model_params["random_state"],
    )

    pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "r2": float(r2_score(y_test, predictions)),
    }
    print(f"Metrics: {metrics}")

    Path("models").mkdir(parents=True, exist_ok=True)
    Path("cv_results").mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, "models/model.pkl")

    with open("cv_results/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)


if __name__ == "__main__":
    main()
