from pydantic import BaseModel
from typing import List
from datetime import datetime
from models.ticket import Ticket

class Order(BaseModel):
    id: str
    timestamp: str
    tickets: List[Ticket]
    price: float

    @property
    def timestamp_datetime(self):
        return datetime.strptime(self.timestamp, '%Y-%m-%d %H:%M:%S')