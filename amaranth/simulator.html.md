# Simulator

The [`amaranth.sim`](#module-amaranth.sim) module, also known as the simulator, makes it possible to evaluate a design’s functionality in a virtual environment before it is implemented in hardware.

## Simulating circuits

<!-- from amaranth import * -->

The following examples simulate one of the two designs below: synchronous counter running in the `sync` clock domain, and combinational adder. They assume familiarity with the language guide <guide>.

```python
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out

class Counter(wiring.Component):
    en: In(1, init=1)
    count: Out(4)

    def elaborate(self, platform):
        m = Module()
        with m.If(self.en):
            m.d.sync += self.count.eq(self.count + 1)
        return m

class Adder(wiring.Component):
    a: In(16)
    b: In(16)
    o: Out(17)

    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.o.eq(self.a + self.b)
        return m
```

### Running a simulation

Simulating a design always requires the three basic steps: constructing the , constructing a [`Simulator`](#amaranth.sim.Simulator) for it, and running the simulation with the [`Simulator.run()`](#amaranth.sim.Simulator.run) or [`Simulator.run_until()`](#amaranth.sim.Simulator.run_until) method:

```python
from amaranth.sim import Simulator

dut = Counter()
sim = Simulator(dut)
sim.run()
```

However, the code above neither stimulates the DUT’s inputs nor measures the DUT’s outputs; the [`Simulator.run()`](#amaranth.sim.Simulator.run) method also immediately returns if no stimulus is added to the simulation. To make it useful, several changes are necessary:

* The [`Simulator.add_clock()`](#amaranth.sim.Simulator.add_clock) method adds a *stimulus*: a process external to the DUT that manipulates its inputs (in this case, toggles the clock of the `sync` domain).
* The [`Simulator.run_until()`](#amaranth.sim.Simulator.run_until) method runs the simulation until a specific deadline is reached.
* The [`Simulator.write_vcd()`](#amaranth.sim.Simulator.write_vcd) method captures the DUT’s inputs, state, and outputs, and writes it to a  file.

The following code simulates a design and capture the values of all the signals used in the design for each moment of simulation time:

```python
dut = Counter()
sim = Simulator(dut)
sim.add_clock(1e-6) # 1 µs period, or 1 MHz
with sim.write_vcd("example1.vcd"):
    sim.run_until(1e-6 * 15) # 15 periods of the clock
```

The captured data is saved to a  file `example1.vcd`, which can be displayed with a *waveform viewer* such as [Surfer](https://surfer-project.org/) or [GTKWave](https://gtkwave.sourceforge.net/):

The [`Simulator.reset()`](#amaranth.sim.Simulator.reset) method reverts the simulation to its initial state. It can be used to speed up tests by capturing the waveforms only when the simulation is known to encounter an error:

```python
try:
    sim.run()
except:
    sim.reset()
    with sim.write_vcd("example1_error.vcd"):
        sim.run()
```

### Testing synchronous circuits

To verify that the DUT works as intended during a simulation, known values are provided as the inputs, and the outputs are compared with the expected results.

This is done by adding a different type of stimulus to the simulator, a *testbench*: an `async` Python function that runs concurrently with the DUT and can manipulate the signals used in the simulation. A testbench is added using the [`Simulator.add_testbench()`](#amaranth.sim.Simulator.add_testbench) method, and receives a [`SimulatorContext`](#amaranth.sim.SimulatorContext) object through which it can interact with the simulator: inspect the value of signals using the [`ctx.get()`](#amaranth.sim.SimulatorContext.get) method, change the value of signals using the [`ctx.set()`](#amaranth.sim.SimulatorContext.set) method, or wait for an active edge of a [clock domain](guide.md#lang-clockdomains) using the [`ctx.tick()`](#amaranth.sim.SimulatorContext.tick) method.

The following example simulates a counter and verifies that it can be stopped using its `en` input:

```python
dut = Counter()

async def testbench_example2(ctx):
    await ctx.tick().repeat(5)     # wait until after the 5th edge of the `sync` domain clock
    assert ctx.get(dut.count) == 5 # verify that the counter has the expected value
    ctx.set(dut.en, False)         # deassert `dut.en`, disabling the counter
    await ctx.tick().repeat(5)     # wait until after the 10th edge of clock
    assert ctx.get(dut.count) == 5 # verify that the counter has not been incrementing
    ctx.set(dut.en, True)          # assert `dut.en`, enabling the counter again

sim = Simulator(dut)
sim.add_clock(1e-6)
sim.add_testbench(testbench_example2) # add the testbench; run_until() calls the function
with sim.write_vcd("example2.vcd"):
    sim.run_until(1e-6 * 15)
```

Since this circuit is synchronous, and the [`ctx.tick()`](#amaranth.sim.SimulatorContext.tick) method waits until after the circuit has reacted to the clock edge, the change to the `en` input affects the behavior of the circuit on the next clock cycle after the change:

### Testing combinational circuits

A testbench that tests a combinational circuit advances simulation time using the [`ctx.delay()`](#amaranth.sim.SimulatorContext.delay) method instead of the [`ctx.tick()`](#amaranth.sim.SimulatorContext.tick) method, since the simulation does not contain a clock in this case. The [`Simulator.run()`](#amaranth.sim.Simulator.run) method stops the simulation and returns once all testbenches finish executing.

The following example simulates an adder:

```python
dut = Adder()

async def testbench_example3(ctx):
    await ctx.delay(1e-6)
    ctx.set(dut.a, 2)
    ctx.set(dut.b, 2)
    assert ctx.get(dut.o) == 4

    await ctx.delay(1e-6)
    ctx.set(dut.a, 1717)
    ctx.set(dut.b, 420)
    assert ctx.get(dut.o) == 2137

    await ctx.delay(2e-6)

sim = Simulator(dut)
sim.add_testbench(testbench_example3)
with sim.write_vcd("example3.vcd"):
    sim.run()
```

Since this circuit is entirely combinational, and the Amaranth simulator uses a *zero-delay model* of combinational circuits, the outputs change in the same instant as the inputs do:

## Replacing circuits with code

#### NOTE
This section describes an advanced technique that is not commonly used. If you are first learning how to use the simulator, you can skip it.

During simulation, it is possible to replace an Amaranth circuit with the equivalent Python code. This can be used to improve simulation performance, or to avoid reimplementing complex Python algorithms in Amaranth if they do not need to be synthesized.

This is done by adding a *process* to the simulator: an `async` Python function that runs as an integral part of the simulation, simultaneously with the DUT. A process is added using the [`Simulator.add_process()`](#amaranth.sim.Simulator.add_process) method, and receives a [`SimulatorContext`](#amaranth.sim.SimulatorContext) object through which it can interact with the simulator. A process is conceptually similar to a testbench but differs from it in two important ways:

* Testbenches run in a well-defined order (from first to last in the order they were added, yielding control only at `await` points) and cannot observe inconsistent intermediate states of a design, but processes run in an undefined order while the design is converging after a change to its inputs.
* In a process, it is not possible to inspect the value of a signal using the [`ctx.get()`](#amaranth.sim.SimulatorContext.get) method, which guarantees that inconsistent intermediate states of a design cannot be observed by a process either.

A process communicates with the rest of the design in the same way an elaboratable would: through `Signal`s.

### Replacing synchronous circuits

Processes cannot inspect values of signals using the [`ctx.get()`](#amaranth.sim.SimulatorContext.get) method. Instead, values of signals in a synchronous process are sampled at each active edge of the clock domain (or, for domains with asynchronous reset, at the assertion of the reset signal) using the [`ctx.tick()`](#amaranth.sim.SimulatorContext.tick) method.

The following code replaces the `Counter` elaboratable with the equivalent Python code in a process, and uses a testbench to verify its correct operation:

```python
m = Module()
m.domains.sync = cd_sync = ClockDomain()
en = Signal(init=1)
count = Signal(4)

async def process_example4(ctx):
    count_value = 0 # initialize counter to 0
    async for clk_edge, rst_value, en_value in ctx.tick().sample(en):
        if rst_value: # can be asserted with or without clk_edge
            count_value = 0 # re-initialize counter
        elif clk_edge and en_value:
            count_value += 1 # advance the counter
            ctx.set(count, count_value) # publish its value to the simulation

async def testbench_example4(ctx):
    await ctx.tick().repeat(5)
    assert ctx.get(count) == 5
    ctx.set(en, False)
    await ctx.tick().repeat(5)
    assert ctx.get(count) == 5
    ctx.set(en, True)

sim = Simulator(m)
sim.add_clock(1e-6)
sim.add_process(process_example4)
sim.add_testbench(testbench_example4)
with sim.write_vcd("example4.vcd", traces=(cd_sync.clk, cd_sync.rst, en, count)):
    sim.run()
```

Unless it is instructed otherwise, the [`Simulator.write_vcd()`](#amaranth.sim.Simulator.write_vcd) method only captures values of signals that appear in the circuit provided to the simulator when it is created. The `en` and `count` signals do not, and are added explicitly using the `traces` argument so that they will appear in the VCD file.

### Replacing combinational circuits

Values of signals in a combinational process are sampled anytime they change using the [`ctx.changed()`](#amaranth.sim.SimulatorContext.changed) method.

The following code replaces the `Adder` elaboratable with the equivalent Python code in a process, and uses a testbench to verify its correct operation:

```python
m = Module()
a = Signal(16)
b = Signal(16)
o = Signal(17)

async def process_example5(ctx):
    async for a_value, b_value in ctx.changed(a, b):
        ctx.set(o, a_value + b_value)

async def testbench_example5(ctx):
    await ctx.delay(1e-6)
    ctx.set(a, 2)
    ctx.set(b, 2)
    assert ctx.get(o) == 4

    await ctx.delay(1e-6)
    ctx.set(a, 1717)
    ctx.set(b, 420)
    assert ctx.get(o) == 2137

    await ctx.delay(2e-6)

sim = Simulator(m)
sim.add_process(process_example5)
sim.add_testbench(testbench_example5)
with sim.write_vcd("example5.vcd", traces=[a, b, o]):
    sim.run()
```

## Reference

### *class* amaranth.sim.Simulator(toplevel)

Simulator for Amaranth designs.

The simulator accepts a *top-level design* (an [elaboratable](guide.md#lang-elaboration)),
*processes* that replace circuits with behavioral code, *clocks* that drive clock domains, and
*testbenches* that exercise the circuits and verify that they work correctly.

The simulator lifecycle consists of four stages:

1. The simulator is created:
   ```default
   sim = Simulator(design)
   ```
2. Processes, clocks, and testbenches are added as necessary:
   ```default
   sim.add_clock(1e-6)
   sim.add_clock(1e-7, domain="fast")
   sim.add_process(process_instr_decoder)
   sim.add_testbench(testbench_cpu_execute)
   ```
3. The simulation is run:
   ```default
   with sim.write_vcd("waveform.vcd"):
       sim.run()
   ```
4. (Optional) The simulator is reset:
   ```default
   sim.reset()
   ```

After the simulator is reset, it may be reused to run the simulation again.

#### NOTE
Resetting the simulator can also be used to amortize the startup cost of repeatedly
simulating a large design.

* **Parameters:**
  **toplevel** (`Elaboratable`) – Simulated design.

#### add_clock(period, \*, phase=None, domain='sync', if_exists=False)

Add a clock to the simulation.

Adds a stimulus that toggles the clock signal of `domain` at a 50% duty cycle.

The driven clock signal will toggle every half-`period` seconds starting at `phase`
seconds after the beginning of the simulation; if not specified, `phase` defaults to
half-`period` to avoid coinciding the first active edge with the beginning of
the simulation.

The clock domain to drive is selected by the `domain` argument, which may be
a `ClockDomain` object or a [`str`](https://docs.python.org/3/library/stdtypes.html#str). If it is a string,
the clock domain with that name is retrieved from the `toplevel` elaboratable.

* **Raises:**
  * [**NameError**](https://docs.python.org/3/library/exceptions.html#NameError) – If `domain` is a [`str`](https://docs.python.org/3/library/stdtypes.html#str), the `toplevel` elaboratable does not have
        a clock domain with that name, and `if_exists` is `False`.
  * **DriverConflict** – If `domain` already has a clock driving it.
  * [**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError) – If the simulation has been advanced since its creation or last reset.

#### add_testbench(constructor, \*, background=False)

Add a testbench to the simulation.

Adds a testbench that runs concurrently with the `toplevel` elaboratable and is able to
manipulate its inputs, outputs, and state.

The behavior of the testbench is defined by its *constructor function*, which is
an `async` function that takes a single argument, the [`SimulatorContext`](#amaranth.sim.SimulatorContext):

```default
async def testbench(ctx):
    ...
    await ctx.tick()
    ...

sim.add_testbench(testbench)
```

This method does not accept coroutines. Rather, the provided `constructor` coroutine
function is called immediately when the testbench is added to create a coroutine, as well as
by the [`reset()`](#amaranth.sim.Simulator.reset) method.

The testbench can be *critical* (the default) or *background* (if the `background=True`
argument is specified). The [`run()`](#amaranth.sim.Simulator.run) method will continue advancing the simulation while
any critical testbenches or processes are running, and will exit when only background
testbenches or processes remain. A background testbench can temporarily become critical
using the [`critical()`](#amaranth.sim.SimulatorContext.critical) context manager.

At each point in time, all of the non-waiting testbenches are executed in the order in
which they were added. If two testbenches share state, or must manipulate the design in
a coordinated way, they may rely on this execution order for correctness.

* **Raises:**
  [**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError) – If the simulation has been advanced since its creation or last reset.

#### add_process(process)

Add a process to the simulation.

Adds a process that is evaluated as a part of the `toplevel` elaboratable and is able to
replace circuits with Python code.

The behavior of the process is defined by its *constructor function*, which is
an `async` function that takes a single argument, the [`SimulatorContext`](#amaranth.sim.SimulatorContext):

```default
async def process(ctx):
    async for clk_edge, rst, ... in ctx.tick().sample(...):
        ...

sim.add_process(process)
```

This method does not accept coroutines. Rather, the provided `constructor` coroutine
function is called immediately when the procss is added to create a coroutine, as well as
by the [`reset()`](#amaranth.sim.Simulator.reset) method.

Processes can be *critical* or *background*, and are always background when added.
The [`run()`](#amaranth.sim.Simulator.run) method will continue advancing the simulation while any critical testbenches
or processes are running, and will exit when only background testbenches or processes
remain. A background process can temporarily become critical using
the [`critical()`](#amaranth.sim.SimulatorContext.critical) context manager.

At each point in time, all of the non-waiting processes are executed in an arbitrary order
that may be different between individual simulation runs.

#### WARNING
If two processes share state, they must do so in a way that does not rely on
a particular order of execution for correctness.

Preferably, the shared state would be stored in `Signal`s (even
if it is not intended to be a part of a circuit), with access to it synchronized using
`await ctx.tick().sample(...)`. Such state is visible in a waveform viewer,
simplifying debugging.

* **Raises:**
  [**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError) – If the simulation has been advanced since its creation or last reset.

#### run()

Run the simulation indefinitely.

This method advances the simulation while any critical testbenches or processes continue
executing. It is equivalent to:

```default
while self.advance():
    pass
```

#### run_until(deadline)

Run the simulation until a specific point in time.

This method advances the simulation until the simulation time reaches `deadline`,
without regard for whether there are critical testbenches or processes executing.

<!-- This should show the code like in :meth:`run` once the code is not horrible. -->

#### advance()

Advance the simulation.

This method advances the simulation by one time step. After this method completes, all of
the events scheduled for the current point in time will have taken effect, and the current
point in time was advanced to the closest point in the future for which any events are
scheduled (which may be the same point in time).

The non-waiting testbenches are executed in the order they were added, and the processes
are executed as necessary.

Returns `True` if the simulation contains any critical testbenches or processes, and
`False` otherwise.

#### write_vcd(vcd_file, gtkw_file=None, \*, traces=())

Capture waveforms to a file.

This context manager captures waveforms for each signal and memory that is referenced from
`toplevel`, as well as any additional signals or memories specified in `traces`,
and saves them to `vcd_file`. If `gtkw_file` is provided, it is populated with
a GTKWave save file displaying `traces` when opened.

Use this context manager to wrap a call to [`run()`](#amaranth.sim.Simulator.run) or [`run_until()`](#amaranth.sim.Simulator.run_until):

```default
with sim.write_vcd("simulation.vcd"):
    sim.run()
```

The `vcd_file` and `gtkw_file` arguments accept either a [file object](https://docs.python.org/3/glossary.html#term-file-object)
or a filename. If a file object is provided, it is closed when exiting the context manager
(once the simulation completes or encounters an error).

The `traces` argument accepts a *trace specification*, which can be one of:

* A [`ValueLike`](reference.md#amaranth.hdl.ValueLike) object, such as a `Signal`;
* A [`MemoryData`](stdlib/memory.md#amaranth.hdl.MemoryData) object or an individual row retrieved from one;
* A [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) or [`list`](https://docs.python.org/3/library/stdtypes.html#list) containing trace specifications;
* A [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) associating [`str`](https://docs.python.org/3/library/stdtypes.html#str) names to trace specifications;
* An [interface object](stdlib/wiring.md#wiring).

* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If a trace specification refers to a signal with a private name.

#### reset()

Reset the simulation.

This method reverts the simulation to its initial state:

* The value of each signal is changed to its initial value;
* The contents of each memory is changed to its initial contents;
* Each clock, testbench, and process is restarted.

### *class* amaranth.sim.SimulatorContext(...)

Simulator context.

Simulator processes and testbenches are `async` Python functions that interact with
the simulation using the only argument they receive: the *context*. Using a context, it is
possible to sample or update signals and wait for events to occur in the simulation.

The context has two kinds of methods: `async` methods and non-`async` methods. Calling
an `async` method may cause the caller to be preempted (be paused such that the simulation
time can advance), while calling non-`async` methods never causes that.

#### NOTE
While a testbench or process is executing without calling `async` methods, no other
testbench or process will run, with one exception: if a testbench calls [`set()`](#amaranth.sim.SimulatorContext.set), all
processes that wait (directly or indirectly) for the updated signals to change will execute
before the call returns.

* **Parameters:**
  * **engine** (*BaseEngine*)
  * **process** (*BaseProcess*)

#### get(expr: [Value](reference.md#amaranth.hdl.Value)) → [int](https://docs.python.org/3/library/functions.html#int)

#### get(expr: [ValueCastable](reference.md#amaranth.hdl.ValueCastable)) → [Any](https://docs.python.org/3/library/typing.html#typing.Any)

Sample the value of an expression.

The behavior of this method depends on the type of `expr`:

- If it is a [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable) whose shape is a [`ShapeCastable`](reference.md#amaranth.hdl.ShapeCastable),
  its numeric value is converted to a higher-level representation using
  [`from_bits()`](reference.md#amaranth.hdl.ShapeCastable.from_bits) and then returned.
- If it is a [`Value`](reference.md#amaranth.hdl.Value) or a [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable) whose shape is
  a [`Shape`](reference.md#amaranth.hdl.Shape), the numeric value is returned as an [`int`](https://docs.python.org/3/library/functions.html#int).

This method is only available in testbenches.

* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If the caller is a process.

#### set(expr: [Value](reference.md#amaranth.hdl.Value), value: [int](https://docs.python.org/3/library/functions.html#int)) → [None](https://docs.python.org/3/library/constants.html#None)

#### set(expr: [ValueCastable](reference.md#amaranth.hdl.ValueCastable), value: [Any](https://docs.python.org/3/library/typing.html#typing.Any)) → [None](https://docs.python.org/3/library/constants.html#None)

Update the value of an expression.

The behavior of this method depends on the type of `expr`:

- If it is a [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable) whose shape is a [`ShapeCastable`](reference.md#amaranth.hdl.ShapeCastable),
  `value` is converted to a numeric representation using
  [`const()`](reference.md#amaranth.hdl.ShapeCastable.const) and then assigned.
- If it is a [`Value`](reference.md#amaranth.hdl.Value) or a [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable) whose shape is
  a [`Shape`](reference.md#amaranth.hdl.Shape), `value` is assigned as-is.

This method is available in both processes and testbenches.

When used in a testbench, this method runs all processes that wait (directly or
indirectly) for the signals in `expr` to change, and returns only after the change
propagates through the simulated circuits.

#### critical()

Context manager that temporarily makes the caller critical.

Testbenches and processes may be *background* or *critical*, where critical ones prevent
[`Simulator.run()`](#amaranth.sim.Simulator.run) from finishing. Processes are always created background, while
testbenches are created critical by default, but may also be created background.
This context manager makes the caller critical for the span of the `with` statement.

This may be useful in cases where an operation (for example, a bus transaction) takes
multiple clock cycles to complete, and must be completed after starting, but the testbench
or process performing it never finishes, always waiting for the next operation to arrive.
In this case, the caller would elevate itself to become critical only for the duration of
the operation itself using this context manager, for example:

```default
async def testbench_bus_transaction(ctx):
    # On every cycle, check whether the bus has an active transaction...
    async for clk_edge, rst_active, bus_active_value in ctx.tick().sample(bus.active):
        if bus_active_value: # ... if it does...
            with ctx.critical(): # ... make this testbench critical...
                addr_value = ctx.get(bus.r_addr)
                ctx.set(bus.r_data, ...) # ... perform the access...
                await ctx.tick()
                ctx.set(bus.done, 1)
                await ctx.tick()
                ctx.set(bus.done, 0) # ... and complete the transaction later.
            # The `run()` method could return at this point, but not before.
```

#### tick(domain: [str](https://docs.python.org/3/library/stdtypes.html#str), \*, context: Elaboratable = None) → [TickTrigger](#amaranth.sim.TickTrigger)

#### tick(domain: ClockDomain) → [TickTrigger](#amaranth.sim.TickTrigger)

Wait until an active clock edge or an asynchronous reset occurs.

This method returns a [`TickTrigger`](#amaranth.sim.TickTrigger) object that, when awaited, pauses the execution
of the calling process or testbench until the active edge of the clock, or the asynchronous
reset (if applicable), occurs. The returned object may be used to repeatedly wait for one
of these events until a condition is satisfied or a specific number of times. See
the [tick trigger reference](#sim-tick-trigger) for more details.

The `domain` may be either a `ClockDomain` or a [`str`](https://docs.python.org/3/library/stdtypes.html#str). If it is
a [`str`](https://docs.python.org/3/library/stdtypes.html#str), a clock domain with this name is looked up in
the [elaboratable](guide.md#lang-elaboration) `context`, or in `toplevel` if
`context` is not provided.

* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `domain` is `"comb"`.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `domain` is a `ClockDomain` and `context` is provided and not
        `None`.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `context` is an elaboratable that is not a direct or indirect submodule of
        `toplevel`.
  * [**NameError**](https://docs.python.org/3/library/exceptions.html#NameError) – If `domain` is a [`str`](https://docs.python.org/3/library/stdtypes.html#str), but there is no clock domain with this name in
        `context` or `toplevel`.

#### delay(interval)

Wait until a time interval has elapsed.

This method returns a [`TriggerCombination`](#amaranth.sim.TriggerCombination) object that, when awaited, pauses
the execution of the calling process or testbench by `interval` seconds. The returned
object may be used to wait for multiple events.

The value captured by this trigger is `True` if the delay has expired when the wait has
completed, and `False` otherwise.

The `interval` may be zero, in which case the caller will be scheduled for execution
immediately after all of the processes and testbenches scheduled for the current time step
finish executing. In other words, if a call to [`Simulator.advance()`](#amaranth.sim.Simulator.advance) schedules a process
or testbench and it performs `await ctx.delay(0)`, this process or testbench will
continue execution only during the next call to [`Simulator.advance()`](#amaranth.sim.Simulator.advance).

#### NOTE
Although the behavior of `await ctx.delay(0)` is well-defined, it may make waveforms
difficult to understand and simulations hard to reason about.

* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `delay` is negative.
* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### changed(\*signals)

Asynchronously wait until one of the signals change.

This method returns a [`TriggerCombination`](#amaranth.sim.TriggerCombination) object that, when awaited, pauses
the execution of the calling process or testbench until any of the `signals` change.
The returned object may be used to wait for multiple events.

The values captured by this trigger are the values of `signals` at the time the wait
has completed.

#### WARNING
The simulation may produce *glitches*: transient changes to signals (e.g. from 0 to 1
and back to 0) during combinational propagation that are invisible in testbenches or
waveform captures. Glitches will wake up **both processes and testbenches** that use
this method to wait for a signal to change, and both processes and testbenches must be
prepared to handle such spurious wakeups. The presence, count, and sequence in which
glitches occur may also vary between simulation runs.

Testbenches that wait for a signal to change using an `await` statement might only
observe the final value of the signal, and testbenches that wait for changes using
an `async for` loop will crash with a [`BrokenTrigger`](#amaranth.sim.BrokenTrigger) exception if they
encounter a glitch.

Processes will observe all of the transient values of the signal.

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### edge(signal, polarity)

Asynchronously wait until a low-to-high or high-to-low transition of a signal occurs.

This method returns a [`TriggerCombination`](#amaranth.sim.TriggerCombination) object that, when awaited, pauses
the execution of the calling process or testbench until the value of `signal`
(a single-bit signal or a single-bit slice of a signal) changes from `not polarity`
to `polarity`. The returned object may be used to wait for multiple events.

The value captured by this trigger is `True` if the relevant transition has occurred
at the time the wait has completed, and `False` otherwise.

#### WARNING
In most cases, this method should not be used to wait for a status signal to be asserted
or deasserted in a testbench because it is likely to introduce a race condition.
Whenever a suitable clock domain is available, use
`await ctx.tick().until(signal == polarity)` instead.

* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `signal` is neither a single-bit `Signal` nor a single-bit slice of
        a `Signal`.
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If the shape of `signal` is a `ShapeCastable`.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `polarity` is neither 0 nor 1.
* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### posedge(signal)

Asynchronously wait until a signal is asserted.

Equivalent to [`edge(signal, 1)`](#amaranth.sim.SimulatorContext.edge).

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### negedge(signal)

Asynchronously wait until a signal is deasserted.

Equivalent to [`edge(signal, 0)`](#amaranth.sim.SimulatorContext.edge).

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

### *exception* amaranth.sim.BrokenTrigger

Exception raised when a trigger that is repeatedly awaited using an `async for` loop has
a matching event occur while the body of the `async for` loop is still executing.

### *exception* amaranth.sim.DomainReset

Exception raised when a tick trigger is repeatedly awaited, and its domain has been reset.

<a id="sim-tick-trigger"></a>

### *class* amaranth.sim.TickTrigger(...)

A trigger that wakes up the caller when the active edge of a clock domain occurs or the domain
is asynchronously reset.

A [`TickTrigger`](#amaranth.sim.TickTrigger) is an immutable object that stores a reference to a clock domain and
a list of expressions to sample.

The [`SimulatorContext.tick()`](#amaranth.sim.SimulatorContext.tick) method creates a tick trigger with an empty list of sampled
expressions, and the [`TickTrigger.sample()`](#amaranth.sim.TickTrigger.sample) method creates a tick trigger based on another
tick trigger that additionally samples the specified expressions.

To wait for a tick trigger to be activated once (a *one-shot* wait), a process or testbench
calls `await trigger`, usually on a newly created tick trigger:

```default
async def testbench(ctx):
    clk_hit, rst_active, a_value, b_value = await ctx.tick().sample(dut.a, dut.b)
```

To repeatedly wait for a tick trigger to be activated (a *multi-shot* wait), a process or
testbench [asynchronously iterates](https://docs.python.org/3/glossary.html#term-asynchronous-iterable) the tick trigger,
usually using the `async for` loop:

```default
async def testbench(ctx):
    async for clk_hit, rst_active, a_value, b_value in ctx.tick().sample(dut.a, dut.b):
        ...
```

Both one-shot and multi-shot waits return the same [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple)
`(clk_hit, rst_active, *values)` of return values:

1. `clk_hit` is `True` if there was an active clock edge at the moment the wait has
   completed, and `False` otherwise (that is, if the clock domain was asynchronously reset).
2. `rst_active` is `True` if the clock domain is reset (synchronously or asynchronously)
   at the moment the wait has completed, `False` otherwise.
3. All following return values correspond to the sampled expressions in the order in which they
   were added.

Aside from the syntax, there are two differences between one-shot and multi-shot waits:

1. A multi-shot wait continues to observe the tick trigger while the process or testbench
   responds to the event. If the tick trigger is activated again before the next iteration of
   the asynchronous iterator (such as while the body of the `async for` loop is executing),
   the next iteration raises a [`BrokenTrigger`](#amaranth.sim.BrokenTrigger) exception to notify the caller of the missed
   event.
2. A repeated one-shot wait may be less efficient than a multi-shot wait.

#### NOTE
The exact behavior of `rst_active` differs depending on whether `domain` uses
synchronous or asynchronous reset; in both cases it is `True` if and only if
the domain reset has been asserted. Reusable processes and testbenches, as well as their
building blocks, should handle both cases.

* **Parameters:**
  * **engine** (*BaseEngine*)
  * **process** (*BaseProcess*)
  * **domain** (*ClockDomain*)
  * **sampled** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*ValueLike*](reference.md#amaranth.hdl.ValueLike) *]*)

#### sample(\*exprs)

Sample expressions when this trigger is activated.

This method returns a new [`TickTrigger`](#amaranth.sim.TickTrigger) object. When awaited, this object returns,
in addition to the values that would be otherwise returned by `await trigger`,
the values of `exprs` (any [`ValueLike`](reference.md#amaranth.hdl.ValueLike)) at exactly the moment at which
the active clock edge, or the asynchronous reset (if applicable), has occurred.

Combining [`tick()`](#amaranth.sim.SimulatorContext.tick) with [`sample()`](#amaranth.sim.TickTrigger.sample) can be used to capture
the state of a circuit after the active clock edge, but before propagation of signal values
that have been updated by that clock edge:

```default
async for clk_edge, rst_active, in_a_value, in_b_value in \
        ctx.tick().sample(in_a, in_b):
    ...
```

Chaining calls to [`sample()`](#amaranth.sim.TickTrigger.sample) has the same effect as calling it once with the combined
list of arguments. The code below has the same behavior as the code above:

```default
async for clk_edge, rst_active, in_a_value, in_b_value in \
        ctx.tick().sample(in_a).sample(in_b):
    ...
```

#### NOTE
Chaining calls to this method is useful for defining reusable building blocks.
The following (simplified for clarity) implementation of [`until()`](#amaranth.sim.TickTrigger.until) takes advantage
of it by first appending `condition` to the end of the list of captured expressions,
checking if it holds, and then removing it from the list of sampled values:

```default
async def until(trigger, condition):
    async for clk_edge, rst_active, *values, done in trigger.sample(condition):
        if done:
            return values
```

* **Parameters:**
  **exprs** ([*ValueLike*](reference.md#amaranth.hdl.ValueLike))
* **Return type:**
  [*TickTrigger*](#amaranth.sim.TickTrigger)

#### *async* until(condition)

Repeat this trigger until a condition is met.

This method awaits this trigger at least once, and returns a [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of the values
that are [`sample()`](#amaranth.sim.TickTrigger.sample)d when `condition` evaluates to a non-zero value. Values
sampled during previous repeats are discarded.

Awaiting a `trigger` returns values indicating the state of the clock and reset signals,
while awaiting `trigger.until(...)` does not:

```default
while True:
    clk_edge, rst_active, *values, flag_value = await trigger.sample(flag) # never raises
    if flag_value:
        break
# `values` may be used after the loop finishes
```

```default
values = await trigger.until(flag) # may raise `DomainReset`
```

* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If the shape of `condition` is a `ShapeCastable`.
  * [**DomainReset**](#amaranth.sim.DomainReset) – If the clock domain has been synchronously or asynchronously reset during the wait.
* **Parameters:**
  **condition** ([*ValueLike*](reference.md#amaranth.hdl.ValueLike))

#### *async* repeat(count)

Repeat this trigger a specific number of times.

This method awaits this trigger at least once, and returns a [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of the values
that are [`sample()`](#amaranth.sim.TickTrigger.sample)d during the last repeat. Values sampled during previous repeats
are discarded.

Awaiting a `trigger` returns values indicating the state of the clock and reset signals,
while awaiting `trigger.repeat(...)` does not:

```default
for _ in range(3):
    clk_edge, rst_active, *values = await trigger # never raises
# `values` may be used after the loop finishes
```

```default
values = await trigger.repeat(3) # may raise `DomainReset`
```

* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `count` is less than 1.
  * [**DomainReset**](#amaranth.sim.DomainReset) – If the clock domain has been synchronously or asynchronously reset during the wait.
* **Parameters:**
  **count** ([*int*](https://docs.python.org/3/library/functions.html#int))

### *class* amaranth.sim.TriggerCombination(...)

A list of triggers, the activation of any of which will wake up the caller.

A [`TriggerCombination`](#amaranth.sim.TriggerCombination) is an immutable object that stores a list of triggers and
expressions to sample. The trigger combination wakes up the caller when any of these triggers
activate, and it samples all of the signals at the same moment.

The [`SimulatorContext.delay()`](#amaranth.sim.SimulatorContext.delay), [`SimulatorContext.changed()`](#amaranth.sim.SimulatorContext.changed), and
[`SimulatorContext.edge()`](#amaranth.sim.SimulatorContext.edge) methods create a trigger combination that consists of just that
one trigger, while [`TriggerCombination.delay()`](#amaranth.sim.TriggerCombination.delay), [`TriggerCombination.changed()`](#amaranth.sim.TriggerCombination.changed), and
[`TriggerCombination.edge()`](#amaranth.sim.TriggerCombination.edge) methods create a trigger combination based on another trigger
combination by extending it with an additional trigger. The [`TriggerCombination.sample()`](#amaranth.sim.TriggerCombination.sample)
method creates a trigger combination based on another trigger combination that wakes up
the caller in the same conditions but additionally samples the specified expressions.

To wait for a trigger combination to be activated once (a *one-shot* wait), a process or
testbench calls `await triggers`, usually on a newly created trigger combination:

```default
async def testbench(ctx):
    a_value, b_value = await ctx.changed(dut.a, dut.b)
```

To repeatedly wait for a trigger combination to be activated (a *multi-shot* wait), a process
or testbench [asynchronously iterates](https://docs.python.org/3/glossary.html#term-asynchronous-iterable) the trigger
combination, usually using the `async for` loop:

```default
async def testbench(ctx):
    async a_value, b_value in ctx.changed(dut.a, dut.b):
        ...
```

Both one-shot and multi-shot waits return the same [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of return values, the elements
of which are determined by the triggers and sampled expressions that have been added to
the trigger combination, in the order in which they were added. For a detailed description of
the return values, refer to [`SimulatorContext.delay()`](#amaranth.sim.SimulatorContext.delay), [`SimulatorContext.changed()`](#amaranth.sim.SimulatorContext.changed),
[`SimulatorContext.edge()`](#amaranth.sim.SimulatorContext.edge), and [`TriggerCombination.sample()`](#amaranth.sim.TriggerCombination.sample).

Aside from the syntax, there are two differences between one-shot and multi-shot waits:

1. A multi-shot wait continues to observe the trigger combination while the process or testbench
   responds to the event. If the trigger combination is activated again before the next
   iteration of the asynchronous iterator (such as while the body of the `async for` loop is
   executing), the next iteration raises a [`BrokenTrigger`](#amaranth.sim.BrokenTrigger) exception to notify the caller
   of the missed event.
2. A repeated one-shot wait may be less efficient than a multi-shot wait.

* **Parameters:**
  * **engine** (*BaseEngine*)
  * **process** (*BaseProcess*)
  * **triggers** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[**DelayTrigger* *|**ChangedTrigger* *|**SampleTrigger* *|**EdgeTrigger* *,*  *...* *]*)

#### sample(\*exprs)

Sample signals when a trigger from this combination is activated.

This method returns a new [`TriggerCombination`](#amaranth.sim.TriggerCombination) object. When awaited, this object
returns, in addition to the values that would be returned by `await trigger`, the values
of `exprs` at exactly the moment at which the wait has completed.

Combining [`delay()`](#amaranth.sim.SimulatorContext.delay), [`changed()`](#amaranth.sim.SimulatorContext.changed), or
[`edge()`](#amaranth.sim.SimulatorContext.edge) with [`sample()`](#amaranth.sim.TriggerCombination.sample) can be used to capture the state of
a circuit at the moment of the event:

```default
async for arst_edge, delay_expired, in_a_value, in_b_value in \
        ctx.posedge(arst).delay(1e-3).sample(in_a, in_b):
    ...
```

Chaining calls to [`sample()`](#amaranth.sim.TriggerCombination.sample) has the same effect as calling it once with the combined
list of arguments. The code below has the same behavior as the code above:

```default
async for arst_edge, delay_expired, in_a_value, in_b_value in \
        ctx.posedge(arst).delay(1e-3).sample(in_a).sample(in_b):
    ...
```

#### NOTE
Chaining calls to this method is useful for defining reusable building blocks. See
the documentation for [`TickTrigger.sample()`](#amaranth.sim.TickTrigger.sample) for a detailed example.

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### delay(interval)

Add a delay trigger to the list of triggers.

This method returns a new [`TriggerCombination`](#amaranth.sim.TriggerCombination) object. When awaited, this object
also waits for the same trigger as [`SimulatorContext.delay()`](#amaranth.sim.SimulatorContext.delay), and returns,
in addition to the values that would be returned by `await trigger`, the value
returned by [`SimulatorContext.delay()`](#amaranth.sim.SimulatorContext.delay).

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### changed(\*signals)

Add a signal change trigger to the list of triggers.

This method returns a new [`TriggerCombination`](#amaranth.sim.TriggerCombination) object. When awaited, this object
also waits for the same trigger as [`SimulatorContext.changed()`](#amaranth.sim.SimulatorContext.changed), and returns,
in addition to the values that would be returned by `await trigger`, the values
returned by [`SimulatorContext.changed()`](#amaranth.sim.SimulatorContext.changed).

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### edge(signal, polarity)

Add a low-to-high or high-to-low transition trigger to the list of triggers.

This method returns a new [`TriggerCombination`](#amaranth.sim.TriggerCombination) object. When awaited, this object
also waits for the same trigger as [`SimulatorContext.edge()`](#amaranth.sim.SimulatorContext.edge), and returns,
in addition to the values that would be returned by `await trigger`, the values
returned by [`SimulatorContext.edge()`](#amaranth.sim.SimulatorContext.edge).

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### posedge(signal)

Add a low-to-high transition trigger to the list of triggers.

Equivalent to [`edge(signal, 1)`](#amaranth.sim.TriggerCombination.edge).

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)

#### negedge(signal)

Add a high-to-low transition trigger to the list of triggers.

Equivalent to [`edge(signal, 0)`](#amaranth.sim.TriggerCombination.edge).

* **Return type:**
  [*TriggerCombination*](#amaranth.sim.TriggerCombination)
