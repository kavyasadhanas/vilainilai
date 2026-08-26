from typing import Dict, Any, Optional

from .farmer_state import FarmerState
from .harvest_state import HarvestState


class DigitalTwin:
    """
    Digital representation of a farmer's harvest,
    constraints, and current market intelligence.
    """

    def __init__(
        self,
        farmer: FarmerState,
        harvest: HarvestState
    ):

        self.farmer = farmer
        self.harvest = harvest

        # Dynamic market intelligence
        self.market_state: Dict[str, Any] = {}

        # Buyer offers
        self.buyer_offers = []

        # Current timestamp/version
        self.state_version = 1

    # ========================================================
    # MARKET STATE
    # ========================================================

    def update_market_state(
        self,
        current_price: float,
        forecast_price: Optional[float] = None,
        demand_direction: Optional[str] = None,
        shock_status: Optional[str] = None,
        market: Optional[str] = None
    ):
        """
        Update the dynamic market information.
        """

        self.market_state = {
            "market": market,
            "current_price_per_kg": current_price,
            "forecast_price_per_kg": forecast_price,
            "demand_direction": demand_direction,
            "shock_status": shock_status
        }

        self.state_version += 1

    # ========================================================
    # BUYER OFFERS
    # ========================================================

    def add_buyer_offer(
        self,
        buyer_name: str,
        price_per_kg: float,
        quantity_kg: float
    ):
        """
        Add a live buyer/trader offer.
        """

        if price_per_kg < 0:
            raise ValueError(
                "Buyer price cannot be negative."
            )

        if quantity_kg <= 0:
            raise ValueError(
                "Buyer quantity must be greater than zero."
            )

        offer = {
            "buyer": buyer_name,
            "price_per_kg": price_per_kg,
            "quantity_kg": quantity_kg
        }

        self.buyer_offers.append(offer)

        self.state_version += 1

    # ========================================================
    # HARVEST UPDATE
    # ========================================================

    def record_sale(
        self,
        quantity_kg: float
    ):
        """
        Update the digital twin after selling part
        of the harvest.
        """

        self.harvest.update_quantity(
            quantity_kg
        )

        self.state_version += 1

    # ========================================================
    # TIME UPDATE
    # ========================================================

    def advance_time(
        self,
        days: float
    ):
        """
        Simulate passage of time and reduce
        remaining shelf life.
        """

        self.harvest.reduce_shelf_life(
            days
        )

        self.state_version += 1

    # ========================================================
    # CURRENT STATE
    # ========================================================

    def get_state(self) -> Dict[str, Any]:
        """
        Return the complete digital twin state.
        """

        return {
            "state_version": self.state_version,

            "farmer": self.farmer.to_dict(),

            "harvest": self.harvest.to_dict(),

            "market": self.market_state,

            "buyer_offers": self.buyer_offers
        }

    # ========================================================
    # OPTIMIZER INPUT
    # ========================================================

    def get_optimizer_input(self) -> Dict[str, Any]:
        """
        Return a simplified state for Member 3's
        optimization engine.
        """

        return {
            "farmer": {
                "location":
                    self.farmer.location,

                "risk_preference":
                    self.farmer.risk_preference
            },

            "harvest": {
                "crop":
                    self.harvest.crop,

                "variety":
                    self.harvest.variety,

                "quantity_kg":
                    self.harvest.quantity_kg,

                "quality":
                    self.harvest.quality,

                "remaining_shelf_life_days":
                    self.harvest.remaining_shelf_life_days,

                "storage_capacity_kg":
                    self.harvest.storage_capacity_kg,

                "storage_cost_per_kg_day":
                    self.harvest.storage_cost_per_kg_day
            },

            "market": self.market_state,

            "buyer_offers":
                self.buyer_offers
        }