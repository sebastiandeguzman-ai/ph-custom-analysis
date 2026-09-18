from __future__ import annotations


import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


try:
    from . import config
except ImportError:
    import config


try:
    from .loader import load_csv
except ImportError:
    import loader
    load_csv = loader.load_csv


try:
    from .processor import (
        filter_by_quarter_and_origin,
        add_duty_per_weight,
        add_high_value_flag,
        grouped as compute_grouped,
        grouped_two as compute_grouped_two,
        export_grouped_tables,
    )
except ImportError:
    import processor
    compute_grouped = processor.grouped
    compute_grouped_two = processor.grouped_two
    export_grouped_tables = processor.export_grouped_tables


try:
    from .validator import run_validations
except ImportError:
    import validator
    run_validations = validator.run_validations




# STATS MODULE & BENCHMARK


def compute_pivot(df: pd.DataFrame) -> pd.DataFrame:
    cat1 = getattr(config, "CATEGORY_1", "countryorigin_iso3")
    cat2 = getattr(config, "CATEGORY_2", "tq")
    measure = getattr(config, "NUM_MEASURE", "dutiablevaluephp")
   
    return pd.pivot_table(
        df,
        index=cat1,
        columns=cat2,
        values=measure,
        aggfunc="sum",
        margins=True,
        margins_name="All",
        dropna=False,
    )




def compute_top10(grouped_df: pd.DataFrame) -> pd.DataFrame:
    top10 = grouped_df.sort_values("measure_sum", ascending=False).head(10)
    return top10.reset_index(drop=True)




def numpy_benchmark(df: pd.DataFrame) -> dict[str, float]:
    measure = getattr(config, "NUM_MEASURE", "dutiablevaluephp")
    data_array = df[measure].to_numpy(dtype=np.float64)


    start_pandas = time.perf_counter()
    pd_sum = float(df[measure].sum())
    pandas_time = time.perf_counter() - start_pandas


    start_numpy = time.perf_counter()
    np_sum = float(np.sum(data_array))
    numpy_time = time.perf_counter() - start_numpy


    return {
        "pandas_time_sec": pandas_time,
        "numpy_time_sec": numpy_time,
        "pandas_sum": pd_sum,
        "numpy_sum": np_sum,
    }




# VISUALIZER MODULE


def plot_bar(top10_df: pd.DataFrame, output_dir: str) -> str:
    cat1 = getattr(config, "CATEGORY_1", "countryorigin_iso3")
    fig, ax = plt.subplots(figsize=(10, 6))
   
    ax.bar(top10_df[cat1].astype(str), top10_df["measure_sum"] / 1e9, color="#1f77b4")
    ax.set_title("Top 10 Origin Countries by Dutiable Value (in Billions PHP)")
    ax.set_xlabel("Country Code")
    ax.set_ylabel("Dutiable Value (Billion PHP)")
    plt.xticks(rotation=45)
    plt.tight_layout()


    file_path = os.path.join(output_dir, "bar.png")
    plt.savefig(file_path, dpi=300)
    plt.close()
    return file_path




def plot_heatmap(pivot_df: pd.DataFrame, output_dir: str) -> str:
    cleaned_pivot = pivot_df.drop(index="All", columns="All", errors="ignore").fillna(0)
    fig, ax = plt.subplots(figsize=(12, 8))


    sns.heatmap(
        cleaned_pivot / 1e9,
        annot=True,
        fmt=".1f",
        cmap="Blues",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Dutiable Value (Billion PHP)"},
    )
    ax.set_title("Dutiable Value Heatmap by Origin Country and Quarter")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Origin Country")
    plt.tight_layout()


    file_path = os.path.join(output_dir, "heatmap.png")
    plt.savefig(file_path, dpi=300)
    plt.close()
    return file_path


def run_pipeline() -> None:
    output_dir = getattr(config, "OUTPUT_DIR", "outputs")
    os.makedirs(output_dir, exist_ok=True)


    df = load_csv()


    bench_results = numpy_benchmark(df)
    print(f"[Benchmark] Pandas time: {bench_results['pandas_time_sec']:.6f}s")
    print(f"[Benchmark] NumPy time:  {bench_results['numpy_time_sec']:.6f}s")


    grouped = compute_grouped(df)
    grouped_two = compute_grouped_two(df)
    pivot = compute_pivot(df)
    top10 = compute_top10(grouped)


    export_grouped_tables(grouped, grouped_two, output_dir)
    pivot.to_csv(os.path.join(output_dir, "pivot.csv"))
    top10.to_csv(os.path.join(output_dir, "top10.csv"), index=False)


    plot_bar(top10, output_dir)
    plot_heatmap(pivot, output_dir)


    raw_measure = getattr(config, "NUM_MEASURE", "dutiablevaluephp")
    raw_rows = len(df)
    raw_sum = float(df[raw_measure].sum())
    grouped_row_sum = int(grouped["row_count"].sum())
    pivot_interior_sum = float(pivot.drop(index="All", columns="All", errors="ignore").sum().sum())


    run_validations(
        raw_rows=raw_rows,
        raw_sum=raw_sum,
        selected_rows=raw_rows,
        grouped_row_sum=grouped_row_sum,
        pivot_interior_sum=pivot_interior_sum,
    )




if __name__ == "__main__":
    run_pipeline()

