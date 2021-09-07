#pragma once

#include "taichi/backends/cuda/cuda_profiler.h"
#include "cupti_toolkit_functions.h"

#include <string>
#include <stdint.h>

TLANG_NAMESPACE_BEGIN

//make sure these metrics can be captured in 1 pass (no kernal replay)
typedef enum CUPTI_METRICS_ONE_PASS {
  CUPTI_METRIC_KERNEL_ELAPSED_CLK_NUMS = 0,
  CUPTI_METRIC_CORE_FREQUENCY_HZS      = 1,
  CUPTI_METRIC_GLOBAL_LOAD_BYTES       = 2,
  CUPTI_METRIC_GLOBAL_STORE_BYTES      = 3,
  CUPTI_METRICS_ONE_PASS_TOTAL         = 4
} CUPTIMetricsOnePass;

const std::vector<std::string> MetricListOnePass = {
  "smsp__cycles_elapsed.avg",               //CUPTI_METRIC_KERNEL_ELAPSED_CLK_NUMS
  "smsp__cycles_elapsed.avg.per_second",    //CUPTI_METRIC_CORE_FREQUENCY_HZS
  "dram__bytes_read.sum",                   //CUPTI_METRIC_GLOBAL_LOAD_BYTES
  "dram__bytes_write.sum"                   //CUPTI_METRIC_GLOBAL_STORE_BYTES
};

//detailed metric (whatever we want)
typedef enum CUPTI_METRICS_DETAILED {
  CUPTI_METRIC_UTILIZATION_RATIO_SM   = 0,
  CUPTI_METRIC_UTILIZATION_RATIO_MEM  = 1,
  CUPTI_METRICS_DETAILED_TOTAL        = 2
} CUPTIMetricsDetailed;

const std::vector<std::string> MetricListDetailed = {
  "sm__throughput.avg.pct_of_peak_sustained_elapsed",                   //CUPTI_METRIC_UTILIZATION_RATIO_SM
  "gpu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed"    //CUPTI_METRIC_UTILIZATION_RATIO_MEM
};

struct CUPTIConfig {
  KernelProfilingMode profiling_mode = KernelProfilingMode::disable;
#if defined(TI_WITH_TOOLKIT_CUDA)
  uint32_t num_ranges = 16384;  // max number of kernels traced by CUPTI
  std::vector<std::string> metric_list;  // metric name list
  CUpti_ProfilerRange profiler_range = CUPTI_AutoRange;
  CUpti_ProfilerReplayMode profiler_replay_mode = CUPTI_KernelReplay;
#endif
};

struct ProfilerRawData {
  std::string chip_name;
  std::vector<uint8_t> config_image;
  std::vector<uint8_t> counter_availability_image;
  std::vector<uint8_t> counter_data_scratch_buffer;
  std::vector<uint8_t> counter_data_image_prefix;
  std::vector<uint8_t> counter_data_image;
};

class CUPTIToolkit {
 public:
  CUPTIToolkit(KernelProfilingMode &mode);
  ~CUPTIToolkit();

  void set_mode(KernelProfilingMode mode);

  bool init_cupti();
  bool deinit_cupti();
  bool begin_profiling();
  bool end_profiling();

  void record_launched_kernel(std::string name);
  bool calculate_metric_values();
  bool statistics_on_traced_records(std::vector<KernelProfileRecord> &records,
                                    double &total_time_ms);
  void clear_traced_records();

 private:
  CUPTIConfig cupti_config_;
  ProfilerRawData cupti_data_;
  std::vector<KernelProfileTracedRecord> traced_records_;
};

TLANG_NAMESPACE_END
