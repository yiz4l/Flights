from uuid import uuid4
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import PushButton, CheckBox, ComboBox, TitleLabel, SingleDirectionScrollArea, CardWidget
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow
from typing import List
from models.order import Order
from db.database import Database
from models.account import Account
from models.flight import Flight
from models.ticket import Ticket
from widgets.flightcard import flightcard
from widgets.pathmap import MapWidget


class flightdetail(FramelessWindow):
    def __init__(self, account: Account, flight: List[Flight]):
        super().__init__()

        self.flight = flight
        self.account = account
        self.total_price = 0

        self.vBoxLayout = QVBoxLayout()
        self.header = flightcard(flight, book_visible=False)

        self.passenger_box = []

        passengers_layout = QVBoxLayout()
        seat_types = ["Economy", "Premium", "First"]
        self.remain = {seat_type: [flight.remain[seat_type] for flight in self.flight] for seat_type in seat_types}
        for passenger in account.passengers:
            self.passenger_box.append((CheckBox(f"{passenger.name} | {passenger.id}"), ComboBox()))
            self.passenger_box[-1][1].addItems(seat_types)
            self.passenger_box[-1][0].setChecked(False)
            self.passenger_box[-1][1].setCurrentIndex(0)
            self.passenger_box[-1][0].stateChanged.connect(self.recalculate_price)
            self.passenger_box[-1][1].currentIndexChanged.connect(self.recalculate_price)
            passenger_layout = QHBoxLayout()
            passenger_layout.addWidget(self.passenger_box[-1][0])
            passenger_layout.addWidget(self.passenger_box[-1][1])
            passenger_card = CardWidget()
            passenger_card.setLayout(passenger_layout)
            passengers_layout.addWidget(passenger_card)
            # passengers_layout.addLayout(passenger_layout)

        passenger_container = QWidget()
        passenger_container.setLayout(passengers_layout)

        scroll_passenger_area = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        scroll_passenger_area.setWidget(passenger_container)
        scroll_passenger_area.setWidgetResizable(True)  # 确保内容自动适应滚动区域大小

        # self.marked_map = MapWidget(map(lambda x: Database.query_airport_location(x.departure_airport), flight))
        locations: List[(float, float)] = []
        for flt in flight:
            if len(locations) == 0 or locations[-1] != Database.query_airport_location(Database.query_airport_code(flt.departure_airport)):
                locations.append(Database.query_airport_location(Database.query_airport_code(flt.departure_airport)))
            locations.append(Database.query_airport_location(Database.query_airport_code(flt.arrival_airport)))
        self.marked_map = MapWidget(locations)

        self.price_label = TitleLabel(f"{self.total_price}")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.price_label.setTextColor(QColor.red)
        self.buy_button = PushButton("Buy")
        self.price_layout = QHBoxLayout()
        self.price_layout.addWidget(self.price_label)
        self.price_layout.addWidget(self.buy_button)

        self.vBoxLayout.addWidget(self.header)
        self.vBoxLayout.addWidget(scroll_passenger_area)
        self.vBoxLayout.addWidget(self.marked_map)
        self.vBoxLayout.addLayout(self.price_layout)
        
        self.buy_button.clicked.connect(self.on_click_buy)

        self.setLayout(self.vBoxLayout)

    def recalculate_price(self):
        self.total_price = 0
        remain = self.remain
        all_seats_available = True

        seat_type_demand = {seat_type: 0 for seat_type in remain.keys()}

        for box in self.passenger_box:
            if box[0].isChecked():
                seat_type = box[1].currentText()
                seat_type_demand[seat_type] += 1
                for flight in self.flight:
                    self.total_price += flight.price[seat_type]

        for seat_type, demand in seat_type_demand.items():
            for remaining in remain[seat_type]:
                if remaining < demand:
                    all_seats_available = False
                    break

        if all_seats_available:
            self.buy_button.setEnabled(True)
            self.buy_button.setText("Buy")
        else:
            self.buy_button.setEnabled(False)
            self.buy_button.setText("No Enough Ticket")

        self.price_label.setText(f"{self.total_price}")

    def on_click_buy(self):
        order = Order(
            id=str(uuid4()),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            tickets=[],
            price=self.total_price
        )
        for box in self.passenger_box:
            if box[0].isChecked():
                seat_type = box[1].currentText()
                for flight in self.flight:
                    order.tickets.append(Ticket(
                        type=seat_type,
                        flight=flight,
                        passenger=self.account.passengers[self.passenger_box.index(box)]
                    ))
        try:
            Database.place_order(self.account, order)
        except Exception as e:
            print(e)
        
        self.close()