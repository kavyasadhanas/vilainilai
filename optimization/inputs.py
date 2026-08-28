from dataclasses import dataclass
from typing import Optional


@dataclass
class DestinationOption:
    """
    One place the farmer could send part of their harvest:
    a market, a buyer/trader offer, or storage.
    """
    id: str                          # e.g. "market_12", "buyer_4", "store"
    kind: str                        # "MARKET" | "BUYER" | "STORE"
    price_per_kg: float              # current price, or predicted price if waiting
    transport_cost_per_kg: float = 0
    commission_per_kg: float = 0
    expected_loss_pct: float = 0     # spoilage as a fraction, e.g. 0.05 = 5%
    capacity_kg: Optional[float] = None   # max this destination can take, None = unlimited
    days_to_realize: int = 0         # 0 = sell today, >0 = wait/store this many days
    storage_cost_per_kg_day: float = 0    # only relevant if kind == "STORE"