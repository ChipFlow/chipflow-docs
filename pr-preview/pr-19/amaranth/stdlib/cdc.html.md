# Clock domain crossing

The [`amaranth.lib.cdc`](#module-amaranth.lib.cdc) module provides building blocks for transferring data between clock domains.

### *class* amaranth.lib.cdc.FFSynchronizer

Resynchronise a signal to a different clock domain.

Consists of a chain of flip-flops. Eliminates metastabilities at the output, but provides
no other guarantee as to the safe domain-crossing of a signal.

* **Parameters:**
  * **i** (*Signal* *(**n* *)* *,* *in*) – Signal to be resynchronised.
  * **o** (*Signal* *(**n* *)* *,* *out*) – Signal connected to synchroniser output.
  * **o_domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of output clock domain.
  * **init** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Initial and reset value of the flip-flops. On FPGAs, even if `reset_less` is `True`,
    the [`FFSynchronizer`](#amaranth.lib.cdc.FFSynchronizer) is still set to this value during initialization.
  * **reset_less** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If `True` (the default), this [`FFSynchronizer`](#amaranth.lib.cdc.FFSynchronizer) is unaffected by `o_domain`
    reset. See the note below for details.
  * **stages** ([*int*](https://docs.python.org/3/library/functions.html#int) *,*  *>=2*) – Number of synchronization stages between input and output. The lowest safe number is 2,
    with higher numbers reducing MTBF further, at the cost of increased latency.
  * **max_input_delay** (*None* *or* [*float*](https://docs.python.org/3/library/functions.html#float)) – Maximum delay from the input signal’s clock to the first synchronization stage, in seconds.
    If specified and the platform does not support it, elaboration will fail.

#### NOTE
[`FFSynchronizer`](#amaranth.lib.cdc.FFSynchronizer) is non-resettable by default. Usually this is the safest option;
on FPGAs the [`FFSynchronizer`](#amaranth.lib.cdc.FFSynchronizer) will still be initialized to its `reset` value when
the FPGA loads its configuration.

However, in designs where the value of the [`FFSynchronizer`](#amaranth.lib.cdc.FFSynchronizer) must be valid immediately
after reset, consider setting `reset_less` to `False` if any of the following is true:

- You are targeting an ASIC, or an FPGA that does not allow arbitrary initial flip-flop states;
- Your design features warm (non-power-on) resets of `o_domain`, so the one-time
  initialization at power on is insufficient;
- Your design features a sequenced reset, and the [`FFSynchronizer`](#amaranth.lib.cdc.FFSynchronizer) must maintain
  its reset value until `o_domain` reset specifically is deasserted.

[`FFSynchronizer`](#amaranth.lib.cdc.FFSynchronizer) is reset by the `o_domain` reset only.

### Platform overrides

Define the `get_ff_sync` platform method to override the implementation of
[`FFSynchronizer`](#amaranth.lib.cdc.FFSynchronizer), e.g. to instantiate library cells directly.

### *class* amaranth.lib.cdc.AsyncFFSynchronizer

Synchronize deassertion of an asynchronous signal.

The signal driven by the [`AsyncFFSynchronizer`](#amaranth.lib.cdc.AsyncFFSynchronizer) is asserted asynchronously and deasserted
synchronously, eliminating metastability during deassertion.

This synchronizer is primarily useful for resets and reset-like signals.

* **Parameters:**
  * **i** (*Signal* *(**1* *)* *,* *in*) – Asynchronous input signal, to be synchronized.
  * **o** (*Signal* *(**1* *)* *,* *out*) – Synchronously released output signal.
  * **o_domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of clock domain to synchronize to.
  * **stages** ([*int*](https://docs.python.org/3/library/functions.html#int) *,*  *>=2*) – Number of synchronization stages between input and output. The lowest safe number is 2,
    with higher numbers reducing MTBF further, at the cost of increased deassertion latency.
  * **async_edge** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The edge of the input signal which causes the output to be set. Must be one of “pos” or “neg”.
  * **max_input_delay** (*None* *or* [*float*](https://docs.python.org/3/library/functions.html#float)) – Maximum delay from the input signal’s clock to the first synchronization stage, in seconds.
    If specified and the platform does not support it, elaboration will fail.

### Platform overrides

Define the `get_async_ff_sync` platform method to override the implementation of
[`AsyncFFSynchronizer`](#amaranth.lib.cdc.AsyncFFSynchronizer), e.g. to instantiate library cells directly.

### *class* amaranth.lib.cdc.ResetSynchronizer

Synchronize deassertion of a clock domain reset.

The reset of the clock domain driven by the [`ResetSynchronizer`](#amaranth.lib.cdc.ResetSynchronizer) is asserted
asynchronously and deasserted synchronously, eliminating metastability during deassertion.

The driven clock domain could use a reset that is asserted either synchronously or
asynchronously; a reset is always deasserted synchronously. A domain with an asynchronously
asserted reset is useful if the clock of the domain may be gated, yet the domain still
needs to be reset promptly; otherwise, synchronously asserted reset (the default) should
be used.

* **Parameters:**
  * **arst** (*Signal* *(**1* *)* *,* *in*) – Asynchronous reset signal, to be synchronized.
  * **domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of clock domain to reset.
  * **stages** ([*int*](https://docs.python.org/3/library/functions.html#int) *,*  *>=2*) – Number of synchronization stages between input and output. The lowest safe number is 2,
    with higher numbers reducing MTBF further, at the cost of increased deassertion latency.
  * **max_input_delay** (*None* *or* [*float*](https://docs.python.org/3/library/functions.html#float)) – Maximum delay from the input signal’s clock to the first synchronization stage, in seconds.
    If specified and the platform does not support it, elaboration will fail.

### Platform overrides

Define the `get_reset_sync` platform method to override the implementation of
[`ResetSynchronizer`](#amaranth.lib.cdc.ResetSynchronizer), e.g. to instantiate library cells directly.

### *class* amaranth.lib.cdc.PulseSynchronizer

A one-clock pulse on the input produces a one-clock pulse on the output.

If the output clock is faster than the input clock, then the input may be safely asserted at
100% duty cycle. Otherwise, if the clock ratio is `n`:1, the input may be asserted at most
once in every `n` input clocks, else pulses may be dropped. Other than this there is
no constraint on the ratio of input and output clock frequency.

* **Parameters:**
  * **i_domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of input clock domain.
  * **o_domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of output clock domain.
  * **stages** ([*int*](https://docs.python.org/3/library/functions.html#int) *,*  *>=2*) – Number of synchronization stages between input and output. The lowest safe number is 2,
    with higher numbers reducing MTBF further, at the cost of increased deassertion latency.
