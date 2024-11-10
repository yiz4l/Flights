from models.order import Order
from widgets.flightcard import flightinfo
from widgets.pathmap import MapWidget
from db.database import Database
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import GroupHeaderCardWidget, PushButton, PrimaryPushButton,\
    FluentIcon, IconWidget, InfoBarIcon, BodyLabel

class ordercard(GroupHeaderCardWidget):
    refund_signal = pyqtSignal(Order)
    
    def __init__(self, order: Order):
        super().__init__()
        
        self.order = order
        self.setTitle(f"Order {order.id} | {order.timestamp}")
        
        for ticket in order.tickets:
            ticketLayout = QHBoxLayout()
            ticketLayout.addWidget(flightinfo(ticket.flight))
            ticketLayout.addWidget(BodyLabel(f"Seat: {ticket.type}"))
            passengerLayout = QVBoxLayout()
            passengerLayout.addWidget(BodyLabel(f"Passenger: {ticket.passenger.name}"))
            passengerLayout.addWidget(BodyLabel(f"ID: {ticket.passenger.id}"))
            ticketLayout.addLayout(passengerLayout)
            self.vBoxLayout.addLayout(ticketLayout)
        
        self.bottomLayout = QHBoxLayout()
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintLabel = BodyLabel("Click the map button to view a route map 👉")
        self.mapButton = PushButton(FluentIcon.GLOBE, "Map")
        self.refundButton = PrimaryPushButton(FluentIcon.RETURN, "Refund")
        self.bottomLayout.addWidget(self.hintIcon, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addWidget(self.hintLabel, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addWidget(self.mapButton, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.bottomLayout.addWidget(self.refundButton, 0, alignment=Qt.AlignmentFlag.AlignRight)

        self.vBoxLayout.addLayout(self.bottomLayout)
        
        self.mapButton.clicked.connect(self.on_click_map)
        self.refundButton.clicked.connect(lambda: self.refund_signal.emit(order))
    
    def on_click_map(self):
        airports = []
        for ticket in self.order.tickets:
            if airports.count(ticket.flight.departure_airport) == 0:
                airports.append(ticket.flight.departure_airport)
            if airports.count(ticket.flight.arrival_airport) == 0:
                airports.append(ticket.flight.arrival_airport)
        locations = [Database.query_airport_location(Database.query_airport_code(airport)) for airport in airports]
        w = MapWidget(locations)
        w.show()
    