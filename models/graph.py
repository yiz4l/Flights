from models.flight import Flight
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class Graph(BaseModel):
    cities: List[str] = []
    flights: Dict[str, List[Flight]] = {}

    def __init__(self, flights: List[Flight]) -> None:
        super().__init__()
        for flight in flights:
            self.add_flight(flight)

    def add_flight(self, flight: Flight) -> None:
        if flight.departure_city not in self.cities:
            self.cities.append(flight.departure_city)
            self.flights[flight.departure_city] = []
        if flight.arrival_city not in self.cities:
            self.cities.append(flight.arrival_city)
            self.flights[flight.arrival_city] = []
        self.flights[flight.departure_city].append(flight)

    def find_path(self, departure_city: str, arrival_city: str, departure_time: datetime) -> List[List[Flight]]:
        result = []

        visit = {str: bool}
        for city in self.cities:
            visit[city] = False

        path: List[Flight] = []

        def dfs(departure_city: str, arrival_city: str, time: datetime) -> None:
            if departure_city == arrival_city:
                result.append(path[:])
                return
            visit[departure_city] = True
            for flight in [x for x in self.flights[departure_city] \
                           if 3600 <=(x.departure_datetime - time).seconds <= 86400]:
                if not visit[flight.arrival_city]:
                    path.append(flight)
                    dfs(flight.arrival_city, arrival_city, flight.arrival_datetime)
                    path.pop()
            visit[departure_city] = False

        dfs(departure_city, arrival_city, departure_time)

        return result