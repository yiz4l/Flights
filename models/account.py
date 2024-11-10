from typing import Optional, List
from pydantic import BaseModel
from models.passenger import Passenger

class Account(BaseModel):
    username: str
    password: str

    id: str
    name: str

    passengers: List[Passenger] = []