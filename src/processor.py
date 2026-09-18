import pandas as pd

def generate_pivot(filtered_df):
    """Creates a pivot table of dutiable value by country and tariff quota."""
    pivot_df = filtered_df.pivot_table(
        index='countryorigin_iso3',
        columns='tq',
        values='dutiablevaluephp',
        aggfunc='sum',
        margins=True,
        margins_name='All',
        dropna=False
    )
    pivot_df.to_csv('outputs/pivot.csv')
    return pivot_df

def generate_top10(grouped_df):
    """Extracts the top 10 groups by total measure sum."""
    top10_df = grouped_df.sort_values(by='measure_sum', ascending=False).head(10)
    top10_df.to_csv('outputs/top10.csv', index=False)
    return top10_df