import pyarrow as pa


def to_py_floats(items):
    return list(map(lambda item: item.as_py(), items))


def binary_search_greater_than_equals(arr, x, start_from_index):
    low = start_from_index
    high = len(arr) - 1

    while low <= high:
        mid = (high + low) // 2
        mid_val = arr[mid]

        if mid_val <= x:
            low = mid + 1
        else:
            high = mid - 1

    return max(high, start_from_index)


def output_entries_to_columns(entries):
    m_z_1_col = []
    intensity_1_col = []
    m_z_2_col = []
    intensity_2_col = []

    for ((m_z_1, intensity_1), (m_z_2, intensity_2)) in entries:
        m_z_1_col.append(m_z_1)
        intensity_1_col.append(intensity_1)
        m_z_2_col.append(m_z_2)
        intensity_2_col.append(intensity_2)

    return [pa.array(m_z_1_col), pa.array(intensity_1_col), pa.array(m_z_2_col), pa.array(intensity_2_col)]
