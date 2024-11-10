from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QVBoxLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, CaptionLabel


class PassengerBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('Enter Passenger Information')
        self.nameLineEdit = LineEdit()
        self.idLineEdit = LineEdit()
        self.phoneLineEdit = LineEdit()

        self.nameLineEdit.setPlaceholderText('Name')
        self.idLineEdit.setPlaceholderText('ID')
        self.phoneLineEdit.setPlaceholderText('Phone Number (Optional)')
        self.nameLineEdit.setClearButtonEnabled(True)
        self.idLineEdit.setClearButtonEnabled(True)

        self.warningLabel = CaptionLabel("Wrong information.")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        self.boxLayout = QVBoxLayout()
        self.boxLayout.addWidget(self.titleLabel)
        self.boxLayout.addWidget(self.nameLineEdit)
        self.boxLayout.addWidget(self.idLineEdit)
        self.boxLayout.addWidget(self.phoneLineEdit)
        self.boxLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        self.viewLayout.addLayout(self.boxLayout)

        self.widget.setMinimumWidth(350)

    def validate(self) -> bool:
        if len(self.nameLineEdit.text()) == 0 or len(self.idLineEdit.text()) != 18:
            self.warningLabel.setHidden(False)
            return False

        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_digits = '10X98765432'

        total_sum = sum(int(self.idLineEdit.text()[i]) * weights[i] for i in range(17))
        check_digit = check_digits[total_sum % 11]

        if self.idLineEdit.text()[-1] != check_digit:
            self.warningLabel.setHidden(False)
            return False

        self.warningLabel.setHidden(True)
        return True