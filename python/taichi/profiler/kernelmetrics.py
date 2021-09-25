class CuptiMetric:
    def __init__(self, name, header, format, scale=1.0):
        #cupti metric
        self.name = name  #(str): metric name for init CuptiToolkit
        #formating
        self.header = header  #(str): header for formatted printing
        self.format = format  #(str): format for print metric value and unit
        self.scale = scale  #(double): scale for metric value


########################## Memory Metrics ##########################
dram_utilization = CuptiMetric(
    'dram__throughput.avg.pct_of_peak_sustained_elapsed', ' global.uti ',
    '   {:6.2f} % ')
dram_bytes_sum = CuptiMetric('dram__bytes.sum', '  global.r&w ', '{:9.3f} MB ',
                             1.0 / 1024 / 1024)
dram_bytes_throughput = CuptiMetric('dram__bytes.sum.per_second',
                                    ' global.r&w/s ', '{:8.3f} GB/s ',
                                    1.0 / 1024 / 1024 / 1024)
dram_bytes_read = CuptiMetric('dram__bytes_read.sum', '   global.r ',
                              '{:8.3f} MB ', 1.0 / 1024 / 1024)
dram_read_throughput = CuptiMetric('dram__bytes_read.sum.per_second',
                                   '   global.r/s ', '{:8.3f} GB/s ',
                                   1.0 / 1024 / 1024 / 1024)
dram_bytes_write = CuptiMetric('dram__bytes_write.sum', '   global.w ',
                               '{:8.3f} MB ', 1.0 / 1024 / 1024)
dram_write_throughput = CuptiMetric('dram__bytes_write.sum.per_second',
                                    '   global.w/s ', '{:8.3f} GB/s ',
                                    1.0 / 1024 / 1024 / 1024)
# global_load = CuptiMetric(
#     'smsp__inst_executed_op_global_ld.sum',
#     ' global.w ',
#     ' {:8.0f} ')
# global_store = CuptiMetric(
#     'smsp__inst_executed_op_global_st.sum',
#     ' global.r ',
#     ' {:8.0f} ')
#####  global load & store #####
global_access_metrics = [
    dram_utilization,
    dram_bytes_sum,
    dram_bytes_throughput,
    dram_bytes_read,
    dram_read_throughput,
    dram_bytes_write,
    dram_write_throughput,
]

shared_utilization = CuptiMetric(
    'l1tex__data_pipe_lsu_wavefronts_mem_shared.avg.pct_of_peak_sustained_elapsed',
    ' uti.shared ', '   {:6.2f} % ')
# shared_load	            smsp__inst_executed_op_shared_ld.sum
# shared_store	          smsp__inst_executed_op_shared_st.sum
shared_transactions_load = CuptiMetric(
    'l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum', ' shared.trans.w ',
    '     {:10.0f} ')
shared_transactions_store = CuptiMetric(
    'l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum', ' shared.trans.r ',
    '     {:10.0f} ')
shared_bank_conflicts_store = CuptiMetric(
    'l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_st.sum',
    ' bank.conflict.w ', '      {:10.0f} ')
shared_bank_conflicts_load = CuptiMetric(
    'l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_ld.sum',
    ' bank.conflict.r ', '      {:10.0f} ')
##### shared load & store ####
shared_access_metrics = [
    shared_utilization,
    shared_transactions_load,
    shared_transactions_store,
    shared_bank_conflicts_store,
    shared_bank_conflicts_load,
]

#
global_op_atom = CuptiMetric(
    'l1tex__t_set_accesses_pipe_lsu_mem_global_op_atom.sum', ' global.atom ',
    '    {:8.0f} ')
global_op_red = CuptiMetric(
    'l1tex__t_set_accesses_pipe_lsu_mem_global_op_red.sum', ' global.red ',
    '   {:8.0f} ')
##### atomic access ####
atomic_access_metrics = [
    global_op_atom,
    global_op_red,
]

########################## Memory Metrics ##########################
sm_throughput = CuptiMetric('sm__throughput.avg.pct_of_peak_sustained_elapsed',
                            ' uti.core ', ' {:6.2f} % ')
dram_throughput = CuptiMetric(
    'gpu__dram_throughput.avg.pct_of_peak_sustained_elapsed', '  uti.mem ',
    ' {:6.2f} % ')
l1tex_throughput = CuptiMetric(
    'l1tex__throughput.avg.pct_of_peak_sustained_elapsed', '   uti.l1 ',
    ' {:6.2f} % ')
l2_throughput = CuptiMetric(
    'lts__throughput.avg.pct_of_peak_sustained_elapsed', '   uti.l2 ',
    ' {:6.2f} % ')
##### device throughput ####
device_utilization_metrics = [
    sm_throughput,
    dram_throughput,
    shared_utilization,
    l1tex_throughput,
    l2_throughput,
]

########################## Misc Metrics ##########################

l1_hit_rate = CuptiMetric('l1tex__t_sector_hit_rate.pct', '   l1.hit ',
                          ' {:6.2f} % ')
l2_hit_rate = CuptiMetric('lts__t_sector_hit_rate.pct', '   l2.hit ',
                          ' {:6.2f} % ')
cache_hit_metrics = [
    l1_hit_rate,
    l2_hit_rate,
]

achieved_occupancy = CuptiMetric(
    'sm__warps_active.avg.pct_of_peak_sustained_active', ' occupancy',
    '   {:6.0f} ')

# Default metrics list
default_metric_list = [dram_bytes_sum]
