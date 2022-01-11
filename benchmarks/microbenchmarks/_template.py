from microbenchmarks._utils import add_result, get_ti_arch, make_result_dict

import taichi as ti


class BenchmarkItem:
    def __init__(self):
        self._name = 'item'
        self._items = {}
        # {tag: {impl: xxx, ...}}

    def get(self):
        return self._items

    def get_tags(self):
        return [tag for tag in self._items]

    def items(self):
        return self._items.items()
