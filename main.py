from src import loader, processor

def main():
    print("=== Phase 1: Loading Data ===")
    df = loader.load_csv()
    print("Loader operational. Shape:", df.shape)

    print("\n=== Phase 2: Processing & Grouping ===")
    processed_df = processor.process_data(df)
    print("Phase 2 complete. Shape:", processed_df.shape)

if __name__ == "__main__":
    main()
