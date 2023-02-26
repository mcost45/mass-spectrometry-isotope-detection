CSV_INPUT_PATH = "data/Regions-OverviewSpectra - CSV.csv"  # Data location (CSV)
CSV_SKIP_ROWS = 10  # Number of lines that should be skipped (i.e. for comments)
CSV_DELIMITER = ";"  # The character separating each value within the csv
CSV_M_Z_NAME = "m/z"
CSV_INTENSITY_NAME = "intensities"
CSV_INCLUDE_COLUMNS = [CSV_M_Z_NAME, CSV_INTENSITY_NAME]
CSV_BROMIDE_OUTPUT_PATH = "data/output-bromide.csv"
CSV_CHLORIDE_OUTPUT_PATH = "data/output-chloride.csv"
CSV_OUTPUT_NAMES = ["m/z 1", "intensity 1", "m/z 2", "intensity 2"]

ERROR_MARGIN_M_Z = 1.04e-5  # Mass to charge ratio error margin
ERROR_MARGIN_INTENSITY_RATIO = 1.04e-5  # Intensity ratio error margin

CHLORIDE_DELTA_M_Z = 1.9970499  # Mass to charge ratio indicating chloride isotopes
CHLORIDE_INTENSITY_RATIO = 75.78 / 24.22  # The difference between two intensity points indicating chloride isotopes

BROMIDE_DELTA_M_Z = 1.997953499  # Mass to charge ratio indicating bromide isotopes
BROMIDE_INTENSITY_RATIO = 50.65 / 49.35  # The difference between two intensity points indicating bromide isotopes

MIN_INTENSITY = 100
