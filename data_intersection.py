import itertools

import config
import pyarrow.compute as pc
from classes.csv_processor import CsvProcessor
from classes.csv_writer import CsvWriter


def _get_table_intersection(table_1, table_2, intersection_name):
    field = pc.field(intersection_name)
    table_2_rows = table_2.select([intersection_name]).to_pylist()
    table_2_values = list(map(lambda x: x[intersection_name], table_2_rows))
    return table_1.filter(field.isin(table_2_values))


def main():
    table_1 = CsvProcessor(config.CSV_INPUT_PATH_1, delimiter=config.CSV_DELIMITER,
                           skip_rows=config.CSV_SKIP_ROWS).csv_to_table()
    table_2 = CsvProcessor(config.CSV_INPUT_PATH_2, delimiter=config.CSV_DELIMITER,
                           skip_rows=config.CSV_SKIP_ROWS).csv_to_table()

    active_table = table_1

    for intersection_name in config.CSV_INTERSECTION_NAMES:
        active_table = _get_table_intersection(active_table, table_2, intersection_name)

    print((len(active_table), "intersecting data points."))

    CsvWriter(config.CSV_OUTPUT_INTERSECTION_PATH, active_table).write()


if __name__ == "__main__":
    main()
