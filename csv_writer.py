import pyarrow.csv as csv

_DEFAULT_KWARGS = {"delimiter": ","}

_WRITE_MSG = "Writing..."
_DONE_MSG = "Done."


class CsvWriter:
    def __init__(self, file_path, table, **kwargs):
        kwargs = _DEFAULT_KWARGS | kwargs
        self.__file_path = file_path
        self.__table = table
        self.__delimiter = kwargs["delimiter"]

    def write(self):
        print(_WRITE_MSG)
        write_options = csv.WriteOptions(include_header=True, delimiter=self.__delimiter)
        csv.write_csv(self.__table, self.__file_path, write_options=write_options)
        print(_DONE_MSG)
