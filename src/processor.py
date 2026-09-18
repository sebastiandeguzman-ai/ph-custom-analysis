import sys
import pandas as pd

def filter_by_quarter_and_origin(
    df: pd.DataFrame,
    quarter: str,
    country_iso3: str
) -> pd.DataFrame:

    mask = (
        (df["tq"] == quarter)
        & (df["countryorigin_iso3"].notna())
        & (df["countryorigin_iso3"] == country_iso3)
    )
    filtered = df.loc[mask]
    
    if filtered.empty:
        message = (
            f"No records found for quarter='{quarter}' "
            f"and countryorigin_iso3='{country_iso3}'."
        )
        print(message, file=sys.stderr)
        raise ValueError(message)

    return filtered

def add_duty_per_weight(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["duty_per_weight"] = result["dutiestaxes"] / result["q"].replace(0, pd.NA)
    return result

def add_high_value_flag(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    threshold = result["dutiablevaluephp"].quantile(0.75)
    result["high_value_flag"] = result["dutiablevaluephp"] > threshold
    return result

def grouped(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("countryorigin_iso3", dropna=False).agg(
        row_count=("countryorigin_iso3", "size"),
        valid_measure_count=("dutiablevaluephp", "count"),
        measure_sum=("dutiablevaluephp", "sum"),
        measure_mean=("dutiablevaluephp", "mean"),
    ).reset_index()
    return grouped

def grouped_two(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(
        ["countryorigin_iso3", "tq"], dropna=False
    ).agg(
        row_count=("countryorigin_iso3", "size"),
        measure_sum=("dutiablevaluephp", "sum"),
    ).reset_index()
    return grouped
