#pragma once

#if defined(TI_WITH_TOOLKIT_CUDA)

#include <cupti_target.h>
#include <cupti_result.h>

#include <nvperf_host.h>
#include <nvperf_cuda_host.h>
#include <nvperf_target.h>


#define CUPTI_API_CALL(apiFuncCall)                                            \
do {                                                                           \
    CUptiResult _status = apiFuncCall;                                         \
    if (_status != CUPTI_SUCCESS) {                                            \
        const char *errstr;                                                    \
        cuptiGetResultString(_status, &errstr);                                \
        fprintf(stderr, "%s:%d: error: function %s failed with error %s.\n",   \
                __FILE__, __LINE__, #apiFuncCall, errstr);                     \
        exit(-1);                                                              \
    }                                                                          \
} while (0)


/**
 * \brief Profiler range attribute
 *
 * A metric enabled in the session's configuration is collected separately per unique range-stack in the pass.
 * This is an attribute to collect metrics around each kernel in a profiling session or in an user defined range.
 */
typedef enum
{
    /**
     * Invalid value
     */
    CUPTI_Range_INVALID,
    /**
     * Ranges are auto defined around each kernel in a profiling session
     */
    CUPTI_AutoRange,
    /**
     * A range in which metric data to be collected is defined by the user
     */
    CUPTI_UserRange,
    /**
     * Range count
     */
    CUPTI_Range_COUNT,
} CUpti_ProfilerRange;



/**
 * \brief Profiler replay attribute
 *
 * For metrics which require multipass collection, a replay of the GPU kernel(s) is required.
 * This is an attribute which specify how the replay of the kernel(s) to be measured is done.
 */
typedef enum
{
    /**
     * Invalid Value
     */
    CUPTI_Replay_INVALID,
    /**
     * Replay is done by CUPTI user around the process
     */
    CUPTI_ApplicationReplay,
    /**
     * Replay is done around kernel implicitly by CUPTI
     */
    CUPTI_KernelReplay,
    /**
     * Replay is done by CUPTI user within a process
     */
    CUPTI_UserReplay,
    /**
     * Replay count
     */
    CUPTI_Replay_COUNT,
} CUpti_ProfilerReplayMode;




/**
 * \defgroup CUPTI_PROFILER_API CUPTI Profiler API
 * Functions, types, and enums that implement the CUPTI Profiler API.
 * @{
 */
#ifndef CUPTI_PROFILER_STRUCT_SIZE
#define CUPTI_PROFILER_STRUCT_SIZE(type_, lastfield_)                     (offsetof(type_, lastfield_) + sizeof(((type_*)0)->lastfield_))
#endif


/**
 * \brief Default parameter for cuptiProfilerInitialize
 */
typedef struct CUpti_Profiler_Initialize_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_Initialize_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

} CUpti_Profiler_Initialize_Params;
#define CUpti_Profiler_Initialize_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_Initialize_Params, pPriv)

/**
 * \brief Initializes the profiler interface
 *
 * Loads the required libraries in the process address space.
 * Sets up the hooks with the CUDA driver.
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerInitialize(CUpti_Profiler_Initialize_Params *pParams);






/**
 * \brief Default parameter for cuptiProfilerDeInitialize
 */
typedef struct CUpti_Profiler_DeInitialize_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_DeInitialize_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

} CUpti_Profiler_DeInitialize_Params;
#define CUpti_Profiler_DeInitialize_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_DeInitialize_Params, pPriv)


/**
 * \brief DeInitializes the profiler interface
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerDeInitialize(CUpti_Profiler_DeInitialize_Params *pParams);









typedef void * CUcontext;


/**
 * \brief Params for cuptiProfilerGetCounterAvailability
 */
typedef struct CUpti_Profiler_GetCounterAvailability_Params
{
    
    size_t structSize;                                  //!< [in] CUpti_Profiler_GetCounterAvailability_Params_STRUCT_SIZE
    void* pPriv;                                        //!< [in] assign to NULL    
    CUcontext ctx;                                      //!< [in] if NULL, the current CUcontext is used
    size_t counterAvailabilityImageSize;                //!< [in/out] If `pCounterAvailabilityImage` is NULL, then the required size is returned in
                                                        //!< `counterAvailabilityImageSize`, otherwise `counterAvailabilityImageSize` should be set to the size of
                                                        //!< `pCounterAvailabilityImage`, and on return it would be overwritten with number of actual bytes copied
    uint8_t* pCounterAvailabilityImage;                 //!< [in] buffer receiving counter availability image, may be NULL
} CUpti_Profiler_GetCounterAvailability_Params;
#define CUpti_Profiler_GetCounterAvailability_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_GetCounterAvailability_Params, pCounterAvailabilityImage)

/**
 * \brief Query counter availibility 
 * 
 * Use this API to query counter availability information in a buffer which can be used to filter unavailable raw metrics on host.
 * Note: This API may fail, if any profiling or sampling session is active on the specified context or its device.
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerGetCounterAvailability(CUpti_Profiler_GetCounterAvailability_Params *pParams);







/**
 * \brief Input parameter to define the counterDataImage
 */
typedef struct CUpti_Profiler_CounterDataImageOptions
{
    size_t structSize;                                          //!< [in] CUpti_Profiler_CounterDataImageOptions_Params_STRUCT_SIZE
    void* pPriv;                                                //!< [in] assign to NULL

    const uint8_t* pCounterDataPrefix;                          /**< [in] Address of CounterDataPrefix generated from NVPW_CounterDataBuilder_GetCounterDataPrefix().
                                                                    Must be align(8).*/
    size_t counterDataPrefixSize;                               //!< [in] Size of CounterDataPrefix generated from NVPW_CounterDataBuilder_GetCounterDataPrefix().
    uint32_t maxNumRanges;                                      //!< [in] Maximum number of ranges that can be profiled
    uint32_t maxNumRangeTreeNodes;                              //!< [in] Maximum number of RangeTree nodes; must be >= maxNumRanges
    uint32_t maxRangeNameLength;                                //!< [in] Maximum string length of each RangeName, including the trailing NULL character
} CUpti_Profiler_CounterDataImageOptions;
#define CUpti_Profiler_CounterDataImageOptions_STRUCT_SIZE                       CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_CounterDataImageOptions, maxRangeNameLength)


/**
 * \brief Params for cuptiProfilerCounterDataImageCalculateSize
 */
typedef struct CUpti_Profiler_CounterDataImage_CalculateSize_Params
{
    size_t structSize;                                          //!< [in] CUpti_Profiler_CounterDataImage_CalculateSize_Params_STRUCT_SIZE
    void* pPriv;                                                //!< [in] assign to NULL

    size_t sizeofCounterDataImageOptions;                       //!< [in] CUpti_Profiler_CounterDataImageOptions_STRUCT_SIZE
    const CUpti_Profiler_CounterDataImageOptions* pOptions;     //!< [in] Pointer to Counter Data Image Options
    size_t counterDataImageSize;                                //!< [out]
} CUpti_Profiler_CounterDataImage_CalculateSize_Params;
#define CUpti_Profiler_CounterDataImage_CalculateSize_Params_STRUCT_SIZE         CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_CounterDataImage_CalculateSize_Params, counterDataImageSize)




/**
 * \brief Params for cuptiProfilerCounterDataImageInitialize
 */
typedef struct CUpti_Profiler_CounterDataImage_Initialize_Params
{
    size_t structSize;                                          //!< [in] CUpti_Profiler_CounterDataImage_Initialize_Params_STRUCT_SIZE
    void* pPriv;                                                //!< [in] assign to NULL

    size_t sizeofCounterDataImageOptions;                       //!< [in] CUpti_Profiler_CounterDataImageOptions_STRUCT_SIZE
    const CUpti_Profiler_CounterDataImageOptions* pOptions;     //!< [in] Pointer to Counter Data Image Options
    size_t counterDataImageSize;                                //!< [in] Size calculated from cuptiProfilerCounterDataImageCalculateSize
    uint8_t* pCounterDataImage;                                 //!< [in] The buffer to be initialized.
} CUpti_Profiler_CounterDataImage_Initialize_Params;
#define CUpti_Profiler_CounterDataImage_Initialize_Params_STRUCT_SIZE            CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_CounterDataImage_Initialize_Params, pCounterDataImage)

/**
 * \brief A CounterData image allocates space for values for each counter for each range.
 *
 * User borne the resposibility of managing the counterDataImage allocations.
 * CounterDataPrefix contains meta data about the metrics that will be stored in counterDataImage.
 * Use these APIs to calculate the allocation size and initialize counterData image.
 */
extern "C"
CUptiResult cuptiProfilerCounterDataImageCalculateSize(CUpti_Profiler_CounterDataImage_CalculateSize_Params* pParams);

extern "C"
CUptiResult cuptiProfilerCounterDataImageInitialize(CUpti_Profiler_CounterDataImage_Initialize_Params* pParams);







/**
 * \brief Params for cuptiProfilerCounterDataImageCalculateScratchBufferSize
 */
typedef struct CUpti_Profiler_CounterDataImage_CalculateScratchBufferSize_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_CounterDataImage_CalculateScratchBufferSize_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    size_t counterDataImageSize;                            //!< [in] size calculated from cuptiProfilerCounterDataImageCalculateSize
    uint8_t* pCounterDataImage;                             //!< [in]
    size_t counterDataScratchBufferSize;                    //!< [out]
} CUpti_Profiler_CounterDataImage_CalculateScratchBufferSize_Params;
#define CUpti_Profiler_CounterDataImage_CalculateScratchBufferSize_Params_STRUCT_SIZE    CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_CounterDataImage_CalculateScratchBufferSize_Params, counterDataScratchBufferSize)

/**
 * \brief Params for cuptiProfilerCounterDataImageInitializeScratchBuffer
 */
typedef struct CUpti_Profiler_CounterDataImage_InitializeScratchBuffer_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_CounterDataImage_InitializeScratchBuffer_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    size_t counterDataImageSize;                            //!< [in] size calculated from cuptiProfilerCounterDataImageCalculateSize
    uint8_t* pCounterDataImage;                             //!< [in]
    size_t counterDataScratchBufferSize;                    //!< [in] size calculated using cuptiProfilerCounterDataImageCalculateScratchBufferSize
    uint8_t* pCounterDataScratchBuffer;                     //!< [in] the scratch buffer to be initialized.
} CUpti_Profiler_CounterDataImage_InitializeScratchBuffer_Params;
#define CUpti_Profiler_CounterDataImage_InitializeScratchBuffer_Params_STRUCT_SIZE       CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_CounterDataImage_InitializeScratchBuffer_Params, pCounterDataScratchBuffer)

/**
 * \brief A temporary storage for CounterData image needed for internal operations
 *
 * Use these APIs to calculate the allocation size and initialize counterData image scratch buffer.
 */

extern "C"
CUptiResult cuptiProfilerCounterDataImageCalculateScratchBufferSize(CUpti_Profiler_CounterDataImage_CalculateScratchBufferSize_Params* pParams);

extern "C"
CUptiResult cuptiProfilerCounterDataImageInitializeScratchBuffer(CUpti_Profiler_CounterDataImage_InitializeScratchBuffer_Params* pParams);







/**
 * \brief Params for cuptiProfilerBeginSession
 */
typedef struct CUpti_Profiler_BeginSession_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_BeginSession_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
    size_t counterDataImageSize;                            //!< [in] size calculated from cuptiProfilerCounterDataImageCalculateSize
    uint8_t* pCounterDataImage;                             //!< [in] address of CounterDataImage
    size_t counterDataScratchBufferSize;                    //!< [in] size calculated from cuptiProfilerCounterDataImageInitializeScratchBuffer
    uint8_t* pCounterDataScratchBuffer;                     //!< [in] address of CounterDataImage scratch buffer
    uint8_t bDumpCounterDataInFile;                          //!< [in] [optional]
    const char* pCounterDataFilePath;                        //!< [in] [optional]
    CUpti_ProfilerRange range;                               //!< [in] CUpti_ProfilerRange
    CUpti_ProfilerReplayMode replayMode;                     //!< [in] CUpti_ProfilerReplayMode
    /* Replay options, required when replay is done by cupti user */
    size_t maxRangesPerPass;                                //!< [in] Maximum number of ranges that can be recorded in a single pass.
    size_t maxLaunchesPerPass;                              //!< [in] Maximum number of kernel launches that can be recorded in a single pass; must be >= maxRangesPerPass.

} CUpti_Profiler_BeginSession_Params;
#define CUpti_Profiler_BeginSession_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_BeginSession_Params, maxLaunchesPerPass)
/**
 * \brief Params for cuptiProfilerEndSession
 */
typedef struct CUpti_Profiler_EndSession_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_EndSession_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
} CUpti_Profiler_EndSession_Params;
#define CUpti_Profiler_EndSession_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_EndSession_Params, ctx)

/**
 * \brief Begin profiling session sets up the profiling on the device
 *
 * Although, it doesn't start the profiling but GPU resources needed for profiling are allocated.
 * Outside of a session, the GPU will return to its normal operating state.
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerBeginSession(CUpti_Profiler_BeginSession_Params* pParams);
/**
 * \brief Ends profiling session
 *
 * Frees up the GPU resources acquired for profiling.
 * Outside of a session, the GPU will return to it's normal operating state.
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerEndSession(CUpti_Profiler_EndSession_Params* pParams);

/**
 * \brief Params for cuptiProfilerSetConfig
 */
typedef struct CUpti_Profiler_SetConfig_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_SetConfig_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
    const uint8_t* pConfig;                                 //!< [in] Config created by NVPW_RawMetricsConfig_GetConfigImage(). Must be align(8).
    size_t configSize;                                      //!< [in] size of config
    uint16_t minNestingLevel;                               //!< [in] the lowest nesting level to be profiled; must be >= 1
    uint16_t numNestingLevels;                              //!< [in] the number of nesting levels to profile; must be >= 1
    size_t passIndex;                                       //!< [in] Set this to zero for in-app replay; set this to the output of EndPass() for application replay
    uint16_t targetNestingLevel;                            //!< [in] Set this to minNestingLevel for in-app replay; set this to the output of EndPass() for application
} CUpti_Profiler_SetConfig_Params;

#define CUpti_Profiler_SetConfig_Params_STRUCT_SIZE                    CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_SetConfig_Params, targetNestingLevel)

/**
 * \brief Params for cuptiProfilerUnsetConfig
 */
typedef struct CUpti_Profiler_UnsetConfig_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_UnsetConfig_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
} CUpti_Profiler_UnsetConfig_Params;
#define CUpti_Profiler_UnsetConfig_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_UnsetConfig_Params, ctx)

/**
 * \brief Set metrics configuration to be profiled
 *
 * Use these APIs to set the config to profile in a session. It can be used for advanced cases such as where multiple
 * configurations are collected into a single CounterData Image on the need basis, without restarting the session.
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerSetConfig(CUpti_Profiler_SetConfig_Params* pParams);
/**
 * \brief Unset metrics configuration profiled
 *
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerUnsetConfig(CUpti_Profiler_UnsetConfig_Params* pParams);

// /**
//  * \brief Params for cuptiProfilerBeginPass
//  */
// typedef struct CUpti_Profiler_BeginPass_Params
// {
//     size_t structSize;                                      //!< [in] CUpti_Profiler_BeginPass_Params_STRUCT_SIZE
//     void* pPriv;                                            //!< [in] assign to NULL

//     CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
// } CUpti_Profiler_BeginPass_Params;
// #define CUpti_Profiler_BeginPass_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_BeginPass_Params, ctx)

// /**
//  * \brief Params for cuptiProfilerEndPass
//  */
// typedef struct CUpti_Profiler_EndPass_Params
// {
//     size_t structSize;                                      //!< [in] CUpti_Profiler_EndPass_Params_STRUCT_SIZE
//     void* pPriv;                                            //!< [in] assign to NULL

//     CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
//     uint16_t targetNestingLevel;                            //!  [out] The targetNestingLevel that will be collected by the *next* BeginPass.
//     size_t passIndex;                                       //!< [out] The passIndex that will be collected by the *next* BeginPass
//     uint8_t allPassesSubmitted;                             //!< [out] becomes true when the last pass has been queued to the GPU
// } CUpti_Profiler_EndPass_Params;
// #define CUpti_Profiler_EndPass_Params_STRUCT_SIZE                    CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_EndPass_Params, allPassesSubmitted)

// /**
//  * \brief Replay API: used for multipass collection.

//  * These APIs are used if user chooses to replay by itself \ref CUPTI_UserReplay or \ref CUPTI_ApplicationReplay
//  * for multipass collection of the metrics configurations.
//  * It's a no-op in case of \ref CUPTI_KernelReplay.
//  */
// extern "C"
// CUptiResult cuptiProfilerBeginPass(CUpti_Profiler_BeginPass_Params* pParams);

// /**
//  * \brief Replay API: used for multipass collection.

//  * These APIs are used if user chooses to replay by itself \ref CUPTI_UserReplay or \ref CUPTI_ApplicationReplay
//  * for multipass collection of the metrics configurations.
//  * Its a no-op in case of \ref CUPTI_KernelReplay.
//  * Returns information for next pass.
//  */
// extern "C"
// CUptiResult cuptiProfilerEndPass(CUpti_Profiler_EndPass_Params* pParams);

/**
 * \brief Params for cuptiProfilerEnableProfiling
 */
typedef struct CUpti_Profiler_EnableProfiling_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_EnableProfiling_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
} CUpti_Profiler_EnableProfiling_Params;
#define CUpti_Profiler_EnableProfiling_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_EnableProfiling_Params, ctx)

/**
 * \brief Params for cuptiProfilerDisableProfiling
 */
typedef struct CUpti_Profiler_DisableProfiling_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_DisableProfiling_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
} CUpti_Profiler_DisableProfiling_Params;
#define CUpti_Profiler_DisableProfiling_Params_STRUCT_SIZE                  CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_DisableProfiling_Params, ctx)

/**
 * \brief Enables Profiling
 *
 * In \ref CUPTI_AutoRange, these APIs are used to enable/disable profiling for the kernels to be executed in
 * a profiling session.
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerEnableProfiling(CUpti_Profiler_EnableProfiling_Params* pParams);

/**
 * \brief Disable Profiling
 *
 * In \ref CUPTI_AutoRange, these APIs are used to enable/disable profiling for the kernels to be executed in
 * a profiling session.
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerDisableProfiling(CUpti_Profiler_DisableProfiling_Params* pParams);





/**
 * \brief Params for cuptiProfilerFlushCounterData
 */
typedef struct CUpti_Profiler_FlushCounterData_Params
{
    size_t structSize;                                      //!< [in] CUpti_Profiler_FlushCounterData_Params_STRUCT_SIZE
    void* pPriv;                                            //!< [in] assign to NULL

    CUcontext ctx;                                          //!< [in] if NULL, the current CUcontext is used
    size_t numRangesDropped;                                //!< [out] number of ranges whose data was dropped in the processed passes
    size_t numTraceBytesDropped;                            //!< [out] number of bytes not written to TraceBuffer due to buffer full
} CUpti_Profiler_FlushCounterData_Params;
#define CUpti_Profiler_FlushCounterData_Params_STRUCT_SIZE           CUPTI_PROFILER_STRUCT_SIZE(CUpti_Profiler_FlushCounterData_Params, numTraceBytesDropped)

/**
 * \brief Decode all the submitted passes
 *
 * Flush Counter data API to ensure every pass is decoded into the counterDataImage passed at beginSession.
 * This will cause the CPU/GPU sync to collect all the undecoded pass.
 */
extern "C"
CUptiResult CUPTIAPI cuptiProfilerFlushCounterData(CUpti_Profiler_FlushCounterData_Params* pParams);


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


template <typename T>

class ScopeExit
{
public:
    ScopeExit(T t) : t(t) {}
    ~ScopeExit() { t(); }
    T t;
};

template <typename T>
ScopeExit<T> MoveScopeExit(T t) {
    return ScopeExit<T>(t);
};

#define NV_ANONYMOUS_VARIABLE_DIRECT(name, line) name##line
#define NV_ANONYMOUS_VARIABLE_INDIRECT(name, line) NV_ANONYMOUS_VARIABLE_DIRECT(name, line)

#define SCOPE_EXIT(func) const auto NV_ANONYMOUS_VARIABLE_INDIRECT(EXIT, __LINE__) = MoveScopeExit([=](){func;})




inline bool ParseMetricNameString(const std::string& metricName, std::string* reqName, bool* isolated, bool* keepInstances)
{
    std::string& name = *reqName;
    name = metricName;
    if (name.empty())
    {
        return false;
    }

    // boost program_options sometimes inserts a \n between the metric name and a '&' at the end
    size_t pos = name.find('\n');
    if (pos != std::string::npos)
    {
        name.erase(pos, 1);
    }

    // trim whitespace
    while (name.back() == ' ')
    {
        name.pop_back();
        if (name.empty())
        {
            return false;
        }
    }

    *keepInstances = false;
    if (name.back() == '+')
    {
        *keepInstances = true;
        name.pop_back();
        if (name.empty())
        {
            return false;
        }
    }

    *isolated = true;
    if (name.back() == '$')
    {
        name.pop_back();
        if (name.empty())
        {
            return false;
        }
    }
    else if (name.back() == '&')
    {
        *isolated = false;
        name.pop_back();
        if (name.empty())
        {
            return false;
        }
    }

    return true;
}




static const char* GetNVPWResultString(NVPA_Status status) {
    const char* errorMsg = NULL;
    switch (status)
    {
    case NVPA_STATUS_ERROR:
        errorMsg = "NVPA_STATUS_ERROR";
        break;
    case NVPA_STATUS_INTERNAL_ERROR:
        errorMsg = "NVPA_STATUS_INTERNAL_ERROR";
        break;
    case NVPA_STATUS_NOT_INITIALIZED:
        errorMsg = "NVPA_STATUS_NOT_INITIALIZED";
        break;
    case NVPA_STATUS_NOT_LOADED:
        errorMsg = "NVPA_STATUS_NOT_LOADED";
        break;
    case NVPA_STATUS_FUNCTION_NOT_FOUND:
        errorMsg = "NVPA_STATUS_FUNCTION_NOT_FOUND";
        break;
    case NVPA_STATUS_NOT_SUPPORTED:
        errorMsg = "NVPA_STATUS_NOT_SUPPORTED";
        break;
    case NVPA_STATUS_NOT_IMPLEMENTED:
        errorMsg = "NVPA_STATUS_NOT_IMPLEMENTED";
        break;
    case NVPA_STATUS_INVALID_ARGUMENT:
        errorMsg = "NVPA_STATUS_INVALID_ARGUMENT";
        break;
    case NVPA_STATUS_INVALID_METRIC_ID:
        errorMsg = "NVPA_STATUS_INVALID_METRIC_ID";
        break;
    case NVPA_STATUS_DRIVER_NOT_LOADED:
        errorMsg = "NVPA_STATUS_DRIVER_NOT_LOADED";
        break;
    case NVPA_STATUS_OUT_OF_MEMORY:
        errorMsg = "NVPA_STATUS_OUT_OF_MEMORY";
        break;
    case NVPA_STATUS_INVALID_THREAD_STATE:
        errorMsg = "NVPA_STATUS_INVALID_THREAD_STATE";
        break;
    case NVPA_STATUS_FAILED_CONTEXT_ALLOC:
        errorMsg = "NVPA_STATUS_FAILED_CONTEXT_ALLOC";
        break;
    case NVPA_STATUS_UNSUPPORTED_GPU:
        errorMsg = "NVPA_STATUS_UNSUPPORTED_GPU";
        break;
    case NVPA_STATUS_INSUFFICIENT_DRIVER_VERSION:
        errorMsg = "NVPA_STATUS_INSUFFICIENT_DRIVER_VERSION";
        break;
    case NVPA_STATUS_OBJECT_NOT_REGISTERED:
        errorMsg = "NVPA_STATUS_OBJECT_NOT_REGISTERED";
        break;
    case NVPA_STATUS_INSUFFICIENT_PRIVILEGE:
        errorMsg = "NVPA_STATUS_INSUFFICIENT_PRIVILEGE";
        break;
    case NVPA_STATUS_INVALID_CONTEXT_STATE:
        errorMsg = "NVPA_STATUS_INVALID_CONTEXT_STATE";
        break;
    case NVPA_STATUS_INVALID_OBJECT_STATE:
        errorMsg = "NVPA_STATUS_INVALID_OBJECT_STATE";
        break;
    case NVPA_STATUS_RESOURCE_UNAVAILABLE:
        errorMsg = "NVPA_STATUS_RESOURCE_UNAVAILABLE";
        break;
    case NVPA_STATUS_DRIVER_LOADED_TOO_LATE:
        errorMsg = "NVPA_STATUS_DRIVER_LOADED_TOO_LATE";
        break;
    case NVPA_STATUS_INSUFFICIENT_SPACE:
        errorMsg = "NVPA_STATUS_INSUFFICIENT_SPACE";
        break;
    case NVPA_STATUS_OBJECT_MISMATCH:
        errorMsg = "NVPA_STATUS_OBJECT_MISMATCH";
        break;
    case NVPA_STATUS_VIRTUALIZED_DEVICE_NOT_SUPPORTED:
        errorMsg = "NVPA_STATUS_VIRTUALIZED_DEVICE_NOT_SUPPORTED";
        break;
    default:
        break;
    }

    return errorMsg;
}


#define NVPW_API_CALL(apiFuncCall)                                             \
do {                                                                           \
    NVPA_Status _status = apiFuncCall;                                         \
    if (_status != NVPA_STATUS_SUCCESS) {                                      \
        fprintf(stderr, "%s:%d: error: function %s failed with error %d.\n",   \
                __FILE__, __LINE__, #apiFuncCall, _status);                    \
        exit(-1);                                                              \
    }                                                                          \
} while (0)


#define RETURN_IF_NVPW_ERROR(retval, actual)                                        \
do {                                                                                \
    NVPA_Status status = actual;                                                    \
    if (NVPA_STATUS_SUCCESS != status) {                                            \
        fprintf(stderr, "FAILED: %s with error %s\n", #actual, GetNVPWResultString(status)); \
        return retval;                                                              \
    }                                                                               \
} while (0)



// #ifndef NVPA_STRUCT_SIZE
// #define NVPA_STRUCT_SIZE(type_, lastfield_)                     (offsetof(type_, lastfield_) + sizeof(((type_*)0)->lastfield_))
// #endif // NVPA_STRUCT_SIZE


// typedef struct NVPW_InitializeHost_Params
// {
//     /// [in]
//     size_t structSize;
//     /// [in] assign to NULL
//     void* pPriv;
// } NVPW_InitializeHost_Params;
// #define NVPW_InitializeHost_Params_STRUCT_SIZE NVPA_STRUCT_SIZE(NVPW_InitializeHost_Params, pPriv)

// /// Load the host library.
// extern "C"
// NVPA_Status NVPW_InitializeHost(NVPW_InitializeHost_Params* pParams);

#endif