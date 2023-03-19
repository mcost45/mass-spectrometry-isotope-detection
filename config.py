CSV_INPUT_PATH = "data/demo-input.csv"  # Data location (CSV)
CSV_SKIP_ROWS = 0  # Number of lines that should be skipped (i.e. for comments)
CSV_DELIMITER = ","  # The character separating each value within the csv
CSV_M_Z_NAME = "m/z"
CSV_INTENSITY_NAME = "intensities"
CSV_INCLUDE_COLUMNS = [CSV_M_Z_NAME, CSV_INTENSITY_NAME]
CSV_BROMIDE_OUTPUT_PATH = "data/output-bromide.csv"
CSV_CHLORIDE_OUTPUT_PATH = "data/output-chloride.csv"
CSV_OUTPUT_NAMES = ["m/z 1", "intensity 1", "m/z 2", "intensity 2"]

MIN_INTENSITY = 100  # Thresholds data by intensity
REL_ERROR_MARGIN_INTENSITY_RATIO = 0.01  # Intensity ratio error margin

REL_ERROR_MARGIN_M_Z_PLUS = 10.4 / ((10 ** 6) * 0.9999896)
REL_ERROR_MARGIN_M_Z_MINUS = 10.4 / ((10 ** 6) * 1.0000104)

CHLORIDE_DELTA_M_Z = 1.9970499  # Mass to charge ratio indicating chloride isotopes
CHLORIDE_INTENSITY_RATIO = 0.31996  # Intensity ratio indicating chloride isotopes
CHLORIDE_INTENSITY_RATIO_ERROR_MARGIN = 0.00032

BROMIDE_DELTA_M_Z = 1.997953499  # Mass to charge ratio indicating bromide isotopes
BROMIDE_INTENSITY_RATIO = 0.97355  # Intensity ratio indicating chloride isotopes
BROMIDE_INTENSITY_RATIO_ERROR_MARGIN = 0.0001

# Data Intersection Config
CSV_INPUT_PATH_1 = "data/output-bromide-0.001.csv"
CSV_INPUT_PATH_2 = "data/output-bromide-0.001-TEST.csv"
CSV_INTERSECTION_NAMES = ["m/z 1", "m/z 2"]
CSV_OUTPUT_INTERSECTION_PATH = "data/demo-intersection-output.csv"
