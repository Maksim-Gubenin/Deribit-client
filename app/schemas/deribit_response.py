from typing import NotRequired, TypedDict


class DeribitIndexPriceResult(TypedDict):
    """
    TypedDict for Deribit API index price result data.
    """

    estimated_delivery_price: float
    index_price: float


class DeribitResponse(TypedDict):
    """
    Complete TypedDict for Deribit API JSON-RPC 2.0 responses.
    """

    jsonrpc: str
    result: DeribitIndexPriceResult
    usIn: int
    usOut: NotRequired[int]
    usDiff: NotRequired[int]
    testnet: NotRequired[bool]
