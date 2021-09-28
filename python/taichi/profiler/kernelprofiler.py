from contextlib import contextmanager

from taichi.core import ti_core as _ti_core
from taichi.lang import impl
from taichi.profiler.kernelmetrics import default_metric_list

import taichi as ti


class StatisticalResult:
    """Statistical result of records.

    Profiling records with the same kernel name will be counted in a ``StatisticalResult`` instance via ``insert_record(time)``.
    Currently, only the kernel elapsed time is counted, other statistics related to the kernel will be added in the feature.
    """
    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.min_time = 0.0
        self.max_time = 0.0
        self.total_time = 0.0

    def __lt__(self, other):
        # For sorted()
        return self.total_time < other.total_time

    def insert_record(self, time):
        if self.counter == 0:
            self.min_time = time
            self.max_time = time
        self.counter += 1
        self.total_time += time
        self.min_time = min(self.min_time, time)
        self.max_time = max(self.max_time, time)


class KernelProfiler:
    """Kernel profiler of Taichi.

    Kernel profiler acquires kernel profiling records from backend, counts records in python scope,
    and outputs results by printing : :func:`~taichi.profiler.kernelprofiler.KernelProfiler.print_info`.
    """
    def __init__(self):
        """Constructor of class KernelProfiler.

        ``_profiling_mode`` is a boolean value, turn ON/OFF profiler by :func:`~taichi.profiler.kernelprofiler.KernelProfiler.set_kernel_profiler_mode`.
        ``_total_time_ms`` is a float value, get the value in seconds with :func:`~taichi.profiler.kernelprofiler.KernelProfiler.get_total_time`.
        ``_traced_records`` is a list of profiling records, acquired from backend by :func:`~taichi.profiler.kernelprofiler.KernelProfiler.update_records`.
        ``_statistical_results`` is a dict of statistical profiling results, statistics via :func:`~taichi.profiler.kernelprofiler.KernelProfiler.count_results`.
        """
        self._profiling_mode = False
        self._metric_list = []
        self._total_time_ms = 0.0
        self._traced_records = []
        self._statistical_results = {}

    # ======================= private methods ==========================

    def clear_frontend(self):
        self._total_time_ms = 0.0
        self._traced_records.clear()
        self._statistical_results.clear()

    def clear_info(self):
        #sync first
        impl.get_runtime().sync()
        #clear backend & frontend
        impl.get_runtime().prog.clear_kernel_profile_info()
        self.clear_frontend()

    def update_records(self):
        # Acquires profiling records from a backend
        impl.get_runtime().sync()
        self.clear_frontend()
        self._traced_records = impl.get_runtime(
        ).prog.get_kernel_profiler_records()

    def count_results(self):
        # Counts the statistical results.
        # Profiling records with the same kernel name will be counted in a instance of class StatisticalResult.
        # Presenting kernel profiling results in a statistical perspective.
        for record in self._traced_records:
            if self._statistical_results.get(record.name) == None:
                self._statistical_results[record.name] = StatisticalResult(
                    record.name)
            self._statistical_results[record.name].insert_record(
                record.kernel_time)
            self._total_time_ms += record.kernel_time
        self._statistical_results = {
            k: v
            for k, v in sorted(self._statistical_results.items(),
                               key=lambda item: item[1],
                               reverse=True)
        }

    def count_info(self):
        # headers
        table_header = f'Kernel Profiler(count) @ {_ti_core.arch_name(ti.cfg.arch).upper()}'
        column_header = '[      %     total   count |      min       avg       max   ] Kernel name'
        # partition line
        outer_partition_line = '=' * len(column_header)
        inner_partition_line = '-' * len(column_header)

        #message in one line
        string_list = []
        values_list = []
        for key in self._statistical_results:
            result = self._statistical_results[key]
            fraction = result.total_time / self._total_time_ms * 100.0
            string_list.append(
                '[{:6.2f}% {:7.3f} s {:6d}x |{:9.3f} {:9.3f} {:9.3f} ms] {}')
            values_list.append([
                fraction,
                result.total_time / 1000.0,
                result.counter,
                result.min_time,
                result.total_time / result.counter,  # avg_time
                result.max_time,
                result.name
            ])

        # summary
        summary_line = '[100.00%] Total execution time: '
        summary_line += f'{self._total_time_ms/1000:7.3f} s   '
        summary_line += f'number of results: {len(self._statistical_results)}'

        # print
        print(outer_partition_line)
        print(table_header)
        print(outer_partition_line)
        print(column_header)
        print(inner_partition_line)
        result_num = len(self._statistical_results)
        for idx in range(result_num):
            print(string_list[idx].format(*values_list[idx]))
        print(inner_partition_line)
        print(summary_line)
        print(outer_partition_line)

    def trace_info(self):
        metric_list = self._metric_list
        values_num = len(self._traced_records[0].metric_values)

        # headers
        table_header = f"Kernel Profiler(trace) @ {_ti_core.arch_name(ti.cfg.arch).upper()}"
        column_header = ('[  start.time | kernel.time |')  #default
        for idx in range(values_num):
            column_header += metric_list[idx].header + '|'
        column_header = (column_header + '] Kernel name').replace("|]", "]")

        # partition line
        outer_partition_line = '=' * len(column_header)
        inner_partition_line = '-' * len(column_header)

        # message in one line: formatted_str.format(*values)
        fake_timestamp = 0.0
        string_list = []
        values_list = []
        for record in self._traced_records:
            formatted_str = '[{:9.3f} ms |{:9.3f} ms |'  #default
            values = [fake_timestamp, record.kernel_time]  #default
            for idx in range(values_num):
                formatted_str += metric_list[idx].format + '|'
                values += [record.metric_values[idx] * metric_list[idx].scale]
            formatted_str = (formatted_str + '] ' + record.name)
            string_list.append(formatted_str.replace("|]", "]"))
            values_list.append(values)
            fake_timestamp += record.kernel_time

        # print
        print(outer_partition_line)
        print(table_header)
        print(outer_partition_line)
        print(column_header)
        print(inner_partition_line)
        record_num = len(self._traced_records)
        for idx in range(record_num):
            print(string_list[idx].format(*values_list[idx]))
        print(inner_partition_line)
        print(f"Number of records:  {len(self._traced_records)}")
        print(outer_partition_line)

    # ======================== public methods ============================

    def set_kernel_profiler_mode(self, mode=False):
        if type(mode) is bool:
            self._profiling_mode = mode
        else:
            raise TypeError(f'Arg `mode` must be of type boolean. '
                            f'Type {type(mode)} '
                            f'is not supported')

    def get_kernel_profiler_mode(self):
        return self._profiling_mode

    def get_total_time(self):
        self.update_records()  # traced records
        self.count_results()  # _total_time_ms is counted here
        return self._total_time_ms / 1000  # ms to s

    def query_info(self, name):
        self.update_records()  # traced records
        self.count_results()  # statistical results
        # TODO : query self.StatisticalResult in python scope
        return impl.get_runtime().prog.query_kernel_profile_info(name)

    def set_metrics(self, metric_list=default_metric_list):
        """API TODO docstring"""
        self._metric_list = metric_list
        metric_name_list = [metric.name for metric in metric_list]
        self.clear_info()
        impl.get_runtime().prog.reinit_kernel_profiler_with_metrics(
            metric_name_list)

    @contextmanager
    def collect_metrics(self, metric_list=default_metric_list):
        """API TODO docstring"""
        _ti_core.info("with Profiler.run()")
        self.set_metrics(metric_list)
        yield self
        _ti_core.info("end of Profiler.run()")
        self.set_metrics()  #back to default metric list

    # print info mode
    COUNT = 'count'  # print the statistical results (min,max,avg time) of Taichi kernels.
    TRACE = 'trace'  # print the records of launched Taichi kernels with specific profiling metrics (time, memory load/store and core utilization etc.)

    def print_info(self, mode=COUNT):
        """Print the profiling results of Taichi kernels.

        To enable this profiler, set ``kernel_profiler=True`` in ``ti.init()``.
        The default print mode is ``COUNT`` mode: print the statistical results (min,max,avg time) of Taichi kernels,
        another mode ``TRACE``: print the records of launched Taichi kernels with specific profiling metrics (time, memory load/store and core utilization etc.)

        Args:
            mode (str): the way to print profiling results
        """

        self.update_records()  # trace records
        self.count_results()  # statistical results

        #count mode (default) : print statistical results of all kernel
        if mode == self.COUNT:
            self.count_info()

        #trace mode : print records of launched kernel
        if mode == self.TRACE:
            self.trace_info()


_ti_kernel_profiler = KernelProfiler()


def get_default_kernel_profiler():
    """We have only one :class:`~taichi.profiler.kernelprofiler.KernelProfiler` instance(i.e. ``_ti_kernel_profiler``) now.

    For ``KernelProfiler`` using ``CuptiToolkit``, GPU devices can only work in a certain configuration.
    Profiling mode and metrics are configured by the host(CPU) via CUPTI APIs, and device(GPU) will use
    its counter registers to collect specific metrics.
    So if there are multiple instances of ``KernelProfiler``, the device will work in the latest configuration,
    the profiling configuration of other instances will be changed as a result.
    For data retention purposes, multiple instances will be considered in the future.
    """
    return _ti_kernel_profiler
