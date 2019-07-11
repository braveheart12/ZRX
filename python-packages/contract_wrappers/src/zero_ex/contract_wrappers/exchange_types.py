"""Handy names for TypedDicts that represent the tuples in the Exchange ABI.

The `TypedDict`:code: classes in the .exchange module represent tuples
encountered in the Exchange contract's ABI.  However, they have weird names,
containing hashes of the tuple's field names, because the name of a Solidity
`struct`:code: isn't conveyed through the ABI.

The classes in this module simply provide human-readable names for those
hash-named classes in the generated wrapper.
"""

from .exchange import (
    Tuple0xbb41e5b3,
    Tuple0x260219a2,
    Tuple0x054ca44e,
    Tuple0xb1e4a1ae,
)


# Would rather not repeat ourselves below, but base classes are mentioned in
# the class docstrings because of a bug in sphinx rendering.  Using the `..
# autoclass` directive, with the `:show-inheritance:` role, results in docs
# being rendered with just "Bases: dict", and no mention of the direct ancestor
# of each of these classes.


class FillResults(Tuple0xbb41e5b3):
    """The `FillResults`:code: Solidity struct.

    Also known as
    `zero_ex.contract_wrappers.exchange.Tuple0xbb41e5b3`:py:class:.
    """


class Order(Tuple0x260219a2):
    """The `Order`:code: Solidity struct.

    Also known as
    `zero_ex.contract_wrappers.exchange.Tuple0x260219a2`:py:class:.
    """


class MatchedFillResults(Tuple0x054ca44e):
    """The `MatchedFillResults`:code: Solidity struct.

    Also known as
    `zero_ex.contract_wrappers.exchange.Tuple0x054ca44e`:py:class:.
    """


class OrderInfo(Tuple0xb1e4a1ae):
    """The `OrderInfo`:code: Solidity struct.

    Also known as
    `zero_ex.contract_wrappers.exchange.Tuple0xb1e4a1ae`:py:class:.
    """
