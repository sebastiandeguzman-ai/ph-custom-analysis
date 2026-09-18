import os

# Paths
DATA_PATH = os.path.join("data", "2015.csv")
OUTPUT_DIR = "outputs"

# Dataset Specs (Customs 2015 Reference Values)
EXPECTED_SHA256 = "b3b5a3a95340179a716a05611d51ad4906484d38363d1ac36494a404c04e4370"
EXPECTED_RAW_ROWS = 2236612
EXPECTED_RAW_SUM = 3587267375257.0

# Selected Analysis Fields
REQUIRED_COLUMNS = {"countryorigin_iso3", "tq", "dutiablevaluephp"}
CAT_COL_1 = "countryorigin_iso3"
CAT_COL_2 = "tq"
NUM_MEASURE = "dutiablevaluephp"
