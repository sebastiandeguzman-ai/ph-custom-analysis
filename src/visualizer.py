''' TO ADD FOR OTHER PHASES:
#compute_grouped:
df.groupby(CATEGORY_1)->df.groupby(CATEGORY_1, dropna=False)

#compute_grouped_two:
df.groupby([CATEGORY_1, CATEGORY_2])->df.groupby([CATEGORY_1, CATEGORY_2], dropna=False)

#compute_pivot — inside pd.pivot_table(...), add a new kwarg:
        margins_name="All",+ dropna=False,)
        '''

from __future__ import annotations

import os
import pandas as pd

try:
    from . import config
except ImportError:
    import config

CATEGORY_1 = getattr(config, "CATEGORY_1", "countryorigin_iso3")
CATEGORY_2 = getattr(config, "CATEGORY_2", "tq")
MEASURE = getattr(config, "NUM_MEASURE", "dutiablevaluephp")

def _safe_load_csv() -> pd.DataFrame:
    try:
        try:
            from . import loader
        except ImportError:
            import loader
        return loader.load_csv()
    except (SyntaxError, ImportError) as exc:
        print(f"[stats.py] loader.py unavailable ({exc}); "
              f"falling back to plain pd.read_csv({config.DATA_PATH!r})")
        return pd.read_csv(config.DATA_PATH)

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


from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import pandas as pd

try:
    import seaborn as sns
except ImportError:
    sns = None
    print(
        "[visualizer.py] seaborn not installed - heatmap.png will fall back "
        "to matplotlib's imshow(). Run `pip install seaborn` to match the "
        "spec exactly (it asks for a seaborn heatmap)."
    )

try:
    from . import config
except ImportError:
    import config

#match the CATEGORY_1 name used _
CATEGORY_1 = getattr(config, "CATEGORY_1", "countryorigin_iso3")

# bar--
def plot_bar(top10: pd.DataFrame, output_dir: str | None = None) -> str:
    """Matplotlib bar chart of top10.csv values -> bar.png"""
    output_dir = output_dir or config.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "bar.png")

    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(top10[CATEGORY_1].astype(str), top10["measure_sum"])
        ax.set_xlabel(CATEGORY_1)
        ax.set_ylabel("measure_sum")
        ax.set_title("Top 10 groups by measure sum")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        fig.savefig(out_path)
        plt.close(fig)
    except Exception as exc:
        print(f"[visualizer.py] Failed to render bar.png: {exc}")
        raise
    return out_path



# heatmap ---

def plot_heatmap(pivot: pd.DataFrame, output_dir: str | None = None) -> str:
    output_dir = output_dir or config.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "heatmap.png")

    data = pivot.drop(index="All", errors="ignore").drop(columns="All", errors="ignore")

    try:
        fig, ax = plt.subplots(figsize=(10, 8))
        if sns is not None:
            sns.heatmap(data, annot=True, fmt=".0f", cmap="viridis", ax=ax)
        else:
            im = ax.imshow(data.values, cmap="viridis")
            ax.set_xticks(range(len(data.columns)))
            ax.set_xticklabels(data.columns, rotation=45, ha="right")
            ax.set_yticks(range(len(data.index)))
            ax.set_yticklabels(data.index)
            fig.colorbar(im, ax=ax)
        ax.set_title("Measure sum by category (margins excluded)")
        fig.tight_layout()
        fig.savefig(out_path)
        plt.close(fig)
    except Exception as exc:
        print(f"[visualizer.py] Failed to render heatmap.png: {exc}")
        raise
    return out_path

#orchestra--
def run(tables: dict, output_dir: str | None = None) -> dict:
    bar_path = plot_bar(tables["top10"], output_dir)
    heatmap_path = plot_heatmap(tables["pivot"], output_dir)
    return {"bar": bar_path, "heatmap": heatmap_path}


if __name__ == "__main__":
    import numpy as np

    rng = np.random.default_rng(0)
    fake_top10 = pd.DataFrame({
        CATEGORY_1: [f"cat{i}" for i in range(6)],
        "measure_sum": rng.integers(10, 200, size=6),
    })
    fake_pivot = pd.DataFrame(
        rng.integers(0, 100, size=(3, 3)),
        index=["A", "B", "All"],
        columns=["x", "y", "All"],
    )
    plot_bar(fake_top10, output_dir="/tmp/phase5_test")
    plot_heatmap(fake_pivot, output_dir="/tmp/phase5_test")
    print("Standalone test charts written to /tmp/phase5_test")



try:
    from . import config, stats, visualizer
except ImportError:
    import config
    import stats
    import visualizer


def main() -> None:
    df = loader.load_csv()

    #filter
    filtered = transform.filter_by_quarter_and_origin(df, QUARTER, COUNTRY_ISO3)
    filtered = transform.add_duty_per_weight(filtered)
    filtered = transform.add_high_value_flag(filtered)

    #aggr
    grouped_df = aggregate.grouped(filtered)
    grouped_two_df = aggregate.grouped_two(filtered)
    aggregate.export_grouped_tables(grouped_df, grouped_two_df, output_dir=config.OUTPUT_DIR)

    #validate pivot
    pivot_df = validate.generate_pivot(filtered)
    top10_df = validate.generate_top10(grouped_df)
    validate.run_validations(
        raw_rows=len(df),
        raw_sum=float(df[config.NUM_MEASURE].sum()) if hasattr(config, "NUM_MEASURE") else None,
        selected_rows=len(filtered),
        grouped_row_sum=int(grouped_df["row_count"].sum()),
        pivot_interior_sum=float(
            pivot_df.drop(index="All", errors="ignore").drop(columns="All", errors="ignore").to_numpy().sum()
        ),
    )

    #charts--
    tables = {"top10": top10_df, "pivot": pivot_df}
    charts = visualizer.run(tables, output_dir=config.OUTPUT_DIR)

    print(f"Pipeline complete: {config.OUTPUT_DIR}")
    print(" - grouped.csv, grouped_two.csv, pivot.csv, top10.csv, validation.csv")
    print(f" - {charts['bar']}")
    print(f" - {charts['heatmap']}")

if __name__ == "__main__":
    main()
