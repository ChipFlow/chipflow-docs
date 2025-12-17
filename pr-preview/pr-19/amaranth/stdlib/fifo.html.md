# First-in first-out queues

The `amaranth.lib.fifo` module provides building blocks for first-in, first-out queues.

### *class* amaranth.lib.fifo.FIFOInterface(\*, width, depth)

Data written to the input interface (`w_data`, `w_rdy`, `w_en`) is buffered and can be
read at the output interface (`r_data`, `r_rdy`, `r_en`). The data entry written first
to the input also appears first on the output.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width of data entries.
  * **depth** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Depth of the queue. If zero, the FIFO cannot be read from or written to.
* **Attributes:**
  * **w_data** (*Signal(width), in*) – Input data.
  * **w_rdy** (*Signal(1), out*) – Asserted if there is space in the queue, i.e. `w_en` can be asserted to write
    a new entry.
  * **w_en** (*Signal(1), in*) – Write strobe. Latches `w_data` into the queue. Does nothing if `w_rdy` is not asserted.
  * **w_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.
  * **r_data** (*Signal(width), out*) – Output data. The conditions in which `r_data` is valid depends on the type of the queue.
  * **r_rdy** (*Signal(1), out*) – Asserted if there is an entry in the queue, i.e. `r_en` can be asserted to read
    an existing entry.
  * **r_en** (*Signal(1), in*) – Read strobe. Makes the next entry (if any) available on `r_data` at the next cycle.
    Does nothing if `r_rdy` is not asserted.
  * **r_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.

#### NOTE
The [`FIFOInterface`](#amaranth.lib.fifo.FIFOInterface) class can be used directly to substitute a FIFO in tests, or inherited from in a custom FIFO implementation.

### *class* amaranth.lib.fifo.SyncFIFO(\*, width, depth)

Synchronous first in, first out queue.

Read and write interfaces are accessed from the same clock domain. If different clock domains
are needed, use [`AsyncFIFO`](#amaranth.lib.fifo.AsyncFIFO).

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width of data entries.
  * **depth** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Depth of the queue. If zero, the FIFO cannot be read from or written to.
* **Attributes:**
  * **level** (*Signal(range(depth + 1)), out*) – Number of unread entries. This level is the same between read and write for synchronous FIFOs.
  * **w_data** (*Signal(width), in*) – Input data.
  * **w_rdy** (*Signal(1), out*) – Asserted if there is space in the queue, i.e. `w_en` can be asserted to write
    a new entry.
  * **w_en** (*Signal(1), in*) – Write strobe. Latches `w_data` into the queue. Does nothing if `w_rdy` is not asserted.
  * **w_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.
  * **r_data** (*Signal(width), out*) – Output data. Valid if `r_rdy` is asserted.
  * **r_rdy** (*Signal(1), out*) – Asserted if there is an entry in the queue, i.e. `r_en` can be asserted to read
    an existing entry.
  * **r_en** (*Signal(1), in*) – Read strobe. Makes the next entry (if any) available on `r_data` at the next cycle.
    Does nothing if `r_rdy` is not asserted.
  * **r_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.

### *class* amaranth.lib.fifo.SyncFIFOBuffered(\*, width, depth)

Buffered synchronous first in, first out queue.

This queue’s interface is identical to [`SyncFIFO`](#amaranth.lib.fifo.SyncFIFO), but it
does not use asynchronous memory reads, which are incompatible with FPGA block RAMs.

In exchange, the latency between an entry being written to an empty queue and that entry
becoming available on the output is increased by one cycle compared to [`SyncFIFO`](#amaranth.lib.fifo.SyncFIFO).

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width of data entries.
  * **depth** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Depth of the queue. If zero, the FIFO cannot be read from or written to.
* **Attributes:**
  * **level** (*Signal(range(depth + 1)), out*) – Number of unread entries. This level is the same between read and write for synchronous FIFOs.
  * **w_data** (*Signal(width), in*) – Input data.
  * **w_rdy** (*Signal(1), out*) – Asserted if there is space in the queue, i.e. `w_en` can be asserted to write
    a new entry.
  * **w_en** (*Signal(1), in*) – Write strobe. Latches `w_data` into the queue. Does nothing if `w_rdy` is not asserted.
  * **w_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.
  * **r_data** (*Signal(width), out*) – Output data. Valid if `r_rdy` is asserted.
  * **r_rdy** (*Signal(1), out*) – Asserted if there is an entry in the queue, i.e. `r_en` can be asserted to read
    an existing entry.
  * **r_en** (*Signal(1), in*) – Read strobe. Makes the next entry (if any) available on `r_data` at the next cycle.
    Does nothing if `r_rdy` is not asserted.
  * **r_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.

### *class* amaranth.lib.fifo.AsyncFIFO(\*, width, depth, r_domain='read', w_domain='write', exact_depth=False)

Asynchronous first in, first out queue.

Read and write interfaces are accessed from different clock domains, which can be set when
constructing the FIFO.

[`AsyncFIFO`](#amaranth.lib.fifo.AsyncFIFO) can be reset from the write clock domain. When the write domain reset is
asserted, the FIFO becomes empty. When the read domain is reset, data remains in the FIFO - the
read domain logic should correctly handle this case.

[`AsyncFIFO`](#amaranth.lib.fifo.AsyncFIFO) only supports power of 2 depths. Unless `exact_depth` is specified,
the `depth` parameter is rounded up to the next power of 2.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width of data entries.
  * **depth** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Depth of the queue. If zero, the FIFO cannot be read from or written to.
  * **r_domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Read clock domain.
  * **w_domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Write clock domain.
* **Attributes:**
  * **w_data** (*Signal(width), in*) – Input data.
  * **w_rdy** (*Signal(1), out*) – Asserted if there is space in the queue, i.e. `w_en` can be asserted to write
    a new entry.
  * **w_en** (*Signal(1), in*) – Write strobe. Latches `w_data` into the queue. Does nothing if `w_rdy` is not asserted.
  * **w_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.
  * **r_data** (*Signal(width), out*) – Output data. Valid if `r_rdy` is asserted.
  * **r_rdy** (*Signal(1), out*) – Asserted if there is an entry in the queue, i.e. `r_en` can be asserted to read
    an existing entry.
  * **r_en** (*Signal(1), in*) – Read strobe. Makes the next entry (if any) available on `r_data` at the next cycle.
    Does nothing if `r_rdy` is not asserted.
  * **r_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.
  * **r_rst** (*Signal(1), out*) – Asserted, for at least one read-domain clock cycle, after the FIFO has been reset by
    the write-domain reset.

### *class* amaranth.lib.fifo.AsyncFIFOBuffered(\*, width, depth, r_domain='read', w_domain='write', exact_depth=False)

Buffered asynchronous first in, first out queue.

Read and write interfaces are accessed from different clock domains, which can be set when
constructing the FIFO.

[`AsyncFIFOBuffered`](#amaranth.lib.fifo.AsyncFIFOBuffered) only supports power of 2 plus one depths. Unless `exact_depth`
is specified, the `depth` parameter is rounded up to the next power of 2 plus one.
(The output buffer acts as an additional queue element.)

This queue’s interface is identical to [`AsyncFIFO`](#amaranth.lib.fifo.AsyncFIFO), but it has an additional register
on the output, improving timing in case of block RAM that has large clock-to-output delay.

In exchange, the latency between an entry being written to an empty queue and that entry
becoming available on the output is increased by one cycle compared to [`AsyncFIFO`](#amaranth.lib.fifo.AsyncFIFO).

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width of data entries.
  * **depth** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Depth of the queue. If zero, the FIFO cannot be read from or written to.
  * **r_domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Read clock domain.
  * **w_domain** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Write clock domain.
* **Attributes:**
  * **w_data** (*Signal(width), in*) – Input data.
  * **w_rdy** (*Signal(1), out*) – Asserted if there is space in the queue, i.e. `w_en` can be asserted to write
    a new entry.
  * **w_en** (*Signal(1), in*) – Write strobe. Latches `w_data` into the queue. Does nothing if `w_rdy` is not asserted.
  * **w_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.
  * **r_data** (*Signal(width), out*) – Output data. Valid if `r_rdy` is asserted.
  * **r_rdy** (*Signal(1), out*) – Asserted if there is an entry in the queue, i.e. `r_en` can be asserted to read
    an existing entry.
  * **r_en** (*Signal(1), in*) – Read strobe. Makes the next entry (if any) available on `r_data` at the next cycle.
    Does nothing if `r_rdy` is not asserted.
  * **r_level** (*Signal(range(depth + 1)), out*) – Number of unread entries.
  * **r_rst** (*Signal(1), out*) – Asserted, for at least one read-domain clock cycle, after the FIFO has been reset by
    the write-domain reset.
