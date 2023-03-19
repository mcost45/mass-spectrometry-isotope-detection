import pyarrow.csv as csv
import multiprocessing as mp

_DEFAULT_KWARGS = {"delimiter": ",", "skip_rows": 0, "include_columns": None}

_ROWS_END_MSG = "rows."
_POINTS_END_MSG = "points."
_CHUNKS_END_MSG = "chunks."
_READING_CSV_MSG = "Reading CSV..."
_FILTERING_MSG = "Filtering..."
_CHUNKING_MSG = "Chunking..."
_PARALLEL_MATCHING_MSG = "Matching data in parallel..."
_POINTS_REDUCED_MSG = "points reduced to"
_DONE_MSG = "Done."


def _worker(chunk, match_callback):
    return match_callback(chunk)


class CsvProcessor:
    def __init__(self, file_path, **kwargs):
        kwargs = _DEFAULT_KWARGS | kwargs
        self.__file_path = file_path
        self.__filter_callback = kwargs.get("filter_callback")
        self.__chunk_callback = kwargs.get("chunk_callback")
        self.__match_callback = kwargs.get("match_callback")
        self.__delimiter = kwargs.get("delimiter")
        self.__skip_rows = kwargs.get("skip_rows")
        self.__include_columns = kwargs.get("include_columns")

    def process(self):
        table = self.csv_to_table()
        filtered_table = self.__filter_table(table)
        chunk_indices = self.__table_to_chunks(filtered_table)
        return self.__process_chunks_parallel(filtered_table, chunk_indices)

    def csv_to_table(self):
        print(_READING_CSV_MSG)
        read_options = csv.ReadOptions(use_threads=True, skip_rows=self.__skip_rows)
        parse_options = csv.ParseOptions(delimiter=self.__delimiter)
        convert_options = csv.ConvertOptions(include_columns=self.__include_columns)

        table = csv.read_csv(self.__file_path, read_options=read_options, parse_options=parse_options,
                             convert_options=convert_options)
        print(len(table), _ROWS_END_MSG)
        print(_DONE_MSG)
        return table

    def __filter_table(self, table):
        print(_FILTERING_MSG)
        original_len = len(table)
        filtered_table = self.__filter_callback(table)
        print(original_len, _POINTS_REDUCED_MSG, len(filtered_table), _POINTS_END_MSG)
        print(_DONE_MSG)
        return filtered_table

    def __table_to_chunks(self, table):
        print(_CHUNKING_MSG)
        chunks = self.__chunk_callback(table)
        print(len(chunks), _CHUNKS_END_MSG)
        print(_DONE_MSG)
        return chunks

    def __process_chunks_parallel(self, table, chunk_indices):
        print(_PARALLEL_MATCHING_MSG)
        pool_count = mp.cpu_count()
        pool = mp.Pool(pool_count)
        async_results = []
        self.__task_count = len(chunk_indices)

        for (start, end) in chunk_indices:
            chunk = table.slice(offset=start, length=end - start + 1)
            async_results.append(
                pool.apply_async(_worker, args=(chunk, self.__match_callback)))

        pool.close()
        pool.join()
        print(_DONE_MSG)

        return list(filter(lambda x: x is not None, map(lambda x: x.get(), async_results)))
