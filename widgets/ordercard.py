from models.order import Order
from widgets.flightcard import flightinfo
from widgets.pathmap import MapWidget
from db.database import Database
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import GroupHeaderCardWidget, PushButton, PrimaryPushButton,\
    FluentIcon, IconWidget, InfoBarIcon, BodyLabel
from typing import List

class ordercard(GroupHeaderCardWidget):
    refund_signal = pyqtSignal(Order)
    
    def __init__(self, order: Order):
        super().__init__()
        
        self.order = order
        self.setTitle(f"Order {order.id} | {order.timestamp}")
        up = True
        
        for ticket in order.tickets:
            ticketLayout = QHBoxLayout()
            ticketLayout.addWidget(flightinfo(ticket.flight))
            ticketLayout.addWidget(BodyLabel(f"Seat: {ticket.type}"))
            if ticket.type == 'Premium':
                up = False
            passengerLayout = QVBoxLayout()
            passengerLayout.addWidget(BodyLabel(f"Passenger: {ticket.passenger.name}"))
            passengerLayout.addWidget(BodyLabel(f"ID: {ticket.passenger.id}"))
            ticketLayout.addLayout(passengerLayout)
            self.vBoxLayout.addLayout(ticketLayout)
        
        self.bottomLayout = QHBoxLayout()
        self.upgrades = PushButton(FluentIcon.UP, "Upgrades")
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintLabel = BodyLabel("Click the map button to view a route map 👉")
        self.refundButton = PrimaryPushButton(FluentIcon.RETURN, "Refund")
        self.mapButton = PushButton(FluentIcon.GLOBE, "Map")
        self.bottomLayout.addWidget(self.upgrades, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addWidget(self.hintIcon, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addWidget(self.hintLabel, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addWidget(self.mapButton, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.bottomLayout.addWidget(self.refundButton, 0, alignment=Qt.AlignmentFlag.AlignRight)

        self.vBoxLayout.addLayout(self.bottomLayout)
        
        self.upgrades.clicked.connect(self.on_click_upgrade)
        self.mapButton.clicked.connect(self.on_click_map)
        self.refundButton.clicked.connect(lambda: self.refund_signal.emit(order))

        if not up:
            self.upgrades.setEnabled(False)

    def on_click_map(self):
        locations: List[tuple] = []
        
        # 处理第一个机票
        if len(self.order.tickets) > 0:
            first_ticket = self.order.tickets[0]
            first_dep = Database.query_airport_location(Database.query_airport_code(first_ticket.flight.departure_airport))
            first_arr = Database.query_airport_location(Database.query_airport_code(first_ticket.flight.arrival_airport))
            locations.extend([first_dep, first_arr])
        
        # 处理后续机票
        for i in range(1, len(self.order.tickets)):
            current_ticket = self.order.tickets[i]
            dep_loc = Database.query_airport_location(Database.query_airport_code(current_ticket.flight.departure_airport))
            arr_loc = Database.query_airport_location(Database.query_airport_code(current_ticket.flight.arrival_airport))
            
            # 如果当前航班的出发地与上一个航班的到达地不同，则添加新的出发地
            if dep_loc != locations[-1]:
                locations.append(dep_loc)
            locations.append(arr_loc)
        
        self.w = MapWidget(locations)
        self.w.resize(800, 600)
        self.w.show()

    def on_click_upgrade(self):
        Database.upgrade_order(self.order.tickets)
    