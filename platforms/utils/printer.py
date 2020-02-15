import columnar


def print_table_ex(rows: list,
                   headers: list = None,
                   title: str = None,
                   terminal_width=200):
    if not headers:
        headers = rows[0]
        rows = rows[1:]
    if title:
        print(f'\n\n\n{title}\n')
    print(
        columnar.columnar(rows, headers=headers,
                          terminal_width=terminal_width))


def print_table(rowsandheaders: list, title: str = None):
    ''' Expects a list object of [<rows>, <headers>] '''
    print_table_ex(rowsandheaders[0], rowsandheaders[1], title)
