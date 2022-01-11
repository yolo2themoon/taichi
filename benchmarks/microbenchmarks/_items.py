from microbenchmarks._template import BenchmarkItem
from microbenchmarks._utils import _size2tag

import taichi as ti


class DataType(BenchmarkItem):
    def __init__(self):
        self._name = 'dtype'
        self._items = {
            str(ti.i32): {
                'impl': ti.i32,
                'size': 4
            },
            str(ti.i64): {
                'impl': ti.i64,
                'size': 8
            },
            str(ti.f32): {
                'impl': ti.f32,
                'size': 4
            },
            str(ti.f64): {
                'impl': ti.f64,
                'size': 8
            }
        }


class DataSize(BenchmarkItem):
    def __init__(self):
        self._name = 'dsize'
        self._items = {}
        for i in range(1, 10):  # [4KB,16KB...256MB]
            size_bytes = (4**i) * 1024  # kibibytes(KiB) = 1024
            self._items[_size2tag(size_bytes)] = {'impl': size_bytes}


class Container(BenchmarkItem):
    def __init__(self):
        self._name = 'container'
        self._items = {
            'field': {
                'impl': ti.field
            },
            'ndarray': {
                'impl': ti.ndarray
            }
        }
