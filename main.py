from src import loader, processor

def main():
    print("=== Phase 1: Loading Data ===")
    df = loader.load_csv()
    print("Loader operational. Shape:", df.shape)

    print("\n=== Phase 2: Processing & Grouping ===")
    processed_df = processor.add_duty_per_weight(df)
    processed_df = processor.add_high_value_flag(processed_df)
    grouped_df = processor.grouped(processed_df)
    grouped_two_df = processor.grouped_two(processed_df)
    processor.export_grouped_tables(grouped_df, grouped_two_df)

    print("Phase 2 complete. Shape:", processed_df.shape)

if __name__ == "__main__":
    main()
