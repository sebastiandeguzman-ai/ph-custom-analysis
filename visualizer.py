
from __future__ import annotations

import os
import pandas as pd

try:
    from . import config
except ImportError:
    import config

CATEGORY_1 = getattr(config, "CATEGORY_1", "category")
CATEGORY_2 = getattr(config, "CATEGORY_2", "subcategory")
MEASURE = getattr(config, "NUM_MEASURE", "value")
#to fix: catgery name s 

def _safe_load_csv() -> pd.DataFrame:

    try:
        from . import loader
    except ImportError:
        import loader
    return loader.load_csv()

def compute_grouped(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(CATEGORY_1)
        .agg(
            row_count=(MEASURE, "size"),
            valid_measure_count=(MEASURE, "count"),
            measure_sum=(MEASURE, "sum"),
            measure_mean=(MEASURE, "mean"),
        )
        .reset_index()
    )
    return grouped

# grouped_two.csv__
def compute_grouped_two(df: pd.DataFrame) -> pd.DataFrame:
    grouped_two = (
        df.groupby([CATEGORY_1, CATEGORY_2])
        .agg(
            row_count=(MEASURE, "size"),
            measure_sum=(MEASURE, "sum"),
        )
        .reset_index()
    )
    return grouped_two


# pivot.csv----
def compute_pivot(df: pd.DataFrame) -> pd.DataFrame:
    pivot = pd.pivot_table(
        df,
        index=CATEGORY_1,
        columns=CATEGORY_2,
        values=MEASURE,
        aggfunc="sum",
        margins=True,
        margins_name="All",
    )
    return pivot



#top10.csv __-
def compute_top10(grouped: pd.DataFrame) -> pd.DataFrame:
    top10 = grouped.sort_values("measure_sum", ascending=False).head(10)
    return top10.reset_index(drop=True)


def run(df: pd.DataFrame | None = None, output_dir: str | None = None) -> dict:
    output_dir = output_dir or config.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    if df is None:
        df = _safe_load_csv()

    grouped = compute_grouped(df)
    grouped_two = compute_grouped_two(df)
    pivot = compute_pivot(df)
    top10 = compute_top10(grouped)

    grouped.to_csv(os.path.join(output_dir, "grouped.csv"), index=False)
    grouped_two.to_csv(os.path.join(output_dir, "grouped_two.csv"), index=False)
    pivot.to_csv(os.path.join(output_dir, "pivot.csv"))
    top10.to_csv(os.path.join(output_dir, "top10.csv"), index=False)

    return {
        "grouped": grouped,
        "grouped_two": grouped_two,
        "pivot": pivot,
        "top10": top10,
    }


if __name__ == "__main__":
    tables = run()
    print(tables["top10"])
