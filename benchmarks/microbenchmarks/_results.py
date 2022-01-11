from microbenchmarks._utils import End2EndTimer
from microbenchmarks._template import BenchmarkItem

import taichi as ti

def kernel_executor(repeat, func, *args):
    # compile & warmup
    for i in range(repeat):
        func(*args)
    ti.clear_kernel_profile_info()

    for i in range(repeat):
        func(*args)
    return ti.kernel_profiler_total_time()*1000/repeat #ms

def end2end_executor(repeat, func, *args):
    # compile & warmup
    for i in range(repeat):
        func(*args)

    timer = End2EndTimer()
    timer.tick()
    for i in range(repeat):
        func(*args)
    time_in_s = timer.tock()
    return time_in_s * 1000 / repeat #ms

class Results(BenchmarkItem):
    def __init__(self):
        self._name = 'results'
        self._items = {
            'default_time_ms': {'impl': end2end_executor},
            'end2end_time_ms': {'impl': end2end_executor},
            'kernel_elapsed_time_ms': {'impl': kernel_executor}
        }

    def executor(self, result, *args):
        return self._items[result]['impl'](*args)