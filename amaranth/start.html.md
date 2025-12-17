# Getting started

This section demonstrates the basic Amaranth workflow to provide a cursory overview of the language and the toolchain. See the tutorial <tutorial> for a step-by-step introduction to the language, and the language guide <guide> for a detailed explanation of every language construct.

<!-- TODO: add link to build system doc -->
<!-- TODO: add link to more complex examples? -->

## A counter

As a first example, consider a counter with a fixed limit, enable, and overflow. The code for this example is shown below. [`Download`](_code/up_counter.py) and run it:

```shell
$ python3 up_counter.py
```

### Implementing a counter

A 16-bit up counter with enable input, overflow output, and a limit fixed at design time can be implemented in Amaranth as follows:

```default
from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out


class UpCounter(wiring.Component):
    """
    A 16-bit up counter with a fixed limit.

    Parameters
    ----------
    limit : int
        The value at which the counter overflows.

    Attributes
    ----------
    en : Signal, in
        The counter is incremented if ``en`` is asserted, and retains
        its value otherwise.
    ovf : Signal, out
        ``ovf`` is asserted when the counter reaches its limit.
    """

    en: In(1)
    ovf: Out(1)

    def __init__(self, limit):
        self.limit = limit
        self.count = Signal(16)

        super().__init__()

    def elaborate(self, platform):
        m = Module()

        m.d.comb += self.ovf.eq(self.count == self.limit)

        with m.If(self.en):
            with m.If(self.ovf):
                m.d.sync += self.count.eq(0)
            with m.Else():
                m.d.sync += self.count.eq(self.count + 1)

        return m
```

The reusable building block of Amaranth designs is a `Component`: a Python class declares its interface (`en` and `ovf`, in this case) and implements the `elaborate` method that defines its behavior.

<!-- TODO: link to Elaboratable reference -->

Most `elaborate` implementations use a `Module` helper to describe combinational (`m.d.comb`) and synchronous (`m.d.sync`) logic controlled with conditional syntax (`m.If`, `m.Elif`, `m.Else`) similar to Python’s. They can also instantiate vendor-defined black boxes or modules written in other HDLs.

<!-- TODO: link to DSL reference -->

### Testing a counter

To verify its functionality, the counter can be simulated for a small amount of time, with a test bench driving it and checking a few simple conditions:

```default
from amaranth.sim import Simulator


dut = UpCounter(25)
async def bench(ctx):
    # Disabled counter should not overflow.
    ctx.set(dut.en, 0)
    for _ in range(30):
        await ctx.tick()
        assert not ctx.get(dut.ovf)

    # Once enabled, the counter should overflow in 25 cycles.
    ctx.set(dut.en, 1)
    for _ in range(24):
        await ctx.tick()
        assert not ctx.get(dut.ovf)
    await ctx.tick()
    assert ctx.get(dut.ovf)

    # The overflow should clear in one cycle.
    await ctx.tick()
    assert not ctx.get(dut.ovf)


sim = Simulator(dut)
sim.add_clock(1e-6) # 1 MHz
sim.add_testbench(bench)
with sim.write_vcd("up_counter.vcd"):
    sim.run()
```

The testbench is implemented as a Python `async` function that is simulated concurrently with the counter itself. The testbench can inspect the simulated signals using `ctx.get(sig)`, update them using `ctx.set(sig, val)`, and advance the simulation by one clock cycle with `await ctx.tick()`. See the simulator documentation <simulator> for details.

When run, the testbench finishes successfully, since all of the assertions hold, and produces a VCD file with waveforms recorded for every `Signal` as well as the clock of the `sync` domain:

### Converting a counter

Although some Amaranth workflows do not include Verilog at all, it is still the de facto standard for HDL interoperability. Any Amaranth design can be converted to synthesizable Verilog using the corresponding backend:

```default
from amaranth.back import verilog


top = UpCounter(25)
with open("up_counter.v", "w") as f:
    f.write(verilog.convert(top))
```

The signals that will be connected to the ports of the top-level Verilog module should be specified explicitly. The rising edge clock and synchronous reset signals of the `sync` domain are added automatically; if necessary, the control signals can be configured explicitly. The result is the following Verilog code (lightly edited for clarity):

<!-- TODO: link to clock domain section of language reference -->
```verilog
(* generator = "Amaranth" *)
module top(ovf, clk, rst, en);
  reg \$auto$verilog_backend.cc:2255:dump_module$1  = 0;
  (* src = "up_counter.py:36" *)
  wire \$1 ;
  (* src = "up_counter.py:42" *)
  wire [16:0] \$3 ;
  (* src = "up_counter.py:42" *)
  wire [16:0] \$4 ;
  (* src = "<site-packages>/amaranth/hdl/ir.py:509" *)
  input clk;
  wire clk;
  (* src = "up_counter.py:29" *)
  reg [15:0] count = 16'h0000;
  (* src = "up_counter.py:29" *)
  reg [15:0] \count$next ;
  (* src = "<site-packages>/amaranth/lib/wiring.py:1647" *)
  input en;
  wire en;
  (* src = "<site-packages>/amaranth/lib/wiring.py:1647" *)
  output ovf;
  wire ovf;
  (* src = "<site-packages>/amaranth/hdl/ir.py:509" *)
  input rst;
  wire rst;
  assign \$1  = count == (* src = "up_counter.py:36" *) 5'h19;
  assign \$4  = count + (* src = "up_counter.py:42" *) 1'h1;
  always @(posedge clk)
    count <= \count$next ;
  always @* begin
    if (\$auto$verilog_backend.cc:2255:dump_module$1 ) begin end
    \count$next  = count;
    (* src = "up_counter.py:38" *)
    if (en) begin
      (* full_case = 32'd1 *)
      (* src = "up_counter.py:39" *)
      if (ovf) begin
        \count$next  = 16'h0000;
      end else begin
        \count$next  = \$4 [15:0];
      end
    end
    (* src = "<site-packages>/amaranth/hdl/xfrm.py:534" *)
    if (rst) begin
      \count$next  = 16'h0000;
    end
  end
  assign \$3  = \$4 ;
  assign ovf = \$1 ;
endmodule
```

To aid debugging, the generated Verilog code has the same general structure as the Amaranth source code (although more verbose), and contains extensive source location information.

#### NOTE
Unfortunately, at the moment none of the supported toolchains will use the source location information in diagnostic messages.

## A blinking LED

Although Amaranth works well as a standalone HDL, it also includes a build system that integrates with FPGA toolchains, and many board definition files for common developer boards that include pinouts and programming adapter invocations. The following code will blink a LED with a frequency of 1 Hz on any board that has a LED and an oscillator:

```default
from amaranth import *


class LEDBlinker(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        led = platform.request("led")

        half_freq = int(platform.default_clk_frequency // 2)
        timer = Signal(range(half_freq + 1))

        with m.If(timer == half_freq):
            m.d.sync += led.o.eq(~led.o)
            m.d.sync += timer.eq(0)
        with m.Else():
            m.d.sync += timer.eq(timer + 1)

        return m
```

The `LEDBlinker` module will use the first LED available on the board, and derive the clock divisor from the oscillator frequency specified in the clock constraint. It can be used, for example, with the [Lattice iCEStick evaluation board](https://www.latticesemi.com/icestick), one of the many boards already supported by Amaranth:

<!-- TODO: link to list of supported boards -->
```default
from amaranth_boards.icestick import ICEStickPlatform


ICEStickPlatform().build(LEDBlinker(), do_program=True)
```

With only a single line of code, the design is synthesized, placed, routed, and programmed to the on-board Flash memory. Although not all applications will use the Amaranth build system, the designs that choose it can benefit from the “turnkey” built-in workflows; if necessary, the built-in workflows can be customized to include user-specified options, commands, and files.

<!-- TODO: link to build system reference -->

#### NOTE
The ability to check with minimal effort whether the entire toolchain functions correctly is so important that it is built into every board definition file. To use it with the iCEStick board, run:

```shell
$ python3 -m amaranth_boards.icestick
```

This command will build and program a test bitstream similar to the example above.
