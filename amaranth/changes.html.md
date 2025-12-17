# Changelog

This document describes changes to the public interfaces in the Amaranth language and standard library. It does not include most bug fixes or implementation changes; versions which do not include notable changes are not listed here.

## Documentation for past releases

Documentation for past releases of the Amaranth language and toolchain is available online:

* [Amaranth 0.5.4](https://amaranth-lang.org/docs/amaranth/v0.5.3/)
* [Amaranth 0.5.3](https://amaranth-lang.org/docs/amaranth/v0.5.3/)
* [Amaranth 0.5.2](https://amaranth-lang.org/docs/amaranth/v0.5.2/)
* [Amaranth 0.5.1](https://amaranth-lang.org/docs/amaranth/v0.5.1/)
* [Amaranth 0.5.0](https://amaranth-lang.org/docs/amaranth/v0.5.0/)
* [Amaranth 0.4.5](https://amaranth-lang.org/docs/amaranth/v0.4.5/)
* [Amaranth 0.4.4](https://amaranth-lang.org/docs/amaranth/v0.4.4/)
* [Amaranth 0.4.3](https://amaranth-lang.org/docs/amaranth/v0.4.3/)
* [Amaranth 0.4.2](https://amaranth-lang.org/docs/amaranth/v0.4.2/)
* [Amaranth 0.4.1](https://amaranth-lang.org/docs/amaranth/v0.4.1/)
* [Amaranth 0.4.0](https://amaranth-lang.org/docs/amaranth/v0.4.0/)
* [Amaranth 0.3](https://amaranth-lang.org/docs/amaranth/v0.3/)

## Version 0.5.4

Updated to address deprecations in Yosys 0.48.

## Version 0.5.3

### Language changes

* Added: individual bits of the same signal can now be assigned from different modules or domains.

### Toolchain changes

* Added: the Amaranth RPC server can now elaborate [`amaranth.lib.wiring.Component`](stdlib/wiring.md#amaranth.lib.wiring.Component) objects on demand.

## Version 0.5.2

### Standard library changes

* Added: constants of [`amaranth.lib.data.ArrayLayout`](stdlib/data.md#amaranth.lib.data.ArrayLayout) can be indexed with negative integers or slices.
* Added: `len()` works on constants of [`amaranth.lib.data.ArrayLayout`](stdlib/data.md#amaranth.lib.data.ArrayLayout).
* Added: constants of [`amaranth.lib.data.ArrayLayout`](stdlib/data.md#amaranth.lib.data.ArrayLayout) are iterable.

### Platform integration changes

* Added: `Platform.request()` accepts `dir="-"` for resources with subsignals.

## Version 0.5.1

### Implemented RFCs

* [RFC 69](https://amaranth-lang.org/rfcs/0069-simulation-port.html): Add a `lib.io.PortLike` object usable in simulation

### Standard library changes

* Added: views of [`amaranth.lib.data.ArrayLayout`](stdlib/data.md#amaranth.lib.data.ArrayLayout) can be indexed with negative integers or slices.
* Added: `len()` works on views of [`amaranth.lib.data.ArrayLayout`](stdlib/data.md#amaranth.lib.data.ArrayLayout).
* Added: views of [`amaranth.lib.data.ArrayLayout`](stdlib/data.md#amaranth.lib.data.ArrayLayout) are iterable.
* Added: [`io.SimulationPort`](stdlib/io.md#amaranth.lib.io.SimulationPort). ([RFC 69](https://amaranth-lang.org/rfcs/0069-simulation-port.html))

## Version 0.5.0

The Migen compatibility layer has been removed.

### Migrating from version 0.4

Apply the following changes to code written against Amaranth 0.4 to migrate it to version 0.5:

* Update uses of `reset=` keyword argument to `init=`.
* Ensure all elaboratables are subclasses of `Elaboratable`.
* Replace uses of `m.Case()` with no patterns with `m.Default()`.
* Replace uses of `Value.matches()` with no patterns with `Const(1)`.
* Ensure clock domains aren’t used outside the module that defines them, or its submodules; move clock domain definitions upwards in the hierarchy as necessary
* Replace imports of `amaranth.asserts.Assert`, `Assume`, and `Cover` with imports from `amaranth.hdl`.
* Remove uses of `name=` keyword argument of `Assert`, `Assume`, and `Cover`; a message can be used instead.
* Replace uses of `amaranth.hdl.Memory` with [`amaranth.lib.memory.Memory`](stdlib/memory.md#amaranth.lib.memory.Memory).
* Update uses of `platform.request` to pass `dir="-"` and use [`amaranth.lib.io`](stdlib/io.md#module-amaranth.lib.io) buffers.
* Remove uses of `amaranth.lib.coding.*` by inlining or copying the implementation of the modules.
* Convert uses of `Simulator.add_sync_process` used as testbenches to [`Simulator.add_testbench`](simulator.md#amaranth.sim.Simulator.add_testbench).
* Convert other uses of `Simulator.add_sync_process` to [`Simulator.add_process`](simulator.md#amaranth.sim.Simulator.add_process).
* Convert simulator processes and testbenches to use the new async API.
* Update uses of [`Simulator.add_clock`](simulator.md#amaranth.sim.Simulator.add_clock) with explicit `phase` to take into account simulator no longer adding implicit `period / 2`. (Previously, [`Simulator.add_clock`](simulator.md#amaranth.sim.Simulator.add_clock) was documented to first toggle the clock at the time `phase`, but actually first toggled the clock at `period / 2 + phase`.)
* Update uses of [`Simulator.run_until`](simulator.md#amaranth.sim.Simulator.run_until) to remove the `run_passive=True` argument. If the code uses `run_passive=False`, ensure it still works with the new behavior.
* Update uses of `amaranth.utils.log2_int(need_pow2=False)` to `amaranth.utils.ceil_log2()`.
* Update uses of `amaranth.utils.log2_int(need_pow2=True)` to `amaranth.utils.exact_log2()`.
* Replace uses of `a.implies(b)` with ~a | b.

### Implemented RFCs

* [RFC 17](https://amaranth-lang.org/rfcs/0017-remove-log2-int.html): Remove `log2_int`
* [RFC 27](https://amaranth-lang.org/rfcs/0027-simulator-testbenches.html): Testbench processes for the simulator
* [RFC 30](https://amaranth-lang.org/rfcs/0030-component-metadata.html): Component metadata
* [RFC 36](https://amaranth-lang.org/rfcs/0036-async-testbench-functions.html): Async testbench functions
* [RFC 39](https://amaranth-lang.org/rfcs/0039-empty-case.html): Change semantics of no-argument `m.Case()`
* [RFC 42](https://amaranth-lang.org/rfcs/0042-const-from-shape-castable.html): `Const` from shape-castable
* [RFC 43](https://amaranth-lang.org/rfcs/0043-rename-reset-to-init.html): Rename `reset=` to `init=`
* [RFC 45](https://amaranth-lang.org/rfcs/0045-lib-memory.html): Move `hdl.Memory` to `lib.Memory`
* [RFC 46](https://amaranth-lang.org/rfcs/0046-shape-range-1.html): Change `Shape.cast(range(1))` to `unsigned(0)`
* [RFC 50](https://amaranth-lang.org/rfcs/0050-print.html): `Print` statement and string formatting
* [RFC 51](https://amaranth-lang.org/rfcs/0051-const-from-bits.html): Add `ShapeCastable.from_bits` and `amaranth.lib.data.Const`
* [RFC 53](https://amaranth-lang.org/rfcs/0053-ioport.html): Low-level I/O primitives
* [RFC 55](https://amaranth-lang.org/rfcs/0055-lib-io.html): New `lib.io` components
* [RFC 58](https://amaranth-lang.org/rfcs/0058-valuecastable-format.html): Core support for `ValueCastable` formatting
* [RFC 59](https://amaranth-lang.org/rfcs/0059-no-domain-upwards-propagation.html): Get rid of upwards propagation of clock domains
* [RFC 61](https://amaranth-lang.org/rfcs/0061-minimal-streams.html): Minimal streams
* [RFC 62](https://amaranth-lang.org/rfcs/0062-memory-data.html): The `MemoryData` class
* [RFC 63](https://amaranth-lang.org/rfcs/0063-remove-lib-coding.html): Remove `amaranth.lib.coding`
* [RFC 65](https://amaranth-lang.org/rfcs/0065-format-struct-enum.html): Special formatting for structures and enums

### Language changes

* Added: `Slice` objects have been made const-castable.
* Added: `amaranth.utils.ceil_log2()`, `amaranth.utils.exact_log2()`. ([RFC 17](https://amaranth-lang.org/rfcs/0017-remove-log2-int.html))
* Added: `Format` objects, `Print` statements, messages in `Assert`, `Assume` and `Cover`. ([RFC 50](https://amaranth-lang.org/rfcs/0050-print.html))
* Added: [`ShapeCastable.from_bits()`](reference.md#amaranth.hdl.ShapeCastable.from_bits) method. ([RFC 51](https://amaranth-lang.org/rfcs/0051-const-from-bits.html))
* Added: IO values, `IOPort` objects, `IOBufferInstance` objects. ([RFC 53](https://amaranth-lang.org/rfcs/0053-ioport.html))
* Added: [`MemoryData`](stdlib/memory.md#amaranth.hdl.MemoryData) objects. ([RFC 62](https://amaranth-lang.org/rfcs/0062-memory-data.html))
* Changed: `m.Case()` with no patterns is never active instead of always active. ([RFC 39](https://amaranth-lang.org/rfcs/0039-empty-case.html))
* Changed: `Value.matches()` with no patterns is `Const(0)` instead of `Const(1)`. ([RFC 39](https://amaranth-lang.org/rfcs/0039-empty-case.html))
* Changed: `Signal(range(stop), init=stop)` warning has been changed into a hard error and made to trigger on any out-of range value.
* Changed: `Signal(range(0))` is now valid without a warning.
* Changed: `Const(value, shape)` now accepts shape-castable objects as `shape`. ([RFC 42](https://amaranth-lang.org/rfcs/0042-const-from-shape-castable.html))
* Changed: `Shape.cast(range(1))` is now `unsigned(0)`. ([RFC 46](https://amaranth-lang.org/rfcs/0046-shape-range-1.html))
* Changed: the `reset=` argument of `Signal`, `Signal.like()`, [`amaranth.lib.wiring.Member`](stdlib/wiring.md#amaranth.lib.wiring.Member), [`amaranth.lib.cdc.FFSynchronizer`](stdlib/cdc.md#amaranth.lib.cdc.FFSynchronizer), and `m.FSM()` has been renamed to `init=`. ([RFC 43](https://amaranth-lang.org/rfcs/0043-rename-reset-to-init.html))
* Changed: [`Shape`](reference.md#amaranth.hdl.Shape) has been made immutable and hashable.
* Changed: `Assert`, `Assume`, `Cover` have been moved to [`amaranth.hdl`](reference.md#module-amaranth.hdl) from `amaranth.asserts`. ([RFC 50](https://amaranth-lang.org/rfcs/0050-print.html))
* Changed: `Instance` IO ports now accept only IO values, not plain values. ([RFC 53](https://amaranth-lang.org/rfcs/0053-ioport.html))
* Deprecated: `amaranth.utils.log2_int()`. ([RFC 17](https://amaranth-lang.org/rfcs/0017-remove-log2-int.html))
* Deprecated: `amaranth.hdl.Memory`. ([RFC 45](https://amaranth-lang.org/rfcs/0045-lib-memory.html))
* Deprecated: upwards propagation of clock domains. ([RFC 59](https://amaranth-lang.org/rfcs/0059-no-domain-upwards-propagation.html))
* Deprecated: `Value.implies()`.
* Removed: (deprecated in 0.4.0) `Const.normalize()`. ([RFC 5](https://amaranth-lang.org/rfcs/0005-remove-const-normalize.html))
* Removed: (deprecated in 0.4.0) `Repl`. ([RFC 10](https://amaranth-lang.org/rfcs/0010-move-repl-to-value.html))
* Removed: (deprecated in 0.4.0) `ast.Sample`, `ast.Past`, `ast.Stable`, `ast.Rose`, `ast.Fell`.
* Removed: assertion names in `Assert`, `Assume` and `Cover`. ([RFC 50](https://amaranth-lang.org/rfcs/0050-print.html))
* Removed: accepting non-subclasses of `Elaboratable` as elaboratables.

### Standard library changes

* Added: [`amaranth.lib.memory`](stdlib/memory.md#module-amaranth.lib.memory). ([RFC 45](https://amaranth-lang.org/rfcs/0045-lib-memory.html))
* Added: [`amaranth.lib.data.Const`](stdlib/data.md#amaranth.lib.data.Const) class. ([RFC 51](https://amaranth-lang.org/rfcs/0051-const-from-bits.html))
* Changed: [`amaranth.lib.data.Layout.const()`](stdlib/data.md#amaranth.lib.data.Layout.const) returns a [`amaranth.lib.data.Const`](stdlib/data.md#amaranth.lib.data.Const), not a view ([RFC 51](https://amaranth-lang.org/rfcs/0051-const-from-bits.html))
* Changed: [`amaranth.lib.wiring.Signature.is_compliant()`](stdlib/wiring.md#amaranth.lib.wiring.Signature.is_compliant) no longer rejects reset-less signals.
* Added: [`amaranth.lib.io.SingleEndedPort`](stdlib/io.md#amaranth.lib.io.SingleEndedPort), [`amaranth.lib.io.DifferentialPort`](stdlib/io.md#amaranth.lib.io.DifferentialPort). ([RFC 55](https://amaranth-lang.org/rfcs/0055-lib-io.html))
* Added: [`amaranth.lib.io.Buffer`](stdlib/io.md#amaranth.lib.io.Buffer), [`amaranth.lib.io.FFBuffer`](stdlib/io.md#amaranth.lib.io.FFBuffer), [`amaranth.lib.io.DDRBuffer`](stdlib/io.md#amaranth.lib.io.DDRBuffer). ([RFC 55](https://amaranth-lang.org/rfcs/0055-lib-io.html))
* Added: [`amaranth.lib.meta`](stdlib/meta.md#module-amaranth.lib.meta), [`amaranth.lib.wiring.ComponentMetadata`](stdlib/wiring.md#amaranth.lib.wiring.ComponentMetadata). ([RFC 30](https://amaranth-lang.org/rfcs/0030-component-metadata.html))
* Added: [`amaranth.lib.stream`](stdlib/stream.md#module-amaranth.lib.stream). ([RFC 61](https://amaranth-lang.org/rfcs/0061-minimal-streams.html))
* Deprecated: [`amaranth.lib.coding`](stdlib/coding.md#module-amaranth.lib.coding). ([RFC 63](https://amaranth-lang.org/rfcs/0063-remove-lib-coding.html))
* Removed: (deprecated in 0.4.0) `amaranth.lib.scheduler`. ([RFC 19](https://amaranth-lang.org/rfcs/0019-remove-scheduler.html))
* Removed: (deprecated in 0.4.0) [`amaranth.lib.fifo.FIFOInterface`](stdlib/fifo.md#amaranth.lib.fifo.FIFOInterface) with `fwft=False`. ([RFC 20](https://amaranth-lang.org/rfcs/0020-deprecate-non-fwft-fifos.html))
* Removed: (deprecated in 0.4.0) [`amaranth.lib.fifo.SyncFIFO`](stdlib/fifo.md#amaranth.lib.fifo.SyncFIFO) with `fwft=False`. ([RFC 20](https://amaranth-lang.org/rfcs/0020-deprecate-non-fwft-fifos.html))

### Toolchain changes

* Added: [`Simulator.add_testbench`](simulator.md#amaranth.sim.Simulator.add_testbench). ([RFC 27](https://amaranth-lang.org/rfcs/0027-simulator-testbenches.html))
* Added: async function support in [`Simulator.add_testbench`](simulator.md#amaranth.sim.Simulator.add_testbench) and [`Simulator.add_process`](simulator.md#amaranth.sim.Simulator.add_process). ([RFC 36](https://amaranth-lang.org/rfcs/0036-async-testbench-functions.html))
* Added: support for `amaranth.hdl.Assert` in simulation. ([RFC 50](https://amaranth-lang.org/rfcs/0050-print.html))
* Changed: [`Simulator.add_clock`](simulator.md#amaranth.sim.Simulator.add_clock) no longer implicitly adds `period / 2` when `phase` is specified, actually matching the documentation.
* Changed: [`Simulator.run_until`](simulator.md#amaranth.sim.Simulator.run_until) always runs the simulation until the given deadline, even when no critical processes or testbenches are present.
* Deprecated: `Settle` simulation command. ([RFC 27](https://amaranth-lang.org/rfcs/0027-simulator-testbenches.html))
* Deprecated: `Simulator.add_sync_process`. ([RFC 27](https://amaranth-lang.org/rfcs/0027-simulator-testbenches.html))
* Deprecated: generator-based simulation processes and testbenches. ([RFC 36](https://amaranth-lang.org/rfcs/0036-async-testbench-functions.html))
* Deprecated: the `run_passive` argument to [`Simulator.run_until`](simulator.md#amaranth.sim.Simulator.run_until) has been deprecated, and does nothing.
* Removed: (deprecated in 0.4.0) use of mixed-case toolchain environment variable names, such as `NMIGEN_ENV_Diamond` or `AMARANTH_ENV_Diamond`; use upper-case environment variable names, such as `AMARANTH_ENV_DIAMOND`.

### Platform integration changes

* Added: `BuildPlan.execute_local_docker()`.
* Added: `BuildPlan.extract()`.
* Added: `build.sh`  begins with `#!/bin/sh`.
* Changed: `IntelPlatform` renamed to `AlteraPlatform`.
* Deprecated: argument `run_script=` in `BuildPlan.execute_local()`.
* Removed: (deprecated in 0.4.0) `vendor.intel`, `vendor.lattice_ecp5`, `vendor.lattice_ice40`, `vendor.lattice_machxo2_3l`, `vendor.quicklogic`, `vendor.xilinx`. ([RFC 18](https://amaranth-lang.org/rfcs/0018-reorganize-vendor-platforms.html))

## Version 0.4.0

Support has been added for a new and improved way of defining data structures in [`amaranth.lib.data`](stdlib/data.md#module-amaranth.lib.data) and component interfaces in [`amaranth.lib.wiring`](stdlib/wiring.md#module-amaranth.lib.wiring), as defined in [RFC 1](https://amaranth-lang.org/rfcs/0001-aggregate-data-structures.html) and [RFC 2](https://amaranth-lang.org/rfcs/0002-interfaces.html). `Record` has been deprecated. In a departure from the usual policy, to give designers additional time to migrate, `Record` will be removed in Amaranth 0.6 (one release later than normal).

Support for enumerations has been extended. A shape for enumeration members can be provided for an enumeration class, as defined in [RFC 3](https://amaranth-lang.org/rfcs/0003-enumeration-shapes.html).

The language includes several new extension points for integration with `Value` based data structures defined outside of the core language. In particular, `Signal(shape)` may now return a `Signal` object wrapped in another if `shape` implements the call protocol, as defined in [RFC 15](https://amaranth-lang.org/rfcs/0015-lifting-shape-castables.html).

Several issues with shape inference have been resolved. Notably, `a - b` where both `a` and `b` are unsigned now returns a signed value.

Support for Python 3.6 and 3.7 has been removed, and support for Python 3.11 and 3.12 has been added.

Features deprecated in version 0.3 have been removed. In particular, the `nmigen.*` namespace is not provided, `# nmigen:` annotations are not recognized, and `NMIGEN_*` envronment variables are not used.

The Migen compatibility layer remains deprecated (as it had been since Amaranth 0.1), and is now scheduled to be removed in version 0.5.

### Migrating from version 0.3

Apply the following changes to code written against Amaranth 0.3 to migrate it to version 0.4:

* Update shell environment to use `AMARANTH_*` environment variables instead of `NMIGEN_*` environment variables.
* Update shell environment to use `AMARANTH_ENV_<TOOLCHAIN>` (with all-uppercase `<TOOLCHAIN>` name) environment variable names instead of `AMARANTH_ENV_<Toolchain>` or `NMIGEN_ENV_<Toolchain>` (with mixed-case `<Toolchain>` name).
* Update imports of the form `from amaranth.vendor.some_vendor import SomeVendorPlatform` to `from amaranth.vendor import SomeVendorPlatform`. This change will reduce future churn.
* Replace uses of `Const.normalize(value, shape)` with `Const(value, shape).value`.
* Replace uses of `Repl(value, count)` with `value.replicate(count)`.
* Replace uses of `Record` with [`amaranth.lib.data`](stdlib/data.md#module-amaranth.lib.data) and [`amaranth.lib.wiring`](stdlib/wiring.md#module-amaranth.lib.wiring). The appropriate replacement depends on the use case. If `Record` was being used for data storage and accessing the bit-level representation, use [`amaranth.lib.data`](stdlib/data.md#module-amaranth.lib.data). If `Record` was being used for connecting design components together, use [`amaranth.lib.wiring`](stdlib/wiring.md#module-amaranth.lib.wiring).
* Replace uses of `Sample`, `Past`, `Stable`, `Rose`, `Fell` with a manually instantiated register, e.g. `past_x = Signal.like(x); m.d.sync += past_x.eq(x)`.
* Remove uses of `amaranth.compat` by migrating to native Amaranth syntax.
* Ensure the `Pin` instance returned by `platform.request` is not cast to value directly, but used for its fields. Replace code like `leds = Cat(platform.request(led, n) for n in range(4))` with `leds = Cat(platform.request(led, n).o for n in range(4))` (note the `.o`).
* Remove uses of `amaranth.lib.scheduler.RoundRobin` by inlining or copying the implementation of that class.
* Remove uses of `amaranth.lib.fifo.SyncFIFO(fwft=False)` and `amaranth.lib.fifo.FIFOInterface(fwft=False)` by converting code to use `fwft=True` FIFOs or copying the implementation of those classes.

While code that uses the features listed as deprecated below will work in Amaranth 0.4, they will be removed in the next version.

### Implemented RFCs

* [RFC 1](https://amaranth-lang.org/rfcs/0001-aggregate-data-structures.html): Aggregate data structure library
* [RFC 2](https://amaranth-lang.org/rfcs/0002-interfaces.html): Interface definition library
* [RFC 3](https://amaranth-lang.org/rfcs/0003-enumeration-shapes.html): Enumeration shapes
* [RFC 4](https://amaranth-lang.org/rfcs/0004-const-castable-exprs.html): Constant-castable expressions
* [RFC 5](https://amaranth-lang.org/rfcs/0005-remove-const-normalize.html): Remove `Const.normalize`
* [RFC 6](https://amaranth-lang.org/rfcs/0006-stdlib-crc.html): CRC generator
* [RFC 8](https://amaranth-lang.org/rfcs/0008-aggregate-extensibility.html): Aggregate extensibility
* [RFC 9](https://amaranth-lang.org/rfcs/0009-const-init-shape-castable.html): Constant initialization for shape-castable objects
* [RFC 10](https://amaranth-lang.org/rfcs/0010-move-repl-to-value.html): Move `Repl` to `Value.replicate`
* [RFC 18](https://amaranth-lang.org/rfcs/0018-reorganize-vendor-platforms.html): Reorganize vendor platforms
* [RFC 19](https://amaranth-lang.org/rfcs/0019-remove-scheduler.html): Remove `amaranth.lib.scheduler`
* [RFC 15](https://amaranth-lang.org/rfcs/0015-lifting-shape-castables.html): Lifting shape-castable objects
* [RFC 20](https://amaranth-lang.org/rfcs/0020-deprecate-non-fwft-fifos.html): Deprecate non-FWFT FIFOs
* [RFC 22](https://amaranth-lang.org/rfcs/0022-valuecastable-shape.html): Define `ValueCastable.shape()`
* [RFC 28](https://amaranth-lang.org/rfcs/0028-override-value-operators.html): Allow overriding `Value` operators
* [RFC 31](https://amaranth-lang.org/rfcs/0031-enumeration-type-safety.html): Enumeration type safety
* [RFC 34](https://amaranth-lang.org/rfcs/0034-interface-rename.html): Rename `amaranth.lib.wiring.Interface` to `PureInterface`
* [RFC 35](https://amaranth-lang.org/rfcs/0035-shapelike-valuelike.html): Add `ShapeLike`, `ValueLike`
* [RFC 37](https://amaranth-lang.org/rfcs/0037-make-signature-immutable.html): Make `Signature` immutable
* [RFC 38](https://amaranth-lang.org/rfcs/0038-component-signature-immutability.html): `Component.signature` immutability

### Language changes

* Added: [`ShapeCastable`](reference.md#amaranth.hdl.ShapeCastable), similar to [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable).
* Added: [`ShapeLike`](reference.md#amaranth.hdl.ShapeLike) and [`ValueLike`](reference.md#amaranth.hdl.ValueLike). ([RFC 35](https://amaranth-lang.org/rfcs/0035-shapelike-valuelike.html))
* Added: [`Value.as_signed()`](reference.md#amaranth.hdl.Value.as_signed) and [`Value.as_unsigned()`](reference.md#amaranth.hdl.Value.as_unsigned) can be used on left-hand side of assignment (with no difference in behavior).
* Added: `Const.cast()`. ([RFC 4](https://amaranth-lang.org/rfcs/0004-const-castable-exprs.html))
* Added: `Signal(reset=)`, [`Value.matches()`](reference.md#amaranth.hdl.Value.matches), `with m.Case():` accept any constant-castable objects. ([RFC 4](https://amaranth-lang.org/rfcs/0004-const-castable-exprs.html))
* Added: [`Value.replicate()`](reference.md#amaranth.hdl.Value.replicate), superseding `Repl`. ([RFC 10](https://amaranth-lang.org/rfcs/0010-move-repl-to-value.html))
* Added: `Memory` supports transparent read ports with read enable.
* Changed: creating a `Signal` with a shape that is a [`ShapeCastable`](reference.md#amaranth.hdl.ShapeCastable) implementing [`ShapeCastable.__call__()`](reference.md#amaranth.hdl.ShapeCastable.__call__) wraps the returned object using that method. ([RFC 15](https://amaranth-lang.org/rfcs/0015-lifting-shape-castables.html))
* Changed: [`Value.cast()`](reference.md#amaranth.hdl.Value.cast) casts [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable) objects recursively.
* Changed: [`Value.cast()`](reference.md#amaranth.hdl.Value.cast) treats instances of classes derived from both [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) and [`int`](https://docs.python.org/3/library/functions.html#int) (including [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)) as enumerations rather than integers.
* Changed: [`Value.matches()`](reference.md#amaranth.hdl.Value.matches) with an empty list of patterns returns `Const(1)` rather than `Const(0)`, to match the behavior of `with m.Case():`.
* Changed: `Cat()` warns if an enumeration without an explicitly specified shape is used. ([RFC 3](https://amaranth-lang.org/rfcs/0003-enumeration-shapes.html))
* Changed: `signed(0)` is no longer constructible. (The semantics of this shape were never defined.)
* Changed: [`Value.__abs__()`](reference.md#amaranth.hdl.Value.__abs__) returns an unsigned value.
* Deprecated: `ast.Sample`, `ast.Past`, `ast.Stable`, `ast.Rose`, `ast.Fell`. (Predating the RFC process.)
* Deprecated: `Const.normalize()`; use `Const(value, shape).value` instead of `Const.normalize(value, shape)`. ([RFC 5](https://amaranth-lang.org/rfcs/0005-remove-const-normalize.html))
* Deprecated: `Repl`; use [`Value.replicate()`](reference.md#amaranth.hdl.Value.replicate) instead. ([RFC 10](https://amaranth-lang.org/rfcs/0010-move-repl-to-value.html))
* Deprecated: `Record`; use [`amaranth.lib.data`](stdlib/data.md#module-amaranth.lib.data) and [`amaranth.lib.wiring`](stdlib/wiring.md#module-amaranth.lib.wiring) instead. ([RFC 1](https://amaranth-lang.org/rfcs/0001-aggregate-data-structures.html), [RFC 2](https://amaranth-lang.org/rfcs/0002-interfaces.html))
* Removed: (deprecated in 0.1) casting of [`Shape`](reference.md#amaranth.hdl.Shape) to and from a `(width, signed)` tuple.
* Removed: (deprecated in 0.3) `ast.UserValue`.
* Removed: (deprecated in 0.3) support for `# nmigen:` linter instructions at the beginning of file.

### Standard library changes

* Added: [`amaranth.lib.enum`](stdlib/enum.md#module-amaranth.lib.enum). ([RFC 3](https://amaranth-lang.org/rfcs/0003-enumeration-shapes.html))
* Added: [`amaranth.lib.data`](stdlib/data.md#module-amaranth.lib.data). ([RFC 1](https://amaranth-lang.org/rfcs/0001-aggregate-data-structures.html))
* Added: [`amaranth.lib.wiring`](stdlib/wiring.md#module-amaranth.lib.wiring). ([RFC 2](https://amaranth-lang.org/rfcs/0002-interfaces.html))
* Added: [`amaranth.lib.crc`](stdlib/crc.md#module-amaranth.lib.crc). ([RFC 6](https://amaranth-lang.org/rfcs/0006-stdlib-crc.html))
* Deprecated: `amaranth.lib.scheduler`. ([RFC 19](https://amaranth-lang.org/rfcs/0019-remove-scheduler.html))
* Deprecated: [`amaranth.lib.fifo.FIFOInterface`](stdlib/fifo.md#amaranth.lib.fifo.FIFOInterface) with `fwft=False`. ([RFC 20](https://amaranth-lang.org/rfcs/0020-deprecate-non-fwft-fifos.html))
* Deprecated: [`amaranth.lib.fifo.SyncFIFO`](stdlib/fifo.md#amaranth.lib.fifo.SyncFIFO) with `fwft=False`. ([RFC 20](https://amaranth-lang.org/rfcs/0020-deprecate-non-fwft-fifos.html))

### Toolchain changes

* Changed: text files are written with LF line endings on Windows, like on other platforms.
* Added: `debug_verilog` override in `build.TemplatedPlatform`.
* Added: `env=` argument to `build.run.BuildPlan.execute_local()`.
* Changed: `build.run.BuildPlan.add_file()` rejects absolute paths.
* Deprecated: use of mixed-case toolchain environment variable names, such as `NMIGEN_ENV_Diamond` or `AMARANTH_ENV_Diamond`; use upper-case environment variable names, such as `AMARANTH_ENV_DIAMOND`.
* Removed: (deprecated in 0.3) `sim.Simulator.step()`.
* Removed: (deprecated in 0.3) `back.pysim`.
* Removed: (deprecated in 0.3) support for invoking `back.rtlil.convert()` and `back.verilog.convert()` without an explicit ports= argument.
* Removed: (deprecated in 0.3) [`test`](https://docs.python.org/3/library/test.html#module-test).

### Platform integration changes

* Added: `icepack_opts` override in `vendor.LatticeICE40Platform`.
* Added: `OSCH` as `default_clk` clock source in `vendor.LatticeMachXO2Platform`, `vendor.LatticeMachXO3LPlatform`.
* Added: Xray toolchain support in `vendor.XilinxPlatform`.
* Added: Artix UltraScale+ part support in `vendor.XilinxPlatform`.
* Added: `vendor.GowinPlatform`.
* Deprecated: `vendor.intel`, `vendor.lattice_ecp5`, `vendor.lattice_ice40`, `vendor.lattice_machxo2_3l`, `vendor.quicklogic`, `vendor.xilinx`; import platforms directly from `vendor` instead. ([RFC 18](https://amaranth-lang.org/rfcs/0018-reorganize-vendor-platforms.html))
* Removed: (deprecated in 0.3) `lattice_machxo2`
* Removed: (deprecated in 0.3) `lattice_machxo_2_3l.LatticeMachXO2Or3LPlatform` SVF programming vector `{{name}}.svf`.
* Removed: (deprecated in 0.3) `xilinx_spartan_3_6.XilinxSpartan3APlatform`, `xilinx_spartan_3_6.XilinxSpartan6Platform`, `xilinx_7series.Xilinx7SeriesPlatform`, `xilinx_ultrascale.XilinxUltrascalePlatform`.

## Version 0.3

The project has been renamed from nMigen to Amaranth.

Features deprecated in version 0.2 have been removed.

### Migrating from version 0.2

Apply the following changes to code written against nMigen 0.2 to migrate it to Amaranth 0.3:

* Update `import nmigen as nm` [explicit prelude imports](guide.md#lang-prelude) to be `import amaranth as am`, and adjust the code to use the `am.*` namespace.
* Update `import nmigen.*` imports to be `import amaranth.*`.
* Update `import nmigen_boards.*` imports to be `import amaranth_boards.*`.
* Update board definitions using `vendor.lattice_machxo2.LatticeMachXO2Platform` to use `vendor.lattice_machxo_2_3l.LatticeMachXO2Platform`.
* Update board definitions using `vendor.xilinx_spartan_3_6.XilinxSpartan3APlatform`, `vendor.xilinx_spartan_3_6.XilinxSpartan6Platform`, `vendor.xilinx_7series.Xilinx7SeriesPlatform`, `vendor.xilinx_ultrascale.XilinxUltrascalePlatform` to use `vendor.xilinx.XilinxPlatform`.
* Switch uses of `hdl.ast.UserValue` to `ValueCastable`; note that `ValueCastable` does not inherit from `Value`, and inheriting from `Value` is not supported.
* Switch uses of `back.pysim` to `sim`.
* Add an explicit `ports=` argument to uses of `back.rtlil.convert()` and `back.verilog.convert()` if missing.
* Remove uses of `test.utils.FHDLTestCase` and vendor the implementation of `test.utils.FHDLTestCase.assertFormal` if necessary.

While code that uses the features listed as deprecated below will work in Amaranth 0.3, they will be removed in the next version.

### Language changes

* Added: [`Value`](reference.md#amaranth.hdl.Value) can be used with [`abs()`](https://docs.python.org/3/library/functions.html#abs).
* Added: [`Value.rotate_left()`](reference.md#amaranth.hdl.Value.rotate_left) and [`Value.rotate_right()`](reference.md#amaranth.hdl.Value.rotate_right).
* Added: [`Value.shift_left()`](reference.md#amaranth.hdl.Value.shift_left) and [`Value.shift_right()`](reference.md#amaranth.hdl.Value.shift_right).
* Added: [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable).
* Deprecated: `ast.UserValue`; use [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable) instead.
* Added: Division and modulo operators can be used with a negative divisor.
* Deprecated: `# nmigen:` linter instructions at the beginning of file; use `# amaranth:` instead.

### Standard library changes

* Added: [`cdc.PulseSynchronizer`](stdlib/cdc.md#amaranth.lib.cdc.PulseSynchronizer).
* Added: [`cdc.AsyncFFSynchronizer`](stdlib/cdc.md#amaranth.lib.cdc.AsyncFFSynchronizer).
* Changed: [`fifo.AsyncFIFO`](stdlib/fifo.md#amaranth.lib.fifo.AsyncFIFO) is reset when the write domain is reset.
* Added: `fifo.AsyncFIFO.r_rst` is asserted when the write domain is reset.
* Added: `fifo.FIFOInterface.r_level` and `fifo.FIFOInterface.w_level`.

### Toolchain changes

* Changed: Backend and simulator reject wires larger than 65536 bits.
* Added: Backend emits Yosys enumeration attributes for [enumeration-shaped](guide.md#lang-shapeenum) signals.
* Added: If a compatible Yosys version is not installed, `back.verilog` will fall back to the [amaranth-yosys](https://github.com/amaranth-lang/amaranth-yosys) PyPI package. The package can be [installed](install.md#install) as `amaranth[builtin-yosys]` to ensure this dependency is available.
* Added: `back.cxxrtl`.
* Added: `sim`, a simulator interface with support for multiple simulation backends.
* Deprecated: `back.pysim`; use `sim` instead.
* Removed: The `with Simulator(fragment, ...) as sim:` form.
* Removed: [`sim.Simulator.add_process()`](simulator.md#amaranth.sim.Simulator.add_process) with a generator argument.
* Deprecated: `sim.Simulator.step()`; use [`sim.Simulator.advance()`](simulator.md#amaranth.sim.Simulator.advance) instead.
* Added: `build.BuildPlan.execute_remote_ssh()`.
* Deprecated: `test.utils.FHDLTestCase`, with no replacement.
* Deprecated: `back.rtlil.convert()` and `back.verilog.convert()` without an explicit ports= argument.
* Changed: VCD output now uses a top-level “bench” module that contains testbench only signals.
* Deprecated: `NMIGEN_*` environment variables; use `AMARANTH_*` environment variables instead.

### Platform integration changes

* Added: `SB_LFOSC` and `SB_HFOSC` as `default_clk` clock sources in `lattice_ice40.LatticeICE40Platform`.
* Added: `lattice_machxo2.LatticeMachXO2Platform` generates binary (`.bit`) bitstreams.
* Added: `lattice_machxo_2_3l.LatticeMachXO3LPlatform`.
* Deprecated: `lattice_machxo2`; use `lattice_machxo_2_3l.LatticeMachXO2Platform` instead.
* Removed: `xilinx_7series.Xilinx7SeriesPlatform.grade`; this family has no temperature grades.
* Removed: `xilinx_ultrascale.XilinxUltrascalePlatform.grade`; this family has temperature grade as part of speed grade.
* Added: Symbiflow toolchain support for `xilinx_7series.Xilinx7SeriesPlatform`.
* Added: `lattice_machxo_2_3l.LatticeMachXO2Or3LPlatform` generates separate Flash and SRAM SVF programming vectors, `{{name}}_flash.svf` and `{{name}}_sram.svf`.
* Deprecated: `lattice_machxo_2_3l.LatticeMachXO2Or3LPlatform` SVF programming vector `{{name}}.svf`; use `{{name}}_flash.svf` instead.
* Added: `quicklogic.QuicklogicPlatform`.
* Added: `cyclonev_oscillator` as `default_clk` clock source in `intel.IntelPlatform`.
* Added: `add_settings` and `add_constraints` overrides in `intel.IntelPlatform`.
* Added: `xilinx.XilinxPlatform`.
* Deprecated: `xilinx_spartan_3_6.XilinxSpartan3APlatform`, `xilinx_spartan_3_6.XilinxSpartan6Platform`, `xilinx_7series.Xilinx7SeriesPlatform`, `xilinx_ultrascale.XilinxUltrascalePlatform`; use `xilinx.XilinxPlatform` instead.
* Added: Mistral toolchain support for `intel.IntelPlatform`.
* Added: `synth_design_opts` override in `xilinx.XilinxPlatform`.

## Versions 0.1, 0.2

No changelog is provided for these versions.

The PyPI packages were published under the `nmigen` namespace, rather than `amaranth`.
