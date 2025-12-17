# Input/output buffers

The [`amaranth.lib.io`](#module-amaranth.lib.io) module provides a platform-independent way to instantiate platform-specific input/output buffers: combinational, synchronous, and double data rate (DDR).

## Introduction

The Amaranth language provides [core I/O values](../guide.md#lang-iovalues) that designate connections to external devices, and [I/O buffer instances](../guide.md#lang-iobufferinstance) that implement platform-independent combinational I/O buffers. This low-level mechanism is foundational to all I/O in Amaranth and must be used whenever a device-specific platform is unavailable, but is limited in its capabilities. The [`amaranth.lib.io`](#module-amaranth.lib.io) module builds on top of it to provide *library I/O ports* that specialize and annotate I/O values, and *buffer components* that connect ports to logic.

#### NOTE
Unfortunately, the terminology related to I/O has several ambiguities:

* A “port” could refer to an *interface port* (`Signal` objects created by the [`amaranth.lib.wiring`](wiring.md#module-amaranth.lib.wiring) module), a *core I/O port* (`amaranth.hdl.IOPort` object), or a *library I/O port* ([`amaranth.lib.io.PortLike`](#amaranth.lib.io.PortLike) object).
* A “I/O buffer” could refer to an *I/O buffer instance* (`amaranth.hdl.IOBufferInstance`) or a *I/O buffer component* ([`amaranth.lib.io.Buffer`](#amaranth.lib.io.Buffer), [`FFBuffer`](#amaranth.lib.io.FFBuffer), or [`DDRBuffer`](#amaranth.lib.io.DDRBuffer) objects).

Amaranth documentation always uses the least ambiguous form of these terms.

## Examples

<!-- from amaranth import *

class MockPlatform:
    def request(self, name, *, dir):
        from amaranth.hdl import IOPort
        from amaranth.lib import io
        if name == "led":
            return io.SingleEndedPort(IOPort(1, name=name), direction="o")
        if name == "clk24":
            return io.SingleEndedPort(IOPort(1, name=name), direction="i")
        if name == "d":
            return io.SingleEndedPort(IOPort(8, name=name), direction="io")
        if name == "re":
            return io.SingleEndedPort(IOPort(1, name=name), direction="i")
        if name == "we":
            return io.SingleEndedPort(IOPort(1, name=name), direction="i")
        if name == "dclk":
            return io.SingleEndedPort(IOPort(1, name=name), direction="o")
        if name == "dout":
            return io.SingleEndedPort(IOPort(8, name=name), direction="o")
        raise NameError

    def get_io_buffer(self, buffer):
        return Fragment()

    def build(self, top):
        from amaranth.back import rtlil
        return rtlil.convert(Fragment.get(top, self), ports=[]) -->

All of the following examples assume that one of the built-in FPGA platforms is used.

```python
from amaranth.sim import Simulator
from amaranth.lib import io, wiring, stream
from amaranth.lib.wiring import In, Out
```

### LED output

In this example, a library I/O port for a LED is requested from the platform and driven to blink the LED:

```python
class Toplevel(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        delay = Signal(24)
        state = Signal()
        with m.If(delay == 0):
            m.d.sync += delay.eq(~0)
            m.d.sync += state.eq(~state)
        with m.Else():
            m.d.sync += delay.eq(delay - 1)

        m.submodules.led = led = io.Buffer("o", platform.request("led", dir="-"))
        m.d.comb += led.o.eq(state)

        return m
```

<!-- MockPlatform().build(Toplevel()) -->

### Clock input

In this example, a clock domain is created and driven from an external clock source:

```python
class Toplevel(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.domains.sync = cd_sync = ClockDomain(local=True)

        m.submodules.clk24 = clk24 = io.Buffer("i", platform.request("clk24", dir="-"))
        m.d.comb += cd_sync.clk.eq(clk24.i)

        ...

        return m
```

<!-- MockPlatform().build(Toplevel()) -->

### Bidirectional bus

This example implements a peripheral for a clocked parallel bus. This peripheral can store and recall one byte of data. The data is stored with a write enable pulse, and recalled with a read enable pulse:

```python
class Toplevel(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.submodules.bus_d = bus_d = io.FFBuffer("io", platform.request("d", dir="-"))
        m.submodules.bus_re = bus_re = io.Buffer("i", platform.request("re", dir="-"))
        m.submodules.bus_we = bus_we = io.Buffer("i", platform.request("we", dir="-"))

        data = Signal.like(bus_d.i)
        with m.If(bus_re.i):
            m.d.comb += bus_d.oe.eq(1)
            m.d.comb += bus_d.o.eq(data)
        with m.Elif(bus_we.i):
            m.d.sync += data.eq(bus_d.i)

        return m
```

<!-- MockPlatform().build(Toplevel()) -->

This bus requires a turn-around time of at least 1 cycle to avoid electrical contention.

Note that data appears on the bus one cycle after the read enable input is asserted, and that the write enable input stores the data present on the bus in the *previous* cycle. This is called *pipelining* and is typical for clocked buses; see [`FFBuffer`](#amaranth.lib.io.FFBuffer) for a waveform diagram. Although it increases the maximum clock frequency at which the bus can run, it also makes the bus signaling more complicated.

### Clock forwarding

In this example of a [source-synchronous interface](https://en.wikipedia.org/wiki/Source-synchronous), a clock signal is generated with the same phase as the DDR data signals associated with it:

```python
class SourceSynchronousOutput(wiring.Component):
    dout: In(16)

    def elaborate(self, platform):
        m = Module()

        m.submodules.bus_dclk = bus_dclk = \
            io.DDRBuffer("o", platform.request("dclk", dir="-"))
        m.d.comb += [
            bus_dclk.o[0].eq(1),
            bus_dclk.o[1].eq(0),
        ]

        m.submodules.bus_dout = bus_dout = \
            io.DDRBuffer("o", platform.request("dout", dir="-"))
        m.d.comb += [
            bus_dout.o[0].eq(self.dout[:8]),
            bus_dout.o[1].eq(self.dout[8:]),
        ]

        return m
```

<!-- MockPlatform().build(SourceSynchronousOutput()) -->

This component transmits `dout` on each cycle as two halves: the low 8 bits on the rising edge of the data clock, and the high 8 bits on the falling edge of the data clock. The transmission is *edge-aligned*, meaning that the data edges exactly coincide with the clock edges.

## Simulation

The Amaranth simulator, [`amaranth.sim`](../simulator.md#module-amaranth.sim), cannot simulate [core I/O values](../guide.md#lang-iovalues) or [I/O buffer instances](../guide.md#lang-iobufferinstance) as it only operates on unidirectionally driven two-state wires. This module provides a simulation-only library I/O port, [`SimulationPort`](#amaranth.lib.io.SimulationPort), so that components that use library I/O buffers can be tested.

A component that is designed for testing should accept the library I/O ports it will drive as constructor parameters rather than requesting them from the platform directly. Synthesizable designs will instantiate the component with a [`SingleEndedPort`](#amaranth.lib.io.SingleEndedPort), [`DifferentialPort`](#amaranth.lib.io.DifferentialPort), or a platform-specific library I/O port, while tests will instantiate the component with a [`SimulationPort`](#amaranth.lib.io.SimulationPort). Tests are able to inject inputs into the component using `sim_port.i`, capture the outputs of the component via `sim_port.o`, and ensure that the component is driving the outputs at the appropriate times using `sim_port.oe`.

For example, consider a simple serializer that accepts a stream of multi-bit data words and outputs them bit by bit. It can be tested as follows:

```python
class OutputSerializer(wiring.Component):
    data: In(stream.Signature(8))

    def __init__(self, dclk_port, dout_port):
        self.dclk_port = dclk_port
        self.dout_port = dout_port

        super().__init__()

    def elaborate(self, platform):
        m = Module()

        m.submodules.dclk = dclk = io.Buffer("o", self.dclk_port)
        m.submodules.dout = dout = io.Buffer("o", self.dout_port)

        index = Signal(range(8))
        m.d.comb += dout.o.eq(self.data.payload.bit_select(index, 1))

        with m.If(self.data.valid):
            m.d.sync += dclk.o.eq(~dclk.o)
            with m.If(dclk.o):
                m.d.sync += index.eq(index + 1)
                with m.If(index == 7):
                    m.d.comb += self.data.ready.eq(1)

        return m

def test_output_serializer():
    dclk_port = io.SimulationPort("o", 1)
    dout_port = io.SimulationPort("o", 1)

    dut = OutputSerializer(dclk_port, dout_port)

    async def testbench_write_data(ctx):
        ctx.set(dut.data.payload, 0xA1)
        ctx.set(dut.data.valid, 1)
        await ctx.tick().until(dut.data.ready)
        ctx.set(dut.data.valid, 0)

    async def testbench_sample_output(ctx):
        for bit in [1,0,0,0,0,1,0,1]:
            _, dout_value = await ctx.posedge(dut.dclk_port.o).sample(dut.dout_port.o)
            assert ctx.get(dut.dout_port.oe) == 1, "DUT is not driving the data output"
            assert dout_value == bit, "DUT drives the wrong value on data output"

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_testbench(testbench_write_data)
    sim.add_testbench(testbench_sample_output)
    sim.run()
```

<!-- test_output_serializer() -->

## Ports

### *class* amaranth.lib.io.Direction

Represents direction of a library I/O port, or of an I/O buffer component.

#### Input *= 'i'*

Input direction (from outside world to Amaranth design).

#### Output *= 'o'*

Output direction (from Amaranth design to outside world).

#### Bidir *= 'io'*

Bidirectional (can be switched between input and output).

#### \_\_and_\_(other)

Narrow the set of possible directions.

* `self & self` returns `self`.
* `Bidir & other` returns `other`.
* `Input & Output` raises [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError).

### *class* amaranth.lib.io.PortLike

Represents an abstract library I/O port that can be passed to a buffer.

The port types supported by most platforms are [`SingleEndedPort`](#amaranth.lib.io.SingleEndedPort) and
[`DifferentialPort`](#amaranth.lib.io.DifferentialPort). Platforms may define additional port types where appropriate.

#### NOTE
`amaranth.hdl.IOPort` is not an instance of [`amaranth.lib.io.PortLike`](#amaranth.lib.io.PortLike).

#### *abstract property* direction

Direction of the port.

* **Return type:**
  [`Direction`](#amaranth.lib.io.Direction)

#### *abstract* \_\_len_\_()

Computes the width of the port.

* **Returns:**
  The number of wires (for single-ended library I/O ports) or wire pairs (for differential
  library I/O ports) this port consists of.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### *abstract* \_\_getitem_\_(key)

Slices the port.

* **Returns:**
  A new [`PortLike`](#amaranth.lib.io.PortLike) instance of the same type as `self`, containing a selection
  of wires of this port according to `key`. Its width is the same as the length of
  the slice (if `key` is a [`slice`](https://docs.python.org/3/library/functions.html#slice)); or 1 (if `key` is an [`int`](https://docs.python.org/3/library/functions.html#int)).
* **Return type:**
  [`PortLike`](#amaranth.lib.io.PortLike)

#### *abstract* \_\_invert_\_()

Inverts polarity of the port.

Inverting polarity of a library I/O port has the same effect as adding inverters to
the `i` and `o` members of an I/O buffer component for that port.

* **Returns:**
  A new [`PortLike`](#amaranth.lib.io.PortLike) instance of the same type as `self`, containing the same
  wires as this port, but with polarity inverted.
* **Return type:**
  [`PortLike`](#amaranth.lib.io.PortLike)

#### \_\_add_\_(other)

Concatenates two library I/O ports of the same type.

The direction of the resulting port is:

* The same as the direction of both, if the two ports have the same direction.
* [`Direction.Input`](#amaranth.lib.io.Direction.Input) if a bidirectional port is concatenated with an input port.
* [`Direction.Output`](#amaranth.lib.io.Direction.Output) if a bidirectional port is concatenated with an output port.

* **Returns:**
  A new `type(self)` which contains wires from `self` followed by wires
  from `other`, preserving their polarity inversion.
* **Return type:**
  `type(self)`
* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If an input port is concatenated with an output port.
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `self` and `other` have different types.

### *class* amaranth.lib.io.SingleEndedPort(io, \*, invert=False, direction=Direction.Bidir)

Represents a single-ended library I/O port.

Implements the [`PortLike`](#amaranth.lib.io.PortLike) interface.

* **Parameters:**
  * **io** (`IOValue`) – Underlying core I/O value.
  * **invert** ([`bool`](https://docs.python.org/3/library/functions.html#bool) or iterable of [`bool`](https://docs.python.org/3/library/functions.html#bool)) – Polarity inversion. If the value is a simple [`bool`](https://docs.python.org/3/library/functions.html#bool), it specifies inversion for
    the entire port. If the value is an iterable of [`bool`](https://docs.python.org/3/library/functions.html#bool), the iterable must have the
    same length as the width of `io`, and the inversion is specified for individual wires.
  * **direction** ([`Direction`](#amaranth.lib.io.Direction) or [`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Set of allowed buffer directions. A string is converted to a [`Direction`](#amaranth.lib.io.Direction) first.
    If equal to [`Input`](#amaranth.lib.io.Direction.Input) or [`Output`](#amaranth.lib.io.Direction.Output), this port can only be
    used with buffers of matching direction. If equal to [`Bidir`](#amaranth.lib.io.Direction.Bidir), this port
    can be used with buffers of any direction.
* **Attributes:**
  * **io** (`IOValue`) – The `io` parameter.
  * **invert** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of [`bool`](https://docs.python.org/3/library/functions.html#bool)) – The `invert` parameter, normalized to specify polarity inversion per-wire.
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – The `direction` parameter, normalized to the [`Direction`](#amaranth.lib.io.Direction) enumeration.

### *class* amaranth.lib.io.DifferentialPort(p, n, \*, invert=False, direction=Direction.Bidir)

Represents a differential library I/O port.

Implements the [`PortLike`](#amaranth.lib.io.PortLike) interface.

* **Parameters:**
  * **p** (`IOValue`) – Underlying core I/O value for the true (positive) half of the port.
  * **n** (`IOValue`) – Underlying core I/O value for the complement (negative) half of the port.
    Must have the same width as `p`.
  * **invert** ([`bool`](https://docs.python.org/3/library/functions.html#bool) or iterable of [`bool`](https://docs.python.org/3/library/functions.html#bool)) – Polarity inversion. If the value is a simple [`bool`](https://docs.python.org/3/library/functions.html#bool), it specifies inversion for
    the entire port. If the value is an iterable of [`bool`](https://docs.python.org/3/library/functions.html#bool), the iterable must have the
    same length as the width of `p` and `n`, and the inversion is specified for
    individual wires.
  * **direction** ([`Direction`](#amaranth.lib.io.Direction) or [`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Set of allowed buffer directions. A string is converted to a [`Direction`](#amaranth.lib.io.Direction) first.
    If equal to [`Input`](#amaranth.lib.io.Direction.Input) or [`Output`](#amaranth.lib.io.Direction.Output), this port can only be
    used with buffers of matching direction. If equal to [`Bidir`](#amaranth.lib.io.Direction.Bidir), this port
    can be used with buffers of any direction.
* **Attributes:**
  * **p** (`IOValue`) – The `p` parameter.
  * **n** (`IOValue`) – The `n` parameter.
  * **invert** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of [`bool`](https://docs.python.org/3/library/functions.html#bool)) – The `invert` parameter, normalized to specify polarity inversion per-wire.
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – The `direction` parameter, normalized to the [`Direction`](#amaranth.lib.io.Direction) enumeration.

### *class* amaranth.lib.io.SimulationPort(direction, width, \*, invert=False, name=None, src_loc_at=0)

Represents a simulation library I/O port.

Implements the [`PortLike`](#amaranth.lib.io.PortLike) interface.

* **Parameters:**
  * **direction** ([`Direction`](#amaranth.lib.io.Direction) or [`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Set of allowed buffer directions. A string is converted to a [`Direction`](#amaranth.lib.io.Direction) first.
    If equal to [`Input`](#amaranth.lib.io.Direction.Input) or [`Output`](#amaranth.lib.io.Direction.Output), this port can only be
    used with buffers of matching direction. If equal to [`Bidir`](#amaranth.lib.io.Direction.Bidir), this port
    can be used with buffers of any direction.
  * **width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Width of the port. The width of each of the attributes `i`, `o`, `oe` (whenever
    present) equals `width`.
  * **invert** ([`bool`](https://docs.python.org/3/library/functions.html#bool) or iterable of [`bool`](https://docs.python.org/3/library/functions.html#bool)) – Polarity inversion. If the value is a simple [`bool`](https://docs.python.org/3/library/functions.html#bool), it specifies inversion for
    the entire port. If the value is an iterable of [`bool`](https://docs.python.org/3/library/functions.html#bool), the iterable must have the
    same length as the width of `p` and `n`, and the inversion is specified for
    individual wires.
  * **name** ([`str`](https://docs.python.org/3/library/stdtypes.html#str) or `None`) – Name of the port. This name is only used to derive the names of the input, output, and
    output enable signals.
  * **src_loc_at** ([`int`](https://docs.python.org/3/library/functions.html#int)) – [Source location](../reference.md#lang-srcloc). Used to infer `name` if not specified.
* **Attributes:**
  * **i** (`Signal`) – Input signal. Present if `direction in (Input, Bidir)`.
  * **o** (`Signal`) – Ouptut signal. Present if `direction in (Output, Bidir)`.
  * **oe** (`Signal`) – Output enable signal. Present if `direction in (Output, Bidir)`.
  * **invert** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of [`bool`](https://docs.python.org/3/library/functions.html#bool)) – The `invert` parameter, normalized to specify polarity inversion per-wire.
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – The `direction` parameter, normalized to the [`Direction`](#amaranth.lib.io.Direction) enumeration.

## Buffers

### *class* amaranth.lib.io.Buffer(direction, port)

A combinational I/O buffer component.

This buffer can be used on any platform; if the platform does not specialize its implementation,
an [I/O buffer instance](../guide.md#lang-iobufferinstance) is used.

The following diagram defines the timing relationship between the underlying core I/O value
(for differential ports, the core I/O value of the true half) and the `i`, `o`, and
`oe` members:

* **Parameters:**
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – Direction of the buffer.
  * **port** ([`PortLike`](#amaranth.lib.io.PortLike)) – Port driven by the buffer.
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – Unless `port.direction in (direction, Bidir)`.
* **Attributes:**
  **signature** ([`Buffer.Signature`](#amaranth.lib.io.Buffer.Signature)) – `Signature(direction, len(port)).flip()`.

#### *class* Signature(direction, width)

Signature of a combinational I/O buffer.

* **Parameters:**
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – Direction of the buffer.
  * **width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Width of the buffer.
* **Members:**
  * **i** (`In(width)`) – Present if `direction in (Input, Bidir)`.
  * **o** (`Out(width)`) – Present if `direction in (Output, Bidir)`.
  * **oe** (`Out(1, init=0)`) – Present if `direction is Bidir`.
  * **oe** (`Out(1, init=1)`) – Present if `direction is Output`.

### *class* amaranth.lib.io.FFBuffer(direction, port, \*, i_domain=None, o_domain=None)

A registered I/O buffer component.

This buffer can be used on any platform; if the platform does not specialize its implementation,
an [I/O buffer instance](../guide.md#lang-iobufferinstance) is used, combined with reset-less
registers on `i`, `o`, and  `oe` members.

The following diagram defines the timing relationship between the underlying core I/O value
(for differential ports, the core I/O value of the true half) and the `i`, `o`, and
`oe` members:

#### WARNING
On some platforms, this buffer can only be used with rising edge clock domains, and will
raise an exception during conversion of the design to a netlist otherwise.

This limitation will be lifted in the future.

* **Parameters:**
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – Direction of the buffer.
  * **port** ([`PortLike`](#amaranth.lib.io.PortLike)) – Port driven by the buffer.
  * **i_domain** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the input register’s clock domain. Used when `direction in (Input, Bidir)`.
    Defaults to `"sync"`.
  * **o_domain** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the output and output enable registers’ clock domain. Used when
    `direction in (Output, Bidir)`. Defaults to `"sync"`.
* **Attributes:**
  **signature** ([`FFBuffer.Signature`](#amaranth.lib.io.FFBuffer.Signature)) – `Signature(direction, len(port)).flip()`.

#### *class* Signature(direction, width)

Signature of a registered I/O buffer.

* **Parameters:**
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – Direction of the buffer.
  * **width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Width of the buffer.
* **Members:**
  * **i** (`In(width)`) – Present if `direction in (Input, Bidir)`.
  * **o** (`Out(width)`) – Present if `direction in (Output, Bidir)`.
  * **oe** (`Out(1, init=0)`) – Present if `direction is Bidir`.
  * **oe** (`Out(1, init=1)`) – Present if `direction is Output`.

### *class* amaranth.lib.io.DDRBuffer(direction, port, \*, i_domain=None, o_domain=None)

A double data rate I/O buffer component.

This buffer is only available on platforms that support double data rate I/O.

The following diagram defines the timing relationship between the underlying core I/O value
(for differential ports, the core I/O value of the true half) and the `i`, `o`, and
`oe` members:

<!-- This diagram should have `port` phase shifted, but it hits wavedrom/wavedrom#416.
It is also affected by wavedrom/wavedrom#417. -->

The output data (labelled *a*, *b*) is input from `o` into internal registers at
the beginning of clock cycle 2, and transmitted at points labelled *1*, *2* during the same
clock cycle. The output latency *t1* is defined as the amount of cycles between the time of
capture of `o` and the time of transmission of rising edge data plus one cycle, and is 1
for this diagram.

The received data is captured into internal registers during the clock cycle 4 at points
labelled *5*, *6*, and output to `i` during the next clock cycle (labelled *d*, *e*).
The input latency *t2* is defined as the amount of cycles between the time of reception of
rising edge data and the time of update of `i`, and is 1 for this diagram.

The output enable signal is input from `oe` once per cycle and affects the entire cycle it
applies to. Its latency is defined in the same way as the output latency, and is equal to *t1*.

#### WARNING
Some platforms include additional pipeline registers that may cause latencies *t1* and *t2*
to be higher than one cycle. At the moment there is no way to query these latencies.

This limitation will be lifted in the future.

#### WARNING
On all supported platforms, this buffer can only be used with rising edge clock domains,
and will raise an exception during conversion of the design to a netlist otherwise.

This limitation may be lifted in the future.

#### WARNING
Double data rate I/O buffers are not compatible with [`SimulationPort`](#amaranth.lib.io.SimulationPort).

This limitation may be lifted in the future.

* **Parameters:**
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – Direction of the buffer.
  * **port** ([`PortLike`](#amaranth.lib.io.PortLike)) – Port driven by the buffer.
  * **i_domain** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the input register’s clock domain. Used when `direction in (Input, Bidir)`.
    Defaults to `"sync"`.
  * **o_domain** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the output and output enable registers’ clock domain. Used when
    `direction in (Output, Bidir)`. Defaults to `"sync"`.
* **Attributes:**
  **signature** ([`DDRBuffer.Signature`](#amaranth.lib.io.DDRBuffer.Signature)) – `Signature(direction, len(port)).flip()`.

#### *class* Signature(direction, width)

Signature of a double data rate I/O buffer.

* **Parameters:**
  * **direction** ([`Direction`](#amaranth.lib.io.Direction)) – Direction of the buffer.
  * **width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Width of the buffer.
* **Members:**
  * **i** (`In(ArrayLayout(width, 2))`) – Present if `direction in (Input, Bidir)`.
  * **o** (`Out(ArrayLayout(width, 2))`) – Present if `direction in (Output, Bidir)`.
  * **oe** (`Out(1, init=0)`) – Present if `direction is Bidir`.
  * **oe** (`Out(1, init=1)`) – Present if `direction is Output`.
