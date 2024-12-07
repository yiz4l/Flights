from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy
from qfluentwidgets import CardWidget, IconWidget, BodyLabel, StrongBodyLabel, CaptionLabel, PushButton, InfoBadge, InfoBadgePosition
from datetime import datetime
from typing import List
from models.flight import Flight

class flightcard(CardWidget):
    book_signal = pyqtSignal(list)

    def __init__(self, flights: List[Flight], book_visible: bool = True):
        super().__init__()
        self.flights = flights

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        
        departure_time = flights[0].departure_datetime

        for flight in flights:
            self.vBoxLayout.addWidget(flightinfo(flight, departure_time))

        self.bookButton = PushButton("Book")
        self.bookButton.clicked.connect(lambda: self.book_signal.emit(flights))

        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addWidget(self.bookButton)
        
        if not book_visible:
            self.bookButton.hide()

        self.setLayout(self.hBoxLayout)

class flightinfo(QWidget):
    def __init__(self, flight: Flight, departure_time: datetime = None):
        super().__init__()

        if departure_time is None:
            departure_time = flight.departure_datetime
            
        departureDays = (flight.departure_datetime.date() - departure_time.date()).days
        arrivalDays = (flight.arrival_datetime.date() - departure_time.date()).days
        
        self.hBoxLayout = QHBoxLayout(self)
        self.flightInfoBoxLayout = QVBoxLayout()
        self.departureBoxLayOut = QVBoxLayout()
        self.arrivalBoxLayOut = QVBoxLayout()

        self.iconWidget = IconWidget(f'assets/icons/{flight.flt[0:2]}.png')
        self.iconWidget.setFixedSize(48, 48)
        self.companyLabel = StrongBodyLabel(flight.company)
        self.fltLabel = CaptionLabel(flight.flt)
        self.modelLabel = CaptionLabel(flight.model)
        
        self.companyLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.fltLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.modelLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.departureTimeLabel = BodyLabel(flight.departure_time[-8:-3])
        # self.departureTimeBadge = InfoBadge.custom(f'+{departureDays}','#005fb8', '#60cdff')
        self.arrivalTimeLabel = BodyLabel(flight.arrival_time[-8:-3])
        # self.arrivalTimeBadge = InfoBadge.custom(f'+{arrivalDays}','#005fb8', '#60cdff')
        self.departureAirportLabel = CaptionLabel(flight.departure_airport)
        self.arrivalAirportLabel = CaptionLabel(flight.arrival_airport)
        
        if departureDays > 0:
            InfoBadge.success(f'+{departureDays}', parent=self, target=self.departureTimeLabel, position=InfoBadgePosition.TOP_RIGHT)
        if arrivalDays > 0:
            InfoBadge.success(f'+{arrivalDays}', parent=self, target=self.arrivalTimeLabel, position=InfoBadgePosition.TOP_RIGHT)
        
        self.init_ui()

    def init_ui(self):
        self.flightInfoBoxLayout.addWidget(self.companyLabel)
        self.aircraftInfoBoxLayout = QHBoxLayout()
        self.aircraftInfoBoxLayout.addWidget(self.fltLabel)
        self.aircraftInfoBoxLayout.addWidget(self.modelLabel)
        self.flightInfoBoxLayout.addLayout(self.aircraftInfoBoxLayout)

        self.departureBoxLayOut.addWidget(self.departureTimeLabel)
        self.departureBoxLayOut.addWidget(self.departureAirportLabel)
        self.arrivalBoxLayOut.addWidget(self.arrivalTimeLabel)
        self.arrivalBoxLayOut.addWidget(self.arrivalAirportLabel)

        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.flightInfoBoxLayout)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addLayout(self.departureBoxLayOut)
        arrowIcon = IconWidget('assets/pics/arrow.png')
        arrowIcon.setFixedSize(60, 4)
        self.hBoxLayout.addWidget(arrowIcon)
        self.hBoxLayout.addLayout(self.arrivalBoxLayOut)

        self.setLayout(self.hBoxLayout)