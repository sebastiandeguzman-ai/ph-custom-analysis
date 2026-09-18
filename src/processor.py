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
