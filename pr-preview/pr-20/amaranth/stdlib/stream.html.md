# Data streams

The [`amaranth.lib.stream`](#module-amaranth.lib.stream) module provides a mechanism for unidirectional exchange of arbitrary data between modules.

## Introduction

One of the most common flow control mechanisms is *ready/valid handshaking*, where a *producer* pushes data to a *consumer* whenever it becomes available, and the consumer signals to the producer whether it can accept more data. In Amaranth, this mechanism is implemented using an [interface](wiring.md#wiring) with three members:

- `payload` (driven by the producer), containing the data;
- `valid` (driven by the producer), indicating that data is currently available in `payload`;
- `ready` (driven by the consumer), indicating that data is accepted if available.

This module provides such an interface, [`stream.Interface`](#amaranth.lib.stream.Interface), and defines the exact rules governing the flow of data through it.

<a id="stream-rules"></a>

## Data transfer rules

The producer and the consumer must be synchronized: they must belong to the same [clock domain](../guide.md#lang-clockdomains), and any [control flow modifiers](../guide.md#lang-controlinserter) must be applied to both, in the same order.

Data flows through a stream according to the following four rules:

1. On each cycle where both `valid` and `ready` are asserted, a transfer is performed: the contents of `payload` are conveyed from the producer to the consumer.
2. Once the producer asserts `valid`, it must not deassert `valid` or change the contents of `payload` until a transfer is performed.
3. The producer must not wait for `ready` to be asserted before asserting `valid`: any form of feedback from `ready` that causes `valid` to become asserted is prohibited.
4. The consumer may assert or deassert `ready` at any time, including via combinational feedback from `valid`.

Some producers and consumers may be designed without support for backpressure. Such producers must tie `ready` to `Const(1)` by specifying `always_ready=True` when constructing a stream, and consumers may (but are not required to) do the same. Similarly, some producers and consumers may be designed such that a payload is provided or must be provided on each cycle. Such consumers must tie `valid` to `Const(1)` by specifying `always_valid=True` when constructing a stream, and producers may (but are not required to) do the same.

If these control signals are tied to `Const(1)`, then the [`wiring.connect`](wiring.md#amaranth.lib.wiring.connect) function ensures that only compatible streams are connected together. For example, if the producer does not support backpressure (`ready` tied to `Const(1)`), it can only be connected to consumers that do not require backpressure. However, consumers that do not require backpressure can be connected to producers with or without support for backpressure. The `valid` control signal is treated similarly.

These rules ensure that producers and consumers that are developed independently can be safely used together, without unduly restricting the application-specific conditions that determine assertion of `valid` and `ready`.

## Examples

The following examples demonstrate the use of streams for a data processing pipeline that receives serial data input from an external device, transforms it by negating the 2’s complement value, and transmits it to another external device whenever requested. Similar pipelines, albeit more complex, are widely used in  applications.

The use of a unified data transfer mechanism enables uniform testing of individual units, and makes it possible to add a queue to the pipeline using only two additional connections.

<!-- from amaranth import * -->
```python
from amaranth.lib import stream, wiring
from amaranth.lib.wiring import In, Out
```

The pipeline is tested using the built-in simulator </simulator> and the two helper functions defined below:

```python
from amaranth.sim import Simulator

async def stream_get(ctx, stream):
    ctx.set(stream.ready, 1)
    payload, = await ctx.tick().sample(stream.payload).until(stream.valid)
    ctx.set(stream.ready, 0)
    return payload

async def stream_put(ctx, stream, payload):
    ctx.set(stream.valid, 1)
    ctx.set(stream.payload, payload)
    await ctx.tick().until(stream.ready)
    ctx.set(stream.valid, 0)
```

#### NOTE
“Minimal streams” as defined in [RFC 61](https://amaranth-lang.org/rfcs/0061-minimal-streams.html) do not provide built-in helper functions for testing pending further work on the clock domain system. They will be provided in a later release. For the time being, you can copy the helper functions above to test your designs that use streams.

### Serial receiver

The serial receiver captures the serial output of an external device and converts it to a stream of words. While the `ssel` signal is high, each low-to-high transition on the `sclk` input captures the value of the `sdat` signal; eight consecutive captured bits are assembled into a word ( first) and pushed into the pipeline for processing. If the `ssel` signal is low, no data transmission occurs and the transmitter and the receiver are instead synchronized with each other.

In this example, the external device does not provide a way to pause data transmission. If the pipeline isn’t ready to accept the next payload, it is necessary to discard data at some point; here, it is done in the serial receiver.

```python
class SerialReceiver(wiring.Component):
    ssel: In(1)
    sclk: In(1)
    sdat: In(1)

    stream: Out(stream.Signature(signed(8)))

    def elaborate(self, platform):
        m = Module()

        # Detect edges on the `sclk` input:
        sclk_reg = Signal()
        sclk_edge = ~sclk_reg & self.sclk
        m.d.sync += sclk_reg.eq(self.sclk)

        # Capture `sdat` and bits into payloads:
        count = Signal(range(8))
        data = Signal(8)
        done = Signal()
        with m.If(~self.ssel):
            m.d.sync += count.eq(0)
        with m.Elif(sclk_edge):
            m.d.sync += count.eq(count + 1)
            m.d.sync += data.eq(Cat(self.sdat, data))
            m.d.sync += done.eq(count == 7)

        # Push assembled payloads into the pipeline:
        with m.If(done & (~self.stream.valid | self.stream.ready)):
            m.d.sync += self.stream.payload.eq(data)
            m.d.sync += self.stream.valid.eq(1)
            m.d.sync += done.eq(0)
        with m.Elif(self.stream.ready):
            m.d.sync += self.stream.valid.eq(0)
        # Payload is discarded if `done & self.stream.valid & ~self.stream.ready`.

        return m
```

```python
def test_serial_receiver():
    dut = SerialReceiver()

    async def testbench_input(ctx):
        await ctx.tick()
        ctx.set(dut.ssel, 1)
        await ctx.tick()
        for bit in [1, 0, 1, 0, 0, 1, 1, 1]:
            ctx.set(dut.sdat, bit)
            ctx.set(dut.sclk, 0)
            await ctx.tick()
            ctx.set(dut.sclk, 1)
            await ctx.tick()
        ctx.set(dut.ssel, 0)
        await ctx.tick()

    async def testbench_output(ctx):
        expected_word = 0b10100111
        payload = await stream_get(ctx, dut.stream)
        assert (payload & 0xff) == (expected_word & 0xff), \
            f"{payload & 0xff:08b} != {expected_word & 0xff:08b} (expected)"

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_testbench(testbench_input)
    sim.add_testbench(testbench_output)
    with sim.write_vcd("stream_serial_receiver.vcd"):
        sim.run()
```

<!-- test_serial_receiver() -->

The serial protocol recognized by the receiver is illustrated with the following diagram (corresponding to `stream_serial_receiver.vcd`):

### Serial transmitter

The serial transmitter accepts a stream of words and provides it to the serial input of an external device whenever requested. Its serial interface is the same as that of the serial receiver, with the exception that the `sclk` and `sdat` signals are outputs. The `ssel` signal remains an input; the external device uses it for flow control.

```python
class SerialTransmitter(wiring.Component):
    ssel: In(1)
    sclk: Out(1)
    sdat: Out(1)

    stream: In(stream.Signature(signed(8)))

    def elaborate(self, platform):
        m = Module()

        count = Signal(range(9))
        data = Signal(8)

        with m.If(~self.ssel):
            m.d.sync += count.eq(0)
            m.d.sync += self.sclk.eq(1)
        with m.Elif(count != 0):
            m.d.comb += self.stream.ready.eq(0)
            m.d.sync += self.sclk.eq(~self.sclk)
            with m.If(self.sclk):
                m.d.sync += data.eq(Cat(0, data))
                m.d.sync += self.sdat.eq(data[-1])
            with m.Else():
                m.d.sync += count.eq(count - 1)
        with m.Else():
            m.d.comb += self.stream.ready.eq(1)
            with m.If(self.stream.valid):
                m.d.sync += count.eq(8)
                m.d.sync += data.eq(self.stream.payload)

        return m
```

```python
def test_serial_transmitter():
    dut = SerialTransmitter()

    async def testbench_input(ctx):
        await stream_put(ctx, dut.stream, 0b10100111)

    async def testbench_output(ctx):
        await ctx.tick()
        ctx.set(dut.ssel, 1)
        for index, expected_bit in enumerate([1, 0, 1, 0, 0, 1, 1, 1]):
            _, sdat = await ctx.posedge(dut.sclk).sample(dut.sdat)
            assert sdat == expected_bit, \
                f"bit {index}: {sdat} != {expected_bit} (expected)"
        ctx.set(dut.ssel, 0)
        await ctx.tick()

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_testbench(testbench_input)
    sim.add_testbench(testbench_output)
    with sim.write_vcd("stream_serial_transmitter.vcd"):
        sim.run()
```

<!-- test_serial_transmitter() -->

### Value negator

The value negator accepts a stream of words, negates the 2’s complement value of these words, and provides the result as a stream of words again. In a practical  application, this unit could be replaced with, for example, a  filter.

```python
class ValueNegator(wiring.Component):
    i_stream: In(stream.Signature(signed(8)))
    o_stream: Out(stream.Signature(signed(8)))

    def elaborate(self, platform):
        m = Module()

        with m.If(self.i_stream.valid & (~self.o_stream.valid | self.o_stream.ready)):
            m.d.comb += self.i_stream.ready.eq(1)
            m.d.sync += self.o_stream.payload.eq(-self.i_stream.payload)
            m.d.sync += self.o_stream.valid.eq(1)
        with m.Elif(self.o_stream.ready):
            m.d.sync += self.o_stream.valid.eq(0)

        return m
```

```python
def test_value_negator():
    dut = ValueNegator()

    async def testbench_input(ctx):
        await stream_put(ctx, dut.i_stream, 1)
        await stream_put(ctx, dut.i_stream, 17)

    async def testbench_output(ctx):
        assert await stream_get(ctx, dut.o_stream) == -1
        assert await stream_get(ctx, dut.o_stream) == -17

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_testbench(testbench_input)
    sim.add_testbench(testbench_output)
    with sim.write_vcd("stream_value_negator.vcd"):
        sim.run()
```

<!-- test_value_negator() -->

### Complete pipeline

The complete pipeline consists of a serial receiver, a value negator, a FIFO queue, and a serial transmitter connected in series. Without queueing, any momentary mismatch between the rate at which the serial data is produced and consumed would result in data loss. A FIFO queue from the [`lib.fifo`](fifo.md#module-amaranth.lib.fifo) standard library module is used to avoid this problem.

```python
from amaranth.lib.fifo import SyncFIFOBuffered

class ExamplePipeline(wiring.Component):
    i_ssel: In(1)
    i_sclk: In(1)
    i_sdat: In(1)

    o_ssel: In(1)
    o_sclk: Out(1)
    o_sdat: Out(1)

    def elaborate(self, platform):
        m = Module()

        # Create and connect serial receiver:
        m.submodules.receiver = receiver = SerialReceiver()
        m.d.comb += [
            receiver.ssel.eq(self.i_ssel),
            receiver.sclk.eq(self.i_sclk),
            receiver.sdat.eq(self.i_sdat),
        ]

        # Create and connect value negator:
        m.submodules.negator = negator = ValueNegator()
        wiring.connect(m, receiver=receiver.stream, negator=negator.i_stream)

        # Create and connect FIFO queue:
        m.submodules.queue = queue = SyncFIFOBuffered(width=8, depth=16)
        wiring.connect(m, negator=negator.o_stream, queue=queue.w_stream)

        # Create and connect serial transmitter:
        m.submodules.transmitter = transmitter = SerialTransmitter()
        wiring.connect(m, queue=queue.r_stream, transmitter=transmitter.stream)

        # Connect outputs:
        m.d.comb += [
            transmitter.ssel.eq(self.o_ssel),
            self.o_sclk.eq(transmitter.sclk),
            self.o_sdat.eq(transmitter.sdat),
        ]

        return m
```

```python
def test_example_pipeline():
    dut = ExamplePipeline()

    async def testbench_input(ctx):
        for value in [1, 17]:
            ctx.set(dut.i_ssel, 1)
            for bit in reversed(range(8)):
                ctx.set(dut.i_sclk, 0)
                ctx.set(dut.i_sdat, bool(value & (1 << bit)))
                await ctx.tick()
                ctx.set(dut.i_sclk, 1)
                await ctx.tick()
            await ctx.tick()
            ctx.set(dut.i_ssel, 0)
            ctx.set(dut.i_sclk, 0)
            await ctx.tick()

    async def testbench_output(ctx):
        await ctx.tick()
        ctx.set(dut.o_ssel, 1)
        for index, expected_value in enumerate([-1, -17]):
            value = 0
            for _ in range(8):
                _, sdat = await ctx.posedge(dut.o_sclk).sample(dut.o_sdat)
                value = (value << 1) | sdat
            assert value == (expected_value & 0xff), \
                f"word {index}: {value:08b} != {expected_value & 0xff:08b} (expected)"
        await ctx.tick()
        ctx.set(dut.o_ssel, 0)

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_testbench(testbench_input)
    sim.add_testbench(testbench_output)
    with sim.write_vcd("stream_example_pipeline.vcd"):
        sim.run()
```

<!-- test_example_pipeline() -->

This data processing pipeline overlaps reception and transmission of serial data, with only a few cycles of latency between the completion of reception and the beginning of transmission of the processed data:

![image](amaranth/stdlib/_images/stream_pipeline.png)

Implementing such an efficient pipeline can be difficult without the use of appropriate abstractions. The use of streams allows the designer to focus on the data processing and simplifies testing by ensuring that the interaction of the individual units is standard and well-defined.

## Reference

Components that communicate using streams must not only use a [`stream.Interface`](#amaranth.lib.stream.Interface), but also follow the [data transfer rules](#stream-rules).

### *class* amaranth.lib.stream.Signature(payload_shape, \*, payload_init=None, always_valid=False, always_ready=False)

Signature of a unidirectional data stream.

#### NOTE
“Minimal streams” as defined in [RFC 61](https://amaranth-lang.org/rfcs/0061-minimal-streams.html) lack support for complex payloads, such as
multiple lanes or packetization, as well as introspection of the payload. This limitation
will be lifted in a later release.

* **Parameters:**
  * **payload_shape** ([`ShapeLike`](../reference.md#amaranth.hdl.ShapeLike)) – Shape of the payload member.
  * **payload_init** ([constant-castable](../guide.md#lang-constcasting) object) – Initial value of the payload member.
  * **always_valid** ([`bool`](https://docs.python.org/3/library/functions.html#bool)) – Whether the stream has a payload available each cycle.
  * **always_ready** ([`bool`](https://docs.python.org/3/library/functions.html#bool)) – Whether the stream has its payload accepted whenever it is available (i.e. whether it lacks
    support for backpressure).
* **Members:**
  * **payload** (`Out(payload_shape)`) – Payload.
  * **valid** (`Out(1)`) – Whether a payload is available. If the stream is `always_valid`, `Const(1)`.
  * **ready** (`In(1)`) – Whether a payload is accepted. If the stream is `always_ready`, `Const(1)`.

### *class* amaranth.lib.stream.Interface(signature, \*, path=None, src_loc_at=0)

A unidirectional data stream.

* **Attributes:**
  **signature** ([`Signature`](#amaranth.lib.stream.Signature)) – Signature of this data stream.
* **Parameters:**
  **signature** ([*Signature*](#amaranth.lib.stream.Signature))

#### *property* p

Shortcut for `self.payload`.

This shortcut reduces repetition when manipulating the payload, for example:

```default
m.d.comb += [
    self.o_stream.p.result.eq(self.i_stream.p.first + self.i_stream.p.second),
    self.o_stream.valid.eq(self.i_stream.valid),
    self.i_stream.ready.eq(self.o_stream.ready),
]
```
