from src import loader, processor, validator


def main():
    print("=== Phase 1: Loading Data ===")
    df = loader.load_csv()
    
    # 1. Capture raw metrics immediately after loading
    raw_rows = len(df)
    raw_sum = df["dutiablevaluephp"].sum()
    print("Loader operational. Shape:", df.shape)

    print("\n=== Phase 2: Processing & Grouping ===")
    processed_df = processor.add_duty_per_weight(df)
    processed_df = processor.add_high_value_flag(processed_df)
    grouped_df = processor.grouped(processed_df)
    grouped_two_df = processor.grouped_two(processed_df)
    processor.export_grouped_tables(grouped_df, grouped_two_df)
    print("Phase 2 complete. Shape:", processed_df.shape)

    print("\n=== Phase 3: Reshaping Data ===")
    pivot_df = processor.generate_pivot(processed_df)
    top10_df = processor.generate_top10(grouped_df)

    # 2. Calculate validation inputs
    selected_rows = raw_rows
    grouped_row_sum = grouped_df["row_count"].sum()

    # Calculate interior sum excluding 'All' margins safely
    if "All" in pivot_df.index and "All" in pivot_df.columns:
        pivot_interior_sum = (
            pivot_df.drop(index="All", columns="All").fillna(0).values.sum()
        )
    else:
        pivot_interior_sum = pivot_df.fillna(0).values.sum()

    print("\n=== Phase 3: Running Validations ===")
    validator.run_validations(
        raw_rows=raw_rows,
        raw_sum=raw_sum,
        selected_rows=selected_rows,
        grouped_row_sum=grouped_row_sum,
        pivot_interior_sum=pivot_interior_sum,
    )

    print("\n=== Phase 4: Generating Visualizations ===")
    tables = {"top10": top10_df, "pivot": pivot_df}
    charts = visualizer.run(tables)

    print("\nPipeline execution complete!")
    print("Outputs generated in outputs/:")
    print(
        " - grouped.csv, grouped_two.csv, pivot.csv, top10.csv, validation.csv"
    )
    print(f" - {charts['bar']}")
    print(f" - {charts['heatmap']}")


if __name__ == "__main__":
    main()
