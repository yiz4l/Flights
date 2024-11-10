from pydantic import BaseModel
from models.flight import Flight
from models.passenger import Passenger

class Ticket(BaseModel):
    type: str
    flight: Flight
    passenger: Passenger