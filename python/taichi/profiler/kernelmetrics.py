

class CuptiMetric:
    def __init__(self,name,header,string,scale=1.0):
        #cupti metric
        self.name = name     #string
        #formating
        self.header = header #string
        self.string = string #string
        #unit
        self.scale = scale   #double

# Default metrics
dram_bytes_read = CuptiMetric(
    'dram__bytes_read.sum',  # metric name for init CuptiToolkit
    ' mem.load    ',         # header for formated print
    '{:9.3f} MB ',           # metric value and unit for formated print
    1.0/1024/1024)
dram_bytes_write = CuptiMetric(
    'dram__bytes_write.sum',
    ' mem.store    ',
    ' {:9.3f} MB ',
    1.0/1024/1024)
utilization_ratio_core = CuptiMetric(
    'sm__throughput.avg.pct_of_peak_sustained_elapsed',
    ' uti.core  ',
    ' {:6.2f}  % ')
utilization_ratio_mem = CuptiMetric(
    'gpu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed',
    ' uti.mem  ',
    ' {:6.2f} % ')
# Default metrics list
default_metric_list = [
    dram_bytes_read,
    dram_bytes_write,
    utilization_ratio_core,
    utilization_ratio_mem
]

# Do not use this metric
kernel_elapsed_time = CuptiMetric(
    ['smsp__cycles_elapsed.avg','smsp__cycles_elapsed.avg.per_second'],
    '     time    ',
    '{:9.3f} ms')
# `kernel_elapsed_time` is only used for demonstration.
# It requires two CUPTI metrics, kernel elapsed clocks and the core frequency, to calculate it.
# Taichi automatically collects `kernel_elapsed_time` by hardcoding it in the CUDA backend class `CuptiToolkit`.


# _list = default_metric_list
# metric_name_list = [metric.name for metric in _list]
# header = ('[' + ''.join(metric.header + '|' for metric in _list) + ']' + ' Kernel name').replace("|]","]")
# record = ('[' + ''.join(metric.string + '|' for metric in _list) + ']' + ' Kernel name').replace("|]","]")
# print(header)
# print(record.format(*[metric.value for metric in _list]))
# # >>>
# # [ mem.load    | mem.store    | uti.core  | uti.mem  ] Kernel name
# # [    0.000 MB |     0.000 MB |   0.00  % |   0.00 % ] Kernel name


    # def collect(self, metric_list=default_metric_list):
    #     self.clear_info()
    #     self.reinit_backend(metric_list)


