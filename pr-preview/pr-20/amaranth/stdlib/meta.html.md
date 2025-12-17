<a id="meta"></a>

# Interface metadata

The [`amaranth.lib.meta`](#module-amaranth.lib.meta) module provides a way to annotate objects in an Amaranth design and exchange these annotations with external tools in a standardized format.

<!-- from amaranth import *
from amaranth.lib import wiring, meta
from amaranth.lib.wiring import In, Out -->

## Introduction

Many Amaranth designs stay entirely within the Amaranth ecosystem, using the facilities it provides to define, test, and build hardware. In this case, the design is available for exploration using Python code, and metadata is not necessary. However, if an Amaranth design needs to fit into an existing ecosystem, or, conversely, to integrate components developed for another ecosystem, metadata can be used to exchange structured information about the design.

Consider a simple [component](wiring.md#wiring):

```python
class Adder(wiring.Component):
    a: In(unsigned(32))
    b: In(unsigned(32))
    o: Out(unsigned(33))

    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.o.eq(self.a + self.b)
        return m
```

<!-- TODO: link to Verilog backend doc when we have it -->

While it can be easily converted to Verilog, external tools will find the interface of the resulting module opaque unless they parse its Verilog source (a difficult and unrewarding task), or are provided with a description of it. Components can describe their signature with JSON-based metadata:

```pycon
>>> adder = Adder()
>>> adder.metadata 
<amaranth.lib.wiring.ComponentMetadata for ...Adder object at ...>
>>> adder.metadata.as_json() 
{
    'interface': {
        'members': {
            'a': {
                'type': 'port',
                'name': 'a',
                'dir': 'in',
                'width': 32,
                'signed': False,
                'init': '0'
            },
            'b': {
                'type': 'port',
                'name': 'b',
                'dir': 'in',
                'width': 32,
                'signed': False,
                'init': '0'
            },
            'o': {
                'type': 'port',
                'name': 'o',
                'dir': 'out',
                'width': 33,
                'signed': False,
                'init': '0'
            }
        },
        'annotations': {}
    }
}
```

<!-- # The way doctest requires this object to be formatted is truly hideous, even with +NORMALIZE_WHITESPACE.
assert adder.metadata.as_json() == {'interface': {'members': {'a': {'type': 'port', 'name': 'a', 'dir': 'in', 'width': 32, 'signed': False, 'init': '0'}, 'b': {'type': 'port', 'name': 'b', 'dir': 'in', 'width': 32, 'signed': False, 'init': '0'}, 'o': {'type': 'port', 'name': 'o', 'dir': 'out', 'width': 33, 'signed': False, 'init': '0'}}, 'annotations': {}}} -->

All metadata in Amaranth must adhere to a schema in the [JSON Schema](https://json-schema.org) language, which is integral to its definition, and can be used to validate the generated JSON:

```pycon
>>> wiring.ComponentMetadata.validate(adder.metadata.as_json())
```

The built-in component metadata can be extended to provide arbitrary information about an interface through user-defined annotations. For example, a memory bus interface could provide the layout of any memory-mapped peripherals accessible through that bus.

## Defining annotations

Consider a simple control and status register (CSR) bus that provides the memory layout of the accessible registers via an annotation:

```python
class CSRLayoutAnnotation(meta.Annotation):
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://amaranth-lang.org/schema/example/0/csr-layout.json",
        "type": "object",
        "properties": {
            "registers": {
                "type": "object",
                "patternProperties": {
                    "^.+$": {
                        "type": "integer",
                        "minimum": 0,
                    },
                },
            },
        },
        "requiredProperties": [
            "registers",
        ],
    }

    def __init__(self, origin):
        self._origin = origin

    @property
    def origin(self):
        return self._origin

    def as_json(self):
        instance = {
            "registers": self.origin.registers,
        }
        # Validating the value returned by `as_json()` ensures its conformance.
        self.validate(instance)
        return instance


class CSRSignature(wiring.Signature):
    def __init__(self):
        super().__init__({
            "addr":     Out(16),
            "w_en":     Out(1),
            "w_data":   Out(32),
            "r_en":     Out(1),
            "r_data":   In(32),
        })

    def annotations(self, obj, /):
        # Unfortunately `super()` cannot be used in `wiring.Signature` subclasses;
        # instead, use a direct call to a superclass method. In this case that is
        # `wiring.Signature` itself, but in a more complex class hierarchy it could
        # be different.
        return wiring.Signature.annotations(self, obj) + (CSRLayoutAnnotation(obj),)
```

A component that embeds a few CSR registers would define their addresses:

```python
class MyPeripheral(wiring.Component):
    csr_bus: In(CSRSignature())

    def __init__(self):
        super().__init__()
        self.csr_bus.registers = {
            "control": 0x0000,
            "status":  0x0004,
            "data":    0x0008,
        }
```

```pycon
>>> peripheral = MyPeripheral()
>>> peripheral.metadata.as_json() 
{
    'interface': {
        'members': {
            'csr_bus': {
                'type': 'interface',
                'members': {
                    'addr': {
                        'type': 'port',
                        'name': 'csr_bus__addr',
                        'dir': 'in',
                        'width': 16,
                        'signed': False,
                        'init': '0'
                    },
                    'w_en': {
                        'type': 'port',
                        'name': 'csr_bus__w_en',
                        'dir': 'in',
                        'width': 1,
                        'signed': False,
                        'init': '0'
                    },
                    'w_data': {
                        'type': 'port',
                        'name': 'csr_bus__w_data',
                        'dir': 'in',
                        'width': 32,
                        'signed': False,
                        'init': '0'
                    },
                    'r_en': {
                        'type': 'port',
                        'name': 'csr_bus__r_en',
                        'dir': 'in',
                        'width': 1,
                        'signed': False,
                        'init': '0'
                    },
                    'r_data': {
                        'type': 'port',
                        'name': 'csr_bus__r_data',
                        'dir': 'out',
                        'width': 32,
                        'signed': False,
                        'init': '0'
                    },
                },
                'annotations': {
                    'https://amaranth-lang.org/schema/example/0/csr-layout.json': {
                        'registers': {
                            'control': 0,
                            'status':  4,
                            'data':    8
                        }
                    }
                }
            }
        },
        'annotations': {}
    }
}
```

<!-- # The way doctest requires this object to be formatted is truly hideous, even with +NORMALIZE_WHITESPACE.
assert peripheral.metadata.as_json() == {'interface': {'members': {'csr_bus': {'type': 'interface', 'members': {'addr': {'type': 'port', 'name': 'csr_bus__addr', 'dir': 'in', 'width': 16, 'signed': False, 'init': '0'}, 'w_en': {'type': 'port', 'name': 'csr_bus__w_en', 'dir': 'in', 'width': 1, 'signed': False, 'init': '0'}, 'w_data': {'type': 'port', 'name': 'csr_bus__w_data', 'dir': 'in', 'width': 32, 'signed': False, 'init': '0'}, 'r_en': {'type': 'port', 'name': 'csr_bus__r_en', 'dir': 'in', 'width': 1, 'signed': False, 'init': '0'}, 'r_data': {'type': 'port', 'name': 'csr_bus__r_data', 'dir': 'out', 'width': 32, 'signed': False, 'init': '0'}}, 'annotations': {'https://amaranth-lang.org/schema/example/0/csr-layout.json': {'registers': {'control': 0, 'status': 4, 'data': 8}}}}}, 'annotations': {}}} -->

## Identifying schemas

An [`Annotation`](#amaranth.lib.meta.Annotation) schema must have a `"$id"` property, whose value is a URL that serves as its globally unique identifier. The suggested format of this URL is:

```default
<protocol>://<domain>/schema/<package>/<version>/<path>.json
```

where:

> * `<domain>` is a domain name registered to the person or entity defining the annotation;
> * `<package>` is the name of the Python package providing the [`Annotation`](#amaranth.lib.meta.Annotation) subclass;
> * `<version>` is the version of that package;
> * `<path>` is a non-empty string specific to the annotation.

#### NOTE
Annotations used in the Amaranth project packages are published under [https://amaranth-lang.org/schema/](https://amaranth-lang.org/schema/) according to this URL format, and are covered by the usual compatibility commitment.

Other projects that define additional Amaranth annotations are encouraged, but not required, to make their schemas publicly accessible; the only requirement is for the URL to be globally unique.

## Reference

### *exception* amaranth.lib.meta.InvalidSchema

Exception raised when a subclass of [`Annotation`](#amaranth.lib.meta.Annotation) is defined with a non-conformant
[`schema`](#amaranth.lib.meta.Annotation.schema).

### *exception* amaranth.lib.meta.InvalidAnnotation

Exception raised by [`Annotation.validate()`](#amaranth.lib.meta.Annotation.validate) when the JSON representation of
an annotation does not conform to its schema.

### *class* amaranth.lib.meta.Annotation

Interface annotation.

Annotations are containers for metadata that can be retrieved from an interface object using
the [`Signature.annotations`](wiring.md#amaranth.lib.wiring.Signature.annotations) method.

Annotations have a JSON representation whose structure is defined by the [JSON Schema](https://json-schema.org)
language.

#### *classmethod* \_\_init_subclass_\_()

Defining a subclass of [`Annotation`](#amaranth.lib.meta.Annotation) causes its [`schema`](#amaranth.lib.meta.Annotation.schema) to be validated.

* **Raises:**
  * [**InvalidSchema**](#amaranth.lib.meta.InvalidSchema) – If [`schema`](#amaranth.lib.meta.Annotation.schema) doesn’t conform to the 2020-12 draft of [JSON Schema](https://json-schema.org).
  * [**InvalidSchema**](#amaranth.lib.meta.InvalidSchema) – If [`schema`](#amaranth.lib.meta.Annotation.schema) doesn’t have a  [“$id” keyword](https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-01#name-the-id-keyword) at its root. This requirement is
        specific to [`Annotation`](#amaranth.lib.meta.Annotation) schemas.

#### schema *= { "$id": "...", ... }*

Schema of this annotation, expressed in the [JSON Schema](https://json-schema.org) language.

Subclasses of [`Annotation`](#amaranth.lib.meta.Annotation) must define this class attribute.

* **Type:**
  [`dict`](https://docs.python.org/3/library/stdtypes.html#dict)

#### *abstract property* origin

Python object described by this [`Annotation`](#amaranth.lib.meta.Annotation) instance.

Subclasses of [`Annotation`](#amaranth.lib.meta.Annotation) must implement this property.

#### *abstract* as_json()

Convert to a JSON representation.

Subclasses of [`Annotation`](#amaranth.lib.meta.Annotation) must implement this method.

JSON representation returned by this method must adhere to [`schema`](#amaranth.lib.meta.Annotation.schema) and pass
validation by [`validate()`](#amaranth.lib.meta.Annotation.validate).

* **Returns:**
  JSON representation of this annotation, expressed in Python primitive types
  ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict), [`list`](https://docs.python.org/3/library/stdtypes.html#list), [`str`](https://docs.python.org/3/library/stdtypes.html#str), [`int`](https://docs.python.org/3/library/functions.html#int), [`bool`](https://docs.python.org/3/library/functions.html#bool)).
* **Return type:**
  [`dict`](https://docs.python.org/3/library/stdtypes.html#dict)

#### *classmethod* validate(instance)

Validate a JSON representation against [`schema`](#amaranth.lib.meta.Annotation.schema).

* **Parameters:**
  **instance** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict)) – JSON representation to validate, either previously returned by [`as_json()`](#amaranth.lib.meta.Annotation.as_json)
  or retrieved from an external source.
* **Raises:**
  [**InvalidAnnotation**](#amaranth.lib.meta.InvalidAnnotation) – If `instance` doesn’t conform to [`schema`](#amaranth.lib.meta.Annotation.schema).
