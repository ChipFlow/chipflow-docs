<!-- # Required to capture warnings in doctests.
import sys; sys.stderr = sys.stdout -->

# Language guide

This guide introduces the Amaranth language in depth. It assumes familiarity with synchronous digital logic and the Python programming language, but does not require prior experience with any hardware description language. See the tutorial <tutorial> for a step-by-step introduction to the language, and the reference <reference> for a detailed description of the Python classes that underlie the language’s syntax.

<!-- TODO: link to a good synchronous logic tutorial and a Python tutorial? -->

<a id="lang-prelude"></a>

## The prelude

Because Amaranth is a regular Python library, it needs to be imported before use. The root `amaranth` module, called *the prelude*, is carefully curated to export a small amount of the most essential names, useful in nearly every design. In source files dedicated to Amaranth code, it is a good practice to use a [glob import](https://docs.python.org/3/tutorial/modules.html#tut-pkg-import-star) for readability:

```default
from amaranth import *
```

However, if a source file uses Amaranth together with other libraries, or if glob imports are frowned upon, it is conventional to use a short alias instead:

```default
import amaranth as am
```

All of the examples below assume that a glob import is used.

<!-- from amaranth import * -->

<a id="lang-shapes"></a>

## Shapes

A [`Shape`](reference.md#amaranth.hdl.Shape) describes the bit width and signedness of an Amaranth value. It can be constructed directly:

```pycon
>>> Shape(width=5, signed=False)
unsigned(5)
>>> Shape(width=12, signed=True)
signed(12)
```

However, in most cases, the signedness of a shape is known upfront, and the convenient aliases [`signed()`](reference.md#amaranth.hdl.signed) and [`unsigned()`](reference.md#amaranth.hdl.unsigned) can be used:

```pycon
>>> unsigned(5) == Shape(width=5, signed=False)
True
>>> signed(12) == Shape(width=12, signed=True)
True
```

### Shapes of values

All values have a `.shape()` method that computes their shape. The width of a value `v`, `v.shape().width`, can also be retrieved with `len(v)`.

```pycon
>>> Const(5).shape()
unsigned(3)
>>> len(Const(5))
3
```

<a id="lang-values"></a>

## Values

The basic building block of the Amaranth language is a *value*, which is a term for a binary number that is computed or stored anywhere in the design. Each value has a *width*—the amount of bits used to represent the value—and a *signedness*—the interpretation of the value by arithmetic operations—collectively called its *shape*. Signed values always use [two’s complement](https://en.wikipedia.org/wiki/Two's_complement) representation.

<a id="lang-constants"></a>

## Constants

The simplest Amaranth value is a *constant*, representing a fixed number, and introduced using `Const(...)` or its short alias `C(...)`:

```pycon
>>> ten = Const(10)
>>> minus_two = C(-2)
```

The code above does not specify any shape for the constants. If the shape is omitted, Amaranth uses unsigned shape for positive numbers and signed shape for negative numbers, with the width inferred from the smallest amount of bits necessary to represent the number. As a special case, in order to get the same inferred shape for `True` and `False`, `0` is considered to be 1-bit unsigned.

```pycon
>>> ten.shape()
unsigned(4)
>>> minus_two.shape()
signed(2)
>>> C(0).shape()
unsigned(1)
```

The shape of the constant can be specified explicitly, in which case the number’s binary representation will be truncated or extended to fit the shape. Although rarely useful, 0-bit constants are permitted.

```pycon
>>> Const(360, unsigned(8)).value
104
>>> Const(129, signed(8)).value
-127
>>> Const(1, unsigned(0)).value
0
```

<a id="lang-shapelike"></a>

## Shape casting

Shapes can be *cast* from other objects, which are called *shape-like*. Casting is a convenient way to specify a shape indirectly, for example, by a range of numbers representable by values with that shape. Shapes are shape-like objects as well.

Casting to a shape can be done explicitly with [`Shape.cast()`](reference.md#amaranth.hdl.Shape.cast), but is usually implicit, since shape-like objects are accepted anywhere shapes are.

<a id="lang-shapeint"></a>

### Shapes from integers

Casting a shape from an integer `i` is a shorthand for constructing a shape with [`unsigned(i)`](reference.md#amaranth.hdl.unsigned):

```pycon
>>> Shape.cast(5)
unsigned(5)
>>> C(0, 3).shape()
unsigned(3)
```

<a id="lang-shaperange"></a>

### Shapes from ranges

Casting a shape from a [`range`](https://docs.python.org/3/library/stdtypes.html#range) `r` produces a shape that:

> * has a width large enough to represent both `min(r)` and `max(r)`, but not larger, and
> * is signed if `r` contains any negative values, unsigned otherwise.

Specifying a shape with a range is convenient for counters, indexes, and all other values whose width is derived from a set of numbers they must be able to fit:

```pycon
>>> Const(0, range(100)).shape()
unsigned(7)
>>> items = [1, 2, 3]
>>> C(1, range(len(items))).shape()
unsigned(2)
```

<a id="lang-exclrange"></a>

#### NOTE
Python ranges are *exclusive* or *half-open*, meaning they do not contain their `.stop` element. Because of this, values with shapes cast from a `range(stop)` where `stop` is a power of 2 are not wide enough to represent `stop` itself:

<!-- >>> import warnings
>>> _warning_filters_backup = warnings.catch_warnings()
>>> _warning_filters_backup.__enter__() # have to do this horrific hack to make it work with `PYTHONWARNINGS=error` :(
>>> warnings.simplefilter("default", amaranth.hdl._ast.SyntaxWarning) -->
```pycon
>>> fencepost = C(256, range(256))
<...>:1: SyntaxWarning: Value 256 equals the non-inclusive end of the constant shape range(0, 256); this is likely an off-by-one error
  fencepost = C(256, range(256))
>>> fencepost.shape()
unsigned(8)
>>> fencepost.value
0
```

<!-- >>> _warning_filters_backup.__exit__() -->

Amaranth detects uses of `Const` and `Signal` that invoke such an off-by-one error, and emits a diagnostic message.

#### NOTE
An empty range always casts to an `unsigned(0)`, even if both of its bounds are negative.
This happens because, being empty, it does not contain any negative values.

```pycon
>>> Shape.cast(range(-1, -1))
unsigned(0)
```

<a id="lang-shapeenum"></a>

### Shapes from enumerations

Casting a shape from an [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) subclass requires all of the enumeration members to have [constant-castable](#lang-constcasting) values. The shape has a width large enough to represent the value of every member, and is signed only if there is a member with a negative value.

Specifying a shape with an enumeration is convenient for finite state machines, multiplexers, complex control signals, and all other values whose width is derived from a few distinct choices they must be able to fit:

<!-- import enum -->
```python
class Direction(enum.Enum):
    TOP    = 0
    LEFT   = 1
    BOTTOM = 2
    RIGHT  = 3
```

```pycon
>>> Shape.cast(Direction)
unsigned(2)
```

The [`amaranth.lib.enum`](stdlib/enum.md#module-amaranth.lib.enum) module extends the standard enumerations such that their shape can be specified explicitly when they are defined:

<!-- import amaranth.lib.enum -->
```python
class Funct4(amaranth.lib.enum.Enum, shape=unsigned(4)):
    ADD = 0
    SUB = 1
    MUL = 2
```

```pycon
>>> Shape.cast(Funct4)
unsigned(4)
```

#### NOTE
The enumeration does not have to subclass [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) or have [`int`](https://docs.python.org/3/library/functions.html#int) as one of its base classes; it only needs to have integers as values of every member. Using enumerations based on [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) rather than [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) prevents unwanted implicit conversion of enum members to integers.

<a id="lang-shapecustom"></a>

### Custom shapes

Any Python value that implements the [`ShapeCastable`](reference.md#amaranth.hdl.ShapeCastable) interface can extend the language with a custom shape-like object. For example, the standard library module [`amaranth.lib.data`](stdlib/data.md#module-amaranth.lib.data) uses this facility to add support for aggregate data types to the language.

<a id="lang-valuelike"></a>

## Value casting

Like shapes, values may be *cast* from other objects, which are called *value-like*. Casting to values allows objects that are not provided by Amaranth, such as integers or enumeration members, to be used in Amaranth expressions directly. Custom value-like objects can be defined by implementing the [`ValueCastable`](reference.md#amaranth.hdl.ValueCastable) interface. Values are value-like objects as well.

Casting to a value can be done explicitly with [`Value.cast()`](reference.md#amaranth.hdl.Value.cast), but is usually implicit, since value-like objects are accepted anywhere values are.

### Values from integers

Casting a value from an integer `i` is equivalent to `Const(i)`:

```pycon
>>> Value.cast(5)
(const 3'd5)
```

#### NOTE
If a value subclasses [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) or its class otherwise inherits from both [`int`](https://docs.python.org/3/library/functions.html#int) and `Enum`, it is treated as an enumeration.

### Values from enumeration members

Casting a value from an enumeration member `m` is equivalent to `Const(m.value, type(m))`:

```pycon
>>> Value.cast(Direction.LEFT)
(const 2'd1)
```

#### NOTE
If a value subclasses [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) or its class otherwise inherits from both [`int`](https://docs.python.org/3/library/functions.html#int) and `Enum`, it is treated as an enumeration.

<a id="lang-constcasting"></a>

## Constant casting

A subset of [values](#lang-values) are *constant-castable*. If a value is constant-castable and all of its operands are also constant-castable, it can be converted to a `Const`, the numeric value of which can then be read by Python code. This provides a way to perform computation on Amaranth values while constructing the design.

Constant-castable objects are accepted anywhere a constant integer is accepted. Casting to a constant can also be done explicitly with `Const.cast()`:

```pycon
>>> Const.cast(Cat(C(10, 4), C(1, 2)))
(const 6'd26)
```

They may be used in enumeration members, provided the enumeration inherits from [`amaranth.lib.enum.Enum`](stdlib/enum.md#amaranth.lib.enum.Enum):

```python
class Funct(amaranth.lib.enum.Enum, shape=4):
    ADD = 0
    ...

class Op(amaranth.lib.enum.Enum, shape=1):
    REG = 0
    IMM = 1

class Instr(amaranth.lib.enum.Enum, shape=5):
    ADD  = Cat(Funct.ADD, Op.REG)
    ADDI = Cat(Funct.ADD, Op.IMM)
    ...
```

They may also be provided as a pattern to the [match operator](#lang-matchop) and the [Case block](#lang-switch).

#### NOTE
At the moment, only the following expressions are constant-castable:

* `Const`
* `Cat()`
* `Slice`

This list will be expanded in the future.

<a id="lang-signals"></a>

## Signals

A *signal* is a value representing a (potentially) varying number. Signals can be [*assigned*](#lang-assigns) in a [combinational](#lang-comb) or [synchronous](#lang-sync) domain, in which case they are generated as wires or registers, respectively. Signals always have a well-defined value; they cannot be uninitialized or undefined.

### Signal shapes

A signal can be created with an explicitly specified shape (any [shape-like](#lang-shapelike) object); if omitted, the shape defaults to [`unsigned(1)`](reference.md#amaranth.hdl.unsigned). Although rarely useful, 0-bit signals are permitted.

```pycon
>>> Signal().shape()
unsigned(1)
>>> Signal(4).shape()
unsigned(4)
>>> Signal(range(-8, 7)).shape()
signed(4)
>>> Signal(Direction).shape()
unsigned(2)
>>> Signal(0).shape()
unsigned(0)
```

<a id="lang-signalname"></a>

### Signal names

Each signal has a *name*, which is used in the waveform viewer, diagnostic messages, Verilog output, and so on. In most cases, the name is omitted and inferred from the name of the variable or attribute the signal is placed into:

<!-- class dummy(object): pass
self = dummy() -->
```pycon
>>> foo = Signal()
>>> foo.name
'foo'
>>> self.bar = Signal()
>>> self.bar.name
'bar'
```

However, the name can also be specified explicitly with the `name=` parameter:

```pycon
>>> foo2 = Signal(name="second_foo")
>>> foo2.name
'second_foo'
```

The names do not need to be unique; if two signals with the same name end up in the same namespace while preparing for simulation or synthesis, one of them will be renamed to remove the ambiguity.

<a id="lang-initial"></a>

### Initial signal values

Each signal has an *initial value*, specified with the `init=` parameter. If the initial value is not specified explicitly, zero is used by default. An initial value can be specified with an integer or an enumeration member.

Signals [assigned](#lang-assigns) in a [combinational](#lang-comb) domain assume their initial value when none of the assignments are [active](#lang-active). Signals assigned in a [synchronous](#lang-sync) domain assume their initial value after *power-on reset* and, unless the signal is [reset-less](#lang-resetless), *explicit reset*. Signals that are used but never assigned are equivalent to constants of their initial value.

```pycon
>>> Signal(4).init
0
>>> Signal(4, init=5).init
5
>>> Signal(Direction, init=Direction.LEFT).init
1
```

<a id="lang-resetless"></a>

### Reset-less signals

Signals assigned in a [synchronous](#lang-sync) domain can be *resettable* or *reset-less*, specified with the `reset_less=` parameter. If the parameter is not specified, signals are resettable by default. Resettable signals assume their [initial value](#lang-initial) on explicit reset, which can be asserted via the [clock domain](#lang-clockdomains) or by [modifying control flow](#lang-controlinserter) with `ResetInserter`. Reset-less signals are not affected by explicit reset.

Signals assigned in a [combinational](#lang-comb) domain are not affected by the `reset_less` parameter.

```pycon
>>> Signal().reset_less
False
>>> Signal(reset_less=True).reset_less
True
```

<a id="lang-operators"></a>

## Operators

To describe computations, Amaranth values can be combined with each other or with [value-like](#lang-valuelike) objects using a rich set of arithmetic, bitwise, logical, bit sequence, and other *operators* to form *expressions*, which are themselves values.

<a id="lang-abstractexpr"></a>

### Performing or describing computations?

Code written in the Python language *performs* computations on concrete objects, like integers, with the goal of calculating a concrete result:

```pycon
>>> a = 5
>>> a + 1
6
```

In contrast, code written in the Amaranth language *describes* computations on abstract objects, like [signals](#lang-signals), with the goal of generating a hardware *circuit* that can be simulated, synthesized, and so on. Amaranth expressions are ordinary Python objects that represent parts of this circuit:

```pycon
>>> a = Signal(8, init=5)
>>> a + 1
(+ (sig a) (const 1'd1))
```

Although the syntax is similar, it is important to remember that Amaranth values exist on a higher level of abstraction than Python values. For example, expressions that include Amaranth values cannot be used in Python control flow structures:

```pycon
>>> if a == 0:
...     print("Zero!")
Traceback (most recent call last):
  ...
TypeError: Attempted to convert Amaranth value to Python boolean
```

Because the value of `a`, and therefore `a == 0`, is not known at the time when the `if` statement is executed, there is no way to decide whether the body of the statement should be executed—in fact, if the design is synthesized, by the time `a` has any concrete value, the Python program has long finished! To solve this problem, Amaranth provides its own [control flow syntax](#lang-control) that, also, manipulates circuits.

<a id="lang-widthext"></a>

### Width extension

Many of the operations described below (for example, addition, equality, bitwise OR, and part select) extend the width of one or both operands to match the width of the expression. When this happens, unsigned values are always zero-extended and signed values are always sign-extended regardless of the operation or signedness of the result.

<a id="lang-arithops"></a>

### Arithmetic operators

Most arithmetic operations on integers provided by Python can be used on Amaranth values, too.

Although Python integers have unlimited precision and Amaranth values are represented with a [finite amount of bits](#lang-values), arithmetics on Amaranth values never overflows because the width of the arithmetic expression is always sufficient to represent all possible results.

```pycon
>>> a = Signal(8)
>>> (a + 1).shape() # needs to represent 1 to 256
unsigned(9)
```

Similarly, although Python integers are always signed and Amaranth values can be either [signed or unsigned](#lang-values), if any of the operands of an Amaranth arithmetic expression is signed, the expression itself is also signed, matching the behavior of Python.

```pycon
>>> a = Signal(unsigned(8))
>>> b = Signal(signed(8))
>>> (a + b).shape() # needs to represent -128 to 382
signed(10)
```

While arithmetic computations never result in an overflow, [assigning](#lang-assigns) their results to signals may truncate the most significant bits.

The following table lists the arithmetic operations provided by Amaranth:

| Operation   | Description    |
|-------------|----------------|
| `a + b`     | addition       |
| `-a`        | negation       |
| `a - b`     | subtraction    |
| `a * b`     | multiplication |
| `a // b`    | floor division |
| `a % b`     | modulo         |
| `abs(a)`    | absolute value |

<a id="lang-cmpops"></a>

### Comparison operators

All comparison operations on integers provided by Python can be used on Amaranth values. However, due to a limitation of Python, chained comparisons (e.g. `a < b < c`) cannot be used.

Similar to arithmetic operations, if any operand of a comparison expression is signed, a signed comparison is performed. The result of a comparison is a 1-bit unsigned value.

The following table lists the comparison operations provided by Amaranth:

| Operation   | Description           |
|-------------|-----------------------|
| `a == b`    | equality              |
| `a != b`    | inequality            |
| `a < b`     | less than             |
| `a <= b`    | less than or equal    |
| `a > b`     | greater than          |
| `a >= b`    | greater than or equal |

<a id="lang-bitops"></a>

### Bitwise, shift, and rotate operators

All bitwise and shift operations on integers provided by Python can be used on Amaranth values as well.

Similar to arithmetic operations, if any operand of a bitwise expression is signed, the expression itself is signed as well. A shift expression is signed if the shifted value is signed. A rotate expression is always unsigned.

Rotate operations with variable rotate amounts cannot be efficiently synthesized for non-power-of-2 widths of the rotated value. Because of that, the rotate operations are only provided for constant rotate amounts, specified as Python [`int`](https://docs.python.org/3/library/functions.html#int)s.

The following table lists the bitwise and shift operations provided by Amaranth:

| Operation           | Description                               | Notes                                        |
|---------------------|-------------------------------------------|----------------------------------------------|
| `~a`                | bitwise NOT; complement                   |                                              |
| `a & b`             | bitwise AND                               |                                              |
| `a | b`             | bitwise OR                                |                                              |
| `a ^ b`             | bitwise XOR                               |                                              |
| `a >> b`            | arithmetic right shift by variable amount | <sup>[1](#opb1)</sup>, <sup>[2](#opb2)</sup> |
| `a << b`            | left shift by variable amount             | <sup>[2](#opb2)</sup>                        |
| `a.rotate_left(i)`  | left rotate by constant amount            | <sup>[3](#opb3)</sup>                        |
| `a.rotate_right(i)` | right rotate by constant amount           | <sup>[3](#opb3)</sup>                        |
| `a.shift_left(i)`   | left shift by constant amount             | <sup>[3](#opb3)</sup>                        |
| `a.shift_right(i)`  | right shift by constant amount            | <sup>[3](#opb3)</sup>                        |
* <a id='opb1'>**[1]**</a> Logical and arithmetic right shift of an unsigned value are equivalent. Logical right shift of a signed value can be expressed by [converting it to unsigned](#lang-convops) first.
* <a id='opb2'>**[2]**</a> Shift amount must be unsigned; integer shifts in Python require the amount to be positive.
* <a id='opb3'>**[3]**</a> Shift and rotate amounts can be negative, in which case the direction is reversed.

<a id="lang-hugeshift"></a>

#### NOTE
Because Amaranth ensures that the width of a variable left shift expression is wide enough to represent any possible result, variable left shift by a wide amount produces exponentially wider intermediate values, stressing the synthesis tools:

```pycon
>>> (1 << C(0, 32)).shape()
unsigned(4294967296)
```

Although Amaranth will detect and reject expressions wide enough to break other tools, it is a good practice to explicitly limit the width of a shift amount in a variable left shift.

<a id="lang-reduceops"></a>

<a id="lang-bool"></a>

### Reduction operators

Bitwise reduction operations on integers are not provided by Python, but are very useful for hardware. They are similar to bitwise operations applied “sideways”; for example, if bitwise AND is a binary operator that applies AND to each pair of bits between its two operands, then reduction AND is an unary operator that applies AND to all of the bits in its sole operand.

The result of a reduction is a 1-bit unsigned value.

The following table lists the reduction operations provided by Amaranth:

| Operation   | Description                                  | Notes                                       |
|-------------|----------------------------------------------|---------------------------------------------|
| `a.all()`   | reduction AND; are all bits set?             | <sup>[4](#opr1)</sup>                       |
| `a.any()`   | reduction OR; is any bit set?                | <sup>[4](#opr1)</sup> <sup>[6](#opr3)</sup> |
| `a.xor()`   | reduction XOR; is an odd number of bits set? |                                             |
| `a.bool()`  | conversion to boolean; is non-zero?          | <sup>[5](#opr2)</sup> <sup>[6](#opr3)</sup> |
* <a id='opr1'>**[4]**</a> Conceptually the same as applying the Python [`all()`](https://docs.python.org/3/library/functions.html#all) or [`any()`](https://docs.python.org/3/library/functions.html#any) function to the value viewed as a collection of bits.
* <a id='opr2'>**[5]**</a> Conceptually the same as applying the Python [`bool`](https://docs.python.org/3/library/functions.html#bool) function to the value viewed as an integer.
* <a id='opr3'>**[6]**</a> While the [`Value.any()`](reference.md#amaranth.hdl.Value.any) and [`Value.bool()`](reference.md#amaranth.hdl.Value.bool)  operators return the same value, the use of `a.any()` implies that `a` is semantically a bit sequence, and the use of `a.bool()` implies that `a` is semantically a number.

<a id="lang-logicops"></a>

### Logical operators

Unlike the arithmetic or bitwise operators, it is not possible to change the behavior of the Python logical operators `not`, `and`, and `or`. Due to that, logical expressions in Amaranth are written using bitwise operations on boolean (1-bit unsigned) values, with explicit boolean conversions added where necessary.

The following table lists the Python logical expressions and their Amaranth equivalents:

| Python expression   | Amaranth expression (any operands)   |
|---------------------|--------------------------------------|
| `not a`             | `~(a).bool()`                        |
| `a and b`           | `(a).bool() & (b).bool()`            |
| `a or b`            | `(a).bool() | (b).bool()`            |

When the operands are known to be boolean values, such as comparisons, reductions, or boolean signals, the `.bool()` conversion may be omitted for clarity:

| Python expression   | Amaranth expression (boolean operands)   |
|---------------------|------------------------------------------|
| `not p`             | `~(p)`                                   |
| `p and q`           | `(p) & (q)`                              |
| `p or q`            | `(p) | (q)`                              |

<a id="lang-logicprecedence"></a>

#### WARNING
Because of Python [operator precedence](https://docs.python.org/3/reference/expressions.html#operator-summary), logical operators bind less tightly than comparison operators whereas bitwise operators bind more tightly than comparison operators. As a result, all logical expressions in Amaranth **must** have parenthesized operands.

Omitting parentheses around operands in an Amaranth a logical expression is likely to introduce a subtle bug:

```pycon
>>> en = Signal()
>>> addr = Signal(8)
>>> en & (addr == 0) # correct
(& (sig en) (== (sig addr) (const 1'd0)))
>>> en & addr == 0 # WRONG! addr is truncated to 1 bit
(== (& (sig en) (sig addr)) (const 1'd0))
```

<!-- TODO: can we detect this footgun automatically? #380 -->

<a id="lang-negatebool"></a>

#### WARNING
When applied to Amaranth boolean values, the `~` operator computes negation, and when applied to Python boolean values, the `not` operator also computes negation. However, the `~` operator applied to Python boolean values produces an unexpected result:

<!-- >>> import warnings
>>> _warning_filters_backup = warnings.catch_warnings()
>>> _warning_filters_backup.__enter__() # have to do this horrific hack to make it work with `PYTHONWARNINGS=error` :(
>>> warnings.simplefilter("ignore", DeprecationWarning) -->
```pycon
>>> ~False
-1
>>> ~True
-2
```

Because of this, Python booleans used in Amaranth logical expressions **must** be negated with the `not` operator, not the `~` operator. Negating a Python boolean with the `~` operator in an Amaranth logical expression is likely to introduce a subtle bug:

```pycon
>>> stb = Signal()
>>> use_stb = True
>>> (not use_stb) | stb # correct
(| (const 1'd0) (sig stb))
>>> ~use_stb | stb # WRONG! MSB of 2-bit wide OR expression is always 1
(| (const 2'sd-2) (sig stb))
```

<!-- >>> _warning_filters_backup.__exit__() -->

Amaranth automatically detects some cases of misuse of `~` and emits a detailed diagnostic message.

<!-- TODO: this isn't quite reliable, #380 -->

<a id="lang-seqops"></a>

### Bit sequence operators

Apart from acting as numbers, Amaranth values can also be treated as bit [sequences](https://docs.python.org/3/library/stdtypes.html#typesseq), supporting slicing, concatenation, replication, and other sequence operations. Since some of the operators Python defines for sequences clash with the operators it defines for numbers, Amaranth gives these operators a different name. Except for the names, Amaranth values follow Python sequence semantics, with the least significant bit at index 0.

Because every Amaranth value has a single fixed width, bit slicing and replication operations require the subscripts and count to be constant, specified as Python [`int`](https://docs.python.org/3/library/functions.html#int)s. It is often useful to slice a value with a constant width and variable offset, but this cannot be expressed with the Python slice notation. To solve this problem, Amaranth provides additional *part select* operations with the necessary semantics.

The result of any bit sequence operation is an unsigned value.

The following table lists the bit sequence operations provided by Amaranth:

| Operation             | Description                                      | Notes                 |
|-----------------------|--------------------------------------------------|-----------------------|
| `len(a)`              | bit length; value width                          | <sup>[7](#ops1)</sup> |
| `a[i:j:k]`            | bit slicing by constant subscripts               | <sup>[8](#ops2)</sup> |
| `iter(a)`             | bit iteration                                    |                       |
| `a.bit_select(b, w)`  | overlapping part select with variable offset     |                       |
| `a.word_select(b, w)` | non-overlapping part select with variable offset |                       |
| `Cat(a, b)`           | concatenation                                    | <sup>[9](#ops3)</sup> |
| `a.replicate(n)`      | replication                                      |                       |
* <a id='ops1'>**[7]**</a> Words “length” and “width” have the same meaning when talking about Amaranth values. Conventionally, “width” is used.
* <a id='ops2'>**[8]**</a> All variations of the Python slice notation are supported, including “extended slicing”. E.g. all of `a[0]`, `a[1:9]`, `a[2:]`, `a[:-2]`, `a[::-1]`, `a[0:8:2]` select bits in the same way as other Python sequence types select their elements.
* <a id='ops3'>**[9]**</a> In the concatenated value, `a` occupies the least significant bits, and `b` the most significant bits. Any number of arguments (zero, one, two, or more) are supported.

For the operators introduced by Amaranth, the following table explains them in terms of Python code operating on tuples of bits rather than Amaranth values:

| Amaranth operation    | Equivalent Python code   |
|-----------------------|--------------------------|
| `Cat(a, b)`           | `a + b`                  |
| `a.replicate(n)`      | `a * n`                  |
| `a.bit_select(b, w)`  | `a[b:b+w]`               |
| `a.word_select(b, w)` | `a[b*w:b*w+w]`           |

#### WARNING
In Python, the digits of a number are written right-to-left (0th exponent at the right), and the elements of a sequence are written left-to-right (0th element at the left). This mismatch can cause confusion when numeric operations (like shifts) are mixed with bit sequence operations (like concatenations). For example, `Cat(C(0b1001), C(0b1010))` has the same value as `C(0b1010_1001)`, `val[4:]` is equivalent to `val >> 4`, and `val[-1]` refers to the most significant bit.

Such confusion can often be avoided by not using numeric and bit sequence operations in the same expression. For example, although it may seem natural to describe a shift register with a numeric shift and a sequence slice operations, using sequence operations alone would make it easier to understand.

#### NOTE
Could Amaranth have used a different indexing or iteration order for values? Yes, but it would be necessary to either place the most significant bit at index 0, or deliberately break the Python sequence type interface. Both of these options would cause more issues than using different iteration orders for numeric and sequence operations.

<a id="lang-matchop"></a>

### Match operator

The `val.matches(*patterns)` operator examines a value against a set of patterns. It evaluates to `Const(1)` if the value *matches* any of the patterns, and to `Const(0)` otherwise. What it means for a value to match a pattern depends on the type of the pattern.

If the pattern is a [`str`](https://docs.python.org/3/library/stdtypes.html#str), it is treated as a bit mask with “don’t care” bits. After removing whitespace, each character of the pattern is compared to the corresponding bit of the value, where the leftmost character of the pattern (with the lowest index) corresponds to the most significant bit of the value. If the pattern character is `'0'` or `'1'`, the comparison succeeds if the bit equals `0` or `1` correspondingly. If the pattern character is `'-'`, the comparison always succeeds. Aside from spaces and tabs, which are ignored, no other characters are accepted.

Otherwise, the pattern is [cast to a constant](#lang-constcasting) and compared to `val` using the [equality operator](#lang-cmpops).

For example, given a 8-bit value `val`, `val.matches(1, '---- -01-')` is equivalent to `(val == 1) | ((val & 0b0000_0110) == 0b0000_0010)`. Bit patterns in this operator are treated similarly to [bit sequence operators](#lang-bitops).

The [Case](#lang-switch) control flow block accepts the same patterns, with the same meaning, as the match operator.

<a id="lang-convops"></a>

### Conversion operators

The `.as_signed()` and `.as_unsigned()` conversion operators reinterpret the bits of a value with the requested signedness. This is useful when the same value is sometimes treated as signed and sometimes as unsigned, or when a signed value is constructed using slices or concatenations.

For example, `(pc + imm[:7].as_signed()).as_unsigned()` sign-extends the 7 least significant bits of `imm` to the width of `pc`, performs the addition, and produces an unsigned result.

<a id="lang-muxop"></a>

### Choice operator

The `Mux(sel, val1, val0)` choice expression (similar to the [conditional expression](https://docs.python.org/3/reference/expressions.html#if-expr) in Python) is equal to the operand `val1` if `sel` is non-zero, and to the other operand `val0` otherwise. If any of `val1` or `val0` are signed, the expression itself is signed as well.

<a id="lang-array"></a>

## Arrays

An *array* is a mutable collection that can be indexed not only with an [`int`](https://docs.python.org/3/library/functions.html#int) or with a [value-like](#lang-valuelike) object. When indexed with an [`int`](https://docs.python.org/3/library/functions.html#int), it behaves like a [`list`](https://docs.python.org/3/library/stdtypes.html#list). When indexed with a value-like object, it returns a proxy object containing the elements of the array that has three useful properties:

* The result of accessing an attribute of the proxy object or indexing it is another proxy object that contains the elements transformed in the same way.
* When the proxy object is [cast to a value](#lang-valuelike), all of its elements are also cast to a value, and an element is selected using the index originally used with the array.
* The proxy object can be used both in an expression and [as the target of an assignment](#lang-assigns).

Crucially, this means that any Python object can be added to an array; the only requirement is that the final result of any computation involving it is a value-like object. For example:

```python
pixels = Array([
    {"r": 180, "g": 92, "b": 230},
    {"r": 74, "g": 130, "b": 128},
    {"r": 115, "g": 58, "b": 31},
])
```

```pycon
>>> index = Signal(range(len(pixels)))
>>> pixels[index]["r"]
(proxy (array [180, 74, 115]) (sig index))
```

#### NOTE
An array becomes immutable after it is indexed for the first time. The elements of the array do not themselves become immutable, but it is not recommended to mutate them as the behavior can become unpredictable.

#### NOTE
Arrays, `amaranth.hdl.Array`, are distinct from and serve a different function than [`amaranth.lib.data.ArrayLayout`](stdlib/data.md#amaranth.lib.data.ArrayLayout).

<a id="lang-data"></a>

## Data structures

Amaranth provides aggregate data structures in the standard library module [`amaranth.lib.data`](stdlib/data.md#module-amaranth.lib.data).

<a id="lang-modules"></a>

## Modules

A *module* is a unit of the Amaranth design hierarchy: the smallest collection of logic that can be independently simulated, synthesized, or otherwise processed. Modules associate signals with [control domains](#lang-domains), provide [control flow syntax](#lang-control), manage [clock domains](#lang-clockdomains), and aggregate [submodules](#lang-submodules).

Every Amaranth design starts with a fresh module:

```pycon
>>> m = Module()
```

<a id="lang-domains"></a>

## Control domains

A *control domain* is a named group of [signals](#lang-signals) that change their value in identical conditions.

All designs have a single predefined *combinational domain*, containing all signals that change immediately when any value used to compute them changes. The name `comb` is reserved for the combinational domain, and refers to the same domain in all modules.

A design can also have any amount of user-defined *synchronous domains*, also called [clock domains](#lang-clockdomains), containing signals that change when a specific edge occurs on the domain’s clock signal or, for domains with asynchronous reset, on the domain’s reset signal. Most modules only use a single synchronous domain, conventionally called `sync`, but the name `sync` does not have to be used, and lacks any special meaning beyond being the default.

The behavior of assignments differs for signals in [combinational](#lang-comb) and [synchronous](#lang-sync) domains. Collectively, signals in synchronous domains contain the state of a design, whereas signals in the combinational domain cannot form feedback loops or hold state.

<a id="lang-assigns"></a>

### Assigning to signals

*Assignments* are used to change the values of signals. An assignment statement can be introduced with the `.eq(...)` syntax:

```pycon
>>> s = Signal()
>>> s.eq(1)
(eq (sig s) (const 1'd1))
```

Similar to [how Amaranth operators work](#lang-abstractexpr), an Amaranth assignment is an ordinary Python object used to describe a part of a circuit. An assignment does not have any effect on the signal it changes until it is added to a control domain in a module. Once added, it introduces logic into the circuit generated from that module.

<a id="lang-assignable"></a>

### Assignable values

An assignment can affect a value that is more complex than just a signal. It is possible to assign to any combination of [signals](#lang-signals), [bit slices](#lang-seqops), [concatenations](#lang-seqops), [part selects](#lang-seqops), and [array proxy objects](#lang-array) as long as it includes no other values:

```pycon
>>> a = Signal(8)
>>> b = Signal(4)
>>> Cat(a, b).eq(0)
(eq (cat (sig a) (sig b)) (const 1'd0))
>>> a[:4].eq(b)
(eq (slice (sig a) 0:4) (sig b))
>>> Cat(a, a).bit_select(b, 2).eq(0b11)
(eq (part (cat (sig a) (sig a)) (sig b) 2 1) (const 2'd3))
```

<a id="lang-assigndomains"></a>

### Assignment domains

The `m.d.<domain> += ...` syntax is used to add assignments to a specific control domain in a module. It can add just a single assignment, or an entire sequence of them:

```python
a = Signal()
b = Signal()
c = Signal()
m.d.comb += a.eq(1)
m.d.sync += [
    b.eq(c),
    c.eq(b),
]
```

If the name of a domain is not known upfront, the `m.d["<domain>"] += ...` syntax can be used instead:

```python
def add_toggle(num):
    t = Signal()
    m.d[f"sync_{num}"] += t.eq(~t)
add_toggle(2)
```

<a id="lang-signalgranularity"></a>

Every signal bit included in the target of an assignment becomes a part of the domain, or equivalently, *driven* by that domain. A signal bit can be either undriven or driven by exactly one domain; it is an error to add two assignments to the same signal bit to two different domains:

```pycon
>>> d = Signal()
>>> m.d.comb += d.eq(1)
>>> m.d.sync += d.eq(0)
Traceback (most recent call last):
  ...
amaranth.hdl.dsl.SyntaxError: Driver-driver conflict: trying to drive (sig d) bit 0 from d.sync, but it is already driven from d.comb
```

However, two different bits of a signal can be driven from two different domains without an issue:

```python
e = Signal(2)
m.d.comb += e[0].eq(1)
m.d.sync += e[1].eq(0)
```

In addition to assignments, [assertions](#lang-assert) and [debug prints](#lang-print) can be added using the same syntax.

<a id="lang-assignorder"></a>

### Assignment order

Unlike with two different domains, adding multiple assignments to the same signal to the same domain is well-defined.

Assignments to different signal bits apply independently. For example, the following two snippets are equivalent:

```python
a = Signal(8)
m.d.comb += [
    a[0:4].eq(C(1, 4)),
    a[4:8].eq(C(2, 4)),
]
```

```python
a = Signal(8)
m.d.comb += a.eq(Cat(C(1, 4), C(2, 4)))
```

If multiple assignments change the value of the same signal bits, the assignment that is added last determines the final value. For example, the following two snippets are equivalent:

```python
b = Signal(9)
m.d.comb += [
    b[0:9].eq(Cat(C(1, 3), C(2, 3), C(3, 3))),
    b[0:6].eq(Cat(C(4, 3), C(5, 3))),
    b[3:6].eq(C(6, 3)),
]
```

```python
b = Signal(9)
m.d.comb += b.eq(Cat(C(4, 3), C(6, 3), C(3, 3)))
```

Multiple assignments to the same signal bits are more useful when combined with control structures, which can make some of the assignments [active or inactive](#lang-active). If all assignments to some signal bits are [inactive](#lang-active), their final values are determined by the signal’s domain, [combinational](#lang-comb) or [synchronous](#lang-sync).

<a id="lang-control"></a>

## Control flow

Although it is possible to write any decision tree as a combination of [assignments](#lang-assigns) and [choice expressions](#lang-muxop), Amaranth provides *control flow syntax* tailored for this task: [If/Elif/Else](#lang-if), [Switch/Case](#lang-switch), and [FSM/State](#lang-fsm). The control flow syntax uses `with` blocks (it is implemented using [context managers](https://docs.python.org/3/reference/datamodel.html#context-managers)), for example:

```python
timer = Signal(8)
with m.If(timer == 0):
    m.d.sync += timer.eq(10)
with m.Else():
    m.d.sync += timer.eq(timer - 1)
```

While some Amaranth control structures are superficially similar to imperative control flow statements (such as Python’s `if`), their function—together with [expressions](#lang-abstractexpr) and [assignments](#lang-assigns)—is to describe circuits. The code above is equivalent to:

```python
timer = Signal(8)
m.d.sync += timer.eq(Mux(timer == 0, 10, timer - 1))
```

Because all branches of a decision tree affect the generated circuit, all of the Python code inside Amaranth control structures is always evaluated in the order in which it appears in the program. This can be observed through Python code with side effects, such as `print()`:

```python
timer = Signal(8)
with m.If(timer == 0):
    print("inside `If`")
    m.d.sync += timer.eq(10)
with m.Else():
    print("inside `Else`")
    m.d.sync += timer.eq(timer - 1)
```

```none
inside `If`
inside `Else`
```

<a id="lang-active"></a>

### Active and inactive assignments

An assignment added inside an Amaranth control structure, i.e. `with m.<...>:` block, is *active* if the condition of the control structure is satisfied, and *inactive* otherwise. For any given set of conditions, the final value of every signal assigned in a module is the same as if the inactive assignments were removed and the active assignments were performed unconditionally, taking into account the [assignment order](#lang-assignorder).

For example, there are two possible cases in the circuit generated from the following code:

```python
timer = Signal(8)
m.d.sync += timer.eq(timer - 1)
with m.If(timer == 0):
    m.d.sync += timer.eq(10)
```

When `timer == 0` is true, the code reduces to:

```default
m.d.sync += timer.eq(timer - 1)
m.d.sync += timer.eq(10)
```

Due to the [assignment order](#lang-assignorder), it further reduces to:

```default
m.d.sync += timer.eq(10)
```

When `timer == 0` is false, the code reduces to:

```default
m.d.sync += timer.eq(timer - 1)
```

Combining these cases together, the code above is equivalent to:

```python
timer = Signal(8)
m.d.sync += timer.eq(Mux(timer == 0, 10, timer - 1))
```

<a id="lang-if"></a>

### `If`/`Elif`/`Else` control blocks

Conditional control flow is described using a `with m.If(cond1):` block, which may be followed by one or more `with m.Elif(cond2):` blocks, and optionally a final `with m.Else():` block. This structure parallels Python’s own [if/elif/else](https://docs.python.org/3/reference/compound_stmts.html#if) control flow syntax. For example:

<!-- x_coord = Signal(8)
is_fporch = Signal()
is_active = Signal()
is_bporch = Signal() -->
```python
with m.If(x_coord < 4):
    m.d.comb += is_bporch.eq(1)
    m.d.sync += x_coord.eq(x_coord + 1)
with m.Elif((x_coord >= 4) & (x_coord < 364)):
    m.d.comb += is_active.eq(1)
    m.d.sync += x_coord.eq(x_coord + 1)
with m.Elif((x_coord >= 364) & (x_coord < 374)):
    m.d.comb += is_fporch.eq(1)
    m.d.sync += x_coord.eq(x_coord + 1)
with m.Else():
    m.d.sync += x_coord.eq(0)
```

Within a single `If`/`Elif`/`Else` sequence of blocks, the statements within at most one block will be active at any time. This will be the first block in the order of definition whose condition, [converted to boolean](#lang-bool), is true.

If an `Else` block is present, then the statements within exactly one block will be active at any time, and the sequence as a whole is called a *full condition*.

<a id="lang-switch"></a>

### `Switch`/`Case` control blocks

Case comparison, where a single value is examined against several different *patterns*, is described using a `with m.Switch(value):` block. This block can contain any amount of `with m.Case(*patterns)` and `with m.Default():` blocks. This structure parallels Python’s own [match/case](https://docs.python.org/3/reference/compound_stmts.html#match) control flow syntax. For example:

<!-- TODO: rename `Switch` to `Match`, to mirror `Value.matches()`? -->
<!-- is_even = Signal()
is_odd  = Signal()
too_big = Signal() -->
```python
value = Signal(4)

with m.Switch(value):
    with m.Case(0, 2, 4):
        m.d.comb += is_even.eq(1)
    with m.Case(1, 3, 5):
        m.d.comb += is_odd.eq(1)
    with m.Default():
        m.d.comb += too_big.eq(1)
```

Within a single `Switch` block, the statements within at most one block will be active at any time. This will be the first `Case` block in the order of definition whose pattern [matches](#lang-matchop) the value, or the first `Default` block, whichever is earlier.

If a `Default` block is present, or the patterns in the `Case` blocks cover every possible `Switch` value, then the statements within exactly one block will be active at any time, and the sequence as a whole is called a *full condition*.

<a id="lang-fsm"></a>

### `FSM`/`State` control blocks

Simple [finite state machines](https://en.wikipedia.org/wiki/Finite-state_machine) are described using a `with m.FSM():` block. This block can contain one or more `with m.State("Name")` blocks. In addition to these blocks, the `m.next = "Name"` syntax chooses which state the FSM enters on the next clock cycle. For example, this FSM performs a bus read transaction once after reset:

```python
bus_addr = Signal(16)
r_data   = Signal(8)
r_en     = Signal()
latched  = Signal.like(r_data)

with m.FSM():
    with m.State("Set Address"):
        m.d.sync += addr.eq(0x1234)
        m.next = "Strobe Read Enable"

    with m.State("Strobe Read Enable"):
        m.d.comb += r_en.eq(1)
        m.next = "Sample Data"

    with m.State("Sample Data"):
        m.d.sync += latched.eq(r_data)
        with m.If(r_data == 0):
            m.next = "Set Address" # try again
```

<!-- TODO: FSM() should require keyword arguments, for good measure -->

The initial (and reset) state of the FSM can be provided when defining it using the `with m.FSM(init="Name"):` argument. If not provided, it is the first state in the order of definition. For example, this definition is equivalent to the one at the beginning of this section:

```python
with m.FSM(init="Set Address"):
    ...
```

The FSM belongs to a [clock domain](#lang-domains), which is specified using the `with m.FSM(domain="dom")` argument. If not specified, it is the `sync` domain. For example, this definition is equivalent to the one at the beginning of this section:

```python
with m.FSM(domain="sync"):
    ...
```

To determine (from code that is outside the FSM definition) whether it is currently in a particular state, the FSM can be captured; its `.ongoing("Name")` method returns a value that is true whenever the FSM is in the corresponding state. For example:

```python
with m.FSM() as fsm:
    ...

with m.If(fsm.ongoing("Set Address")):
    ...
```

Note that in Python, assignments made using `with x() as y:` syntax persist past the end of the block.

<!-- TODO: `ongoing` currently creates a state if it doesn't exist, which seems clearly wrong but maybe some depend on it? add a diagnostic here -->
<!-- TODO: `m.next` does the same, which is worse because adding a diagnostic is harder -->

#### WARNING
If you make a typo in the state name provided to `m.next = ...` or `fsm.ongoing(...)`, an empty and unreachable state with that name will be created with no diagnostic message.

This hazard will be eliminated in the future.

#### WARNING
If a non-string object is provided as a state name to `with m.State(...):`, it is cast to a string first, which may lead to surprising behavior. `with m.State(...):` **does not** treat an enumeration value specially; if one is provided, it is cast to a string, and its numeric value will have no correspondence to the numeric value of the generated state signal.

This hazard will be eliminated in the future.

<!-- TODO: we should probably have `fsm.next = "Name"` or `fsm.next("Name")` instead -->

#### NOTE
If you are nesting two state machines within each other, the `m.next = ...` syntax always refers to the innermost one. To change the state of the outer state machine from within the inner one, use an intermediate signal.

<a id="lang-comb"></a>

## Combinational evaluation

Signals in the combinational [control domain](#lang-domains) change whenever any value used to compute them changes. The final value of a combinational signal is equal to its [initial value](#lang-initial) updated by the [active assignments](#lang-active) in the [assignment order](#lang-assignorder). Combinational signals cannot hold any state.

Consider the following code:

<!-- en = Signal()
b = Signal(8) -->
```python
a = Signal(8, init=1)
with m.If(en):
    m.d.comb += a.eq(b + 1)
```

Whenever the signals `en` or `b` change, the signal `a` changes as well. If `en` is false, the final value of `a` is its initial value, `1`. If `en` is true, the final value of `a` is equal to `b + 1`.

A combinational signal that is computed directly or indirectly based on its own value is a part of a *combinational feedback loop*, sometimes shortened to just *feedback loop*. Combinational feedback loops can be stable (e.g. implement a constant driver or a transparent latch), or unstable (e.g. implement a ring oscillator). Amaranth prohibits using assignments to describe any kind of a combinational feedback loop, including transparent latches.

#### NOTE
In the exceedingly rare case when a combinational feedback loop is desirable, it is possible to implement it by directly instantiating technology primitives (e.g. device-specific LUTs or latches). This is also the only way to introduce a combinational feedback loop with well-defined behavior in simulation and synthesis, regardless of the HDL being used.

<a id="lang-sync"></a>

## Synchronous evaluation

Signals in synchronous [control domains](#lang-domains) change whenever the *active edge* (a 0-to-1 or 1-to-0 transition, configured when [creating the domain](#lang-clockdomains)) occurs on the clock of the synchronous domain. In addition, the signals in [clock domains](#lang-clockdomains) with an asynchronous reset change when such a reset is asserted. The final value of a synchronous signal is equal to its [initial value](#lang-initial) if the reset (of any type) is asserted, or to its current value updated by the [active assignments](#lang-active) in the [assignment order](#lang-assignorder) otherwise. Synchronous signals always hold state.

Consider the following code:

<!-- up = Signal()
down = Signal() -->
```python
timer = Signal(8)

with m.If(up):
    m.d.sync += timer.eq(timer + 1)
with m.Elif(down):
    m.d.sync += timer.eq(timer - 1)
```

Whenever there is a transition on the clock of the `sync` domain, the `timer` signal is incremented by one if `up` is true, decremented by one if `down` is true, and retains its value otherwise.

<a id="lang-assert"></a>

## Assertions

Some properties are so important that if they are violated, the computations described by the design become meaningless. These properties should be guarded with an `Assert` statement that immediately terminates the simulation if its condition is false. Assertions should generally be added to a [synchronous domain](#lang-sync), and may have an optional message printed when it is violated:

```python
ip = Signal(16)
m.d.sync += Assert(ip < 128, "instruction pointer past the end of program code!")
```

Assertions may be nested within a [control block](#lang-control):

<!-- booting = Signal() -->
```python
with m.If(~booting):
    m.d.sync += Assert(ip < 128)
```

#### WARNING
While is is also possible to add assertions to the [combinational domain](#lang-comb), simulations of combinational circuits may have *glitches*: instantaneous, transient changes in the values of expressions that are being computed which do not affect the result of the computation (and are not visible in most waveform viewers for that reason). Depending on the tools used for simulation, a glitch in the condition of an assertion or of a [control block](#lang-control) that contains it may cause the simulation to be terminated, even if the glitch would have been instantaneously resolved afterwards.

If the condition of an assertion is assigned in a synchronous domain, then it is safe to add that assertion in the combinational domain. For example, neither of the assertions in the example below will be violated due to glitches, regardless of which domain the `ip` and `booting` signals are driven by:

```python
ip_sync = Signal.like(ip)
m.d.sync += ip_sync.eq(ip)

m.d.comb += Assert(ip_sync < 128)
with m.If(booting):
    m.d.comb += Assert(ip_sync < 128)
```

Assertions should be added in a [synchronous domain](#lang-sync) when possible. In cases where it is not, such as if the condition is a signal that is assigned in a synchronous domain elsewhere, care should be taken while adding the assertion to the combinational domain.

<a id="lang-print"></a>

## Debug printing

The value of any expression, or of several of them, can be printed to the terminal during simulation using the `Print` statement. When added to the [combinational domain](#lang-comb), the value of an expression is printed whenever it changes:

```python
state = Signal()
m.d.comb += Print(state)
```

When added to a [synchronous domain](#lang-sync), the value of an expression is printed whenever the active edge occurs on the clock of that domain:

```python
m.d.sync += Print("on tick: ", state)
```

The `Print` statement, regardless of the domain, may be nested within a [control block](#lang-control):

```python
old_state = Signal.like(state)
m.d.sync += old_state.eq(state)
with m.If(state != old_state):
    m.d.sync += Print("was: ", old_state, "now: ", state)
```

The arguments to the `Print` statement have the same meaning as the arguments to the Python [`print()`](https://docs.python.org/3/library/functions.html#print) function, with the exception that only `sep` and `end` keyword arguments are supported. In addition, the `Format` helper can be used to apply formatting to the values, similar to the Python [`str.format()`](https://docs.python.org/3/library/stdtypes.html#str.format) method:

```python
addr = Signal(32)
m.d.sync += Print(Format("address: {:08x}", addr))
```

In both `Print` and `Format`, arguments that are not Amaranth [values](#lang-values) are formatted using the usual Python rules. The optional second `message` argument to `Assert` (described [above](#lang-assert)) also accepts a string or the `Format` helper:

```python
m.d.sync += Assert((addr & 0b111) == 0, message=Format("unaligned address {:08x}!", addr))
```

<a id="lang-clockdomains"></a>

## Clock domains

A new synchronous [control domain](#lang-domains), which is more often called a *clock domain*, can be defined in a design by creating a `ClockDomain` object and adding it to the `m.domains` collection:

```python
m.domains.video = cd_video = ClockDomain(local=True)
```

If the name of the domain is not known upfront, another, less concise, syntax can be used instead:

```python
def add_video_domain(n):
    cd = ClockDomain(f"video_{n}", local=True)
    m.domains += cd
    return cd

add_video_domain(2)
```

#### NOTE
Whenever the created `ClockDomain` object is immediately assigned using the `domain_name = ClockDomain(...)` or `m.domains.domain_name = ClockDomain(...)` syntax, the name of the domain may be omitted from the `ClockDomain()` invocation. In other cases, it must be provided as the first argument.

A clock domain always has a clock signal, which can be accessed through the `cd.clk` attribute. By default, the *active edge* of the clock domain is positive; this means that the signals in the domain change when the clock signal transitions from 0 to 1. A clock domain can be configured to have a negative active edge so that signals in it change when the clock signal transitions from 1 to 0:

```python
m.domains.jtag = ClockDomain(clk_edge="neg", local=True)
```

A clock domain also has a reset signal, which can be accessed through the `cd.rst` attribute. The reset signal is always active-high: the signals in the clock domain are reset if the value of the reset signal is 1. The [initial value](#lang-initial) of this signal is 0, so if the reset signal is never assigned, the signals in the clock domain are never explicitly reset (they are still [reset at power-on](#lang-initial)). Nevertheless, if its existence is undesirable, the clock domain can be configured to omit it:

```python
m.domains.startup = ClockDomain(reset_less=True, local=True)
```

Signals in a reset-less clock domain can still be explicitly reset using the `ResetInserter` [control flow modifier](#lang-controlinserter).

If a clock domain is defined in a module, all of its [submodules](#lang-submodules) can refer to that domain under the same name.

#### WARNING
Always provide the `local=True` keyword argument when defining a clock domain. The behavior of clock domains defined without this keyword argument is subject to change in near future, and is intentionally left undocumented.

#### WARNING
Clock domains use synchronous reset unless otherwise specified. Clock domains with asynchronous reset are implemented, but their behavior is subject to change in near future, and is intentionally left undocumented.

<a id="lang-latesignals"></a>

### Late binding of clock and reset signals

Clock domains are *late bound*, which means that their signals and properties can be referred to using the domain’s name before the `ClockDomain` object with that name is created and added to the design. This happens whenever [an assignment is added](#lang-assigns) to a domain. In some cases, it is necessary to refer to the domain’s clock or reset signal using only the domain’s name. The `ClockSignal` and `ResetSignal` values make this possible:

<!-- m = Module()
bus_clk = Signal()
bus_rstn = Signal() -->
```python
m.d.comb += [
    ClockSignal().eq(bus_clk),
    ResetSignal().eq(~bus_rstn),
]
```

In this example, once the design is processed, the clock signal of the clock domain `sync` found in this module or one of its containing modules will be equal to `bus_clk`. The reset signal of the same clock domain will be equal to the negated `bus_rstn`. With the `sync` domain created in the same module, these statements become equivalent to:

<!-- TODO: explain the difference (or lack thereof, eventually) between m.d, m.domain, and m.domains -->
```python
m.domains.sync = cd_sync = ClockDomain(local=True)
m.d.comb += [
    cd_sync.clk.eq(bus_clk),
    cd_sync.rst.eq(~bus_rstn),
]
```

The `ClockSignal` and `ResetSignal` values may also be assigned to other signals and used in expressions. They take a single argument, which is the name of the domain; if not specified, it defaults to `"sync"`.

#### WARNING
Be especially careful when using `ClockSignal` or `cd.clk` in expressions. Assigning to and from a clock signal is usually safe; any other operations may have unpredictable results. Consult the documentation for your synthesis toolchain and platform to understand which operations with a clock signal are permitted.

FPGAs usually have dedicated clocking facilities that can be used to disable, divide, or multiplex clock signals. When targeting an FPGA, these facilities should be used if at all possible, and expressions like `ClockSignal() & en` or `Mux(sel, ClockSignal("a"), ClockSignal("b"))` should be avoided.

<a id="lang-elaboration"></a>

## Elaboration

Amaranth designs are built from a hierarchy of smaller subdivisions, which are called *elaboratables*. The process of creating a data structure representing the behavior of a complete design by composing such subdivisions together is called *elaboration*.

An elaboratable is any Python object that inherits from the `Elaboratable` base class and implements the `elaborate()`  method:

```python
class Counter(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        ...

        return m
```

The `elaborate()` method must either return an instance of `Module` or `Instance` to describe the behavior of the elaboratable, or delegate it by returning another elaboratable object.

#### NOTE
Instances of `Module` also implement the `elaborate()` method, which returns a special object that represents a fragment of a netlist. Such an object cannot be constructed without using `Module`.

The `platform` argument received by the `elaborate()` method can be `None`, an instance of [a built-in platform](platform.md#platform), or a custom object. It is used for [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection) and to contain the state of a design while it is being elaborated.

#### WARNING
The `elaborate()` method should not modify the `self` object it receives other than for debugging and experimentation. Elaborating the same design twice with two identical platform objects should produce two identical netlists. If the design needs to be modified after construction, this should happen before elaboration.

It is not possible to ensure that a design which modifies itself during elaboration is correctly converted to a netlist because the relative order in which the `elaborate()` methods are called within a single design is not guaranteed.

The Amaranth standard library provides *components*: elaboratable objects that also include a description of their interface. Unless otherwise necessary, an elaboratable should inherit from [`amaranth.lib.wiring.Component`](stdlib/wiring.md#amaranth.lib.wiring.Component) rather than plain `Elaboratable`. See the [introduction to interfaces and components](stdlib/wiring.md#wiring-introduction) for details.

<a id="lang-submodules"></a>

### Submodules

An elaboratable can be included within another elaboratable, which is called its *containing elaboratable*, by adding it as a submodule:

```python
m.submodules.counter = counter = Counter()
```

If the name of a submodule is not known upfront, a different syntax should be used:

```python
for n in range(3):
    m.submodules[f"counter_{n}"] = Counter()
```

A submodule can also be added without specifying a name:

```python
counter = Counter()
m.submodules += counter
```

A non-Amaranth design unit can be added as a submodule using an [instance](#lang-instance).

<a id="lang-controlinserter"></a>

### Modifying control flow

Control flow within an elaboratable can be altered without introducing a new clock domain by using *control flow modifiers* that affect [synchronous evaluation](#lang-sync) of signals in a specified domain (or domains). They never affect [combinational evaluation](#lang-comb). There are two control flow modifiers:

* `ResetInserter` introduces a synchronous reset input (or inputs), updating all of the signals in the specified domains to their [initial value](#lang-initial) whenever the active edge occurs on the clock of the domain *if* the synchronous reset input is asserted.
* `EnableInserter` introduces a synchronous enable input (or inputs), preventing any of the signals in the specified domains from changing value whenever the active edge occurs on the clock of the domain *unless* the synchronous enable input is asserted.

Control flow modifiers use the syntax `Modifier(controls)(elaboratable)`, where `controls` is a mapping from [clock domain](#lang-clockdomains) names to 1-wide [values](#lang-values) and `elaboratable` is any [elaboratable](#lang-elaboration) object. When only the `sync` domain is involved, instead of writing `Modifier({"sync": input})(elaboratable)`, the equivalent but shorter `Modifier(input)(elaboratable)` syntax can be used.

The result of applying a control flow modifier to an elaboratable is, itself, an elaboratable object. A common way to use a control flow modifier is to apply it to another elaboratable while adding it as a submodule:

<!-- m = Module() -->
```python
rst = Signal()
m.submodules.counter = counter = ResetInserter(rst)(Counter())
```

A control flow modifier affects all logic within a given elaboratable and clock domain, which includes the submodules of that elaboratable.

#### NOTE
Applying a control flow modifier to an elaboratable does not mutate it; a new proxy object is returned that forwards attribute accesses and method calls to the original elaboratable. Whenever this proxy object is elaborated, it manipulates the circuit defined by the original elaboratable to include the requested control inputs.

#### NOTE
It is possible to apply several control flow modifiers to the same elaboratable, even if the same domain is used. For `ResetInserter`, the signals in a domain are held at their initial value whenever any of the reset inputs for that domain are asserted (logical OR), and for `EnableInserter`, the signals in a domain are allowed to update whenever all of the enable signals for that domain are asserted (logical AND).

Consider the following code:

<!-- z = Signal()
n = Signal(8)
en = Signal()
rst = Signal() -->
```python
m = Module()
m.d.sync += n.eq(n + 1)
m.d.comb += z.eq(n == 0)

m = ResetInserter({"sync": rst})(m)
m = EnableInserter({"sync": en})(m)
```

The application of control flow modifiers in it causes the behavior of the final `m` to be identical to that of this module:

```python
m = Module()
with m.If(en):
    m.d.sync += n.eq(n + 1)
with m.If(rst):
    m.d.sync += n.eq(n.init)
m.d.comb += z.eq(n == 0)
```

<!-- TODO: link to a clock gating primitive if/when we ever get one, from a tip about EnableInserter similar to the tip about ResetInserter above -->

<a id="lang-domainrenamer"></a>

### Renaming domains

A reusable [elaboratable](#lang-elaboration) usually specifies the use of one or more [clock domains](#lang-clockdomains) while leaving the details of clocking and initialization to a later phase in the design process. `DomainRenamer` can be used to alter a reusable elaboratable for integration in a specific design. Most elaboratables use a single clock domain named `sync`, and `DomainRenamer` makes it easy to place such elaboratables in any clock domain of a design.

Clock domains can be renamed using the syntax `DomainRenamer(domains)(elaboratable)`, where `domains` is a mapping from clock domain names to clock domain names and `elaboratable` is any [elaboratable](#lang-elaboration) object. The keys of `domains` correspond to existing clock domain names specified by `elaboratable`, and the values of `domains` correspond to the clock domain names from the containing elaboratable that will be used instead. When only the `sync` domain is being renamed, instead of writing `DomainRenamer({"sync": name})(elaboratable)`, the equivalent but shorter `DomainRenamer(name)(elaboratable)` syntax can be used.

The result of renaming clock domains in an elaboratable is, itself, an elaboratable object. A common way to rename domains is to apply `DomainRenamer` to another elaboratable while adding it as a submodule:

<!-- m = Module() -->
```python
m.submodules.counter = counter = DomainRenamer("video")(counter)
```

Renaming a clock domain affects all logic within a given elaboratable and clock domain, which includes the submodules of that elaboratable. It does not affect any logic outside of that elaboratable.

#### NOTE
Renaming domains in an elaboratable does not mutate it; a new proxy object is returned that forwards attribute accesses and method calls to the original elaboratable. Whenever this proxy object is elaborated, it manipulates the circuit defined by the original elaboratable to use the requested clock domain.

#### NOTE
It is possible to rename domains in an elaboratable and also apply [control flow modifiers](#lang-controlinserter).

Consider the following code:

<!-- count = Signal(8)
zero = Signal() -->
```python
m = Module()
m.d.sync += count.eq(count + 1)
m.d.comb += zero.eq(count == 0)

m = DomainRenamer({"sync": "video"})(m)
```

The renaming of the `sync` clock domain in it causes the behavior of the final `m` to be identical to that of this module:

```python
m = Module()
m.d.video += count.eq(count + 1)
m.d.comb += zero.eq(count == 0)
```

#### WARNING
A combinational signal can change synchronously to a clock domain, as in the example above, in which case it may only be sampled from the same clock domain unless explicitly synchronized. Renaming a clock domain must be assumed to potentially affect any output of an elaboratable.

<a id="lang-memory"></a>

## Memories

Amaranth provides support for memories in the standard library module [`amaranth.lib.memory`](stdlib/memory.md#module-amaranth.lib.memory).

<a id="lang-iovalues"></a>

## I/O values

To interoperate with external circuitry, Amaranth provides *core I/O values*, which represent bundles of wires carrying uninterpreted signals. Unlike regular [values](#lang-values), which represent binary numbers and can be [assigned](#lang-assigns) to create a unidirectional connection or used in computations, core I/O values represent electrical signals that may be digital or analog and have no [shape](#lang-shapes), cannot be assigned, used in computations, or simulated.

Core I/O values are only used to define connections between non-Amaranth building blocks that traverse an Amaranth design, including [instances](#lang-instance) and [I/O buffer instances](#lang-iobufferinstance).

<a id="lang-ioports"></a>

### I/O ports

A *core I/O port* is a core I/O value representing a connection to a port of the topmost module in the [design hierarchy](#lang-submodules). It can be created with an explicitly specified width.

```python
from amaranth.hdl import IOPort
```

```pycon
>>> port = IOPort(4)
>>> port.width
4
```

Core I/O ports can be named in the same way as [signals](#lang-signalname):

```pycon
>>> clk_port = IOPort(1, name="clk")
>>> clk_port.name
'clk'
```

If two core I/O ports with the same name exist in a design, one of them will be renamed to remove the ambiguity. Because the name of a core I/O port is significant, they should be named unambiguously.

<a id="lang-ioops"></a>

### I/O operators

Core I/O values support only a limited set of [sequence](https://docs.python.org/3/library/stdtypes.html#typesseq) operators, all of which return another core I/O value. The following table lists the operators provided by Amaranth for core I/O values:

| Operation   | Description                    | Notes                                           |
|-------------|--------------------------------|-------------------------------------------------|
| `len(a)`    | length; width                  | <sup>[10](#iops1)</sup>                         |
| `a[i:j:k]`  | slicing by constant subscripts | <sup>[11](#iops2)</sup>                         |
| `iter(a)`   | iteration                      |                                                 |
| `Cat(a, b)` | concatenation                  | <sup>[12](#iops3)</sup> <sup>[13](#iops4)</sup> |
* <a id='iops1'>**[10]**</a> Words “length” and “width” have the same meaning when talking about Amaranth I/O values. Conventionally, “width” is used.
* <a id='iops2'>**[11]**</a> All variations of the Python slice notation are supported, including “extended slicing”. E.g. all of `a[0]`, `a[1:9]`, `a[2:]`, `a[:-2]`, `a[::-1]`, `a[0:8:2]` select wires in the same way as other Python sequence types select their elements.
* <a id='iops3'>**[12]**</a> In the concatenated value, `a` occupies the lower indices and `b` the higher indices. Any number of arguments (zero, one, two, or more) are supported.
* <a id='iops4'>**[13]**</a> Concatenation of zero arguments, `Cat()`, returns a 0-bit regular value, however any such value is accepted (and ignored) anywhere an I/O value is expected.

<a id="lang-instance"></a>

## Instances

<!-- attributes are not documented because they can be easily used to break soundness and we don't document them for signals either; they are rarely necessary for interoperability -->

A submodule written in a non-Amaranth language is called an *instance*. An instance can be written in any language supported by the synthesis toolchain; usually, that is (System)Verilog, VHDL, or a language that is translated to one of those two. Adding an instance as a submodule corresponds to “module instantiation” in (System)Verilog and “component instantiation” in VHDL, and is done by specifying the following:

* The *type* of an instance is the name of a (System)Verilog module, VHDL entity or component, or another HDL design unit that is being instantiated.
* The *name* of an instance is the name of the submodule within the containing elaboratable.
* The *attributes* of an instance correspond to attributes of a (System)Verilog module instance, or a custom attribute of a VHDL entity or component instance. Attributes applied to instances are interpreted by the synthesis toolchain rather than the HDL.
* The *parameters* of an instance correspond to parameters of a (System)Verilog module instance, or a generic constant of a VHDL entity or component instance. Not all HDLs allow their design units to be parameterized during instantiation.
* The *inputs*, *outputs*, and *inouts* of an instance correspond to input ports, output ports, and bidirectional ports of the external design unit.

An instance can be added as a submodule using the `m.submodules.name = Instance("type", ...)` syntax, where `"type"` is the type of the instance as a string (which is passed to the synthesis toolchain uninterpreted), and `...` is a list of parameters, inputs, and outputs. Depending on whether the name of an attribute, parameter, input, or output can be written as a part of a Python identifier or not, one of two possible syntaxes is used to specify them:

* An attribute is specified using the `a_ANAME=attr` or `("a", "ANAME", attr)` syntaxes. The `attr` must be an [`int`](https://docs.python.org/3/library/functions.html#int), a [`str`](https://docs.python.org/3/library/stdtypes.html#str), or a `Const`.
* A parameter is specified using the `p_PNAME=param` or `("p", "PNAME", param)` syntaxes. The `param` must be an [`int`](https://docs.python.org/3/library/functions.html#int), a [`str`](https://docs.python.org/3/library/stdtypes.html#str), or a `Const`.
* An input is specified using the `i_INAME=in_val` or `("i", "INAME", in_val)` syntaxes. The `in_val` must be a [core I/O value](#lang-iovalues) or a [value-like](#lang-valuelike) object.
* An output is specified using the `o_ONAME=out_val` or `("o", "ONAME", out_val)` syntaxes. The `out_val` must be a [core I/O value](#lang-iovalues) or a [value-like](#lang-valuelike) object that casts to a [signal](#lang-signals), a concatenation of signals, or a slice of a signal.
* An inout is specified using the `io_IONAME=inout_val` or `("io", "IONAME", inout_val)` syntaxes. The `inout_val` must be a [core I/O value](#lang-iovalues).

The two following examples use both syntaxes to add the same instance of type `external` as a submodule named `processor`:

<!-- i_data = Signal(8)
o_data = Signal(8)
io_pin = IOPort(1)
m = Module() -->
```python
m.submodules.processor = Instance("external",
    p_width=8,
    i_clk=ClockSignal(),
    i_rst=ResetSignal(),
    i_en=1,
    i_mode=Const(3, unsigned(4)),
    i_data_in=i_data,
    o_data_out=o_data,
    io_pin=io_pin,
)
```

<!-- m = Module() -->
```python
m.submodules.processor = Instance("external",
    ("p", "width", 8),
    ("i", "clk", ClockSignal()),
    ("i", "rst", ResetSignal()),
    ("i", "en", 1),
    ("i", "mode", Const(3, unsigned(4))),
    ("i", "data_in", i_data),
    ("o", "data_out", o_data),
    ("io", "pin", io_pin),
)
```

Like a regular submodule, an instance can also be added without specifying a name:

```python
m.submodules += Instance("external",
    # ...
)
```

Although an `Instance` is not an elaboratable, as a special case, it can be returned from the `elaborate()` method. This is conveinent for implementing an elaboratable that adorns an instance with an Amaranth interface:

```python
from amaranth import vendor


class FlipFlop(Elaboratable):
    def __init__(self):
        self.d = Signal()
        self.q = Signal()

    def elaborate(self, platform):
        # Decide on the instance to use based on the platform we are elaborating for.
        if isinstance(platform, vendor.LatticeICE40Platform):
            return Instance("SB_DFF",
                i_C=ClockSignal(),
                i_D=self.d,
                o_Q=self.q
            )
        else:
            raise NotImplementedError
```

<a id="lang-iobufferinstance"></a>

## I/O buffer instances

#### NOTE
I/O buffer instances are a low-level primitive which is documented to ensure that the standard library does not rely on private interfaces in the core language. Most designers should use the [`amaranth.lib.io`](stdlib/io.md#module-amaranth.lib.io) module instead.

An *I/O buffer instance* is a submodule that allows connecting [core I/O values](#lang-iovalues) and regular [values](#lang-values) without the use of an external, toolchain- and technology-dependent [instance](#lang-instance). It can be created in four configurations: input, output, tristatable output, and bidirectional (input/output).

```python
from amaranth.hdl import IOBufferInstance

m = Module()
```

In the input configuration, the buffer instance combinationally drives a signal `i` by the port:

```python
port = IOPort(4)
port_i = Signal(4)
m.submodules += IOBufferInstance(port, i=port_i)
```

In the output configuration, the buffer instance combinationally drives the port by a value `o`:

```python
port = IOPort(4)
port_o = Signal(4)
m.submodules += IOBufferInstance(port, o=port_o)
```

In the tristatable output configuration, the buffer instance combinationally drives the port by a value `o` if `oe` is asserted, and does not drive (leaves in a high-impedance state, or tristates) the port otherwise:

```python
port = IOPort(4)
port_o = Signal(4)
port_oe = Signal()
m.submodules += IOBufferInstance(port, o=port_o, oe=port_oe)
```

In the bidirectional (input/output) configuration, the buffer instance combinationally drives a signal `i` by the port, combinationally drives the port by a value `o` if `oe` is asserted, and does not drive (leaves in a high-impedance state, or tristates) the port otherwise:

```python
port = IOPort(4)
port_i = Signal(4)
port_o = Signal(4)
port_oe = Signal()
m.submodules += IOBufferInstance(port, i=port_i, o=port_o, oe=port_oe)
```

The width of the `i` and `o` values (when present) must be the same as the width of the port, and the width of the `oe` value must be 1.
