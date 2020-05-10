import columnar
import pandas
import numpy


def print_table_ex(rows: list,
                   headers: list = None,
                   title: str = None,
                   terminal_width=200):
    if headers is None:
        headers = rows[0]
        rows = rows[1:]
    if title:
        print(f'\n\n\n{title}\n')
    print(
        columnar.columnar(rows, headers=headers,
                          terminal_width=terminal_width))


def print_table(rowsandheaders: list, title: str = None):
    ''' Expects a list/tuple object of [<rows>, <headers>] '''
    print_table_ex(rowsandheaders[0], rowsandheaders[1], title)


def print_table_from_dicts(data: list = None, title: str = None):
    rows = []
    df = pandas.DataFrame.from_dict(data)
    df = df.replace(numpy.nan, '', regex=True)
    for _, row in df.iterrows():
        rows.append(row.to_list())
    print_table_ex(rows, headers=list(df.columns), title=title)
