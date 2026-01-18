from typing import NotRequired, TypedDict


class DeribitIndexPriceResult(TypedDict):
    estimated_delivery_price: float
    index_price: float


class DeribitResponse(TypedDict):
    jsonrpc: str
    result: DeribitIndexPriceResult
    usIn: int
    usOut: NotRequired[int]
    usDiff: NotRequired[int]
    testnet: NotRequired[bool]
