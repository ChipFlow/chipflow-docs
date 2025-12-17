# Enumerations

The [`amaranth.lib.enum`](#module-amaranth.lib.enum) module is a drop-in replacement for the standard [`enum`](https://docs.python.org/3/library/enum.html#module-enum) module that provides extended [`Enum`](#amaranth.lib.enum.Enum), [`IntEnum`](#amaranth.lib.enum.IntEnum), [`Flag`](#amaranth.lib.enum.Flag), and [`IntFlag`](#amaranth.lib.enum.IntFlag) classes with the ability to specify a shape explicitly.

A shape can be specified for an enumeration with the `shape=` keyword argument:

<!-- from amaranth import * -->
```python
from amaranth.lib import enum

class Funct(enum.Enum, shape=4):
    ADD = 0
    SUB = 1
    MUL = 2
```

```pycon
>>> Shape.cast(Funct)
unsigned(4)
>>> Value.cast(Funct.ADD)
(const 4'd0)
```

Any [constant-castable](../guide.md#lang-constcasting) expression can be used as the value of a member:

```python
class Op(enum.Enum, shape=1):
    REG = 0
    IMM = 1

class Instr(enum.Enum, shape=5):
    ADD  = Cat(Funct.ADD, Op.REG)
    ADDI = Cat(Funct.ADD, Op.IMM)
    SUB  = Cat(Funct.SUB, Op.REG)
    SUBI = Cat(Funct.SUB, Op.IMM)
    ...
```

```pycon
>>> Instr.SUBI
<Instr.SUBI: 17>
```

The `shape=` argument is optional. If not specified, classes from this module behave exactly the same as classes from the standard [`enum`](https://docs.python.org/3/library/enum.html#module-enum) module, and likewise, this module re-exports everything exported by the standard [`enum`](https://docs.python.org/3/library/enum.html#module-enum) module.

```python
import amaranth.lib.enum

class NormalEnum(amaranth.lib.enum.Enum):
    SPAM = 0
    HAM  = 1
```

In this way, this module is a drop-in replacement for the standard [`enum`](https://docs.python.org/3/library/enum.html#module-enum) module, and in an Amaranth project, all `import enum` statements may be replaced with `from amaranth.lib import enum`.

Signals with [`Enum`](#amaranth.lib.enum.Enum) or [`Flag`](#amaranth.lib.enum.Flag) based shape are automatically wrapped in the [`EnumView`](#amaranth.lib.enum.EnumView) or [`FlagView`](#amaranth.lib.enum.FlagView) value-like wrappers, which ensure type safety. Any [value-like](../guide.md#lang-valuelike) can also be explicitly wrapped in a view class by casting it to the enum type:

```pycon
>>> a = Signal(Funct)
>>> b = Signal(Op)
>>> type(a)
<class 'amaranth.lib.enum.EnumView'>
>>> a == b
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: an EnumView can only be compared to value or other EnumView of the same enum type
>>> c = Signal(4)
>>> type(Funct(c))
<class 'amaranth.lib.enum.EnumView'>
```

Like the standard Python [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) and [`enum.IntFlag`](https://docs.python.org/3/library/enum.html#enum.IntFlag) classes, the Amaranth [`IntEnum`](#amaranth.lib.enum.IntEnum) and [`IntFlag`](#amaranth.lib.enum.IntFlag) classes are loosely typed and will not be subject to wrapping in view classes:

```python
class TransparentEnum(enum.IntEnum, shape=unsigned(4)):
    FOO = 0
    BAR = 1
```

```pycon
>>> a = Signal(TransparentEnum)
>>> type(a) is Signal
True
```

It is also possible to define a custom view class for a given enum:

```python
class InstrView(enum.EnumView):
    def has_immediate(self):
        return (self == Instr.ADDI) | (self == Instr.SUBI)

class Instr(enum.Enum, shape=5, view_class=InstrView):
    ADD  = Cat(Funct.ADD, Op.REG)
    ADDI = Cat(Funct.ADD, Op.IMM)
    SUB  = Cat(Funct.SUB, Op.REG)
    SUBI = Cat(Funct.SUB, Op.IMM)
```

```pycon
>>> a = Signal(Instr)
>>> type(a)
<class 'InstrView'>
>>> a.has_immediate()
(| (== (sig a) (const 5'd16)) (== (sig a) (const 5'd17)))
```

## Metaclass

### *class* amaranth.lib.enum.EnumType

Subclass of the standard [`enum.EnumType`](https://docs.python.org/3/library/enum.html#enum.EnumType) that implements the `ShapeCastable`
protocol.

This metaclass provides the [`as_shape()`](#amaranth.lib.enum.EnumType.as_shape) method, making its instances
[shape-like](../guide.md#lang-shapelike), and accepts a `shape=` keyword argument
to specify a shape explicitly. Other than this, it acts the same as the standard
[`enum.EnumType`](https://docs.python.org/3/library/enum.html#enum.EnumType) class; if the `shape=` argument is not specified and
[`as_shape()`](#amaranth.lib.enum.EnumType.as_shape) is never called, it places no restrictions on the enumeration class
or the values of its members.

When a [value-like](../guide.md#lang-valuelike) is cast to an enum type that is an instance
of this metaclass, it can be automatically wrapped in a view class. A custom view class
can be specified by passing the `view_class=` keyword argument when creating the enum class.

#### as_shape()

Cast this enumeration to a shape.

* **Returns:**
  Explicitly provided shape. If not provided, returns the result of shape-casting
  this class [as a standard Python enumeration](../guide.md#lang-shapeenum).
* **Return type:**
  `Shape`
* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If the enumeration has neither an explicitly provided shape nor any members.

#### \_\_call_\_(value, \*args, \*\*kwargs)

Cast the value to this enum type.

When given an integer constant, it returns the corresponding enum value, like a standard
Python enumeration.

When given a [value-like](../guide.md#lang-valuelike), it is cast to a value, then wrapped
in the `view_class` specified for this enum type ([`EnumView`](#amaranth.lib.enum.EnumView) for [`Enum`](#amaranth.lib.enum.Enum),
[`FlagView`](#amaranth.lib.enum.FlagView) for [`Flag`](#amaranth.lib.enum.Flag), or a custom user-defined class). If the type has no
`view_class` (like [`IntEnum`](#amaranth.lib.enum.IntEnum) or [`IntFlag`](#amaranth.lib.enum.IntFlag)), a plain
`Value` is returned.

* **Returns:**
  * *instance of itself* – For integer values, or instances of itself.
  * [`EnumView`](#amaranth.lib.enum.EnumView) or its subclass – For value-castables, as defined by the `view_class` keyword argument.
  * `Value` – For value-castables, when a view class is not specified for this enum.

## Base classes

### *class* amaranth.lib.enum.Enum

Subclass of the standard [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) that has [`EnumType`](#amaranth.lib.enum.EnumType) as
its metaclass and [`EnumView`](#amaranth.lib.enum.EnumView) as its view class.

### *class* amaranth.lib.enum.IntEnum

Subclass of the standard [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) that has [`EnumType`](#amaranth.lib.enum.EnumType) as
its metaclass.

### *class* amaranth.lib.enum.Flag

Subclass of the standard [`enum.Flag`](https://docs.python.org/3/library/enum.html#enum.Flag) that has [`EnumType`](#amaranth.lib.enum.EnumType) as
its metaclass and [`FlagView`](#amaranth.lib.enum.FlagView) as its view class.

### *class* amaranth.lib.enum.IntFlag

Subclass of the standard [`enum.IntFlag`](https://docs.python.org/3/library/enum.html#enum.IntFlag) that has [`EnumType`](#amaranth.lib.enum.EnumType) as
its metaclass.

## View classes

### *class* amaranth.lib.enum.EnumView

The view class used for [`Enum`](#amaranth.lib.enum.Enum).

Wraps a `Value` and only allows type-safe operations. The only operators allowed are
equality comparisons (`==` and `!=`) with another [`EnumView`](#amaranth.lib.enum.EnumView) of the same enum type.

#### \_\_init_\_(enum, target)

Constructs a view with the given enum type and target
(a [value-like](../guide.md#lang-valuelike)).

#### shape()

Returns the underlying enum type.

#### as_value()

Returns the underlying value.

#### eq(other)

Assign to the underlying value.

* **Returns:**
  `self.as_value().eq(other)`
* **Return type:**
  `Assign`

#### \_\_eq_\_(other)

Compares the underlying value for equality.

The other operand has to be either another [`EnumView`](#amaranth.lib.enum.EnumView) with the same enum type, or
a plain value of the underlying enum.

* **Returns:**
  The result of the equality comparison, as a single-bit value.
* **Return type:**
  `Value`

### *class* amaranth.lib.enum.FlagView

The view class used for [`Flag`](#amaranth.lib.enum.Flag).

In addition to the operations allowed by [`EnumView`](#amaranth.lib.enum.EnumView), it allows bitwise operations among
values of the same enum type.

#### \_\_invert_\_()

Inverts all flags in this value and returns another [`FlagView`](#amaranth.lib.enum.FlagView).

Note that this is not equivalent to applying bitwise negation to the underlying value:
just like the Python [`enum.Flag`](https://docs.python.org/3/library/enum.html#enum.Flag) class, only bits corresponding to flags actually
defined in the enumeration are included in the result.

* **Return type:**
  [`FlagView`](#amaranth.lib.enum.FlagView)

#### \_\_and_\_(other)

Performs a bitwise AND and returns another [`FlagView`](#amaranth.lib.enum.FlagView).

The other operand has to be either another [`FlagView`](#amaranth.lib.enum.FlagView) of the same enum type, or
a plain value of the underlying enum type.

* **Return type:**
  [`FlagView`](#amaranth.lib.enum.FlagView)

#### \_\_or_\_(other)

Performs a bitwise OR and returns another [`FlagView`](#amaranth.lib.enum.FlagView).

The other operand has to be either another [`FlagView`](#amaranth.lib.enum.FlagView) of the same enum type, or
a plain value of the underlying enum type.

* **Return type:**
  [`FlagView`](#amaranth.lib.enum.FlagView)

#### \_\_xor_\_(other)

Performs a bitwise XOR and returns another [`FlagView`](#amaranth.lib.enum.FlagView).

The other operand has to be either another [`FlagView`](#amaranth.lib.enum.FlagView) of the same enum type, or
a plain value of the underlying enum type.

* **Return type:**
  [`FlagView`](#amaranth.lib.enum.FlagView)

#### \_\_rand_\_(other)

Performs a bitwise AND and returns another [`FlagView`](#amaranth.lib.enum.FlagView).

The other operand has to be either another [`FlagView`](#amaranth.lib.enum.FlagView) of the same enum type, or
a plain value of the underlying enum type.

* **Return type:**
  [`FlagView`](#amaranth.lib.enum.FlagView)

#### \_\_ror_\_(other)

Performs a bitwise OR and returns another [`FlagView`](#amaranth.lib.enum.FlagView).

The other operand has to be either another [`FlagView`](#amaranth.lib.enum.FlagView) of the same enum type, or
a plain value of the underlying enum type.

* **Return type:**
  [`FlagView`](#amaranth.lib.enum.FlagView)

#### \_\_rxor_\_(other)

Performs a bitwise XOR and returns another [`FlagView`](#amaranth.lib.enum.FlagView).

The other operand has to be either another [`FlagView`](#amaranth.lib.enum.FlagView) of the same enum type, or
a plain value of the underlying enum type.

* **Return type:**
  [`FlagView`](#amaranth.lib.enum.FlagView)
