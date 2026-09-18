import sys
import pandas as pd

def filter_by_quarter_and_origin(
    df: pd.DataFrame,
    quarter: str,
    country_iso3: str
) -> pd.DataFrame:
