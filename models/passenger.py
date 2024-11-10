from pydantic import BaseModel
from typing import Optional


class Passenger(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None