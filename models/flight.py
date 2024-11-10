from typing import Dict
from pydantic import BaseModel
from datetime import datetime

class Flight(BaseModel):
    flt: str
    company: str
    model: str

    price: Dict[str, float]
    remain: Dict[str, int]

    departure_city: str
    arrival_city: str

    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str

    @property
    def departure_datetime(self):
        return datetime.strptime(self.departure_time, '%Y-%m-%d %H:%M:%S')

    @property
    def arrival_datetime(self):
        return datetime.strptime(self.arrival_time, '%Y-%m-%d %H:%M:%S')