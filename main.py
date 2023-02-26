import itertools
import time
import config
import pyarrow as pa
import pyarrow.compute as pc
from csv_processor import CsvProcessor
from csv_writer import CsvWriter
from util import output_entries_to_columns, to_py_floats, binary_search_greater_than_equals

_CHLORIDE_MATCHES = "chloride matches."
_BROMIDE_MATCHES = "bromide matches"
_SECONDS = "seconds"


def _preprocess_table_filter(table):
    return table.filter(pc.field(config.CSV_INTENSITY_NAME) >= config.MIN_INTENSITY)


def _preprocess_table_into_chunks(table):
    m_z_entries = to_py_floats(table[config.CSV_M_Z_NAME])
    table_len = len(table)
    chunk_indices = []
    chunk_threshold_m_z = max(config.CHLORIDE_DELTA_M_Z, config.BROMIDE_DELTA_M_Z) + 2 * config.ERROR_MARGIN_M_Z
    prev_m_z = m_z_entries[0]
    chunk_starts_from_m_z_index = 0

    for count, m_z in enumerate(m_z_entries):
        delta_m_z = m_z - prev_m_z

        if delta_m_z > chunk_threshold_m_z:
            chunk_indices.append([chunk_starts_from_m_z_index, count - 1])
            chunk_starts_from_m_z_index = count

        prev_m_z = m_z

    if len(chunk_indices) == 0 or chunk_indices[1][-1] != table_len:
        chunk_indices.append([chunk_starts_from_m_z_index, table_len])

    return chunk_indices


def _match_chloride_bromide(chunk):
    chloride_entry_pairs = []
    bromide_entry_pairs = []

    chunk_m_z_entries = to_py_floats(chunk[config.CSV_M_Z_NAME])
    chunk_intensity_entries = to_py_floats(chunk[config.CSV_INTENSITY_NAME])

    for i, (m_z, intensity) in enumerate(zip(chunk_m_z_entries, chunk_intensity_entries)):
        (target_chloride_m_z, min_chloride_m_z, max_chloride_m_z) = _determine_chloride_m_z_targets(m_z)
        (target_bromide_m_z, min_bromide_m_z, max_bromide_m_z) = _determine_bromide_m_z_targets(m_z)

        iterate_from = binary_search_greater_than_equals(chunk_m_z_entries, min(min_chloride_m_z, min_bromide_m_z), i)

        for (compare_m_z, compare_intensity) in zip(chunk_m_z_entries[iterate_from:],
                                                    chunk_intensity_entries[iterate_from:]):
            if compare_m_z > max_chloride_m_z and compare_m_z > max_bromide_m_z:
                break

            if min_chloride_m_z <= compare_m_z <= max_chloride_m_z:
                chloride_entry_pairs.append(((m_z, intensity), (compare_m_z, compare_intensity)))

            if min_bromide_m_z <= compare_m_z <= max_bromide_m_z:
                bromide_entry_pairs.append(((m_z, intensity), (compare_m_z, compare_intensity)))

    if len(chloride_entry_pairs) or len(bromide_entry_pairs):
        return chloride_entry_pairs, bromide_entry_pairs


def _determine_chloride_m_z_targets(m_z):
    target_chloride_m_z = m_z + config.CHLORIDE_DELTA_M_Z
    min_chloride_m_z, max_chloride_m_z = _determine_m_z_with_error_margins(m_z)

    return target_chloride_m_z, min_chloride_m_z, max_chloride_m_z


def _determine_bromide_m_z_targets(m_z):
    target_bromide_m_z = m_z + config.BROMIDE_DELTA_M_Z
    min_bromide_m_z, max_bromide_m_z = _determine_m_z_with_error_margins(m_z)

    return target_bromide_m_z, min_bromide_m_z, max_bromide_m_z


def _determine_m_z_with_error_margins(m_z):
    rel_error_margin = m_z * config.ERROR_MARGIN_M_Z
    return m_z - rel_error_margin, m_z + rel_error_margin


def main():
    start = time.time()

    processor = CsvProcessor(config.CSV_INPUT_PATH, _preprocess_table_filter, _preprocess_table_into_chunks,
                             _match_chloride_bromide, delimiter=config.CSV_DELIMITER, skip_rows=config.CSV_SKIP_ROWS,
                             include_columns=config.CSV_INCLUDE_COLUMNS)

    chunk_results = processor.process()
    chloride_entries = []
    bromide_entries = []

    for (chloride_entry_pairs, bromide_entry_pairs) in chunk_results:
        if len(chloride_entry_pairs):
            chloride_entries.append(chloride_entry_pairs)

        if len(bromide_entry_pairs):
            bromide_entries.append(bromide_entry_pairs)

    chloride_entries = list(itertools.chain.from_iterable(chloride_entries))
    bromide_entries = list(itertools.chain.from_iterable(bromide_entries))

    print(len(chloride_entries), _CHLORIDE_MATCHES)
    print(len(bromide_entries), _BROMIDE_MATCHES)

    chloride_entries_pa = output_entries_to_columns(chloride_entries)
    bromide_entries_pa = output_entries_to_columns(bromide_entries)

    chloride_table = pa.Table.from_arrays(chloride_entries_pa, names=config.CSV_OUTPUT_NAMES)
    bromide_table = pa.Table.from_arrays(bromide_entries_pa, names=config.CSV_OUTPUT_NAMES)

    CsvWriter(config.CSV_CHLORIDE_OUTPUT_PATH, chloride_table).write()
    CsvWriter(config.CSV_BROMIDE_OUTPUT_PATH, bromide_table).write()

    end = time.time()
    delta = end - start
    print("\n{:.2f}".format(delta), _SECONDS)


if __name__ == "__main__":
    main()
