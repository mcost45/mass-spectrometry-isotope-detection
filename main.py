import itertools
import time
import config
import pyarrow as pa
import pyarrow.compute as pc
from csv_processor import CsvProcessor
from csv_writer import CsvWriter
from util import output_entries_to_columns, to_py_floats, binary_search_greater_than_equals

_CHLORIDE_MATCHES = "chloride matches."
_BROMIDE_MATCHES = "bromide matches."
_SECONDS = "seconds."


def _preprocess_table_filter(table):
    return table.filter(pc.field(config.CSV_INTENSITY_NAME) >= config.MIN_INTENSITY)


def _preprocess_table_into_chunks(table):
    m_z_entries = to_py_floats(table[config.CSV_M_Z_NAME])
    table_len = len(table)
    chunk_indices = []
    chunk_threshold_delta_m_z = max(config.CHLORIDE_DELTA_M_Z, config.BROMIDE_DELTA_M_Z)

    (_, prev_max_m_z) = _determine_isotope_m_z_targets(m_z_entries[0], chunk_threshold_delta_m_z)
    chunk_starts_from_m_z_index = 0

    for i, m_z in enumerate(m_z_entries):
        (min_m_z, _) = _determine_isotope_m_z_targets(m_z, chunk_threshold_delta_m_z)
        delta_m_z = min_m_z - prev_max_m_z

        if delta_m_z > chunk_threshold_delta_m_z:
            chunk_indices.append([chunk_starts_from_m_z_index, i - 1])
            chunk_starts_from_m_z_index = i

        (_, prev_max_m_z) = _determine_isotope_m_z_targets(m_z, chunk_threshold_delta_m_z)

    if len(chunk_indices) == 0 or chunk_indices[1][-1] != table_len:
        chunk_indices.append([chunk_starts_from_m_z_index, table_len])

    return chunk_indices


def _match_chloride_bromide(chunk):
    chunk_m_z_entries = to_py_floats(chunk[config.CSV_M_Z_NAME])
    chunk_intensity_entries = to_py_floats(chunk[config.CSV_INTENSITY_NAME])

    chloride_entry_pairs = _match_isotopes(chunk_m_z_entries, chunk_intensity_entries, config.CHLORIDE_DELTA_M_Z,
                                           config.CHLORIDE_INTENSITY_RATIO,
                                           config.CHLORIDE_INTENSITY_RATIO_ERROR_MARGIN)
    bromide_entry_pairs = _match_isotopes(chunk_m_z_entries, chunk_intensity_entries, config.BROMIDE_DELTA_M_Z,
                                          config.BROMIDE_INTENSITY_RATIO,
                                          config.BROMIDE_INTENSITY_RATIO_ERROR_MARGIN)

    if len(chloride_entry_pairs) or len(bromide_entry_pairs):
        return chloride_entry_pairs, bromide_entry_pairs


def _match_isotopes(chunk_m_z_entries, chunk_intensity_entries, target_delta_m_z, intensity_ratio,
                    intensity_ratio_error_margin):
    isotope_entry_pairs = []

    for i, (m_z, intensity) in enumerate(zip(chunk_m_z_entries, chunk_intensity_entries)):
        (min_m_z, max_m_z) = _determine_isotope_m_z_targets(m_z, target_delta_m_z)
        (min_intensity, max_intensity) = _determine_isotope_intensity_targets(intensity, intensity_ratio,
                                                                              intensity_ratio_error_margin)
        iterate_from = binary_search_greater_than_equals(chunk_m_z_entries, min_m_z, i)

        for (compare_m_z, compare_intensity) in zip(chunk_m_z_entries[iterate_from:],
                                                    chunk_intensity_entries[iterate_from:]):
            if compare_m_z > max_m_z:
                break

            if (min_intensity <= compare_intensity <= max_intensity) and (min_m_z <= compare_m_z <= max_m_z):
                isotope_entry_pairs.append(((m_z, intensity), (compare_m_z, compare_intensity)))

    return isotope_entry_pairs


def _determine_isotope_m_z_targets(m_z, target_delta_m_z):
    base_minus_error_margin = config.REL_ERROR_MARGIN_M_Z_MINUS * m_z
    base_plus_error_margin = config.REL_ERROR_MARGIN_M_Z_PLUS * m_z

    base_m_z_min = m_z - base_minus_error_margin
    base_m_z_max = m_z + base_plus_error_margin

    target_m_z_min_without_error = base_m_z_min + target_delta_m_z
    target_m_z_max_without_error = base_m_z_max + target_delta_m_z

    target_minus_error_margin = config.REL_ERROR_MARGIN_M_Z_MINUS * target_m_z_min_without_error
    target_plus_error_margin = config.REL_ERROR_MARGIN_M_Z_PLUS * target_m_z_max_without_error

    target_m_z_min = target_m_z_min_without_error - target_minus_error_margin
    target_m_z_max = target_m_z_max_without_error + target_plus_error_margin

    return target_m_z_min, target_m_z_max


def _determine_isotope_intensity_targets(intensity, intensity_ratio, intensity_ratio_error_margin):
    rel_error_margin_intensity_ratio = config.REL_ERROR_MARGIN_INTENSITY_RATIO
    base_error_margin = intensity * rel_error_margin_intensity_ratio

    base_intensity_min = intensity - base_error_margin
    base_intensity_max = intensity + base_error_margin

    target_intensity_min_without_error = base_intensity_min * (intensity_ratio - intensity_ratio_error_margin)
    target_intensity_max_without_error = base_intensity_max * (intensity_ratio + intensity_ratio_error_margin)

    target_minus_error_margin = target_intensity_min_without_error * rel_error_margin_intensity_ratio
    target_max_error_margin = target_intensity_max_without_error * rel_error_margin_intensity_ratio

    target_intensity_min = target_intensity_min_without_error - target_minus_error_margin
    target_intensity_max = target_intensity_max_without_error + target_max_error_margin

    return target_intensity_min, target_intensity_max


def _output_isotope_matches(isotope_chunk_results, match_msg, csv_output_path):
    isotope_entries = []
    for isotope_entry_pairs in isotope_chunk_results:
        if len(isotope_entry_pairs):
            isotope_entries.append(isotope_entry_pairs)

    isotope_entries = list(itertools.chain.from_iterable(isotope_entries))
    print(len(isotope_entries), match_msg)
    isotope_entries_pa = output_entries_to_columns(isotope_entries)
    isotope_table = pa.Table.from_arrays(isotope_entries_pa, names=config.CSV_OUTPUT_NAMES)
    CsvWriter(csv_output_path, isotope_table).write()


def main():
    start = time.time()

    processor = CsvProcessor(config.CSV_INPUT_PATH, _preprocess_table_filter, _preprocess_table_into_chunks,
                             _match_chloride_bromide, delimiter=config.CSV_DELIMITER, skip_rows=config.CSV_SKIP_ROWS,
                             include_columns=config.CSV_INCLUDE_COLUMNS)
    chunk_results = list(zip(*processor.process()))

    if not len(chunk_results):
        chunk_results = [[], []]

    _output_isotope_matches(chunk_results[0], _CHLORIDE_MATCHES, config.CSV_CHLORIDE_OUTPUT_PATH)
    _output_isotope_matches(chunk_results[1], _BROMIDE_MATCHES, config.CSV_BROMIDE_OUTPUT_PATH)

    end = time.time()
    delta = end - start
    print("\n{:.2f}".format(delta), _SECONDS)


if __name__ == "__main__":
    main()
