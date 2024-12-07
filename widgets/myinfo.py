import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from db.database import Database
from models.account import Account
from models.passenger import Passenger
from widgets.passengerbox import PassengerBox
from qfluentwidgets import AvatarWidget, PushButton, FluentIcon, CardWidget, ElevatedCardWidget,\
    BodyLabel, CaptionLabel, TitleLabel, FlowLayout

class myinfoWidget(QWidget):
    def __init__(self, account: Account, parent=None):
        super().__init__(parent=parent)
    
        self.account = account
        self.vBoxLayout = QVBoxLayout()
        self.userLabel = TitleLabel("My Info")
        self.user_card = userCard(account)
        self.passengerLayout = FlowLayout()
        self.passengerLabel = TitleLabel("My Passengers")
        self.refresh()
        
        self.addPassengerButton = PushButton(FluentIcon.ADD, "Add Passenger")
        self.addPassengerButton.clicked.connect(self.on_click_add_passenger)
        
        self.vBoxLayout.addWidget(self.userLabel)
        self.vBoxLayout.addWidget(self.user_card)
        self.vBoxLayout.addWidget(self.passengerLabel)
        self.vBoxLayout.addLayout(self.passengerLayout)
        self.vBoxLayout.addWidget(self.addPassengerButton)
        
        self.setLayout(self.vBoxLayout)
        
        self.setObjectName("InfoWidget")
    
    def refresh(self):
        self.passengerLayout.removeAllWidgets()
        for passenger in self.account.passengers:
            self.passengerLayout.addWidget(passengerCard(passenger))
    
    def on_click_add_passenger(self):
        w = PassengerBox(self)
        w.show()
        if w.exec():
            print("Add passenger")
            Database.add_passenger(self.account, Passenger(
                id=w.idLineEdit.text(),
                name=w.nameLineEdit.text(),
                phone=None if w.phoneLineEdit.text() == "" else w.phoneLineEdit.text(),
            ))
            self.account = Database.query_userinfo(self.account.username)
            self.refresh()
            # self.passengerLayout.addWidget(passengerCard(w.passenger))
        else:
            print("Cancel add passenger")

class userCard(CardWidget):
    def __init__(self, account: Account):
        super().__init__()
        
        self.account = account
        self.avatar = AvatarWidget()
        self.avatar.setRadius(64)
        self.avatar.setText(account.name)
        
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(BodyLabel(account.username))
        self.vBoxLayout.addWidget(CaptionLabel(f'{account.name} | {account.id}'))
        
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.addWidget(self.avatar)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        
        self.changeInfoButton = PushButton(FluentIcon.EDIT, "Change Info")
        self.changeInfoButton.clicked.connect(self.on_click_change_info)
        self.hBoxLayout.addWidget(self.changeInfoButton)
        
        self.setLayout(self.hBoxLayout)
        
    def on_click_change_info(self):
        print("Change info")

class passengerCard(ElevatedCardWidget):
    def __init__(self, passenger: Passenger):
        super().__init__()
        
        self.passenger = passenger
        self.avatar = AvatarWidget()
        self.avatar.setRadius(32)
        self.avatar.setText(passenger.name)
        
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.avatar)
        self.vBoxLayout.addWidget(BodyLabel(passenger.name))
        self.vBoxLayout.addWidget(CaptionLabel(f'{passenger.id}'))
        
        self.changeInfoButton = PushButton(FluentIcon.EDIT, "Change Info")
        self.changeInfoButton.clicked.connect(self.on_click_change_info)
        self.vBoxLayout.addWidget(self.changeInfoButton)
        
        self.setLayout(self.vBoxLayout)
        
    def on_click_change_info(self):
        print("Change info")