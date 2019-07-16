"""Handy names for TypedDicts that represent the tuples in the Exchange ABI.

The `TypedDict`:code: classes in the .exchange module represent tuples
encountered in the Exchange contract's ABI.  However, they have weird names,
containing hashes of the tuple's field names, because the name of a Solidity
`struct`:code: isn't conveyed through the ABI.

The classes in this module simply provide human-readable names for those
hash-named classes in the generated wrapper.
"""

from eth_utils import remove_0x_prefix

from zero_ex import json_schemas

from . import (
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


def order_to_jsdict(
    order: Order,
    exchange_address="0x0000000000000000000000000000000000000000",
    signature: str = None,
) -> dict:
    """Convert a Web3-compatible order struct to a JSON-schema-compatible dict.

    More specifically, do explicit decoding for the `bytes`:code: fields, and
    convert numerics to strings.

    >>> import pprint
    >>> pprint.pprint(order_to_jsdict(
    ...     {
    ...         'maker_address': "0x0000000000000000000000000000000000000000",
    ...         'taker_address': "0x0000000000000000000000000000000000000000",
    ...         'fee_recipient_address':
    ...             "0x0000000000000000000000000000000000000000",
    ...         'sender_address': "0x0000000000000000000000000000000000000000",
    ...         'maker_asset_amount': 1,
    ...         'taker_asset_amount': 1,
    ...         'maker_fee': 0,
    ...         'taker_fee': 0,
    ...         'expiration_time_seconds': 1,
    ...         'salt': 1,
    ...         'maker_asset_data': (0).to_bytes(1, byteorder='big') * 20,
    ...         'taker_asset_data': (0).to_bytes(1, byteorder='big') * 20,
    ...     },
    ... ))
    {'exchangeAddress': '0x0000000000000000000000000000000000000000',
     'expirationTimeSeconds': '1',
     'feeRecipientAddress': '0x0000000000000000000000000000000000000000',
     'makerAddress': '0x0000000000000000000000000000000000000000',
     'makerAssetAmount': '1',
     'makerAssetData': '0x0000000000000000000000000000000000000000',
     'makerFee': '0',
     'salt': '1',
     'senderAddress': '0x0000000000000000000000000000000000000000',
     'takerAddress': '0x0000000000000000000000000000000000000000',
     'takerAssetAmount': '1',
     'takerAssetData': '0x0000000000000000000000000000000000000000',
     'takerFee': '0'}
    """
    jsdict = dict()

    jsdict["makerAddress"] = order["maker_address"]
    jsdict["takerAddress"] = order["taker_address"]
    jsdict["senderAddress"] = order["sender_address"]
    jsdict["feeRecipientAddress"] = order["fee_recipient_address"]

    # encode bytes fields
    jsdict["makerAssetData"] = "0x" + order["maker_asset_data"].hex()
    jsdict["takerAssetData"] = "0x" + order["taker_asset_data"].hex()

    jsdict["exchangeAddress"] = exchange_address

    jsdict["expirationTimeSeconds"] = str(order["expiration_time_seconds"])

    jsdict["makerAssetAmount"] = str(order["maker_asset_amount"])
    jsdict["takerAssetAmount"] = str(order["taker_asset_amount"])

    jsdict["makerFee"] = str(order["maker_fee"])
    jsdict["takerFee"] = str(order["taker_fee"])

    jsdict["salt"] = str(order["salt"])

    if signature is not None:
        jsdict["signature"] = signature

    json_schemas.assert_valid(jsdict, "/orderSchema")

    return jsdict


def jsdict_to_order(jsdict: dict) -> Order:
    r"""Convert a JSON-schema-compatible dict order to a Web3-compatible struct.

    More specifically, do explicit encoding of the `bytes`:code: fields, and
    parse integers from strings.

    >>> import pprint
    >>> pprint.pprint(jsdict_to_order(
    ...     {
    ...         'makerAddress': "0x0000000000000000000000000000000000000000",
    ...         'takerAddress': "0x0000000000000000000000000000000000000000",
    ...         'feeRecipientAddress': "0x0000000000000000000000000000000000000000",
    ...         'senderAddress': "0x0000000000000000000000000000000000000000",
    ...         'makerAssetAmount': "1000000000000000000",
    ...         'takerAssetAmount': "1000000000000000000",
    ...         'makerFee': "0",
    ...         'takerFee': "0",
    ...         'expirationTimeSeconds': "12345",
    ...         'salt': "12345",
    ...         'makerAssetData': "0x0000000000000000000000000000000000000000",
    ...         'takerAssetData': "0x0000000000000000000000000000000000000000",
    ...         'exchangeAddress': "0x0000000000000000000000000000000000000000",
    ...     },
    ... ))
    {'expiration_time_seconds': 12345,
     'fee_recipient_address': '0x0000000000000000000000000000000000000000',
     'maker_address': '0x0000000000000000000000000000000000000000',
     'maker_asset_amount': 1000000000000000000,
     'maker_asset_data': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00',
     'maker_fee': 0,
     'salt': 12345,
     'sender_address': '0x0000000000000000000000000000000000000000',
     'taker_address': '0x0000000000000000000000000000000000000000',
     'taker_asset_amount': 1000000000000000000,
     'taker_asset_data': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00',
     'taker_fee': 0}
    """  # noqa: E501 (line too long)
    json_schemas.assert_valid(jsdict, "/orderSchema")

    return Order(
        maker_address=jsdict["makerAddress"],
        taker_address=jsdict["takerAddress"],
        sender_address=jsdict["senderAddress"],
        fee_recipient_address=jsdict["feeRecipientAddress"],
        maker_asset_data=bytes.fromhex(
            remove_0x_prefix(jsdict["makerAssetData"])
        ),
        taker_asset_data=bytes.fromhex(
            remove_0x_prefix(jsdict["takerAssetData"])
        ),
        maker_asset_amount=int(jsdict["makerAssetAmount"]),
        taker_asset_amount=int(jsdict["takerAssetAmount"]),
        maker_fee=int(jsdict["makerFee"]),
        taker_fee=int(jsdict["takerFee"]),
        expiration_time_seconds=int(jsdict["expirationTimeSeconds"]),
        salt=int(jsdict["salt"]),
    )
