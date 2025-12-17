<a id="wiring"></a>

# Interfaces and connections

The [`amaranth.lib.wiring`](#module-amaranth.lib.wiring) module provides a way to declare the interfaces between design components and connect them to each other in a reliable and convenient way.

<!-- from amaranth import * -->

<a id="wiring-introduction"></a>

## Introduction

### Overview

This module provides four related facilities:

1. Description and construction of interface objects via [`Flow`](#amaranth.lib.wiring.Flow) ([`In`](#amaranth.lib.wiring.In) and [`Out`](#amaranth.lib.wiring.Out)), [`Member`](#amaranth.lib.wiring.Member), and [`Signature`](#amaranth.lib.wiring.Signature), as well as the associated container class [`SignatureMembers`](#amaranth.lib.wiring.SignatureMembers). These classes provide the syntax used in defining components, and are also useful for introspection.
2. Flipping of signatures and interface objects via [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) and [`FlippedInterface`](#amaranth.lib.wiring.FlippedInterface), as well as the associated container class [`FlippedSignatureMembers`](#amaranth.lib.wiring.FlippedSignatureMembers). This facility reduces boilerplate by adapting existing signatures and interface objects: the flip operation changes the [`In`](#amaranth.lib.wiring.In) data flow of a member to [`Out`](#amaranth.lib.wiring.Out) and vice versa.
3. Connecting interface objects together via [`connect()`](#amaranth.lib.wiring.connect). The [`connect()`](#amaranth.lib.wiring.connect) function ensures that the provided interface objects can be connected to each other, and adds the necessary `.eq()` statements to a `Module`.
4. Defining reusable, self-contained components via [`Component`](#amaranth.lib.wiring.Component). Components are `Elaboratable` objects that interact with the rest of the design through an interface specified by their signature.

To use this module, add the following imports to the beginning of the file:

```python
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out
```

The [“Motivation”](#wiring-intro1) and [“Reusable interfaces”](#wiring-intro2) sections describe concepts that are essential for using this module and writing idiomatic Amaranth code. The sections after describe advanced use cases that are only relevant for more complex code.

<a id="wiring-intro1"></a>

### Motivation

Consider a reusable counter with an enable input, configurable limit, and an overflow flag. Using only the core Amaranth language, it could be implemented as:

```python
class BasicCounter(Elaboratable):
    def __init__(self):
        self.en  = Signal()

        self.count = Signal(8)
        self.limit = Signal.like(self.count)

        self.overflow  = Signal()

    def elaborate(self, platform):
        m = Module()

        with m.If(self.en):
            m.d.sync += self.overflow.eq(0)
            with m.If(self.count == self.limit):
                m.d.sync += self.overflow.eq(1)
                m.d.sync += self.count.eq(0)
            with m.Else():
                m.d.sync += self.count.eq(self.count + 1)

        return m
```

Nothing in this implementation indicates the directions of its ports (`en`, `count`, `limit`, and `overflow`) in relation to other parts of the design. To understand whether the value of a port is expected to be provided externally or generated internally, it is first necessary to read the body of the `elaborate` method. If the port is not used within that method in a particular elaboratable, it is not possible to determine its direction, or whether it is even meant to be connected.

The [`amaranth.lib.wiring`](#module-amaranth.lib.wiring) module provides a solution for this problem: *components*. A component is an elaboratable that declares the shapes and directions of its ports in its *signature*. The example above can be rewritten to use the [`Component`](#amaranth.lib.wiring.Component) base class (which itself inherits from `Elaboratable`) to be:

```python
class ComponentCounter(wiring.Component):
    en: In(1)

    count: Out(8)
    limit: In(8)

    overflow: Out(1)

    def elaborate(self, platform):
        m = Module()

        with m.If(self.en):
            m.d.sync += self.overflow.eq(0)
            with m.If(self.count == self.limit):
                m.d.sync += self.overflow.eq(1)
                m.d.sync += self.count.eq(0)
            with m.Else():
                m.d.sync += self.count.eq(self.count + 1)

        return m
```

The code in the constructor *creating* the signals of the counter’s interface one by one is now gone, replaced with the [variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation) *declaring* the counter’s interface. The inherited constructor, `Component.__init__()`, creates the same attributes with the same values as before, and the `elaborate` method is unchanged.

The major difference between the two examples is that the `ComponentCounter` provides unambiguous answers to two questions that previously required examining the `elaborate` method:

1. Which of the Python object’s attributes are ports that are intended to be connected to the rest of the design.
2. What is the direction of the flow of information through the port.

This information, aside from being clear from the source code, can now be retrieved from the `.signature` attribute, which contains an instance of the [`Signature`](#amaranth.lib.wiring.Signature) class:

```pycon
>>> ComponentCounter().signature
Signature({'en': In(1), 'count': Out(8), 'limit': In(8), 'overflow': Out(1)})
```

The [shapes](../guide.md#lang-shapes) of the ports need not be static. The `ComponentCounter` can be made generic, with its range specified when it is constructed, by creating the signature explicitly in its constructor:

```python
class GenericCounter(wiring.Component):
    def __init__(self, width):
        super().__init__({
            "en": In(1),

            "count": Out(width),
            "limit": In(width),

            "overflow": Out(1)
        })

    # The implementation of the `elaborate` method is the same.
    elaborate = ComponentCounter.elaborate
```

```pycon
>>> GenericCounter(16).signature
Signature({'en': In(1), 'count': Out(16), 'limit': In(16), 'overflow': Out(1)})
```

Instances of the `ComponentCounter` and `GenericCounter` class are two examples of *interface objects*. An interface object is a Python object of any type whose a `signature` attribute contains a [`Signature`](#amaranth.lib.wiring.Signature) with which the interface object is compliant (as determined by the [`is_compliant`](#amaranth.lib.wiring.Signature.is_compliant) method of the signature).

The next section introduces the concepts of directionality and connection, and discusses interface objects in more detail.

<a id="wiring-intro2"></a>

### Reusable interfaces

Consider a more complex example where two components are communicating with a *stream* that is using *ready/valid signaling*, where the `valid` signal indicates that the value of `data` provided by the source is meaningful, and the `ready` signal indicates that the sink has consumed the data word:

```python
class DataProducer(wiring.Component):
    en: In(1)

    data: Out(8)
    valid: Out(1)
    ready: In(1)

    def elaborate(self, platform): ...


class DataConsumer(wiring.Component):
    data: In(8)
    valid: In(1)
    ready: Out(1)

    # ... other ports...

    def elaborate(self, platform): ...
```

Data would be transferred between these components by assigning the outputs to the inputs elsewhere in the design:

```python
m = Module()
m.submodules.producer = producer = DataProducer()
m.submodules.consumer = consumer = DataConsumer()

...

m.d.comb += [
    consumer.data.eq(producer.data),
    consumer.valid.eq(producer.valid),
    producer.ready.eq(consumer.ready),
]
```

Although this example is short, it is already repetitive and redundant. The ports on the producer and the consumer, which must match each other for the connection to be made correctly, are declared twice; and the connection itself is made in an error-prone manual way even though the signatures include all of the information required to create it.

The signature of a stream could be defined in a generic way:

```python
class SimpleStreamSignature(wiring.Signature):
    def __init__(self, data_shape):
        super().__init__({
            "data": Out(data_shape),
            "valid": Out(1),
            "ready": In(1)
        })

    def __eq__(self, other):
        return self.members == other.members
```

```pycon
>>> SimpleStreamSignature(8).members
SignatureMembers({'data': Out(8), 'valid': Out(1), 'ready': In(1)})
```

A definition like this is usable, depending on the data flow direction of the members, only in the producer (as in the code above) or only in the consumer. To resolve this problem, this module introduces *flipping*: an operation that reverses the data flow direction of the members of a signature or an interface object while leaving everything else about the object intact. In Amaranth, the (non-flipped) signature definition always declares the data flow directions appropriate for a bus initiator, stream source, controller, and so on. A bus target, stream sink, peripheral, and so on would reuse the source definition by flipping it.

A signature is flipped by calling [`sig.flip()`](#amaranth.lib.wiring.Signature.flip), and an interface object is flipped by calling [`flipped(intf)`](#amaranth.lib.wiring.flipped). These calls return instances of the [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) and [`FlippedInterface`](#amaranth.lib.wiring.FlippedInterface) classes, respectively, which use metaprogramming to wrap another object, changing only the data flow directions of its members and forwarding all other method calls and attribute accesses to the wrapped object.

The example above can be rewritten to use this definition of a stream signature as:

```python
class StreamProducer(wiring.Component):
    en: In(1)
    source: Out(SimpleStreamSignature(8))

    def elaborate(self, platform): ...


class StreamConsumer(wiring.Component):
    sink: Out(SimpleStreamSignature(8).flip())

    def elaborate(self, platform): ...


m = Module()
m.submodules.producer = producer = StreamProducer()
m.submodules.consumer = consumer = StreamConsumer()
```

The producer and the consumer reuse the same signature, relying on flipping to make the port directions complementary:

```pycon
>>> producer.source.signature.members
SignatureMembers({'data': Out(8), 'valid': Out(1), 'ready': In(1)})
>>> producer.source.signature.members['data']
Out(8)
>>> consumer.sink.signature.members
SignatureMembers({'data': Out(8), 'valid': Out(1), 'ready': In(1)}).flip()
>>> consumer.sink.signature.members['data']
In(8)
```

In the `StreamConsumer` definition above, the `sink` member has its direction flipped explicitly because the sink is a stream input; this is the case for every interface due to how port directions are defined. Since this operation is so ubiquitous, it is also performed when `In(...)` is used with a signature rather than a shape. The `StreamConsumer` definition above should normally be written as:

```python
class StreamConsumerUsingIn(wiring.Component):
    sink: In(SimpleStreamSignature(8))

    def elaborate(self, platform): ...
```

The data flow directions of the ports are identical between the two definitions:

```pycon
>>> consumer.sink.signature.members == StreamConsumerUsingIn().sink.signature.members
True
```

If signatures are nested within each other multiple levels deep, the final port direction is determined by how many nested `In(...)` members there are. For each `In(...)` signature wrapping a port, the data flow direction of the port is flipped once:

```pycon
>>> sig = wiring.Signature({"port": Out(1)})
>>> sig.members["port"]
Out(1)
>>> in1 = wiring.Signature({"sig": In(sig)})
>>> in1.members["sig"].signature.members["port"]
In(1)
>>> in2 = wiring.Signature({"sig": In(in1)})
>>> in2.members["sig"].signature.members["sig"].signature.members["port"]
Out(1)
```

Going back to the stream example, the producer and the consumer now communicate with one another using the same set of ports with identical shapes and complementary directions (the auxiliary `en` port being outside of the stream signature), and can be *connected* using the [`connect()`](#amaranth.lib.wiring.connect) function:

```python
wiring.connect(m, producer.source, consumer.sink)
```

This function examines the signatures of the two provided interface objects, ensuring that they are exactly complementary, and then adds combinational `.eq()` statements to the module for each of the port pairs to form the connection. Aside from the *connectability* check, the single line above is equivalent to:

```python
m.d.comb += [
    consumer.sink.data.eq(producer.source.data),
    consumer.sink.valid.eq(producer.source.valid),
    producer.source.ready.eq(consumer.sink.ready),
]
```

Even on the simple example of a stream signature it is clear how using the [`connect()`](#amaranth.lib.wiring.connect) function results in more concise, readable, and robust code. The difference is proportionally more pronounced with more complex signatures. When a signature is being refactored, no changes to the code that uses [`connect()`](#amaranth.lib.wiring.connect) is required.

This explanation concludes the essential knowledge necessary for using this module and writing idiomatic Amaranth code.

<a id="wiring-forwarding"></a>

### Forwarding interior interfaces

Consider a case where a component includes another component as a part of its implementation, and where it is necessary to *forward* the ports of the inner component, that is, expose them within the outer component’s signature. To use the `SimpleStreamSignature` definition above in an example:

```python
class DataProcessorImplementation(wiring.Component):
    source: Out(SimpleStreamSignature(8))

    def elaborate(self, platform): ...


class DataProcessorWrapper(wiring.Component):
    source: Out(SimpleStreamSignature(8))

    def elaborate(self, platform):
        m = Module()
        m.submodules.impl = impl = DataProcessorImplementation()
        m.d.comb += [
            self.source.data.eq(impl.source.data),
            self.source.valid.eq(impl.source.valid),
            impl.source.ready.eq(self.source.ready),
        ]
        return m
```

Because forwarding the ports requires assigning an output to an output and an input to an input, the [`connect()`](#amaranth.lib.wiring.connect) function, which connects outputs to inputs and vice versa, cannot be used—at least not directly. The [`connect()`](#amaranth.lib.wiring.connect) function is designed to cover the usual case of connecting the interfaces of modules *from outside* those modules. In order to connect an interface *from inside* a module, it is necessary to flip that interface first using the [`flipped()`](#amaranth.lib.wiring.flipped) function. The `DataProcessorWrapper` should instead be implemented as:

```python
class DataProcessorWrapper(wiring.Component):
    source: Out(SimpleStreamSignature(8))

    def elaborate(self, platform):
        m = Module()
        m.submodules.impl = impl = DataProcessorImplementation()
        wiring.connect(m, wiring.flipped(self.source), impl.source)
        return m
```

In some cases, *both* of the two interfaces provided to [`connect()`](#amaranth.lib.wiring.connect) must be flipped. For example, the correct way to implement a component that forwards an input interface to an output interface with no processing is:

```python
class DataForwarder(wiring.Component):
    sink: In(SimpleStreamSignature(8))
    source: Out(SimpleStreamSignature(8))

    def elaborate(self, platform):
        m = Module()
        wiring.connect(m, wiring.flipped(self.sink), wiring.flipped(self.source))
        return m
```

#### WARNING
It is important to wrap an interface with the [`flipped()`](#amaranth.lib.wiring.flipped) function whenever it is being connected from inside the module. If the `elaborate` function above had made a connection using `wiring.connect(m, self.sink, self.source)`, it would not work correctly. No diagnostic is emitted in this case.

<a id="wiring-constant-inputs"></a>

### Constant inputs

Sometimes, a component must conform to a particular signature, but some of the input ports required by the signature must have a fixed value at all times. This module addresses this case by allowing both `Signal` and `Const` objects to be used to implement port members:

```python
class ProducerRequiringReady(wiring.Component):
    source: Out(SimpleStreamSignature(8))

    def __init__(self):
        super().__init__()
        self.source.ready = Const(1)

    def elaborate(self, platform): ...


class ConsumerAlwaysReady(wiring.Component):
    sink: In(SimpleStreamSignature(8))

    def __init__(self):
        super().__init__()
        self.sink.ready = Const(1)

    def elaborate(self, platform): ...


class ConsumerPossiblyUnready(wiring.Component):
    sink: In(SimpleStreamSignature(8))

    def elaborate(self, platform): ...
```

```pycon
>>> SimpleStreamSignature(8).is_compliant(ProducerRequiringReady().source)
True
>>> SimpleStreamSignature(8).flip().is_compliant(ConsumerAlwaysReady().sink)
True
```

However, the [`connect()`](#amaranth.lib.wiring.connect) function considers a constant input to be connectable only to a constant output with the same value:

```pycon
>>> wiring.connect(m, ProducerRequiringReady().source, ConsumerAlwaysReady().sink)
>>> wiring.connect(m, ProducerRequiringReady().source, ConsumerPossiblyUnready().sink)
Traceback (most recent call last):
  ...
amaranth.lib.wiring.ConnectionError: Cannot connect to the input member 'arg0.ready' that has a constant value 1
```

This feature reduces the proliferation of similar but subtly incompatible interfaces that are semantically similar, only differing in the presence or absence of optional control or status signals.

<a id="wiring-adapting-interfaces"></a>

### Adapting interfaces

Sometimes, a design requires an interface with a particular signature to be used, but the only implementation available is either a component with an incompatible signature or an elaboratable with no signature at all. If this problem cannot be resolved by other means, *interface adaptation* can be used, where the existing signals are placed into a new interface with the appropriate signature. For example:

```python
class LegacyAXIDataProducer(Elaboratable):
    def __init__(self):
        self.adata = Signal(8)
        self.avalid = Signal()
        self.aready = Signal()

    def elaborate(self, platform): ...


class ModernDataConsumer(wiring.Component):
    sink: In(SimpleStreamSignature(8))


data_producer = LegacyAXIDataProducer()
data_consumer = ModernDataConsumer()

adapted_data_source = SimpleStreamSignature(8).create()
adapted_data_source.data = data_producer.adata
adapted_data_source.valid = data_producer.avalid
adapted_data_source.ready = data_producer.aready

m = Module()
wiring.connect(m, adapted_data_source, data_consumer.sink)
```

When creating an adapted interface, use the [`create`](#amaranth.lib.wiring.Signature.create) method of the signature that is required elsewhere in the design.

<a id="wiring-customizing"></a>

### Customizing signatures and interfaces

The [`amaranth.lib.wiring`](#module-amaranth.lib.wiring) module encourages creation of reusable building blocks. In the examples above, a custom signature, `SimpleStreamSignature`, was introduced to illustrate the essential concepts necessary to use this module. While sufficient for that goal, it does not demonstrate the full capabilities provided by the module.

Consider a simple System-on-Chip memory bus with a configurable address width. In an application like that, additional properties and methods could be usefully defined both on the signature (for example, properties to retrieve the parameters of the interface) and on the created interface object (for example, methods to examine the control and status signals). These can be defined as follows:

```python
from amaranth.lib import enum


class TransferType(enum.Enum, shape=1):
    Write = 0
    Read  = 1


class SimpleBusSignature(wiring.Signature):
    def __init__(self, addr_width=32):
        self._addr_width = addr_width
        super().__init__({
            "en":     Out(1),
            "rw":     Out(TransferType),
            "addr":   Out(self._addr_width),
            "r_data": In(32),
            "w_data": Out(32),
        })

    @property
    def addr_width(self):
        return self._addr_width

    def __eq__(self, other):
        return isinstance(other, SimpleBusSignature) and self.addr_width == other.addr_width

    def __repr__(self):
        return f"SimpleBusSignature({self.addr_width})"

    def create(self, *, path=None, src_loc_at=0):
        return SimpleBusInterface(self, path=path, src_loc_at=1 + src_loc_at)


class SimpleBusInterface(wiring.PureInterface):
    def is_read_xfer(self):
        return self.en & (self.rw == TransferType.Read)

    def is_write_xfer(self):
        return self.en & (self.rw == TransferType.Write)
```

This example demonstrates several important principles of use:

* Defining additional properties for a custom signature. The [`Signature`](#amaranth.lib.wiring.Signature) objects are mutable in a restricted way, and can be frozen with the `freeze` method. In almost all cases, the newly defined properties must be immutable, as shown above.
* Defining a signature-specific `__eq__` method. While anonymous (created from a dictionary of members) instances of [`Signature`](#amaranth.lib.wiring.Signature) compare structurally, instances of [`Signature`](#amaranth.lib.wiring.Signature)-derived classes compare by identity unless the equality operator is overridden. In almost all cases, the equality operator should compare the parameters of the signatures rather than their structures.
* Defining a signature-specific `__repr__` method. Similarly to `__eq__`, the default implementation for [`Signature`](#amaranth.lib.wiring.Signature)-derived classes uses the signature’s identity. In almost all cases, the representation conversion operator should return an expression that constructs an equivalent signature.
* Defining a signature-specific `create` method. The default implementation used in anonymous signatures, [`Signature.create()`](#amaranth.lib.wiring.Signature.create), returns a new instance of [`PureInterface`](#amaranth.lib.wiring.PureInterface). Whenever the custom signature has a corresponding custom interface object class, this method should return a new instance of that class. It should not have any required arguments beyond the ones that [`Signature.create()`](#amaranth.lib.wiring.Signature.create) has (required parameters should be provided when creating the signature and not the interface), but may take additional optional arguments, forwarding them to the interface object constructor.

```pycon
>>> sig32 = SimpleBusSignature(); sig32
SimpleBusSignature(32)
>>> sig24 = SimpleBusSignature(24); sig24
SimpleBusSignature(24)
>>> sig24.addr_width
24
>>> sig24 == SimpleBusSignature(24)
True
>>> bus = sig24.create(); bus
<SimpleBusInterface: SimpleBusSignature(24), en=(sig bus__en), rw=EnumView(TransferType, (sig bus__rw)), addr=(sig bus__addr), r_data=(sig bus__r_data), w_data=(sig bus__w_data)>
>>> bus.is_read_xfer()
(& (sig bus__en) (== (sig bus__rw) (const 1'd1)))
```

The custom properties defined for both the signature and the interface object can be used on the flipped signature and the flipped interface in the usual way:

```pycon
>>> sig32.flip().addr_width
32
>>> wiring.flipped(bus).is_read_xfer()
(& (sig bus__en) (== (sig bus__rw) (const 1'd1)))
```

#### NOTE
Unusually for Python, when the implementation of a property or method is invoked through a flipped object, the `self` argument receives the flipped object that has the type [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) or [`FlippedInterface`](#amaranth.lib.wiring.FlippedInterface). This wrapper object proxies all attribute accesses and method calls to the original signature or interface, the only change being that of the data flow directions. See the documentation for these classes for a more detailed explanation.

#### WARNING
While the wrapper object forwards attribute accesses and method calls, it does not currently proxy special methods such as `__getitem__` or `__add__` that are rarely, if ever, used with interface objects. This limitation may be lifted in the future.

<a id="wiring-path"></a>

### Paths

Whenever an operation in this module needs to refer to the interior of an object, it accepts or produces a *path*: a tuple of strings and integers denoting the attribute names and indexes through which an interior value can be extracted. For example, the path `("buses", 0, "cyc")` into the object `obj` corresponds to the Python expression `obj.buses[0].cyc`.

When they appear in diagnostics, paths are printed as the corresponding Python expression.

## Signatures

### *class* amaranth.lib.wiring.Flow

Direction of data flow. This enumeration has two values, [`Out`](#amaranth.lib.wiring.Out) and [`In`](#amaranth.lib.wiring.In),
the meaning of which depends on the context in which they are used.

#### Out

Outgoing data flow.

When included in a standalone [`Signature`](#amaranth.lib.wiring.Signature), a port [`Member`](#amaranth.lib.wiring.Member) with an [`Out`](#amaranth.lib.wiring.Out)
data flow carries data from an initiator to a responder. That is, the signature
describes the initiator driving the signal and the responder sampling the signal.

When used as the flow of a signature [`Member`](#amaranth.lib.wiring.Member), indicates that the data flow of
the port members of the inner signature remains the same.

When included in the `signature` property of an `Elaboratable`, the signature
describes the elaboratable driving the corresponding signal. That is, the elaboratable is
treated as the initiator.

#### In

Incoming data flow.

When included in a standalone [`Signature`](#amaranth.lib.wiring.Signature), a port [`Member`](#amaranth.lib.wiring.Member) with an [`In`](#amaranth.lib.wiring.In)
data flow carries data from an responder to a initiator. That is, the signature
describes the initiator sampling the signal and the responder driving the signal.

When used as the flow of a signature [`Member`](#amaranth.lib.wiring.Member), indicates that the data flow of
the port members of the inner signature is flipped.

When included in the `signature` property of an `Elaboratable`, the signature
describes the elaboratable sampling the corresponding signal. That is, the elaboratable is
treated as the initiator, the same as in the [`Out`](#amaranth.lib.wiring.Out) case.

#### flip()

Flip the direction of data flow.

* **Returns:**
  [`In`](#amaranth.lib.wiring.In) if called as `Out.flip()`; [`Out`](#amaranth.lib.wiring.Out) if called as `In.flip()`.
* **Return type:**
  [`Flow`](#amaranth.lib.wiring.Flow)

#### \_\_call_\_(description, \*, init=None, reset=None, src_loc_at=0)

Create a [`Member`](#amaranth.lib.wiring.Member) with this data flow and the provided description and
initial value.

* **Returns:**
  `Member(self, description, init=init)`
* **Return type:**
  [`Member`](#amaranth.lib.wiring.Member)

### amaranth.lib.wiring.Out *= Out*

A shortcut for importing [`Flow.Out`](#amaranth.lib.wiring.Flow.Out) as [`amaranth.lib.wiring.Out`](#amaranth.lib.wiring.Out).

### amaranth.lib.wiring.In *= In*

A shortcut for importing [`Flow.In`](#amaranth.lib.wiring.Flow.In) as [`amaranth.lib.wiring.In`](#amaranth.lib.wiring.In).

### *class* amaranth.lib.wiring.Member(flow, description, \*, init=None)

Description of a signature member.

This class is a discriminated union: its instances describe either a port member or
a signature member, and accessing properties for the wrong kind of member raises
an [`AttributeError`](https://docs.python.org/3/library/exceptions.html#AttributeError).

The class is created from a description: a [`Signature`](#amaranth.lib.wiring.Signature) instance (in which case
the [`Member`](#amaranth.lib.wiring.Member) is created as a signature member), or a [shape-like](../guide.md#lang-shapelike)
object (in which case it is created as a port member). After creation the [`Member`](#amaranth.lib.wiring.Member)
instance cannot be modified.

When a `Signal` is created from a description of a port member, the signal’s initial value
is taken from the member description. If this signal is never explicitly assigned a value, it
will equal `init`.

Although instances can be created directly, most often they will be created through
[`In`](#amaranth.lib.wiring.In) and [`Out`](#amaranth.lib.wiring.Out), e.g. `In(unsigned(1))` or `Out(stream.Signature(RGBPixel))`.

#### flip()

Flip the data flow of this member.

* **Returns:**
  A new `member` with `member.flow` equal to `self.flow.flip()`, and identical
  to `self` other than that.
* **Return type:**
  [`Member`](#amaranth.lib.wiring.Member)

#### array(\*dimensions)

Add array dimensions to this member.

The dimensions passed to this method are prepended to the existing dimensions.
For example, `Out(1).array(2)` describes an array of 2 elements, whereas both
`Out(1).array(2, 3)` and `Out(1).array(3).array(2)` both describe a two dimensional
array of 2 by 3 elements.

Dimensions are passed to [`array()`](#amaranth.lib.wiring.Member.array) in the order in which they would be indexed.
That is, `.array(x, y)` creates a member that can be indexed up to `[x-1][y-1]`.

The [`array()`](#amaranth.lib.wiring.Member.array) method is composable: calling `member.array(x)` describes an array of
`x` members even if `member` was already an array.

* **Returns:**
  A new `member` with `member.dimensions` extended by `dimensions`, and
  identical to `self` other than that.
* **Return type:**
  [`Member`](#amaranth.lib.wiring.Member)

#### *property* flow

Data flow of this member.

* **Return type:**
  [`Flow`](#amaranth.lib.wiring.Flow)

#### *property* is_port

Whether this is a description of a port member.

* **Returns:**
  `True` if this is a description of a port member,
  `False` if this is a description of a signature member.
* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### *property* is_signature

Whether this is a description of a signature member.

* **Returns:**
  `True` if this is a description of a signature member,
  `False` if this is a description of a port member.
* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### *property* shape

Shape of a port member.

* **Returns:**
  The shape that was provided when constructing this [`Member`](#amaranth.lib.wiring.Member).
* **Return type:**
  [shape-like object](../guide.md#lang-shapelike)
* **Raises:**
  [**AttributeError**](https://docs.python.org/3/library/exceptions.html#AttributeError) – If `self` describes a signature member.

#### *property* init

Initial value of a port member.

* **Returns:**
  The initial value that was provided when constructing this [`Member`](#amaranth.lib.wiring.Member).
* **Return type:**
  [const-castable object](../guide.md#lang-constcasting)
* **Raises:**
  [**AttributeError**](https://docs.python.org/3/library/exceptions.html#AttributeError) – If `self` describes a signature member.

#### *property* signature

Signature of a signature member.

* **Returns:**
  The signature that was provided when constructing this [`Member`](#amaranth.lib.wiring.Member).
* **Return type:**
  [`Signature`](#amaranth.lib.wiring.Signature)
* **Raises:**
  [**AttributeError**](https://docs.python.org/3/library/exceptions.html#AttributeError) – If `self` describes a port member.

#### *property* dimensions

Array dimensions.

A member will usually have no dimensions; in this case it does not describe an array.
A single dimension describes one-dimensional array, and so on.

* **Returns:**
  Dimensions, if any, of this member, from most to least major.
* **Return type:**
  [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of [`int`](https://docs.python.org/3/library/functions.html#int)

### *exception* amaranth.lib.wiring.SignatureError

This exception is raised when an invalid operation specific to signature manipulation is
performed with [`SignatureMembers`](#amaranth.lib.wiring.SignatureMembers). Other exceptions, such as [`TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError) or
[`NameError`](https://docs.python.org/3/library/exceptions.html#NameError), will still be raised where appropriate.

### *class* amaranth.lib.wiring.SignatureMembers(members=())

Mapping of signature member names to their descriptions.

This container, a [`collections.abc.Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping), is used to implement the `members`
attribute of signature objects.

The keys in this container must be valid Python attribute names that are public (do not begin
with an underscore. The values must be instances of [`Member`](#amaranth.lib.wiring.Member). The container is immutable.

The [`create()`](#amaranth.lib.wiring.SignatureMembers.create) method converts this mapping into a mapping of names to signature members
(signals and interface objects) by creating them from their descriptions. The created mapping
can be used to populate an interface object.

#### flip()

Flip the data flow of the members in this mapping.

* **Returns:**
  Proxy collection `FlippedSignatureMembers(self)` that flips the data flow of
  the members that are accessed using it.
* **Return type:**
  [`FlippedSignatureMembers`](#amaranth.lib.wiring.FlippedSignatureMembers)

#### \_\_eq_\_(other)

Compare the members in this and another mapping.

* **Returns:**
  `True` if the mappings contain the same key-value pairs, `False` otherwise.
* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### \_\_contains_\_(name)

Check whether a member with a given name exists.

* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### \_\_getitem_\_(name)

Retrieves the description of a member with a given name.

* **Return type:**
  [`Member`](#amaranth.lib.wiring.Member)
* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `name` is not a string.
  * [**NameError**](https://docs.python.org/3/library/exceptions.html#NameError) – If `name` is not a valid, public Python attribute name.
  * [**SignatureError**](#amaranth.lib.wiring.SignatureError) – If a member called `name` does not exist in the collection.

#### \_\_setitem_\_(name, member)

Stub that forbids addition of members to the collection.

* **Raises:**
  [**SignatureError**](#amaranth.lib.wiring.SignatureError) – Always.

#### \_\_delitem_\_(name)

Stub that forbids removal of members from the collection.

* **Raises:**
  [**SignatureError**](#amaranth.lib.wiring.SignatureError) – Always.

#### \_\_iter_\_()

Iterate through the names of members in the collection.

* **Returns:**
  Names of members, in the order of insertion.
* **Return type:**
  iterator of [`str`](https://docs.python.org/3/library/stdtypes.html#str)

#### flatten(\*, path=())

Recursively iterate through this collection.

#### NOTE
The [paths](#wiring-path) returned by this method and by [`Signature.flatten()`](#amaranth.lib.wiring.Signature.flatten)
differ. This method yields a single result for each [`Member`](#amaranth.lib.wiring.Member) in the collection,
disregarding their dimensions:

```pycon
>>> sig = wiring.Signature({
...     "items": In(1).array(2)
... })
>>> list(sig.members.flatten())
[(('items',), In(1).array(2))]
```

The [`Signature.flatten()`](#amaranth.lib.wiring.Signature.flatten) method yields multiple results for such a member; see
the documentation for that method for an example.

* **Returns:**
  Pairs of [paths](#wiring-path) and the corresponding members. A path yielded by
  this method is a tuple of strings where each item is a key through which the item may
  be reached.
* **Return type:**
  iterator of ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of [`str`](https://docs.python.org/3/library/stdtypes.html#str), [`Member`](#amaranth.lib.wiring.Member))

#### create(\*, path=None, src_loc_at=0)

Create members from their descriptions.

For each port member, this function creates a `Signal` with the shape and initial
value taken from the member description, and the name constructed from
the [paths](#wiring-path) to the member (by concatenating path items with a double
underscore, `__`).

For each signature member, this function calls [`Signature.create()`](#amaranth.lib.wiring.Signature.create) for that signature.
The resulting object can have any type if a [`Signature`](#amaranth.lib.wiring.Signature) subclass overrides
the [`create`](#amaranth.lib.wiring.SignatureMembers.create) method.

If the member description includes dimensions, in each case, instead of a single member,
a [`list`](https://docs.python.org/3/library/stdtypes.html#list) of members is created for each dimension. (That is, for a single dimension
a list of members is returned, for two dimensions a list of lists is returned, and so on.)

* **Returns:**
  Mapping of names to actual signature members.
* **Return type:**
  dict of [`str`](https://docs.python.org/3/library/stdtypes.html#str) to [value-like](../guide.md#lang-valuelike) or interface object or a potentially nested list of these

### *class* amaranth.lib.wiring.FlippedSignatureMembers(unflipped)

Mapping of signature member names to their descriptions, with the directions flipped.

Although an instance of [`FlippedSignatureMembers`](#amaranth.lib.wiring.FlippedSignatureMembers) could be created directly, it will
be usually created by a call to [`SignatureMembers.flip()`](#amaranth.lib.wiring.SignatureMembers.flip).

This container is a wrapper around [`SignatureMembers`](#amaranth.lib.wiring.SignatureMembers) that contains the same members
as the inner mapping, but flips their data flow when they are accessed. For example:

```python
members = wiring.SignatureMembers({"foo": Out(1)})

flipped_members = members.flip()
assert flipped_members["foo"].flow == In
```

This class implements the same methods, with the same functionality (other than the flipping of
the data flow), as the [`SignatureMembers`](#amaranth.lib.wiring.SignatureMembers) class; see the documentation for that class
for details.

#### flip()

Flips this mapping back to the original one.

* **Returns:**
  `unflipped`
* **Return type:**
  [`SignatureMembers`](#amaranth.lib.wiring.SignatureMembers)

### *class* amaranth.lib.wiring.Signature(members)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a [`Signature`](#amaranth.lib.wiring.Signature) object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when [`connect()`](#amaranth.lib.wiring.connect)ing two interface objects
together. See the [introduction to interfaces](#wiring-intro1) for a more detailed
explanation of why this is useful.

[`Signature`](#amaranth.lib.wiring.Signature) can be used as a base class to define [customized](#wiring-customizing)
signatures and interface objects.

#### WARNING
[`Signature`](#amaranth.lib.wiring.Signature) objects are immutable. Classes inheriting from [`Signature`](#amaranth.lib.wiring.Signature) must
ensure this remains the case when additional functionality is added.

#### flip()

Flip the data flow of the members in this signature.

* **Returns:**
  Proxy object `FlippedSignature(self)` that flips the data flow of the attributes
  corresponding to the members that are accessed using it.

  See the documentation for the [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) class for a detailed discussion
  of how this proxy object works.
* **Return type:**
  [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature)

#### *property* members

Members in this signature.

* **Return type:**
  [`SignatureMembers`](#amaranth.lib.wiring.SignatureMembers)

#### \_\_eq_\_(other)

Compare this signature with another.

The behavior of this operator depends on the types of the arguments. If both `self`
and `other` are instances of the base [`Signature`](#amaranth.lib.wiring.Signature) class, they are compared
structurally (the result is `self.members == other.members`); otherwise they are
compared by identity (the result is `self is other`).

Subclasses of [`Signature`](#amaranth.lib.wiring.Signature) are expected to override this method to take into account
the specifics of the domain. If the subclass has additional properties that do not influence
the [`members`](#amaranth.lib.wiring.Signature.members) dictionary but nevertheless make its instance incompatible with other
instances (for example, whether the feedback is combinational or registered),
the overridden method must take that into account.

* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### flatten(obj)

Recursively iterate through this signature, retrieving member values from an interface
object.

#### NOTE
The [paths](#wiring-path) returned by this method and by
[`SignatureMembers.flatten()`](#amaranth.lib.wiring.SignatureMembers.flatten) differ. This method yield several results for each
[`Member`](#amaranth.lib.wiring.Member) in the collection that has a dimension:

```pycon
>>> sig = wiring.Signature({
...     "items": In(1).array(2)
... })
>>> obj = sig.create()
>>> list(sig.flatten(obj))
[(('items', 0), In(1), (sig obj__items__0)),
 (('items', 1), In(1), (sig obj__items__1))]
```

The [`SignatureMembers.flatten()`](#amaranth.lib.wiring.SignatureMembers.flatten) method yields one result for such a member; see
the documentation for that method for an example.

* **Returns:**
  Tuples of [paths](#wiring-path), flow, and the corresponding member values. A path
  yielded by this method is a tuple of strings or integers where each item is an attribute
  name or index (correspondingly) using which the member value was retrieved.
* **Return type:**
  iterator of ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of [`str`](https://docs.python.org/3/library/stdtypes.html#str) or [`int`](https://docs.python.org/3/library/functions.html#int), [`Flow`](#amaranth.lib.wiring.Flow), [value-like](../guide.md#lang-valuelike))

#### is_compliant(obj, \*, reasons=None, path=('obj',))

Check whether an object matches the description in this signature.

This module places few restrictions on what an interface object may be; it does not
prescribe a specific base class or a specific way of constructing the object, only
the values that its attributes should have. This method ensures consistency between
the signature and the interface object, checking every aspect of the provided interface
object for compliance with the signature.

It verifies that:

* `obj` has a `signature` attribute whose value a [`Signature`](#amaranth.lib.wiring.Signature) instance
  such that `self == obj.signature`;
* for each member, `obj` has an attribute with the same name, whose value:
  * for members with [`dimensions`](#amaranth.lib.wiring.Member.dimensions) specified, contains a list or
    a tuple (or several levels of nested lists or tuples, for multiple dimensions)
    satisfying the requirements below;
  * for port members, is a [value-like](../guide.md#lang-valuelike) object casting to
    a `Signal` or a `Const` whose width and signedness is the same as that
    of the member, and (in case of a `Signal`) whose initial value is that of the
    member;
  * for signature members, matches the description in the signature as verified by
    [`Signature.is_compliant()`](#amaranth.lib.wiring.Signature.is_compliant).

If the verification fails, this method reports the reason(s) by filling the `reasons`
container. These reasons are intended to be human-readable: more than one reason may be
reported but only in cases where this is helpful (e.g. the same error message will not
repeat 10 times for each of the 10 ports in a list).

* **Parameters:**
  * **reasons** ([`list`](https://docs.python.org/3/library/stdtypes.html#list) or `None`) – If provided, a container that receives diagnostic messages.
  * **path** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of [`str`](https://docs.python.org/3/library/stdtypes.html#str)) – The [path](#wiring-path) to `obj`. Could be set to improve diagnostic
    messages if `obj` is nested within another object, or for clarity.
* **Returns:**
  `True` if `obj` matches the description in this signature, `False`
  otherwise. If `False` and `reasons` was not `None`, it will contain
  a detailed explanation why.
* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### create(\*, path=None, src_loc_at=0)

Create an interface object from this signature.

The default [`Signature.create()`](#amaranth.lib.wiring.Signature.create) implementation consists of one line:

```default
def create(self, *, path=None, src_loc_at=0):
    return PureInterface(self, path=path, src_loc_at=1 + src_loc_at)
```

This implementation creates an interface object from this signature that serves purely
as a container for the attributes corresponding to the signature members, and implements
no behavior. Such an implementation is sufficient for signatures created ad-hoc using
the `Signature({ ... })` constructor as well as simple signature subclasses.

When defining a [`Signature`](#amaranth.lib.wiring.Signature) subclass that needs to customize the behavior of
the created interface objects, override this method with a similar implementation
that references the class of your custom interface object:

```python
class CustomSignature(wiring.Signature):
    def create(self, *, path=None, src_loc_at=0):
        return CustomInterface(self, path=path, src_loc_at=1 + src_loc_at)

class CustomInterface(wiring.PureInterface):
    @property
    def my_property(self):
        ...
```

The `path` and `src_loc_at` arguments are necessary to ensure the generated signals
have informative names and accurate source location information.

The custom [`create()`](#amaranth.lib.wiring.Signature.create) method may take positional or keyword arguments in addition to
the two listed above. Such arguments must have a default value, because
the [`SignatureMembers.create()`](#amaranth.lib.wiring.SignatureMembers.create) method will call the [`Signature.create()`](#amaranth.lib.wiring.Signature.create) member
without these additional arguments when this signature is a member of another signature.

#### annotations(obj, /)

Annotate an interface object.

Subclasses of [`Signature`](#amaranth.lib.wiring.Signature) may override this method to provide annotations for
a corresponding interface object. The default implementation provides none.

See [`amaranth.lib.meta`](meta.md#module-amaranth.lib.meta) for details.

* **Returns:**
  `tuple()`
* **Return type:**
  iterable of [`Annotation`](meta.md#amaranth.lib.meta.Annotation)

### *class* amaranth.lib.wiring.FlippedSignature(unflipped)

Description of an interface object, with the members’ directions flipped.

Although an instance of [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) could be created directly, it will be usually
created by a call to [`Signature.flip()`](#amaranth.lib.wiring.Signature.flip).

This proxy is a wrapper around [`Signature`](#amaranth.lib.wiring.Signature) that contains the same description as
the inner mapping, but flips the members’ data flow when they are accessed. It is useful
because [`Signature`](#amaranth.lib.wiring.Signature) objects are mutable and may include custom behavior, and if one was
copied (rather than wrapped) by [`Signature.flip()`](#amaranth.lib.wiring.Signature.flip), the wrong object would be mutated, and
custom behavior would be unavailable.

For example:

```python
sig = wiring.Signature({"foo": Out(1)})

flipped_sig = sig.flip()
assert flipped_sig.members["foo"].flow == In

sig.attr = 1
assert flipped_sig.attr == 1
flipped_sig.attr += 1
assert sig.attr == flipped_sig.attr == 2
```

This class implements the same methods, with the same functionality (other than the flipping of
the members’ data flow), as the [`Signature`](#amaranth.lib.wiring.Signature) class; see the documentation for that class
for details.

It is not possible to inherit from [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) and [`Signature.flip()`](#amaranth.lib.wiring.Signature.flip) must not
be overridden. If a [`Signature`](#amaranth.lib.wiring.Signature) subclass defines a method and this method is called on
a flipped instance of the subclass, it receives the flipped instance as its `self` argument.
To distinguish being called on the flipped instance from being called on the unflipped one, use
`isinstance(self, FlippedSignature)`:

```python
class SignatureKnowsWhenFlipped(wiring.Signature):
    @property
    def is_flipped(self):
        return isinstance(self, wiring.FlippedSignature)

sig = SignatureKnowsWhenFlipped({})
assert sig.is_flipped == False
assert sig.flip().is_flipped == True
```

#### flip()

Flips this signature back to the original one.

* **Returns:**
  `unflipped`
* **Return type:**
  [`Signature`](#amaranth.lib.wiring.Signature)

#### \_\_getattr_\_(name)

Retrieves attribute or method `name` of the unflipped signature.

Performs `getattr(unflipped, name)`, ensuring that, if `name` refers to a property
getter or a method, its `self` argument receives the *flipped* signature. A class
method’s `cls` argument receives the class of the *unflipped* signature, as usual.

#### \_\_setattr_\_(name, value)

Assigns attribute `name` of the unflipped signature to `value`.

Performs `setattr(unflipped, name, value)`, ensuring that, if `name` refers to
a property setter, its `self` argument receives the flipped signature.

#### \_\_delattr_\_(name)

Removes attribute `name` of the unflipped signature.

Performs `delattr(unflipped, name)`, ensuring that, if `name` refers to a property
deleter, its `self` argument receives the flipped signature.

### *class* amaranth.lib.wiring.SignatureMeta

Metaclass for [`Signature`](#amaranth.lib.wiring.Signature) that makes [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) its
‘virtual subclass’.

The object returned by [`Signature.flip()`](#amaranth.lib.wiring.Signature.flip) is an instance of [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature).
It implements all of the methods [`Signature`](#amaranth.lib.wiring.Signature) has, and for subclasses of
[`Signature`](#amaranth.lib.wiring.Signature), it implements all of the methods defined on the subclass as well.
This makes it effectively a subtype of [`Signature`](#amaranth.lib.wiring.Signature) (or a derived class of it), but this
relationship is not captured by the Python type system: [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) only has
[`object`](https://docs.python.org/3/library/functions.html#object) as its base class.

This metaclass extends [`issubclass()`](https://docs.python.org/3/library/functions.html#issubclass) and [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) so that they take into
account the subtyping relationship between [`Signature`](#amaranth.lib.wiring.Signature) and [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature),
described below.

#### \_\_subclasscheck_\_(subclass)

Override of `issubclass(cls, Signature)`.

In addition to the standard behavior of [`issubclass()`](https://docs.python.org/3/library/functions.html#issubclass), this override makes
[`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature) a subclass of [`Signature`](#amaranth.lib.wiring.Signature) or any of its subclasses.

#### \_\_instancecheck_\_(instance)

Override of `isinstance(obj, Signature)`.

In addition to the standard behavior of [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance), this override makes
`isinstance(obj, cls)` act as `isinstance(obj.flip(), cls)` where
`obj` is an instance of [`FlippedSignature`](#amaranth.lib.wiring.FlippedSignature).

## Interfaces

### *class* amaranth.lib.wiring.PureInterface(signature, \*, path=None, src_loc_at=0)

A helper for constructing ad-hoc interfaces.

The [`PureInterface`](#amaranth.lib.wiring.PureInterface) helper primarily exists to be used by the default implementation of
[`Signature.create()`](#amaranth.lib.wiring.Signature.create), but it can also be used in any other context where an interface
object needs to be created without the overhead of defining a class for it.

#### \_\_init_\_(signature, \*, path=None, src_loc_at=0)

Create attributes from a signature.

The sole method defined by this helper is its constructor, which only defines
the `self.signature` attribute as well as the attributes created from the signature
members:

```default
def __init__(self, signature, *, path):
    self.__dict__.update({
        "signature": signature,
        **signature.members.create(path=path)
    })
```

#### NOTE
This implementation can be copied and reused in interface objects that *do* include
custom behavior, if the signature serves as the source of truth for attributes
corresponding to its members. Although it is less repetitive, this approach can confuse
IDEs and type checkers.

### *class* amaranth.lib.wiring.FlippedInterface(unflipped)

An interface object, with its members’ directions flipped.

An instance of [`FlippedInterface`](#amaranth.lib.wiring.FlippedInterface) should only be created by calling [`flipped()`](#amaranth.lib.wiring.flipped),
which ensures that a `FlippedInterface(FlippedInterface(...))` object is never created.

This proxy wraps any interface object and forwards attribute and method access to the wrapped
interface object while flipping its signature and the values of any attributes corresponding to
interface members. It is useful because interface objects may be mutable or include custom
behavior, and explicitly keeping track of whether the interface object is flipped would be very
burdensome.

For example:

```python
intf = wiring.PureInterface(wiring.Signature({"foo": Out(1)}), path=())

flipped_intf = wiring.flipped(intf)
assert flipped_intf.signature.members["foo"].flow == In

intf.attr = 1
assert flipped_intf.attr == 1
flipped_intf.attr += 1
assert intf.attr == flipped_intf.attr == 2
```

It is not possible to inherit from [`FlippedInterface`](#amaranth.lib.wiring.FlippedInterface). If an interface object class
defines a method or a property and it is called on the flipped interface object, the method
receives the flipped interface object as its `self` argument. To distinguish being called
on the flipped interface object from being called on the unflipped one, use
`isinstance(self, FlippedInterface)`:

```python
class InterfaceKnowsWhenFlipped:
    signature = wiring.Signature({})

    @property
    def is_flipped(self):
        return isinstance(self, wiring.FlippedInterface)

intf = InterfaceKnowsWhenFlipped()
assert intf.is_flipped == False
assert wiring.flipped(intf).is_flipped == True
```

#### *property* signature

Signature of the flipped interface.

* **Returns:**
  `unflipped.signature.flip()`
* **Return type:**
  [`Signature`](#amaranth.lib.wiring.Signature)

#### \_\_eq_\_(other)

Compare this flipped interface with another.

* **Returns:**
  `True` if `other` is an instance `FlippedInterface(other_unflipped)` where
  `unflipped == other_unflipped`, `False` otherwise.
* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### \_\_getattr_\_(name)

Retrieves attribute or method `name` of the unflipped interface.

Performs `getattr(unflipped, name)`, with the following caveats:

1. If `name` refers to a signature member, the returned interface object is flipped.
2. If `name` refers to a property getter or a method, its `self` argument receives
   the *flipped* interface. A class method’s `cls` argument receives the class of
   the *unflipped* interface, as usual.

#### \_\_setattr_\_(name, value)

Assigns attribute `name` of the unflipped interface to `value`.

Performs `setattr(unflipped, name, value)`, with the following caveats:

1. If `name` refers to a signature member, the assigned interface object is flipped.
2. If `name` refers to a property setter, its `self` argument receives the flipped
   interface.

#### \_\_delattr_\_(name)

Removes attribute `name` of the unflipped interface.

Performs `delattr(unflipped, name)`, ensuring that, if `name` refers to a property
deleter, its `self` argument receives the flipped interface.

### amaranth.lib.wiring.flipped(interface)

Flip the data flow of the members of the interface object `interface`.

If an interface object is flipped twice, returns the original object:
`flipped(flipped(interface)) is interface`. Otherwise, wraps `interface` in
a [`FlippedInterface`](#amaranth.lib.wiring.FlippedInterface) proxy object that flips the directions of its members.

See the documentation for the [`FlippedInterface`](#amaranth.lib.wiring.FlippedInterface) class for a detailed discussion of how
this proxy object works.

## Making connections

### *exception* amaranth.lib.wiring.ConnectionError

Exception raised when the [`connect()`](#amaranth.lib.wiring.connect) function is requested to perform an impossible,
meaningless, or forbidden connection.

### amaranth.lib.wiring.connect(m, \*args, \*\*kwargs)

Connect interface objects to each other.

This function creates connections between ports of several interface objects. (Any number of
interface objects may be provided; in most cases it is two.)

The connections can be made only if all of the objects satisfy a number of requirements:

* Every interface object must have the same set of port members, and they must have the same
  [`dimensions`](#amaranth.lib.wiring.Member.dimensions).
* For each path, the port members of every interface object must have the same width and initial
  value (for port members corresponding to signals) or constant value (for port members
  corresponding to constants). Signedness may differ.
* For each path, at most one interface object must have the corresponding port member be
  an output.
* For a given path, if any of the interface objects has an input port member corresponding
  to a constant value, then the rest of the interface objects must have output port members
  corresponding to the same constant value.
* When connecting multiple interface objects, at least one connection must be made.

For example, if `obj1` is being connected to `obj2` and `obj3`, and `obj1.a.b`
is an output, then `obj2.a.b` and `obj2.a.b` must exist and be inputs. If `obj2.c`
is an input and its value is `Const(1)`, then `obj1.c` and `obj3.c` must be outputs
whose value is also `Const(1)`. If no ports besides `obj1.a.b` and `obj1.c` exist,
then no ports except for those two must exist on `obj2` and `obj3` either.

Once it is determined that the interface objects can be connected, this function performs
an equivalent of:

```default
m.d.comb += [
    in1.eq(out1),
    in2.eq(out1),
    ...
]
```

Where `out1` is an output and `in1`, `in2`, … are the inputs that have the same
path. (If no interface object has an output for a given path, **no connection at all** is made.)

The positions (within `args`) or names (within `kwargs`) of the arguments do not affect
the connections that are made. There is no difference in behavior between `connect(m, a, b)`
and `connect(m, b, a)` or `connect(m, arbiter=a, decoder=b)`. The names of the keyword
arguments serve only a documentation purpose: they clarify the diagnostic messages when
a connection cannot be made.

## Components

### *class* amaranth.lib.wiring.Component(\*args, src_loc_at=0, \*\*kwargs)

Base class for elaboratable interface objects.

A component is an `Elaboratable` whose interaction with other parts of the design is
defined by its signature. Most if not all elaboratables in idiomatic Amaranth code should be
components, as the signature clarifies the direction of data flow at their boundary. See
the [introduction to interfaces](#wiring-intro1) section for a practical guide to defining
and using components.

There are two ways to define a component. If all instances of a component have the same
signature, it can be defined using [variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation):

```python
class FixedComponent(wiring.Component):
    en: In(1)
    data: Out(8)
```

The variable annotations are collected by the constructor `Component.__init__()`. Only
public (not starting with `_`) annotations with [`In`](#amaranth.lib.wiring.Member) or [`Out`](#amaranth.lib.wiring.Member)
objects are considered; all other annotations are ignored under the assumption that they are
interpreted by some other tool.

It is possible to use inheritance to extend a component: the component’s signature is composed
from the variable annotations in the class that is being constructed as well as all of its
base classes. It is an error to have more than one variable annotation for the same attribute.

If different instances of a component may need to have different signatures, variable
annotations cannot be used. In this case, the constructor should be overridden, and
the computed signature members should be provided to the superclass constructor:

```python
class ParametricComponent(wiring.Component):
    def __init__(self, data_width):
        super().__init__({
            "en": In(1),
            "data": Out(data_width)
        })
```

It is also possible to pass a [`Signature`](#amaranth.lib.wiring.Signature) instance to the superclass constructor.

Aside from initializing the [`signature`](#amaranth.lib.wiring.Component.signature) attribute, the `Component.__init__()`
constructor creates attributes corresponding to all of the members defined in the signature.
If an attribute with the same name as that of a member already exists, an error is raied.

* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If the `signature` object is neither a [`Signature`](#amaranth.lib.wiring.Signature) nor a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict).
        If neither variable annotations nor the `signature` argument are present, or if
        both are present.
  * [**NameError**](https://docs.python.org/3/library/exceptions.html#NameError) – If a name conflict is detected between two variable annotations, or between a member
        and an existing attribute.

#### *property* signature

Signature of the component.

#### WARNING
Do not override this property. Once a component is constructed, its [`signature`](#amaranth.lib.wiring.Component.signature)
property must always return the same [`Signature`](#amaranth.lib.wiring.Signature) instance. The constructor
can be used to customize a component’s signature.

#### *property* metadata

Metadata attached to the component.

* **Return type:**
  [`ComponentMetadata`](#amaranth.lib.wiring.ComponentMetadata)

## Component metadata

### *exception* amaranth.lib.wiring.InvalidMetadata

Exception raised by [`ComponentMetadata.validate()`](#amaranth.lib.wiring.ComponentMetadata.validate) when the JSON representation of
a component’s metadata does not conform to its schema.

### *class* amaranth.lib.wiring.ComponentMetadata(origin)

Component metadata.

Component [metadata](meta.md#meta) describes the interface of a [`Component`](#amaranth.lib.wiring.Component) and can be
exported to JSON for interoperability with non-Amaranth tooling.

* **Parameters:**
  **origin** ([`Component`](#amaranth.lib.wiring.Component)) – Component described by this metadata instance.

#### schema *= { "$id": "https://amaranth-lang.org/schema/amaranth/0.5/component.json", ... }*

Schema of component metadata, expressed in the [JSON Schema](https://json-schema.org) language.

A copy of this schema can be retrieved [from amaranth-lang.org](https://amaranth-lang.org/schema/amaranth/0.5/component.json).

* **Type:**
  [`dict`](https://docs.python.org/3/library/stdtypes.html#dict)

#### *property* origin

Component described by this metadata.

* **Return type:**
  [`Component`](#amaranth.lib.wiring.Component)

#### *classmethod* validate(instance)

Validate a JSON representation of component metadata against [`schema`](#amaranth.lib.wiring.ComponentMetadata.schema).

This method does not validate annotations of the interface members, and consequently does
not make network requests.

* **Parameters:**
  **instance** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict)) – JSON representation to validate, either previously returned by [`as_json()`](#amaranth.lib.wiring.ComponentMetadata.as_json) or
  retrieved from an external source.
* **Raises:**
  [**InvalidMetadata**](#amaranth.lib.wiring.InvalidMetadata) – If `instance` doesn’t conform to [`schema`](#amaranth.lib.wiring.ComponentMetadata.schema).

#### as_json()

Translate to JSON.

* **Returns:**
  JSON representation of [`origin`](#amaranth.lib.wiring.ComponentMetadata.origin) that describes its interface members and includes
  their annotations.
* **Return type:**
  [`dict`](https://docs.python.org/3/library/stdtypes.html#dict)
