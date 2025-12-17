# Language reference

#### WARNING
This reference is a work in progress and is seriously incomplete!

While the wording below states that anything not described in this document isn’t covered by the backwards compatibility guarantee, this should be ignored until the document is complete and this warning is removed.

This reference describes the Python classes that underlie the Amaranth language’s syntax. It assumes familiarity with the language guide <guide>.

<a id="lang-stability"></a>

## Backwards compatibility

As part of the Amaranth backwards compatibility guarantee, any behaviors described in this document will not change from a version to another without at least one version including a warning about the impending change. Any nontrivial change to these behaviors must also go through the public review as a part of the [Amaranth Request for Comments process](https://amaranth-lang.org/rfcs/).

Conversely, any behavior not documented here is subject to change at any time with or without notice, and any names under the [`amaranth.hdl`](#module-amaranth.hdl) module that are not explicitly included in this document, even if they do not begin with an underscore, are internal to the implementation of the language.

<a id="lang-importing"></a>

## Importing syntax

There are two ways to import the Amaranth syntax into a Python file: by importing the [prelude](guide.md#lang-prelude) or by importing individual names from the [`amaranth.hdl`](#module-amaranth.hdl) module. Since the prelude is kept small and rarely extended to avoid breaking downstream code that uses a glob import, there are some names that are only exported from the [`amaranth.hdl`](#module-amaranth.hdl) module. The following three snippets are equivalent:

```python
from amaranth import *

m = Module()
```

```python
import amaranth as am

m = am.Module()
```

```python
from amaranth.hdl import Module

m = Module()
```

The prelude exports exactly the following names:

<!-- must be kept in sync with amaranth/__init__.py! -->
* [`Shape`](#amaranth.hdl.Shape)
* [`unsigned()`](#amaranth.hdl.unsigned)
* [`signed()`](#amaranth.hdl.signed)
* [`Value`](#amaranth.hdl.Value)
* `Const`
* `C()`
* `Mux()`
* `Cat()`
* `Array`
* `Signal`
* `ClockSignal`
* `ResetSignal`
* `Format`
* `Print`
* `Assert()`
* `Module`
* `ClockDomain`
* `Elaboratable`
* `Fragment`
* `Instance`
* `Memory`
* `Record` (deprecated)
* `DomainRenamer`
* `ResetInserter`
* `EnableInserter`

<a id="lang-srcloc"></a>

## Source locations

Many functions and methods in Amaranth take the `src_loc_at=0` keyword argument. These language constructs may inspect the call stack to determine the file and line of its call site, which will be used to annotate generated code when a netlist is generated or to improve diagnostic messages.

Some call sites are not relevant for an Amaranth designer; e.g. when an Amaranth language construct is called from a user-defined utility function, the source location of the call site within this utility function is usually not interesting to the designer. In these cases, one or more levels of function calls can be removed from consideration using the `src_loc_at` argument as follows (using [`Shape.cast()`](#amaranth.hdl.Shape.cast) to demonstrate the concept):

```python
def my_shape_cast(obj, *, src_loc_at=0):
    ... # additionally process `obj`...
    return Shape.cast(obj, src_loc_at=1 + src_loc_at)
```

The number `1` corresponds to the number of call stack frames that should be skipped.

## Shapes

See also the introduction to [shapes](guide.md#lang-shapes) and [casting from shape-like objects](guide.md#lang-shapelike) in the language guide.

### *class* amaranth.hdl.Shape(width=1, signed=False)

Bit width and signedness of a [`Value`](#amaranth.hdl.Value).

A [`Shape`](#amaranth.hdl.Shape) can be obtained by:

* constructing with explicit bit width and signedness;
* using the [`signed()`](#amaranth.hdl.signed) and [`unsigned()`](#amaranth.hdl.unsigned) aliases if the signedness is known upfront;
* casting from a variety of objects using the [`cast()`](#amaranth.hdl.Shape.cast) method.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – The number of bits in the representation of a value. This includes the sign bit for signed
    values. Cannot be zero if the value is signed.
  * **signed** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether the value is signed. Signed values use the
    [two’s complement](https://en.wikipedia.org/wiki/Two's_complement) representation.

#### *static* cast(obj, \*, src_loc_at=0)

Cast `obj` to a shape.

Many [shape-like](guide.md#lang-shapelike) objects can be cast to a shape:

* a [`Shape`](#amaranth.hdl.Shape), where the result is itself;
* an [`int`](https://docs.python.org/3/library/functions.html#int), where the result is [`unsigned(obj)`](#amaranth.hdl.unsigned);
* a [`range`](https://docs.python.org/3/library/stdtypes.html#range), where the result has minimal width required to represent all elements
  of the range, and is signed if any element of the range is signed;
* an [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) whose members are all [constant-castable](guide.md#lang-constcasting)
  or [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum), where the result is wide enough to represent any member of
  the enumeration, and is signed if any member of the enumeration is signed;
* a [`ShapeCastable`](#amaranth.hdl.ShapeCastable) object, where the result is obtained by repeatedly calling
  [`obj.as_shape()`](#amaranth.hdl.ShapeCastable.as_shape).

* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `obj` cannot be converted to a [`Shape`](#amaranth.hdl.Shape).
  * [**RecursionError**](https://docs.python.org/3/library/exceptions.html#RecursionError) – If `obj` is a [`ShapeCastable`](#amaranth.hdl.ShapeCastable) object that casts to itself.

#### \_\_repr_\_()

Python code that creates this shape.

Returns `f"signed({self.width})"` or `f"unsigned({self.width})"`.

### amaranth.hdl.unsigned(width)

Returns `Shape(width, signed=False)`.

### amaranth.hdl.signed(width)

Returns `Shape(width, signed=True)`.

### *class* amaranth.hdl.ShapeCastable

Interface class for objects that can be cast to a [`Shape`](#amaranth.hdl.Shape).

Shapes of values in the Amaranth language are specified using [shape-like objects](guide.md#lang-shapelike). Inheriting a class from [`ShapeCastable`](#amaranth.hdl.ShapeCastable) and implementing all of
the methods described below adds instances of that class to the list of shape-like objects
recognized by the [`Shape.cast()`](#amaranth.hdl.Shape.cast) method. This is a part of the mechanism for seamlessly
extending the Amaranth language in third-party code.

To illustrate their purpose, consider constructing a signal from a shape-castable object
`shape_castable`:

```default
value_like = Signal(shape_castable, init=initializer)
```

The code above is equivalent to:

```default
value_like = shape_castable(Signal(
    shape_castable.as_shape(),
    init=shape_castable.const(initializer)
))
```

Note that the `shape_castable(x)` syntax performs `shape_castable.__call__(x)`.

#### as_shape()

Convert `self` to a [shape-like object](guide.md#lang-shapelike).

This method is called by the Amaranth language to convert `self` to a concrete
[`Shape`](#amaranth.hdl.Shape). It will usually return a [`Shape`](#amaranth.hdl.Shape) object, but it may also return
another shape-like object to delegate its functionality.

This method must be idempotent: when called twice on the same object, the result must be
exactly the same.

This method may also be called by code that is not a part of the Amaranth language.

* **Return type:**
  Any other object recognized by [`Shape.cast()`](#amaranth.hdl.Shape.cast).
* **Raises:**
  [**Exception**](https://docs.python.org/3/library/exceptions.html#Exception) – When the conversion cannot be done. This exception must be propagated by callers
      (except when checking whether an object is shape-castable or not), either directly
      or as a cause of another exception.

#### const(obj)

Convert a constant initializer `obj` to its value representation.

This method is called by the Amaranth language to convert `obj`, which may be an
arbitrary Python object, to a concrete [value-like object](guide.md#lang-valuelike).
The object `obj` will usually be a Python literal that can conveniently represent
a constant value whose shape is described by `self`. While not constrained here,
the result will usually be an instance of the return type of [`__call__()`](#amaranth.hdl.ShapeCastable.__call__).

For any `obj`, the following condition must hold:

```default
Shape.cast(self) == Const.cast(self.const(obj)).shape()
```

This method may also be called by code that is not a part of the Amaranth language.

* **Return type:**
  A [value-like object](guide.md#lang-valuelike) that is [constant-castable](guide.md#lang-constcasting).
* **Raises:**
  [**Exception**](https://docs.python.org/3/library/exceptions.html#Exception) – When the conversion cannot be done. This exception must be propagated by callers,
      either directly or as a cause of another exception. While not constrained here,
      usually the exception class will be [`TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError) or [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError).

#### from_bits(raw)

Lift a bit pattern to a higher-level representation.

This method is called by the Amaranth language to lift `raw`, which is an [`int`](https://docs.python.org/3/library/functions.html#int),
to a higher-level representation, which may be any object accepted by [`const()`](#amaranth.hdl.ShapeCastable.const).
Most importantly, the simulator calls this method when the value of a shape-castable
object is retrieved.

For any valid bit pattern `raw`, the following condition must hold:

```default
Const.cast(self.const(self.from_bits(raw))).value == raw
```

While [`const()`](#amaranth.hdl.ShapeCastable.const) will usually return an Amaranth value or a custom value-castable
object that is convenient to use while constructing the design, this method will usually
return a Python object that is convenient to use while simulating the design. While not
constrained here, these objects should have the same type whenever feasible.

This method may also be called by code that is not a part of the Amaranth language.

* **Return type:**
  unspecified type
* **Raises:**
  [**Exception**](https://docs.python.org/3/library/exceptions.html#Exception) – When the bit pattern isn’t valid. This exception must be propagated by callers,
      either directly or as a cause of another exception. While not constrained here,
      usually the exception class will be [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError).

#### \_\_call_\_(obj)

Lift a [value-like object](guide.md#lang-valuelike) to a higher-level representation.

This method is called by the Amaranth language to lift `obj`, which may be any
[value-like object](guide.md#lang-valuelike) whose shape equals `Shape.cast(self)`,
to a higher-level representation, which may be any value-like object with the same
shape. While not constrained here, usually a [`ShapeCastable`](#amaranth.hdl.ShapeCastable) implementation will
be paired with a [`ValueCastable`](#amaranth.hdl.ValueCastable) implementation, and this method will return
an instance of the latter.

If `obj` is not as described above, this interface does not constrain the behavior
of this method. This may be used to implement another call-based protocol at the same
time.

For any compliant `obj`, the following condition must hold:

```default
Value.cast(self(obj)) == Value.cast(obj)
```

This method may also be called by code that is not a part of the Amaranth language.

* **Return type:**
  A [value-like object](guide.md#lang-valuelike).

#### format(obj, spec)

Format a value.

This method is called by the Amaranth language to implement formatting for custom
shapes. Whenever `"{obj:spec}"` is encountered by `Format`, and `obj`
has a custom shape that has a [`format()`](#amaranth.hdl.ShapeCastable.format) method, `obj.shape().format(obj, "spec")`
is called, and the format specifier is replaced with the result.

The default [`format()`](#amaranth.hdl.ShapeCastable.format) implementation is:

```default
def format(self, obj, spec):
    return Format(f"{{:{spec}}}", Value.cast(obj))
```

* **Return type:**
  `Format`

### *class* amaranth.hdl.ShapeLike

Abstract class representing all objects that can be cast to a [`Shape`](#amaranth.hdl.Shape).

`issubclass(cls, ShapeLike)` returns `True` for:

* [`Shape`](#amaranth.hdl.Shape);
* [`ShapeCastable`](#amaranth.hdl.ShapeCastable) and its subclasses;
* [`int`](https://docs.python.org/3/library/functions.html#int) and its subclasses;
* [`range`](https://docs.python.org/3/library/stdtypes.html#range) and its subclasses;
* `enum.EnumMeta` and its subclasses;
* [`ShapeLike`](#amaranth.hdl.ShapeLike) itself.

`isinstance(obj, ShapeLike)` returns `True` for:

* [`Shape`](#amaranth.hdl.Shape) instances;
* [`ShapeCastable`](#amaranth.hdl.ShapeCastable) instances;
* non-negative [`int`](https://docs.python.org/3/library/functions.html#int) values;
* [`range`](https://docs.python.org/3/library/stdtypes.html#range) instances;
* [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) subclasses where all values are [value-like objects](guide.md#lang-valuelike).

This class cannot be instantiated or subclassed. It can only be used for checking types of
objects.

## Values

See also the introduction to [values](guide.md#lang-values) and [casting from value-like objects](guide.md#lang-valuelike) in the language guide.

### *class* amaranth.hdl.Value(\*, src_loc_at=0)

Abstract representation of a bit pattern computed in a circuit.

The Amaranth language gives Python code the ability to create a circuit netlist by manipulating
objects representing the computations within that circuit. The [`Value`](#amaranth.hdl.Value) class represents
the bit pattern of a constant, or of a circuit input or output, or within a storage element; or
the result of an arithmetic, logical, or bit container operation.

Operations on this class interpret this bit pattern either as an integer, which can be signed
or unsigned depending on the value’s [`shape()`](#amaranth.hdl.Value.shape), or as a bit container. In either case,
the semantics of operations that implement Python’s syntax, like `+` (also known as
[`__add__()`](#amaranth.hdl.Value.__add__)), are identical to the corresponding operation on a Python [`int`](https://docs.python.org/3/library/functions.html#int) (or on
a Python sequence container). The bitwise inversion `~` (also known as [`__invert__()`](#amaranth.hdl.Value.__invert__))
is the sole exception to this rule.

Data that is not conveniently representable by a single integer or a bit container can be
represented by wrapping a [`Value`](#amaranth.hdl.Value) in a [`ValueCastable`](#amaranth.hdl.ValueCastable) subclass that provides
domain-specific operations. It is possible to extend Amaranth in third-party code using
value-castable objects, and the Amaranth standard library provides several built-in ones:

* [`amaranth.lib.enum`](stdlib/enum.md#module-amaranth.lib.enum) classes are a drop-in replacement for the standard Python
  [`enum`](https://docs.python.org/3/library/enum.html#module-enum) classes that can be defined with an Amaranth shape;
* [`amaranth.lib.data`](stdlib/data.md#module-amaranth.lib.data) classes allow defining complex data structures such as structures
  and unions.

Operations on [`Value`](#amaranth.hdl.Value) instances return another [`Value`](#amaranth.hdl.Value) instance. Unless the exact
type and value of the result is explicitly specified below, it should be considered opaque, and
may change without notice between Amaranth releases as long as the semantics remains the same.

#### NOTE
In each of the descriptions below, you will see a line similar to:

**Return type:** [`Value`](#amaranth.hdl.Value), `unsigned(1)`, [assignable](guide.md#lang-assignable)

The first part ([`Value`](#amaranth.hdl.Value)) indicates that the returned object’s type is a subclass
of [`Value`](#amaranth.hdl.Value). The second part (`unsigned(1)`) describes the shape of that value.
The third part, if present, indicates that the value is assignable if `self` is
assignable.

#### *static* cast(obj)

Cast `obj` to an Amaranth value.

Many [value-like](guide.md#lang-valuelike) objects can be cast to a value:

* a [`Value`](#amaranth.hdl.Value) instance, where the result is itself;
* a [`bool`](#amaranth.hdl.Value.bool) or [`int`](https://docs.python.org/3/library/functions.html#int) instance, where the result is `Const(obj)`;
* an [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) instance, or a [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) instance whose members are
  all integers, where the result is a `Const(obj, enum_shape)` where `enum_shape`
  is a shape that can represent every member of the enumeration;
* a [`ValueCastable`](#amaranth.hdl.ValueCastable) instance, where the result is obtained by repeatedly calling
  [`obj.as_value()`](#amaranth.hdl.ValueCastable.as_value).

* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `obj` cannot be converted to a [`Value`](#amaranth.hdl.Value).
  * [**RecursionError**](https://docs.python.org/3/library/exceptions.html#RecursionError) – If `obj` is a [`ValueCastable`](#amaranth.hdl.ValueCastable) object that casts to itself.

#### *abstract* shape()

Shape of `self`.

* **Return type:**
  [shape-like object](guide.md#lang-shapelike)

#### as_unsigned()

Reinterpretation as an unsigned value.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(len(self))`, [assignable](guide.md#lang-assignable)

#### as_signed()

Reinterpretation as a signed value.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `signed(len(self))`, [assignable](guide.md#lang-assignable)
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `len(self) == 0`.

#### \_\_bool_\_()

Forbidden conversion to boolean.

Python uses this operator for its built-in semantics, e.g. `if`, and requires it to
return a [`bool`](#amaranth.hdl.Value.bool). Since this is not possible for Amaranth values, this operator
always raises an exception.

* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – Always.

#### bool()

Conversion to boolean.

Returns the same value as [`any()`](#amaranth.hdl.Value.any), but should be used where `self` is semantically
a number.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_pos_\_()

Unary position, `+self`.

* **Returns:**
  `self`
* **Return type:**
  [`Value`](#amaranth.hdl.Value), `self.shape()`

#### \_\_neg_\_()

Unary negation, `-self`.

<!-- >>> C(-1).value, C(-1).shape()
-1, signed(1)
>>> C(-(-1), signed(1)).value # overflows
-1 -->
* **Return type:**
  [`Value`](#amaranth.hdl.Value), `signed(len(self) + 1)`

#### \_\_add_\_(other)

Addition, `self + other`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(max(self.width(), other.width()) + 1)` – If both `self` and `other` are unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width() + 1, other.width()) + 1)` – If `self` is unsigned and `other` is signed.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width() + 1) + 1)` – If `self` is signed and `other` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width()) + 1)` – If both `self` and `other` are unsigned.

#### \_\_radd_\_(other)

Addition, `other + self` (reflected).

Like [`__add__()`](#amaranth.hdl.Value.__add__), with operands swapped.

#### \_\_sub_\_(other)

Subtraction, `self - other`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width()) + 1)` – If both `self` and `other` are unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width() + 1, other.width()) + 1)` – If `self` is unsigned and `other` is signed.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width() + 1) + 1)` – If `self` is signed and `other` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width()) + 1)` – If both `self` and `other` are unsigned.
* **Return type:**
  [`Value`](#amaranth.hdl.Value)

#### \_\_rsub_\_(other)

Subtraction, `other - self` (reflected).

Like [`__sub__()`](#amaranth.hdl.Value.__sub__), with operands swapped.

#### \_\_mul_\_(other)

Multiplication, `self * other`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(len(self) + len(other))` – If both `self` and `other` are unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(len(self) + len(other))` – If either `self` or `other` are signed.

#### \_\_rmul_\_(other)

Multiplication, `other * self` (reflected).

Like [`__mul__()`](#amaranth.hdl.Value.__mul__), with operands swapped.

#### \_\_floordiv_\_(other)

Flooring division, `self // other`.

If `other` is zero, the result of this operation is zero.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(len(self))` – If both `self` and `other` are unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(len(self) + 1)` – If `self` is unsigned and `other` is signed.
  * [`Value`](#amaranth.hdl.Value), `signed(len(self))` – If `self` is signed and `other` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(len(self) + 1)` – If both `self` and `other` are signed.

#### \_\_rfloordiv_\_(other)

Flooring division, `other // self` (reflected).

If `self` is zero, the result of this operation is zero.

Like [`__floordiv__()`](#amaranth.hdl.Value.__floordiv__), with operands swapped.

#### \_\_mod_\_(other)

Flooring modulo or remainder, `self % other`.

If `other` is zero, the result of this operation is zero.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `other.shape()`

#### \_\_rmod_\_(other)

Flooring modulo or remainder, `other % self` (reflected).

Like [`__mod__()`](#amaranth.hdl.Value.__mod__), with operands swapped.

#### \_\_eq_\_(other)

Equality comparison, `self == other`.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_ne_\_(other)

Inequality comparison, `self != other`.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_lt_\_(other)

Less than comparison, `self < other`.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_le_\_(other)

Less than or equals comparison, `self <= other`.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_gt_\_(other)

Greater than comparison, `self > other`.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_ge_\_(other)

Greater than or equals comparison, `self >= other`.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_abs_\_()

Absolute value, `abs(self)`.

<!-- >>> abs(C(-1)).shape()
unsigned(1)
>>> C(1).shape()
unsigned(1) -->
* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(len(self))`

#### \_\_invert_\_()

Bitwise NOT, `~self`.

The shape of the result is the same as the shape of `self`, even for unsigned values.

#### WARNING
In Python, `~0` equals `-1`. In Amaranth, `~C(0)` equals `C(1)`.
This is the only case where an Amaranth operator deviates from the Python operator
with the same name.

This deviation is necessary because Python does not allow overriding the logical
`and`, `or`, and `not` operators. Amaranth uses `&`, `|`, and
`~` instead; if it wasn’t the case that `~C(0) == C(1)`, that would have
been impossible.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `self.shape()`

#### \_\_and_\_(other)

Bitwise AND, `self & other`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(max(self.width(), other.width()))` – If both `self` and `other` are unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width() + 1, other.width()))` – If `self` is unsigned and `other` is signed.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width() + 1))` – If `self` is signed and `other` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width()))` – If both `self` and `other` are unsigned.

#### \_\_rand_\_(other)

Bitwise AND, `other & self`.

Like [`__and__()`](#amaranth.hdl.Value.__and__), with operands swapped.

#### all()

Reduction AND; are all bits `1`?

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_or_\_(other)

Bitwise OR, `self | other`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(max(self.width(), other.width()))` – If both `self` and `other` are unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width() + 1, other.width()))` – If `self` is unsigned and `other` is signed.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width() + 1))` – If `self` is signed and `other` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width()))` – If both `self` and `other` are unsigned.

#### \_\_ror_\_(other)

Bitwise OR, `other | self`.

Like [`__or__()`](#amaranth.hdl.Value.__or__), with operands swapped.

#### any()

Reduction OR; is any bit `1`?

Performs the same operation as [`bool()`](#amaranth.hdl.Value.bool), but should be used where `self` is
semantically a bit sequence.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_xor_\_(other)

Bitwise XOR, `self ^ other`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(max(self.width(), other.width()))` – If both `self` and `other` are unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width() + 1, other.width()))` – If `self` is unsigned and `other` is signed.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width() + 1))` – If `self` is signed and `other` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(self.width(), other.width()))` – If both `self` and `other` are unsigned.

#### \_\_rxor_\_(other)

Bitwise XOR, `other ^ self`.

Like [`__xor__()`](#amaranth.hdl.Value.__xor__), with operands swapped.

#### xor()

Reduction XOR; are an odd amount of bits `1`?

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`

#### \_\_lshift_\_(other)

Left shift by variable amount, `self << other`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(len(self) + 2 ** len(other) - 1)` – If `self` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(len(self) + 2 ** len(other) - 1)` – If `self` is signed.
* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `other` is signed.

#### \_\_rlshift_\_(other)

Left shift by variable amount, `other << self`.

Like [`__lshift__()`](#amaranth.hdl.Value.__lshift__), with operands swapped.

#### shift_left(amount)

Left shift by constant amount.

If `amount < 0`, performs the same operation as `self.shift_right(-amount)`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(max(len(self) + amount, 0))` – If `self` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(len(self) + amount, 1))` – If `self` is signed.

#### rotate_left(amount)

Left rotate by constant amount.

If `amount < 0`, performs the same operation as `self.rotate_right(-amount)`.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(len(self))`, [assignable](guide.md#lang-assignable)

#### \_\_rshift_\_(other)

Right shift by variable amount, `self >> other`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(len(self))` – If `self` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(len(self))` – If `self` is signed.
* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `other` is signed.

#### \_\_rrshift_\_(other)

Right shift by variable amount, `other >> self`.

Like [`__rshift__()`](#amaranth.hdl.Value.__rshift__), with operands swapped.

#### shift_right(amount)

Right shift by constant amount.

If `amount < 0`, performs the same operation as `self.shift_left(-amount)`.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(max(len(self) - amount, 0))` – If `self` is unsigned.
  * [`Value`](#amaranth.hdl.Value), `signed(max(len(self) - amount, 1))` – If `self` is signed.

#### rotate_right(amount)

Right rotate by constant amount.

If `amount < 0`, performs the same operation as `self.rotate_left(-amount)`.

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(len(self))`, [assignable](guide.md#lang-assignable)

#### \_\_len_\_()

Bit width of `self`.

* **Returns:**
  `self.shape().width`
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### \_\_getitem_\_(key)

Bit slicing.

Selects a constant-width, constant-offset part of `self`. All three slicing syntaxes
(`self[i]`, `self[i:j]`, and `self[i:j:k]`) as well as negative indices are
supported. Like with other Python containers, out-of-bounds indices are trimmed to
the bounds of `self`.

To select a variable-offset part of `self`, use [`bit_select()`](#amaranth.hdl.Value.bit_select) or
[`word_select()`](#amaranth.hdl.Value.word_select) instead.

* **Returns:**
  * [`Value`](#amaranth.hdl.Value), `unsigned(1)`, [assignable](guide.md#lang-assignable) – If `key` is an [`int`](https://docs.python.org/3/library/functions.html#int).
  * [`Value`](#amaranth.hdl.Value), `unsigned(j - i)`, [assignable](guide.md#lang-assignable) – If `key` is a slice `i:j` where `i` and `j` are [`int`](https://docs.python.org/3/library/functions.html#int)s.
  * [`Value`](#amaranth.hdl.Value), `unsigned(len(range(*slice(i, j, k).indices(len(self)))))`, [assignable](guide.md#lang-assignable) – If `key` is a slice `i:j:k` where `i`, `j`, and `k` are [`int`](https://docs.python.org/3/library/functions.html#int)s.

#### \_\_contains_\_(other)

Forbidden membership test operator.

Python requires this operator to return a [`bool`](#amaranth.hdl.Value.bool). Since this is not possible
for Amaranth values, this operator always raises an exception.

To check membership in a set of constant integer values, use [`matches()`](#amaranth.hdl.Value.matches) instead.

* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – Always.

#### bit_select(offset, width)

Part-select with bit granularity.

Selects a constant width, variable offset part of `self`, where parts with successive
offsets overlap by `width - 1` bits. Bits above the most significant bit of `self`
may be selected; they are equal to zero if `self` is unsigned, to `self[-1]` if
`self` is signed, and assigning to them does nothing.

When `offset` is a constant integer and `offset + width <= len(self)`,
this operation is equivalent to `self[offset:offset + width]`.

* **Parameters:**
  * **offset** ([value-like](guide.md#lang-valuelike)) – Index of the first selected bit.
  * **width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Amount of bits to select.
* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(width)`, [assignable](guide.md#lang-assignable)
* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `offset` is signed.
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `width` is negative.

#### word_select(offset, width)

Part-select with word granularity.

Selects a constant width, variable offset part of `self`, where parts with successive
offsets are adjacent but do not overlap. Bits above the most significant bit of `self`
may be selected; they are equal to zero if `self` is unsigned, to `self[-1]` if
`self` is signed, and assigning to them does nothing.

When `offset` is a constant integer and `width:(offset + 1) * width <= len(self)`,
this operation is equivalent to `self[offset * width:(offset + 1) * width]`.

* **Parameters:**
  * **offset** ([value-like](guide.md#lang-valuelike)) – Index of the first selected word.
  * **width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Amount of bits to select.
* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(width)`, [assignable](guide.md#lang-assignable)
* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `offset` is signed.
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `width` is negative.

#### replicate(count)

Replication.

Equivalent to `Cat(self for _ in range(count))`, but not assignable.

<!-- Technically assignable right now, but we don't want to commit to that. -->
* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(len(self) * count)`
* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `count` is negative.

#### matches(\*patterns)

Pattern matching.

Matches against a set of patterns, recognizing the same grammar as `with m.Case()`.
The pattern syntax is described in the [language guide](guide.md#lang-matchop).

Each of the `patterns` may be a [`str`](https://docs.python.org/3/library/stdtypes.html#str) or a [constant-castable object](guide.md#lang-constcasting).

* **Return type:**
  [`Value`](#amaranth.hdl.Value), `unsigned(1)`
* **Raises:**
  [**SyntaxError**](https://docs.python.org/3/library/exceptions.html#SyntaxError) – If a pattern has invalid syntax.

#### eq(value, \*, src_loc_at=0)

[Assignment](guide.md#lang-assigns).

Once it is placed in a domain, an assignment changes the bit pattern of `self` to
equal `value`. If the bit width of `value` is less than that of `self`,
it is zero-extended (for unsigned `value`s) or sign-extended (for signed
`value`s). If the bit width of `value` is greater than that of `self`,
it is truncated.

* **Return type:**
  `Statement`

#### \_\_hash_\_ *= None*

Forbidden hashing.

Python objects are [hashable](https://docs.python.org/3/glossary.html#term-hashable) if they provide a `__hash__` method
that returns an [`int`](https://docs.python.org/3/library/functions.html#int) and an `__eq__` method that returns a [`bool`](#amaranth.hdl.Value.bool).
Amaranth values define [`__eq__()`](#amaranth.hdl.Value.__eq__) to return a [`Value`](#amaranth.hdl.Value), which precludes them
from being hashable.

To use a [`Value`](#amaranth.hdl.Value) as a key in a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict), use the following pattern:

```python
value = Signal()
assoc = {}
assoc[id(value)] = value, "a signal"
_, info = assoc[id(value)]
assert info == "a signal"
```

#### \_\_format_\_(format_desc)

Forbidden formatting.

Since normal Python formatting (f-strings and `str.format`) must immediately return
a string, it is unsuitable for formatting Amaranth values. To format a value at simulation
time, use `Format` instead. If you really want to dump the AST at elaboration time,
use `repr` instead (for instance, via `f"{value!r}"`).

### *class* amaranth.hdl.ValueCastable

Interface class for objects that can be cast to a [`Value`](#amaranth.hdl.Value).

Computations in the Amaranth language are described by combining [value-like objects](guide.md#lang-valuelike). Inheriting a class from [`ValueCastable`](#amaranth.hdl.ValueCastable) and implementing
all of the methods described below adds instances of that class to the list of
value-like objects recognized by the [`Value.cast()`](#amaranth.hdl.Value.cast) method. This is a part of the mechanism
for seamlessly extending the Amaranth language in third-party code.

#### NOTE
All methods and operators defined by the [`Value`](#amaranth.hdl.Value) class will implicitly cast
a [`ValueCastable`](#amaranth.hdl.ValueCastable) object to a [`Value`](#amaranth.hdl.Value), with the exception of arithmetic
operators, which will prefer calling a reflected arithmetic operation on
the [`ValueCastable`](#amaranth.hdl.ValueCastable) argument if it defines one.

For example, if `value_castable` implements `__radd__`, then
`C(1) + value_castable` will perform `value_castable.__radd__(C(1))`, and otherwise
it will perform `C(1).__add__(value_castable.as_value())`.

#### as_value()

Convert `self` to a [value-like object](guide.md#lang-valuelike).

This method is called by the Amaranth language to convert `self` to a concrete
[`Value`](#amaranth.hdl.Value). It will usually return a [`Value`](#amaranth.hdl.Value) object, but it may also return
another value-like object to delegate its functionality.

This method must be idempotent: when called twice on the same object, the result must be
exactly the same.

This method may also be called by code that is not a part of the Amaranth language.

* **Return type:**
  Any other object recognized by [`Value.cast()`](#amaranth.hdl.Value.cast).
* **Raises:**
  [**Exception**](https://docs.python.org/3/library/exceptions.html#Exception) – When the conversion cannot be done. This exception must be propagated by callers,
      either directly or as a cause of another exception.
    
      It is recommended that, in cases where this method raises an exception,
      the [`shape()`](#amaranth.hdl.ValueCastable.shape) method also raises an exception.

#### shape()

Compute the shape of `self`.

This method is not called by the Amaranth language itself; whenever it needs to discover
the shape of a value-castable object, it calls `self.as_value().shape()`. However,
that method must return a [`Shape`](#amaranth.hdl.Shape), and [`ValueCastable`](#amaranth.hdl.ValueCastable) subclasses may have
a richer representation of their shape provided by an instance of a [`ShapeCastable`](#amaranth.hdl.ShapeCastable)
subclass. This method may return such a representation.

This method must be idempotent: when called twice on the same object, the result must be
exactly the same.

The following condition must hold:

```default
Shape.cast(self.shape()) == Value.cast(self).shape()
```

* **Return type:**
  A [shape-like](guide.md#lang-shapelike) object.
* **Raises:**
  [**Exception**](https://docs.python.org/3/library/exceptions.html#Exception) – When the conversion cannot be done. This exception must be propagated by callers,
      either directly or as a cause of another exception.
    
      It is recommended that, in cases where this method raises an exception,
      the [`as_value()`](#amaranth.hdl.ValueCastable.as_value) method also raises an exception.

### *class* amaranth.hdl.ValueLike

Abstract class representing all objects that can be cast to a [`Value`](#amaranth.hdl.Value).

`issubclass(cls, ValueLike)` returns `True` for:

* [`Value`](#amaranth.hdl.Value);
* [`ValueCastable`](#amaranth.hdl.ValueCastable) and its subclasses;
* [`int`](https://docs.python.org/3/library/functions.html#int) and its subclasses (including [`bool`](https://docs.python.org/3/library/functions.html#bool));
* [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) subclasses where all values are [value-like](guide.md#lang-valuelike);
* [`ValueLike`](#amaranth.hdl.ValueLike) itself.

`isinstance(obj, ValueLike)` returns the same value as
`issubclass(type(obj), ValueLike)`.

This class cannot be instantiated or subclassed. It can only be used for checking types of
objects.

#### NOTE
It is possible to define an enumeration with a member that is
[value-like](guide.md#lang-valuelike) but not [constant-castable](guide.md#lang-constcasting),
meaning that `issubclass(BadEnum, ValueLike)` returns `True`, but
`Value.cast(BadEnum.MEMBER)` raises an exception.

The [`amaranth.lib.enum`](stdlib/enum.md#module-amaranth.lib.enum) module prevents such enumerations from being defined when
the shape is specified explicitly. Using [`amaranth.lib.enum`](stdlib/enum.md#module-amaranth.lib.enum) and specifying the shape
ensures that all of your enumeration members are constant-castable and fit in the provided
shape.
