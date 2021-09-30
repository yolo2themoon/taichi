from dataclasses import dataclass

from taichi.core import ti_core as _ti_core


@dataclass
class CuptiMetric:
    """A data class to add CUPTI metric for KernelProfiler.

    This class can be used to add user selected CUPTI metrics.
    Details about CUPTI and its metircs: link

    For examples, see :func:`~taichi.lang.set_kernel_profile_metrics` and :func:`~taichi.lang.collect_metrics_with_context`

    Args:
        name (str): name of the metric collected by CuptiToolkit.
        header (str): column header of this metric.
        format (str): format for print metric value (and unit of this value).
        scale (float): scale of metric value.
    """
    name: str = ''
    header: str = ''
    format: str = ''
    scale: float = 1.0


# Global Memory Metrics
dram_utilization = CuptiMetric(
    name='dram__throughput.avg.pct_of_peak_sustained_elapsed',
    header=' global.uti ',
    format='   {:6.2f} % ')

dram_bytes_sum = CuptiMetric(name='dram__bytes.sum',
                             header='  global.r&w ',
                             format='{:9.3f} MB ',
                             scale=1.0 / 1024 / 1024)

dram_bytes_throughput = CuptiMetric(name='dram__bytes.sum.per_second',
                                    header=' global.r&w/s ',
                                    format='{:8.3f} GB/s ',
                                    scale=1.0 / 1024 / 1024 / 1024)

dram_bytes_read = CuptiMetric(name='dram__bytes_read.sum',
                              header='   global.r ',
                              format='{:8.3f} MB ',
                              scale=1.0 / 1024 / 1024)

dram_read_throughput = CuptiMetric(name='dram__bytes_read.sum.per_second',
                                   header='   global.r/s ',
                                   format='{:8.3f} GB/s ',
                                   scale=1.0 / 1024 / 1024 / 1024)

dram_bytes_write = CuptiMetric(name='dram__bytes_write.sum',
                               header='   global.w ',
                               format='{:8.3f} MB ',
                               scale=1.0 / 1024 / 1024)

dram_write_throughput = CuptiMetric(name='dram__bytes_write.sum.per_second',
                                    header='   global.w/s ',
                                    format='{:8.3f} GB/s ',
                                    scale=1.0 / 1024 / 1024 / 1024)

# Shared Memory Metrics
shared_utilization = CuptiMetric(
    name=
    'l1tex__data_pipe_lsu_wavefronts_mem_shared.avg.pct_of_peak_sustained_elapsed',
    header=' uti.shared ',
    format='   {:6.2f} % ')

shared_transactions_load = CuptiMetric(
    name='l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum',
    header=' shared.trans.w ',
    format='     {:10.0f} ')

shared_transactions_store = CuptiMetric(
    name='l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum',
    header=' shared.trans.r ',
    format='     {:10.0f} ')

shared_bank_conflicts_store = CuptiMetric(
    name='l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_st.sum',
    header=' bank.conflict.w ',
    format='      {:10.0f} ')

shared_bank_conflicts_load = CuptiMetric(
    name='l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_ld.sum',
    header=' bank.conflict.r ',
    format='      {:10.0f} ')

# Atomic Metrics
global_op_atom = CuptiMetric(
    name='l1tex__t_set_accesses_pipe_lsu_mem_global_op_atom.sum',
    header=' global.atom ',
    format='    {:8.0f} ')

global_op_reduction = CuptiMetric(
    name='l1tex__t_set_accesses_pipe_lsu_mem_global_op_red.sum',
    header=' global.red ',
    format='   {:8.0f} ')

# Hardware Utilization Metrics
sm_throughput = CuptiMetric(
    name='sm__throughput.avg.pct_of_peak_sustained_elapsed',
    header=' core.uti ',
    format=' {:6.2f} % ')

dram_throughput = CuptiMetric(
    name='gpu__dram_throughput.avg.pct_of_peak_sustained_elapsed',
    header='  mem.uti ',
    format=' {:6.2f} % ')

l1tex_throughput = CuptiMetric(
    name='l1tex__throughput.avg.pct_of_peak_sustained_elapsed',
    header='   L1.uti ',
    format=' {:6.2f} % ')

l2_throughput = CuptiMetric(
    name='lts__throughput.avg.pct_of_peak_sustained_elapsed',
    header='   L2.uti ',
    format=' {:6.2f} % ')

# Misc Metrics
l1_hit_rate = CuptiMetric(name='l1tex__t_sector_hit_rate.pct',
                          header='   L1.hit ',
                          format=' {:6.2f} % ')

l2_hit_rate = CuptiMetric(name='lts__t_sector_hit_rate.pct',
                          header='   L2.hit ',
                          format=' {:6.2f} % ')

achieved_occupancy = CuptiMetric(
    name='sm__warps_active.avg.pct_of_peak_sustained_active',
    header=' occupancy',
    format='   {:6.0f} ')

# metric suite: global load & store
global_access = [
    dram_utilization,
    dram_bytes_sum,
    dram_bytes_throughput,
    dram_bytes_read,
    dram_read_throughput,
    dram_bytes_write,
    dram_write_throughput,
]

# metric suite: shared load & store
shared_access = [
    shared_utilization,
    shared_transactions_load,
    shared_transactions_store,
    shared_bank_conflicts_store,
    shared_bank_conflicts_load,
]

# metric suite: atomic access
atomic_access = [
    global_op_atom,
    global_op_reduction,
]

# metric suite: cache hit rate
cache_hit_rate = [
    l1_hit_rate,
    l2_hit_rate,
]

# metric suite: device throughput
device_utilization = [
    sm_throughput,
    dram_throughput,
    shared_utilization,
    l1tex_throughput,
    l2_throughput,
]

# Predefined metrics suites
predefined_cupti_metrics = {
    'global_access': global_access,
    'shared_access': shared_access,
    'atomic_access': atomic_access,
    'cache_hit_rate': cache_hit_rate,
    'device_utilization': device_utilization,
}


def get_predefined_cupti_metrics(name=''):
    if name not in predefined_cupti_metrics:
        _ti_core.warn("Valid Taichi predefined metrics list (str):")
        for key in predefined_cupti_metrics:
            _ti_core.warn(f"    '{key}'")
        return None
    else:
        return predefined_cupti_metrics[name]


# Default metrics list
default_cupti_metrics = [dram_bytes_sum]
