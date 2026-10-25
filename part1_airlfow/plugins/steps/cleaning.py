"""Data cleaning for flats_buildings"""

from typing import Tuple

import numpy as np
import pandas as pd

ZERO_AS_MISSING_COLS = ["kitchen_area", "living_area"]
IQR_OUTLIER_COLS = ["ceiling_height", "total_area"]
IQR_K = 1.5


def drop_duplicate_flats(df: pd.DataFrame, id_col: str = "id") -> pd.DataFrame:
    return df.drop_duplicates(subset=[id_col], keep="first").reset_index(drop=True)


def fix_zero_as_missing(df: pd.DataFrame, columns=ZERO_AS_MISSING_COLS) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        df.loc[df[col] <= 0, col] = np.nan
        group_median = df.groupby("rooms")[col].transform("median")
        df[col] = df[col].fillna(group_median)
        df[col] = df[col].fillna(df[col].median())
    return df


def remove_price_outliers(df: pd.DataFrame, price_col: str = "price", k: float = IQR_K) -> pd.DataFrame:
    log_price = np.log1p(df[price_col])
    q1, q3 = log_price.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    mask = log_price.between(lower, upper)
    return df.loc[mask].reset_index(drop=True)


def remove_iqr_outliers(df: pd.DataFrame, columns=IQR_OUTLIER_COLS, k: float = IQR_K) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    for col in columns:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - k * iqr, q3 + k * iqr
        mask &= df[col].between(lower, upper)
    return df.loc[mask].reset_index(drop=True)


def clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    report = {"input_rows": len(df)}

    df = drop_duplicate_flats(df)
    report["after_dedup"] = len(df)

    df = fix_zero_as_missing(df)
    report["after_missing_fix"] = len(df)

    df = remove_price_outliers(df)
    report["after_price_outliers"] = len(df)

    df = remove_iqr_outliers(df)
    report["after_iqr_outliers"] = len(df)

    return df, report
