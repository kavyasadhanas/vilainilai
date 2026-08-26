from pydantic import BaseModel
from typing import Any, Optional


class DashboardResponse(BaseModel):
    farmer_id: int
    harvest: Optional[dict[str, Any]] = None
    recommendation: Optional[dict[str, Any]] = None
    alternatives: list[dict[str, Any]] = []