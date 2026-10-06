/******************************************************************************
 * @file        xHal_Rpi5CarErrorSignals.h
 * @brief       Defines public C++ error numbers and trace signal selectors.
 *
 * @details
 * Defines stable transport numbers and maps short project names to
 * namespace-backed standard exception types and POSIX signal numbers used by
 * xWalk trace macros.
 *
 * @project     xWalk Firmware
 * @module      xWalkTrace
 *
 * @author      Joxy John
 * @date        2026-08-11
 * @version     1.0.0
 *
 * @copyright
 * Copyright (c) 2026 Joxy John.
 * All rights reserved.
 *
 * @note
 * Developed using MISRA C++ coding guidelines.
 ******************************************************************************/

#ifndef XHAL_RPI5CAR_ERROR_SIGNALS_H
#define XHAL_RPI5CAR_ERROR_SIGNALS_H

/******************************************************************************
 * Includes
 ******************************************************************************/

#include <csignal>
#include "xHal_Rpi5CarTypes.h"

/******************************************************************************
 * Enumeration declarations
 ******************************************************************************/

namespace xwalk::hal
{

    /**
     * @brief Assigns stable transport numbers to public trace error selectors.
     *
     * @details
     * Values are independent of platform POSIX signal numbers and mirror the
     * `XWalkErrorSignalNumber` Protobuf enumeration used by `TraceRej`.
     */
    enum class XWalkErrorSignalNumber : uint32
    {
        /**
         * @brief No error selector was supplied or recognized.
         */
        Unspecified = 0U,

        /**
         * @brief Selects an invalid-argument diagnostic.
         */
        InvalidArgument = 1U,

        /**
         * @brief Selects an out-of-range diagnostic.
         */
        OutOfRange = 2U,

        /**
         * @brief Selects a length-error diagnostic.
         */
        LengthError = 3U,

        /**
         * @brief Selects a domain-error diagnostic.
         */
        DomainError = 4U,

        /**
         * @brief Selects a logic-error diagnostic.
         */
        LogicError = 5U,

        /**
         * @brief Selects a runtime-error diagnostic.
         */
        RuntimeError = 6U,

        /**
         * @brief Selects an overflow-error diagnostic.
         */
        OverflowError = 7U,

        /**
         * @brief Selects an underflow-error diagnostic.
         */
        UnderflowError = 8U,

        /**
         * @brief Selects a system-error diagnostic.
         */
        SystemError = 9U,

        /**
         * @brief Selects an allocation-failure diagnostic.
         */
        BadAllocation = 10U,

        /**
         * @brief Selects a bad-cast diagnostic.
         */
        BadCast = 11U,

        /**
         * @brief Selects a bad-type-information diagnostic.
         */
        BadTypeId = 12U,

        /**
         * @brief Selects a bad-function-call diagnostic.
         */
        BadFunctionCall = 13U,

        /**
         * @brief Selects a bad-optional-access diagnostic.
         */
        BadOptionalAccess = 14U,

        /**
         * @brief Selects a bad-variant-access diagnostic.
         */
        BadVariantAccess = 15U,

        /**
         * @brief Selects a bad-weak-pointer diagnostic.
         */
        BadWeakPointer = 16U,

        /**
         * @brief Selects a generic standard-exception diagnostic.
         */
        StandardException = 17U,

        /**
         * @brief Selects a process-abort diagnostic.
         */
        Abort = 18U,

        /**
         * @brief Selects a floating-point-exception diagnostic.
         */
        FloatingPoint = 19U,

        /**
         * @brief Selects an illegal-instruction diagnostic.
         */
        IllegalInstruction = 20U,

        /**
         * @brief Selects a segmentation-fault diagnostic.
         */
        SegmentationFault = 21U,

        /**
         * @brief Selects a termination-request diagnostic.
         */
        Termination = 22U,

        /**
         * @brief Selects an interactive-interrupt diagnostic.
         */
        Interrupt = 23U,

        /**
         * @brief Selects a broken-pipe diagnostic.
         */
        BrokenPipe = 24U,

        /**
         * @brief Selects a terminal-hangup diagnostic.
         */
        Hangup = 25U,

        /**
         * @brief Selects a trace-or-breakpoint diagnostic.
         */
        Trap = 26U,

        /**
         * @brief Selects a request addressed to a different server node.
         *
         * @details
         * The node reports this when a request's `server_ip` is not its own
         * address and the request is not an accepted `0.0.0.0` broadcast.
         */
        WrongServer = 27U
    };

} /* namespace xwalk::hal */

/******************************************************************************
 * C++ exception implementation
 ******************************************************************************/

namespace xwalk::hal
{

    /**
     * @brief Constructs one namespace-backed exception selected by an error macro.
     * @tparam ErrorType Standard exception type selected by a public macro.
     * @param[in] message Fully formatted diagnostic retained when supported.
     * @return Selected exception object.
     */
    template <typename ErrorType> ErrorType makeErrorSignal(const string& message)
    {
        if constexpr (std::is_constructible<ErrorType, const string&>::value)
        {
            return ErrorType(message);
        }
        else if constexpr (std::is_same<ErrorType, systemerror>::value)
        {
            return ErrorType(errorcode{}, message);
        }
        else
        {
            static_assert(std::is_default_constructible<ErrorType>::value,
                          "xWalk error selector must support message or default construction");
            static_cast<void>(message);
            return ErrorType{};
        }
    }

} /* namespace xwalk::hal */

/******************************************************************************
 * C++ exception selector macros
 ******************************************************************************/

/** @brief Selects `std::invalid_argument` for an xWalk error macro. */
#define XWALK_INVAL ::xwalk::hal::invalidargument

/** @brief Selects `std::out_of_range` for an xWalk error macro. */
#define XWALK_RANGE ::xwalk::hal::outofrange

/** @brief Selects `std::length_error` for an xWalk error macro. */
#define XWALK_LENGTH ::xwalk::hal::lengtherror

/** @brief Selects `std::domain_error` for an xWalk error macro. */
#define XWALK_DOMAIN ::xwalk::hal::domainerror

/** @brief Selects `std::logic_error` for an xWalk error macro. */
#define XWALK_LOGIC ::xwalk::hal::logicerror

/** @brief Selects `std::runtime_error` for an xWalk error macro. */
#define XWALK_RUNTIME ::xwalk::hal::runtimeerror

/** @brief Selects `std::overflow_error` for an xWalk error macro. */
#define XWALK_OVERFLOW ::xwalk::hal::overflowerror

/** @brief Selects `std::underflow_error` for an xWalk error macro. */
#define XWALK_UNDERFLOW ::xwalk::hal::underflowerror

/** @brief Selects `std::system_error` for an xWalk error macro. */
#define XWALK_SYSTEM ::xwalk::hal::systemerror

/** @brief Selects `std::bad_alloc` for an xWalk error macro. */
#define XWALK_ALLOC ::xwalk::hal::badallocation

/** @brief Selects `std::bad_cast` for an xWalk error macro. */
#define XWALK_CAST ::xwalk::hal::badcast

/** @brief Selects `std::bad_typeid` for an xWalk error macro. */
#define XWALK_TYPEID ::xwalk::hal::badtypeid

/** @brief Selects `std::bad_function_call` for an xWalk error macro. */
#define XWALK_FUNCTION ::xwalk::hal::badfunctioncall

/** @brief Selects `std::bad_optional_access` for an xWalk error macro. */
#define XWALK_OPTIONAL ::xwalk::hal::badoptionalaccess

/** @brief Selects `std::bad_variant_access` for an xWalk error macro. */
#define XWALK_VARIANT ::xwalk::hal::badvariantaccess

/** @brief Selects `std::bad_weak_ptr` for an xWalk error macro. */
#define XWALK_WEAKPTR ::xwalk::hal::badweakpointer

/** @brief Selects `std::exception` as the generic non-throwing error tag. */
#define XWALK_EXCEPTION ::xwalk::hal::standardexception

/******************************************************************************
 * Operating-system signal selectors
 ******************************************************************************/

namespace xwalk::hal
{

    /** @brief Namespace-backed ISO C process-abort signal number. */
    inline constexpr int32 abortsignal{SIGABRT};
    /** @brief Namespace-backed ISO C floating-point exception signal number. */
    inline constexpr int32 floatingpointsignal{SIGFPE};
    /** @brief Namespace-backed ISO C illegal-instruction signal number. */
    inline constexpr int32 illegalinstructionsignal{SIGILL};
    /** @brief Namespace-backed ISO C segmentation-fault signal number. */
    inline constexpr int32 segmentationfaultsignal{SIGSEGV};
    /** @brief Namespace-backed ISO C termination-request signal number. */
    inline constexpr int32 terminationsignal{SIGTERM};
    /** @brief Namespace-backed ISO C interactive-interrupt signal number. */
    inline constexpr int32 interruptsignal{SIGINT};

#if defined(SIGPIPE)
    /** @brief Namespace-backed POSIX broken-pipe signal number when available. */
    inline constexpr int32 pipesignal{SIGPIPE};
#endif

#if defined(SIGHUP)
    /** @brief Namespace-backed POSIX terminal-hangup signal number when available. */
    inline constexpr int32 hangupsignal{SIGHUP};
#endif

#if defined(SIGTRAP)
    /** @brief Namespace-backed POSIX trace-or-breakpoint signal number when available. */
    inline constexpr int32 trapsignal{SIGTRAP};
#endif

} /* namespace xwalk::hal */

/** @brief Selects the namespace-backed POSIX `SIGABRT` signal number. */
#define XWALK_ABORT ::xwalk::hal::abortsignal
/** @brief Selects the namespace-backed POSIX `SIGFPE` signal number. */
#define XWALK_FLOAT ::xwalk::hal::floatingpointsignal
/** @brief Selects the namespace-backed POSIX `SIGILL` signal number. */
#define XWALK_ILL ::xwalk::hal::illegalinstructionsignal
/** @brief Selects the namespace-backed POSIX `SIGSEGV` signal number. */
#define XWALK_SEGV ::xwalk::hal::segmentationfaultsignal
/** @brief Selects the namespace-backed POSIX `SIGTERM` signal number. */
#define XWALK_TERM ::xwalk::hal::terminationsignal
/** @brief Selects the namespace-backed POSIX `SIGINT` signal number. */
#define XWALK_INT ::xwalk::hal::interruptsignal

#if defined(SIGPIPE)
    /** @brief Selects namespace-backed POSIX `SIGPIPE` when the platform provides it. */
    #define XWALK_PIPE ::xwalk::hal::pipesignal
#endif

#if defined(SIGHUP)
    /** @brief Selects namespace-backed POSIX `SIGHUP` when the platform provides it. */
    #define XWALK_HANG ::xwalk::hal::hangupsignal
#endif

#if defined(SIGTRAP)
    /** @brief Selects namespace-backed POSIX `SIGTRAP` when the platform provides it. */
    #define XWALK_TRAP ::xwalk::hal::trapsignal
#endif

#endif /* XHAL_RPI5CAR_ERROR_SIGNALS_H */
