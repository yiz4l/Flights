from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFrame
from qfluentwidgets import PushButton, FluentIcon, TitleLabel, SingleDirectionScrollArea
from models.account import Account
from widgets.ordercard import ordercard
from models.order import Order
from db.database import Database

class orderlist(QWidget):
    def __init__(self, account: Account, parent=None):
        super().__init__(parent=parent)
        self.account = account

        # 顶部布局
        self.headerLayout = QHBoxLayout()
        self.titleLabel = TitleLabel("Orders")
        self.refreshButton = PushButton(FluentIcon.SYNC, "Refresh")
        self.refreshButton.clicked.connect(self.refresh)
        self.headerLayout.addWidget(self.titleLabel, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.headerLayout.addWidget(self.refreshButton, 0, alignment=Qt.AlignmentFlag.AlignRight)

        # 主布局
        self.vboxLayout = QVBoxLayout(self)
        self.vboxLayout.addLayout(self.headerLayout)

        # 创建 scrollArea 但不设置布局
        self.scrollArea = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(self.scrollWidget)
        self.vboxLayout.addWidget(self.scrollArea)

        self.setObjectName("OrderWidget")

        # 初始刷新
        self.refresh()

    def refresh(self):
        # 清除 scrollLayout 中的旧控件
        for i in reversed(range(self.scrollLayout.count())):
            widget = self.scrollLayout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # 查询订单并添加到 scrollLayout
        self.orders = Database.query_orders(self.account)
        for order in self.orders:
            orderCard = ordercard(order)
            orderCard.refund_signal.connect(self.refund)
            self.scrollLayout.addWidget(orderCard)

    def refund(self, order: Order):
        Database.refund_order(self.account, order)
        self.refresh()