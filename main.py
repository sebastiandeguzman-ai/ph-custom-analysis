from src import loader

def main():
    print("=== Phase 1: Loading Data ===")
    df = loader.load_csv()
    print("Loader operational. Shape:", df.shape)

if __name__ == "__main__":
    main()
