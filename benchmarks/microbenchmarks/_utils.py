import time

import taichi as ti


class End2EndTimer:
    def __init__(self):
        self._ts1 = 0
        self._ts2 = 0

    def tick(self):
        ti.sync()
        self._ts1 = time.perf_counter()

    def tock(self):
        ti.sync()
        self._ts2 = time.perf_counter()
        ret = self._ts2 - self._ts1
        return ret


def _size2tag(size_in_byte):
    size_subsection = [(0.0, 'B'), (1024.0, 'KB'), (1048576.0, 'MB'),
                       (1073741824.0, 'GB'),
                       (float('inf'), 'INF')]  #B KB MB GB
    for dsize, unit in reversed(size_subsection):
        if size_in_byte >= dsize:
            return str(int(size_in_byte / dsize)) + unit
