from datetime import datetime
from typing import List
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCompleter
from qfluentwidgets import EditableComboBox, SegmentedWidget, TransparentToolButton, FluentIcon, FastCalendarPicker, \
    PushButton, SingleDirectionScrollArea, DropDownPushButton, RoundMenu, Action, SwitchButton
from db.database import Database
from models.account import Account
from models.flight import Flight
from models.graph import Graph
from models.ticket import Ticket
from widgets.flightcard import flightinfo, flightcard
from widgets.flightdetail import flightdetail


class TicketWidget(QWidget):
    def __init__(self, account: Account, parent=None):
        super(TicketWidget, self).__init__(parent)
        self.account = account

        self.available_cities_name = Database.query_available_cities()
        # self.domestic_cities = [x for x in self.available_cities if Database.query_country_code(x) == 'CN']
        # self.available_cities_name = map(lambda x: Database.query_city_name(x), self.available_cities)
        self.domestic_cities_name = [x for x in self.available_cities_name\
            if Database.query_country_code_of_city(Database.query_city_code(x)) == 'CN']

        self.departure_combobox = EditableComboBox()
        self.arrival_combobox = EditableComboBox()

        self.calendar_picker = FastCalendarPicker()
        self.calendar_picker.setDate(QDate.currentDate())

        self.scrollFlightsArea = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)

        self.search_button = PushButton(FluentIcon.SEARCH, "Search")
        self.search_button.clicked.connect(self.on_click_search)

        self.transfer_button = SwitchButton()
        self.transfer_button.setOnText("Transfer Allowed")
        self.transfer_button.setOffText("Transfer Not Allowed")

        self.sort_method = "Price"
        self.sort_button = DropDownPushButton(FluentIcon.FILTER, "Sort")
        self.sort_menu = RoundMenu(parent=self.sort_button)
        self.sort_menu.addAction(Action(FluentIcon.TAG, "Price", triggered=self.on_click_price))
        self.sort_menu.addAction(Action(FluentIcon.SEND, "Duration", triggered=self.on_click_duration))
        self.sort_button.setMenu(self.sort_menu)

        self.init_ui()


    def init_ui(self):
        flights_type_segment = SegmentedWidget()
        flights_type_segment.insertItem(0, "Domestic", "Domestic", self.on_click_domestic)
        flights_type_segment.insertItem(1, "International", "International", self.on_click_international)
        flights_type_segment.setCurrentItem("Domestic")

        self.on_click_domestic()

        swap_button = TransparentToolButton(FluentIcon.SYNC)
        swap_button.clicked.connect(self.on_click_swap)

        self.calendar_picker.dateChanged.connect(lambda date: print(date.toString()))

        TicketLayOut = QVBoxLayout()
        LocationLayOut = QHBoxLayout()
        ParameterLayout = QHBoxLayout()

        LocationLayOut.addWidget(self.departure_combobox)
        LocationLayOut.addWidget(swap_button)
        LocationLayOut.addWidget(self.arrival_combobox)

        ParameterLayout.addWidget(self.calendar_picker)
        ParameterLayout.addWidget(self.transfer_button)
        ParameterLayout.addWidget(self.sort_button)
        ParameterLayout.addWidget(self.search_button)

        TicketLayOut.addWidget(flights_type_segment)
        TicketLayOut.addLayout(LocationLayOut)
        TicketLayOut.addLayout(ParameterLayout)
        TicketLayOut.addWidget(self.scrollFlightsArea)
        
        # self.scrollFlightsArea.hide()
        
        self.setLayout(TicketLayOut)
        
        self.setObjectName("TicketWidget")

    def on_click_domestic(self):
        self.departure_combobox.clear()
        self.arrival_combobox.clear()

        self.departure_combobox.addItems(self.domestic_cities_name)
        self.arrival_combobox.addItems(self.domestic_cities_name)

        # self.departure_combobox.setCurrentIndex(self.domestic_cities.index(self.domestic_cities[0]))
        # self.arrival_combobox.setCurrentIndex(self.domestic_cities.index(self.domestic_cities[1]))

        departure_completer = QCompleter(self.domestic_cities_name, self.departure_combobox)
        arrival_completer = QCompleter(self.domestic_cities_name, self.arrival_combobox)
        departure_completer.setMaxVisibleItems(10)
        arrival_completer.setMaxVisibleItems(10)

        self.departure_combobox.setCurrentText("Beijing")
        self.arrival_combobox.setCurrentText("Shanghai")
        self.departure_combobox.setCompleter(departure_completer)
        self.arrival_combobox.setCompleter(arrival_completer)

    def on_click_international(self):
        self.departure_combobox.clear()
        self.arrival_combobox.clear()

        self.departure_combobox.addItems(self.available_cities_name)
        self.arrival_combobox.addItems(self.available_cities_name)

        # self.departure_combobox.setCurrentIndex(self.domestic_cities.index(self.available_cities[0]))
        # self.arrival_combobox.setCurrentIndex(self.domestic_cities.index(self.available_cities[1]))

        departure_completer = QCompleter(self.available_cities_name, self.departure_combobox)
        arrival_completer = QCompleter(self.available_cities_name, self.arrival_combobox)
        departure_completer.setMaxVisibleItems(10)
        arrival_completer.setMaxVisibleItems(10)

        self.departure_combobox.setCurrentText("Beijing")
        self.arrival_combobox.setCurrentText("New York")
        self.departure_combobox.setCompleter(departure_completer)
        self.arrival_combobox.setCompleter(arrival_completer)

    def on_click_swap(self):
        a = self.departure_combobox.currentText()
        b = self.arrival_combobox.currentText()

        # 使用 setCurrentText 方法交换文本内容
        self.departure_combobox.setCurrentText(b)
        self.arrival_combobox.setCurrentText(a)

    def on_click_search(self):
        departure = self.departure_combobox.currentText()
        arrival = self.arrival_combobox.currentText()
        date = self.calendar_picker.getDate().toPyDate()

        graph = Graph(Database.query_flights())
        flights_plans = graph.find_path(departure, arrival, datetime.combine(date, datetime.min.time()))
        if self.sort_method == "Price":
            flights_plans.sort(key=lambda x: sum([y.price['Economy'] for y in x]))
        else:
            flights_plans.sort(key=lambda x: x[-1].arrival_datetime - x[0].departure_datetime)

        self.scrollFlightsArea.setWidget(None)
        
        cards_widget = QWidget()
        cards_layout = QVBoxLayout(cards_widget)
        for flights in flights_plans:
            if not self.transfer_button.isChecked() and len(flights) > 1:
                continue
            fc = flightcard(flights)
            fc.book_signal.connect(self.on_click_book)
            cards_layout.addWidget(fc)
        cards_widget.setLayout(cards_layout)
        
        self.scrollFlightsArea.setWidget(cards_widget)
        self.scrollFlightsArea.show()

    def on_click_price(self):
        self.sort_method = "Price"
        self.sort_button.setText("Price")

    def on_click_duration(self):
        self.sort_method = "Duration"
        self.sort_button.setText("Duration")

    def on_click_book(self, flights: List[Flight]):
        fd = flightdetail(
            account=self.account,
            flight=flights
        )
        fd.show()