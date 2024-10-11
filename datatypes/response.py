from typing import Optional

from pydantic import BaseModel


class RewardResponse(BaseModel):
    address: Optional[str]
    value: Optional[str]
    proof: Optional[str]
