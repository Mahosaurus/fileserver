"""Filesystem helpers – searching, listing, and building HTML tables."""

from pathlib import Path
from collections import defaultdict

from flask_table.html import element
from flask_table import Col, Table


def search_all_files(directory):
    """Recursively search for all files in a directory and its subdirectories."""
    dirpath = Path(directory)
    directory_list = defaultdict(list)
    for x in dirpath.iterdir():
        if x.is_file():
            directory_list[str(x)].append(x)
        if x.is_dir():
            results = search_all_files(x)
            for key in results:
                directory_list[key] = [key]
    return directory_list


def make_table(directory_list, folder_root):
    """Build an HTML table from the directory listing."""
    items = []
    for _, fileitems in directory_list.items():
        for fileitem in fileitems:
            items.append(str(fileitem))
    items = sorted(items, reverse=True)
    table_items = [Item(fp, folder_root) for fp in items]
    tableau = ItemTable(table_items, table_id='myTable')
    return tableau


# ── flask-table classes ──────────────────────────────────────────────

class ExternalURLCol(Col):
    def __init__(self, name, url_attr, **kwargs):
        self.url_attr = url_attr
        super(ExternalURLCol, self).__init__(name, **kwargs)

    def td_contents(self, item, attr_list):
        text = self.from_attr_list(item, attr_list)
        url = self.from_attr_list(item, [self.url_attr])
        return element('a', {'href': url}, content=text)


class ItemTable(Table):
    link = ExternalURLCol('Track', url_attr='url', attr='name')


class Item:
    def __init__(self, filepath, folder_root):
        self.name = str.replace(filepath, str(folder_root), "")
        self.url = "d?file=" + str(filepath)
