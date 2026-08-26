from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class HarvestState:
    """
    Represents the current physical/economic state
    of the farmer's harvest.
    """

    crop: str
    variety: str
    quantity_kg: float
    quality: str
    harvest_date: str
    remaining_shelf_life_days: float
    storage_capacity_kg: float
    storage_cost_per_kg_day: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def update_quantity(self, sold_kg: float):
        """
        Reduce available harvest after a sale.
        """

        if sold_kg < 0:
            raise ValueError(
                "Sold quantity cannot be negative."
            )

        if sold_kg > self.quantity_kg:
            raise ValueError(
                "Sold quantity cannot exceed available harvest."
            )

        self.quantity_kg -= sold_kg

    def reduce_shelf_life(self, days: float):
        """
        Reduce remaining shelf life as time passes.
        """

        if days < 0:
            raise ValueError(
                "Days cannot be negative."
            )

        self.remaining_shelf_life_days = max(
            0,
            self.remaining_shelf_life_days - days
        )