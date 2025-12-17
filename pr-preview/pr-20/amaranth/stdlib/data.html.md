# Data structures

The [`amaranth.lib.data`](#module-amaranth.lib.data) module provides a way to describe the bitwise layout of values and a proxy class for accessing fields of values using the attribute access and indexing syntax.

## Introduction

### Overview

This module provides four related facilities:

1. Low-level bitwise layout description via [`Field`](#amaranth.lib.data.Field) and [`Layout`](#amaranth.lib.data.Layout). These classes are rarely used directly, but are the foundation on which all other functionality is built. They are also useful for introspection.
2. High-level bitwise layout description via [`StructLayout`](#amaranth.lib.data.StructLayout), [`UnionLayout`](#amaranth.lib.data.UnionLayout), [`ArrayLayout`](#amaranth.lib.data.ArrayLayout), and [`FlexibleLayout`](#amaranth.lib.data.FlexibleLayout). These classes are the ones most often used directly, in particular [`StructLayout`](#amaranth.lib.data.StructLayout) and [`ArrayLayout`](#amaranth.lib.data.ArrayLayout).
3. Data views via [`View`](#amaranth.lib.data.View) or its user-defined subclasses. This class is used to apply a layout description to a plain `Value`, enabling structured access to its bits.
4. Data classes [`Struct`](#amaranth.lib.data.Struct) and [`Union`](#amaranth.lib.data.Union). These classes are data views with a layout that is defined using Python [variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation) (also known as type annotations).

To use this module, add the following imports to the beginning of the file:

```python
from amaranth.lib import data
```

### Motivation

The fundamental Amaranth type is a `Value`: a sequence of bits that can also be used as a number. Manipulating values directly is sufficient for simple applications, but in more complex ones, values are often more than just a sequence of bits; they have well-defined internal structure.

<!-- from amaranth import *
m = Module() -->

For example, consider a module that processes pixels, converting them from RGB to grayscale. The color pixel format is RGB565:

This module could be implemented (using a fast but *very* approximate method) as follows:

```python
i_color = Signal(16)
o_gray  = Signal(8)

m.d.comb += o_gray.eq((i_color[0:5] + i_color[5:11] + i_color[11:16]) << 1)
```

While this implementation works, it is repetitive, error-prone, hard to read, and laborous to change; all because the color components are referenced using bit offsets. To improve it, the structure can be described with a [`Layout`](#amaranth.lib.data.Layout) so that the components can be referenced by name:

```python
from amaranth.lib import data, enum

rgb565_layout = data.StructLayout({
    "red":   5,
    "green": 6,
    "blue":  5
})

i_color = Signal(rgb565_layout)
o_gray  = Signal(8)

m.d.comb += o_gray.eq((i_color.red + i_color.green + i_color.blue) << 1)
```

The [`View`](#amaranth.lib.data.View) is [value-like](../guide.md#lang-valuelike) and can be used anywhere a plain value can be used. For example, it can be assigned to in the usual way:

```python
m.d.comb += i_color.eq(0) # everything is black
```

### Composing layouts

Layouts are composable: a [`Layout`](#amaranth.lib.data.Layout) is a [shape](../guide.md#lang-shapes) and can be used as a part of another layout. In this case, an attribute access through a view returns a view as well.

For example, consider a module that processes RGB pixels in groups of up to four at a time, provided by another module, and accumulates their average intensity:

```python
input_layout = data.StructLayout({
    "pixels": data.ArrayLayout(rgb565_layout, 4),
    "valid":  4
})

i_stream = Signal(input_layout)
r_accum  = Signal(32)

m.d.sync += r_accum.eq(
    r_accum + sum((i_stream.pixels[n].red +
                   i_stream.pixels[n].green +
                   i_stream.pixels[n].blue)
                  * i_stream.valid[n]
                  for n in range(len(i_stream.valid))))
```

Note how the width of `i_stream` is never defined explicitly; it is instead inferred from the shapes of its fields.

In the previous section, the precise bitwise layout was important, since RGB565 is an interchange format. In this section however the exact bit positions do not matter, since the layout is only used internally to communicate between two modules in the same design. It is sufficient that both of them use the same layout.

### Defining layouts

Data layouts can be defined in a few different ways depending on the use case.

In case the data format is defined using a family of layouts instead of a single specific one, a function can be used:

```python
def rgb_layout(r_bits, g_bits, b_bits):
    return data.StructLayout({
        "red":   unsigned(r_bits),
        "green": unsigned(g_bits),
        "blue":  unsigned(b_bits)
    })

rgb565_layout = rgb_layout(5, 6, 5)
rgb24_layout  = rgb_layout(8, 8, 8)
```

In case the data has related operations or transformations, [`View`](#amaranth.lib.data.View) can be subclassed to define methods implementing them:

```python
class RGBLayout(data.StructLayout):
    def __init__(self, r_bits, g_bits, b_bits):
        super().__init__({
            "red":   unsigned(r_bits),
            "green": unsigned(g_bits),
            "blue":  unsigned(b_bits)
        })

    def __call__(self, value):
        return RGBView(self, value)

class RGBView(data.View):
    def brightness(self):
        return (self.red + self.green + self.blue)[-8:]
```

Here, the `RGBLayout` class itself is [shape-like](../guide.md#lang-shapelike) and can be used anywhere a shape is accepted. When a `Signal` is constructed with this layout, the returned value is wrapped in an `RGBView`:

```pycon
>>> pixel = Signal(RGBLayout(5, 6, 5))
>>> len(pixel.as_value())
16
>>> pixel.red
(slice (sig pixel) 0:5)
```

In case the data format is static, [`Struct`](#amaranth.lib.data.Struct) (or [`Union`](#amaranth.lib.data.Union)) can be subclassed instead of [`View`](#amaranth.lib.data.View), to reduce the amount of boilerplate needed:

```python
class IEEE754Single(data.Struct):
    fraction: 23
    exponent:  8 = 0x7f
    sign:      1

    def is_subnormal(self):
        return self.exponent == 0
```

### Discriminated unions

This module provides a [`UnionLayout`](#amaranth.lib.data.UnionLayout), which is rarely needed by itself, but is very useful in combination with a *discriminant*: a enumeration indicating which field of the union contains valid data.

For example, consider a module that can direct another module to perform one of a few operations, each of which requires its own parameters. The two modules could communicate through a channel with a layout like this:

```python
class Command(data.Struct):
    class Kind(enum.Enum):
        SET_ADDR  = 0
        SEND_DATA = 1

    valid  : 1
    kind   : Kind
    params : data.UnionLayout({
        "set_addr": data.StructLayout({
            "addr": unsigned(32)
        }),
        "send_data": data.StructLayout({
            "byte": unsigned(8)
        })
    })
```

Here, the shape of the `Command` is inferred, being large enough to accommodate the biggest of all defined parameter structures, and it is not necessary to manage it manually.

One module could submit a command with:

```python
cmd = Signal(Command)

m.d.comb += [
    cmd.valid.eq(1),
    cmd.kind.eq(Command.Kind.SET_ADDR),
    cmd.params.set_addr.addr.eq(0x00001234)
]
```

The other would react to commands as follows:

```python
addr = Signal(32)

with m.If(cmd.valid):
    with m.Switch(cmd.kind):
        with m.Case(Command.Kind.SET_ADDR):
            m.d.sync += addr.eq(cmd.params.set_addr.addr)
        with m.Case(Command.Kind.SEND_DATA):
           ...
```

## Modeling structured data

### *class* amaranth.lib.data.Field(shape, offset)

Description of a data field.

The [`Field`](#amaranth.lib.data.Field) class specifies the signedness and bit positions of a field in
an Amaranth value.

[`Field`](#amaranth.lib.data.Field) objects are immutable.

* **Attributes:**
  * **shape** ([`ShapeLike`](../reference.md#amaranth.hdl.ShapeLike)) – Shape of the field. When initialized or assigned, the object is stored as-is.
  * **offset** ([`int`](https://docs.python.org/3/library/functions.html#int), >=0) – Index of the least significant bit of the field.

#### *property* width

Width of the field.

This property should be used over `self.shape.width` because `self.shape` can be
an arbitrary [shape-like](../guide.md#lang-shapelike) object, which may not have
a `width` property.

* **Returns:**
  `Shape.cast(self.shape).width`
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### \_\_eq_\_(other)

Compare fields.

Two fields are equal if they have the same shape and offset.

### *class* amaranth.lib.data.Layout

Description of a data layout.

The [shape-like](../guide.md#lang-shapelike) [`Layout`](#amaranth.lib.data.Layout) interface associates keys
(string names or integer indexes) with fields, giving identifiers to spans of bits in
an Amaranth value.

It is an abstract base class; [`StructLayout`](#amaranth.lib.data.StructLayout), [`UnionLayout`](#amaranth.lib.data.UnionLayout),
[`ArrayLayout`](#amaranth.lib.data.ArrayLayout), and [`FlexibleLayout`](#amaranth.lib.data.FlexibleLayout) implement concrete layout rules.
New layout rules can be defined by inheriting from this class.

Like all other shape-castable objects, all layouts are immutable. New classes deriving from
[`Layout`](#amaranth.lib.data.Layout) must preserve this invariant.

#### *static* cast(obj)

Cast a [shape-like](../guide.md#lang-shapelike) object to a layout.

This method performs a subset of the operations done by [`Shape.cast()`](../reference.md#amaranth.hdl.Shape.cast); it will
recursively call `.as_shape()`, but only until a layout is returned.

* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `obj` cannot be converted to a [`Layout`](#amaranth.lib.data.Layout) instance.
  * [**RecursionError**](https://docs.python.org/3/library/exceptions.html#RecursionError) – If `obj.as_shape()` returns `obj`.

#### *abstract* \_\_iter_\_()

Iterate fields in the layout.

* **Yields:**
  * [`str`](https://docs.python.org/3/library/stdtypes.html#str) or [`int`](https://docs.python.org/3/library/functions.html#int) – Key (either name or index) for accessing the field.
  * [`Field`](#amaranth.lib.data.Field) – Description of the field.

#### *abstract* \_\_getitem_\_(key)

Retrieve a field from the layout.

* **Returns:**
  The field associated with `key`.
* **Return type:**
  [`Field`](#amaranth.lib.data.Field)
* **Raises:**
  [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If there is no field associated with `key`.

#### *abstract property* size

Size of the layout.

* **Returns:**
  The amount of bits required to store every field in the layout.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### as_shape()

Shape of the layout.

* **Returns:**
  `unsigned(self.size)`
* **Return type:**
  [`Shape`](../reference.md#amaranth.hdl.Shape)

#### \_\_eq_\_(other)

Compare layouts.

Two layouts are equal if they have the same size and the same fields under the same names.
The order of the fields is not considered.

#### \_\_call_\_(target)

Create a view into a target.

When a [`Layout`](#amaranth.lib.data.Layout) is used as the shape of a [`Field`](#amaranth.lib.data.Field) and accessed through
a [`View`](#amaranth.lib.data.View), this method is used to wrap the slice of the underlying value into
another view with this layout.

* **Returns:**
  `View(self, target)`
* **Return type:**
  [`View`](#amaranth.lib.data.View)

#### const(init)

Convert a constant initializer to a constant.

Converts `init`, which may be a sequence or a mapping of field values, to a constant.

* **Returns:**
  A constant that has the same value as a view with this layout that was initialized with
  an all-zero value and had every field assigned to the corresponding value in the order
  in which they appear in `init`.
* **Return type:**
  [`Const`](#amaranth.lib.data.Const)

#### from_bits(raw)

Convert a bit pattern to a constant.

Converts `raw`, which is an [`int`](https://docs.python.org/3/library/functions.html#int), to a constant.

* **Returns:**
  `Const(self, raw)`
* **Return type:**
  [`Const`](#amaranth.lib.data.Const)

## Common data layouts

### *class* amaranth.lib.data.StructLayout(members)

Description of a structure layout.

The fields of a structure layout follow one another without any gaps, and the size of
a structure layout is the sum of the sizes of its members.

For example, the following layout of a 16-bit value:

can be described with:

```python
data.StructLayout({
    "first":  3,
    "second": 7,
    "third":  6
})
```

#### NOTE
Structures that have padding can be described with a [`FlexibleLayout`](#amaranth.lib.data.FlexibleLayout). Alternately,
padding can be added to the layout as fields called `_1`, `_2`, and so on. These fields
won’t be accessible as attributes or by using indexing.

* **Attributes:**
  **members** (mapping of [`str`](https://docs.python.org/3/library/stdtypes.html#str) to [`ShapeLike`](../reference.md#amaranth.hdl.ShapeLike)) – Dictionary of structure members.

#### *property* size

Size of the structure layout.

* **Returns:**
  Index of the most significant bit of the *last* field plus one; or zero if there are
  no fields.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

### *class* amaranth.lib.data.UnionLayout(members)

Description of a union layout.

The fields of a union layout all start from bit 0, and the size of a union layout is the size
of the largest of its members.

For example, the following layout of a 7-bit value:

can be described with:

```python
data.UnionLayout({
    "first":  3,
    "second": 7,
    "third":  6
})
```

* **Attributes:**
  **members** (mapping of [`str`](https://docs.python.org/3/library/stdtypes.html#str) to [`ShapeLike`](../reference.md#amaranth.hdl.ShapeLike)) – Dictionary of union members.

#### *property* size

Size of the union layout.

* **Returns:**
  Index of the most significant bit of the *largest* field plus one; or zero if there are
  no fields.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

### *class* amaranth.lib.data.ArrayLayout(elem_shape, length)

Description of an array layout.

The fields of an array layout follow one another without any gaps, and the size of an array
layout is the size of its element multiplied by its length.

For example, the following layout of a 16-bit value:

can be described with:

```python
data.ArrayLayout(unsigned(4), 4)
```

#### NOTE
Arrays that have padding can be described with a [`FlexibleLayout`](#amaranth.lib.data.FlexibleLayout).

#### NOTE
This class, [`amaranth.lib.data.ArrayLayout`](#amaranth.lib.data.ArrayLayout), is distinct from and serves a different
function than `amaranth.hdl.Array`.

* **Attributes:**
  * **elem_shape** ([`ShapeLike`](../reference.md#amaranth.hdl.ShapeLike)) – Shape of an individual element.
  * **length** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Amount of elements.

#### *property* size

Size of the array layout.

* **Returns:**
  Size of an individual element multiplied by their amount.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

### *class* amaranth.lib.data.FlexibleLayout(size, fields)

Description of a flexible layout.

A flexible layout is similar to a structure layout; while fields in [`StructLayout`](#amaranth.lib.data.StructLayout) are
defined contiguously, the fields in a flexible layout can overlap and have gaps between them.

Because the size and field boundaries in a flexible layout can be defined arbitrarily, it
may also be more convenient to use a flexible layout when the layout information is derived
from an external data file rather than defined in Python code.

For example, the following layout of a 16-bit value:

can be described with:

```python
data.FlexibleLayout(16, {
    "first":  data.Field(unsigned(3), 1),
    "second": data.Field(unsigned(7), 0),
    "third":  data.Field(unsigned(6), 10),
    0:        data.Field(unsigned(1), 14)
})
```

Both strings and integers can be used as names of flexible layout fields, so flexible layouts
can be used to describe structures with arbitrary padding and arrays with arbitrary stride.

If another data structure is used as the source of truth for creating flexible layouts,
consider instead inheriting from the base [`Layout`](#amaranth.lib.data.Layout) class, which may be more convenient.

* **Attributes:**
  * **size** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Size of the layout.
  * **fields** (mapping of [`str`](https://docs.python.org/3/library/stdtypes.html#str) or [`int`](https://docs.python.org/3/library/functions.html#int) to [`Field`](#amaranth.lib.data.Field)) – Fields defined in the layout.

## Data views

### *class* amaranth.lib.data.View(layout, target)

A value viewed through the lens of a layout.

The [value-like](../guide.md#lang-valuelike) class [`View`](#amaranth.lib.data.View) provides access to the fields
of an underlying Amaranth value via the names or indexes defined in the provided layout.

### Creating a view

A view must be created using an explicitly provided layout and target. To create a new
`Signal` that is wrapped in a [`View`](#amaranth.lib.data.View) with a given `layout`, use
`Signal(layout, ...)`, which for a [`Layout`](#amaranth.lib.data.Layout) is equivalent to
`View(layout, Signal(...))`.

### Accessing a view

Slicing a view or accessing its attributes returns a part of the underlying value
corresponding to the field with that index or name, which is itself either a value or
a value-castable object. If the shape of the field is a [`Layout`](#amaranth.lib.data.Layout), it will be
a [`View`](#amaranth.lib.data.View); if it is a class deriving from [`Struct`](#amaranth.lib.data.Struct) or [`Union`](#amaranth.lib.data.Union), it
will be an instance of that data class; if it is another [shape-like](../guide.md#lang-shapelike)
object implementing [`__call__()`](../reference.md#amaranth.hdl.ShapeCastable.__call__), it will be the result of calling that
method.

Slicing a view whose layout is an [`ArrayLayout`](#amaranth.lib.data.ArrayLayout) can be done with an index that is
an Amaranth value rather than a constant integer. The returned element is chosen dynamically
in that case.

A view can only be compared for equality with another view or constant with the same layout,
returning a single-bit [`Value`](../reference.md#amaranth.hdl.Value). No other operators are supported. A view can be
lowered to a [`Value`](../reference.md#amaranth.hdl.Value) using [`as_value()`](#amaranth.lib.data.View.as_value).

### Custom view classes

The [`View`](#amaranth.lib.data.View) class can be inherited from to define additional properties or methods on
a view. The only three names that are reserved on instances of [`View`](#amaranth.lib.data.View) and [`Const`](#amaranth.lib.data.Const)
are [`as_value()`](#amaranth.lib.data.View.as_value), [`Const.as_bits()`](#amaranth.lib.data.Const.as_bits), and [`eq()`](#amaranth.lib.data.View.eq), leaving the rest to the developer.
The [`Struct`](#amaranth.lib.data.Struct) and [`Union`](#amaranth.lib.data.Union) classes provided in this module are subclasses of
[`View`](#amaranth.lib.data.View) that also provide a concise way to define a layout.

#### shape()

Get layout of this view.

* **Returns:**
  The `layout` provided when constructing the view.
* **Return type:**
  [`Layout`](#amaranth.lib.data.Layout)

#### as_value()

Get underlying value.

* **Returns:**
  The `target` provided when constructing the view, or the `Signal` that
  was created.
* **Return type:**
  [`Value`](../reference.md#amaranth.hdl.Value)

#### eq(other)

Assign to the underlying value.

* **Returns:**
  `self.as_value().eq(other)`
* **Return type:**
  `Assign`

#### \_\_getitem_\_(key)

Slice the underlying value.

A field corresponding to `key` is looked up in the layout. If the field’s shape is
a shape-castable object that has a [`__call__()`](../reference.md#amaranth.hdl.ShapeCastable.__call__) method, it is called and
the result is returned. Otherwise, [`as_shape()`](../reference.md#amaranth.hdl.ShapeCastable.as_shape) is called repeatedly on
the shape until either an object with a [`__call__()`](../reference.md#amaranth.hdl.ShapeCastable.__call__) method is reached,
or a [`Shape`](../reference.md#amaranth.hdl.Shape) is returned. In the latter case, returns an unspecified Amaranth
expression with the right shape.

* **Parameters:**
  **key** ([`str`](https://docs.python.org/3/library/stdtypes.html#str) or [`int`](https://docs.python.org/3/library/functions.html#int) or [`ValueCastable`](../reference.md#amaranth.hdl.ValueCastable)) – Name or index of a field.
* **Returns:**
  A slice of the underlying value defined by the field.
* **Return type:**
  [`Value`](../reference.md#amaranth.hdl.Value) or [`ValueCastable`](../reference.md#amaranth.hdl.ValueCastable), [assignable](../guide.md#lang-assignable)
* **Raises:**
  * [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If the layout does not define a field corresponding to `key`.
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `key` is a value-castable object, but the layout of the view is not
        an [`ArrayLayout`](#amaranth.lib.data.ArrayLayout).
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If [`ShapeCastable.__call__()`](../reference.md#amaranth.hdl.ShapeCastable.__call__) does not return a value or a value-castable object.

#### \_\_getattr_\_(name)

Access a field of the underlying value.

Returns `self[name]`.

* **Raises:**
  [**AttributeError**](https://docs.python.org/3/library/exceptions.html#AttributeError) – If the layout does not define a field called `name`, or if `name` starts with
      an underscore.

### *class* amaranth.lib.data.Const(layout, target)

A constant value viewed through the lens of a layout.

The [`Const`](#amaranth.lib.data.Const) class is similar to the [`View`](#amaranth.lib.data.View) class, except that its target is
a specific bit pattern and operations on it return constants.

### Creating a constant

A constant can be created from a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) or [`list`](https://docs.python.org/3/library/stdtypes.html#list) of field values using
[`Layout.const()`](#amaranth.lib.data.Layout.const), or from a bit pattern using [`Layout.from_bits()`](#amaranth.lib.data.Layout.from_bits).

### Accessing a constant

Slicing a constant or accessing its attributes returns a part of the underlying value
corresponding to the field with that index or name. If the shape of the field is
a [`Layout`](#amaranth.lib.data.Layout), the returned value is a [`Const`](#amaranth.lib.data.Const); if it is a different
[shape-like](../guide.md#lang-shapelike) object implementing [`from_bits()`](../reference.md#amaranth.hdl.ShapeCastable.from_bits),
it will be the result of calling that method; otherwise, it is an [`int`](https://docs.python.org/3/library/functions.html#int).

Slicing a constant whose layout is an [`ArrayLayout`](#amaranth.lib.data.ArrayLayout) can be done with an index that is
an Amaranth value rather than a constant integer. The returned element is chosen dynamically
in that case, and the resulting value will be a [`View`](#amaranth.lib.data.View) instead of a [`Const`](#amaranth.lib.data.Const).

A [`Const`](#amaranth.lib.data.Const) can only be compared for equality with another constant or view that has
the same layout. When compared with another constant, the result will be a [`bool`](https://docs.python.org/3/library/functions.html#bool).
When compared with a view, the result will be a single-bit [`Value`](../reference.md#amaranth.hdl.Value). No other operators
are supported. A constant can be lowered to a [`Value`](../reference.md#amaranth.hdl.Value) using [`as_value()`](#amaranth.lib.data.Const.as_value), or to
its underlying bit pattern using [`as_bits()`](#amaranth.lib.data.Const.as_bits).

#### shape()

Get layout of this constant.

* **Returns:**
  The `layout` provided when constructing the constant.
* **Return type:**
  [`Layout`](#amaranth.lib.data.Layout)

#### as_bits()

Get underlying bit pattern.

* **Returns:**
  The `target` provided when constructing the constant.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### as_value()

Convert to a value.

* **Returns:**
  The bit pattern of this constant, as a [`Value`](../reference.md#amaranth.hdl.Value).
* **Return type:**
  [`Const`](#amaranth.lib.data.Const)

#### \_\_getitem_\_(key)

Slice the underlying value.

A field corresponding to `key` is looked up in the layout. If the field’s shape is
a shape-castable object that has a [`from_bits()`](../reference.md#amaranth.hdl.ShapeCastable.from_bits) method, returns
the result of calling that method. Otherwise, returns an [`int`](https://docs.python.org/3/library/functions.html#int).

* **Parameters:**
  **key** ([`str`](https://docs.python.org/3/library/stdtypes.html#str) or [`int`](https://docs.python.org/3/library/functions.html#int) or [`ValueCastable`](../reference.md#amaranth.hdl.ValueCastable)) – Name or index of a field.
* **Returns:**
  A slice of the underlying value defined by the field.
* **Return type:**
  unspecified type or [`int`](https://docs.python.org/3/library/functions.html#int)
* **Raises:**
  * [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If the layout does not define a field corresponding to `key`.
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If `key` is a value-castable object, but the layout of the constant is not
        an [`ArrayLayout`](#amaranth.lib.data.ArrayLayout).
  * [**Exception**](https://docs.python.org/3/library/exceptions.html#Exception) – If the bit pattern of the field is not valid according to
        [`ShapeCastable.from_bits()`](../reference.md#amaranth.hdl.ShapeCastable.from_bits). Usually this will be a [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError).

#### \_\_getattr_\_(name)

Access a field of the underlying value.

Returns `self[name]`.

* **Raises:**
  * [**AttributeError**](https://docs.python.org/3/library/exceptions.html#AttributeError) – If the layout does not define a field called `name`, or if `name` starts with
        an underscore.
  * [**Exception**](https://docs.python.org/3/library/exceptions.html#Exception) – If the bit pattern of the field is not valid according to
        [`ShapeCastable.from_bits()`](../reference.md#amaranth.hdl.ShapeCastable.from_bits). Usually this will be a [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError).

## Data classes

### *class* amaranth.lib.data.Struct(target)

Structures defined with annotations.

The [`Struct`](#amaranth.lib.data.Struct) base class is a subclass of [`View`](#amaranth.lib.data.View) that provides a concise way
to describe the structure layout and initial values for the fields using Python
[variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation).

Any annotations containing [shape-like](../guide.md#lang-shapelike) objects are used,
in the order in which they appear in the source code, to construct a [`StructLayout`](#amaranth.lib.data.StructLayout).
The values assigned to such annotations are used to populate the initial value of the signal
created by the view. Any other annotations are kept as-is.

<!-- from amaranth import *
from amaranth.lib.data import * -->

As an example, a structure for [IEEE 754 single-precision floating-point format](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) can be defined as:

```python
class IEEE754Single(Struct):
    fraction: 23
    exponent:  8 = 0x7f
    sign:      1

    def is_subnormal(self):
        return self.exponent == 0
```

The `IEEE754Single` class itself can be used where a [shape](../guide.md#lang-shapes) is expected:

```pycon
>>> IEEE754Single.as_shape()
StructLayout({'fraction': 23, 'exponent': 8, 'sign': 1})
>>> Signal(IEEE754Single).as_value().shape().width
32
```

Instances of this class can be used where [values](../guide.md#lang-values) are expected:

```pycon
>>> flt = Signal(IEEE754Single)
>>> Signal(32).eq(flt)
(eq (sig $signal) (sig flt))
```

Accessing shape-castable properties returns slices of the underlying value:

```pycon
>>> flt.fraction
(slice (sig flt) 0:23)
>>> flt.is_subnormal()
(== (slice (sig flt) 23:31) (const 1'd0))
```

The initial values for individual fields can be overridden during instantiation:

```pycon
>>> hex(Signal(IEEE754Single).as_value().init)
'0x3f800000'
>>> hex(Signal(IEEE754Single, init={'sign': 1}).as_value().init)
'0xbf800000'
>>> hex(Signal(IEEE754Single, init={'exponent': 0}).as_value().init)
'0x0'
```

Classes inheriting from [`Struct`](#amaranth.lib.data.Struct) can be used as base classes. The only restrictions
are that:

* Classes that do not define a layout cannot be instantiated or converted to a shape;
* A layout can be defined exactly once in the inheritance hierarchy.

Behavior can be shared through inheritance:

```python
class HasChecksum(Struct):
    def checksum(self):
        bits = Value.cast(self)
        return sum(bits[n:n+8] for n in range(0, len(bits), 8))

class BareHeader(HasChecksum):
    address: 16
    length:   8

class HeaderWithParam(HasChecksum):
    address: 16
    length:   8
    param:    8
```

```pycon
>>> HasChecksum.as_shape()
Traceback (most recent call last):
  ...
TypeError: Aggregate class 'HasChecksum' does not have a defined shape
>>> bare = Signal(BareHeader); bare.checksum()
(+ (+ (+ (const 1'd0) (slice (sig bare) 0:8)) (slice (sig bare) 8:16)) (slice (sig bare) 16:24))
>>> param = Signal(HeaderWithParam); param.checksum()
(+ (+ (+ (+ (const 1'd0) (slice (sig param) 0:8)) (slice (sig param) 8:16)) (slice (sig param) 16:24)) (slice (sig param) 24:32))
```

### *class* amaranth.lib.data.Union(target)

Unions defined with annotations.

The [`Union`](#amaranth.lib.data.Union) base class is a subclass of [`View`](#amaranth.lib.data.View) that provides a concise way
to describe the union layout using Python [variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation). It is very similar to the [`Struct`](#amaranth.lib.data.Struct) class, except that its layout
is a [`UnionLayout`](#amaranth.lib.data.UnionLayout).

A [`Union`](#amaranth.lib.data.Union) can have only one field with a specified initial value. If an initial value is
explicitly provided during instantiation, it overrides the initial value specified with
an annotation:

```python
class VarInt(Union):
    int8:  8
    int16: 16 = 0x100
```

```pycon
>>> Signal(VarInt).as_value().init
256
>>> Signal(VarInt, init={'int8': 10}).as_value().init
10
```
