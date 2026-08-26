from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class FarmerState:
    """
    Represents the farmer-specific state used by VilaiNilai.
    """

    farmer_id: str
    location: str
    risk_preference: str = "MEDIUM"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)