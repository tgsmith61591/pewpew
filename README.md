## `pewpew`

`pewpew` is a simple, easy-to-use library of tracing utilities to quickly identify
hotspots and opportunities for optimizations in your code.


### Advanced usage

#### 1. Controlling package behavior with environment variables

* `PEWPEW_TRACE_HISTORY_SIZE`

  The size of the trace history `pewpew` will retain. This is controlled
  by the `PEWPEW_TRACE_HISTORY_SIZE` environment variable. If not defined,
  the trace history will be allowed to grow to an arbitrary length. If set,
  once reached and exceeded, a corresponding number of traces from
  the front of the history (old traces) will be dropped.
