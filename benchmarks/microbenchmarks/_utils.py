import copy
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


def get_ti_arch(arch: str):
    arch_dict = {
        'cuda': ti.cuda,
        'vulkan': ti.vulkan,
        'opengl': ti.opengl,
        'x64': ti.x64,
        'cc': ti.cc,
        'metal': ti.metal
    }
    return arch_dict[arch]


def _size2tag(size_in_byte):
    size_subsection = [(0.0, 'B'), (1024.0, 'KB'), (1048576.0, 'MB'),
                       (1073741824.0, 'GB'),
                       (float('inf'), 'INF')]  #B KB MB GB
    for dsize, unit in reversed(size_subsection):
        if size_in_byte >= dsize:
            return str(int(size_in_byte / dsize)) + unit


def make_result_dict(tag_list):
    return {'tags': copy.deepcopy(tag_list), 'attributes': {}, 'results': {}}


def add_result(result_dict, name, result):
    result_dict['results'][name] = copy.deepcopy(result)
