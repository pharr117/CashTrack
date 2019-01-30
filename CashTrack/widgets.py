from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QDialog, QGridLayout, QTextEdit, QDoubleSpinBox, QComboBox, QVBoxLayout
from PySide2.QtCore import Qt, Property
from PySide2.QtGui import QColor, QFont


FONT = "Arial Black"
MAIN_COLOR = "#336699"

#   Class: AnimatedLabel
#
#   A class that deifnes a label widget that has a color property to allow
#   for color animations on the text.
#   Parameters:
#       label_text: text placed on the label
class AnimatedLabel(QLabel):

    def __init__(self, label_text):
        super().__init__(label_text)
        self.label_text = label_text
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont(FONT))
        self.setColor(QColor(MAIN_COLOR))

    def setColor(self,color):
        self.setStyleSheet("color: rgb(%d, %d, %d)" % (color.red(), color.green(), color.blue()))
    def getColor(self):
        return Qt.black

    colorProp = Property(QColor, getColor, setColor)

#   Class: BaseButton
#
#   A class that creates a small sized button and connects a slot to the clicked
#   signal
#   Parameters:
#       label_text: the text that is placed on the label
#       callback_func: the function that will be called on button click
class BaseButton(QPushButton):
    def __init__(self, label_text, callback_func):
        super().__init__(label_text)
        self.callback_func = callback_func
        self.clicked.connect(self.callback_func)
        self.setStyleSheet("max-width: 80px; max-height: 40px; color: %s; font: 8pt %s" % (MAIN_COLOR, FONT))

#   Class: BiggerButton
#
#   A class that creates a large sized button and connects a slot to the clicked
#   signal
#   Parameters:
#       label_text: the text that is placed on the label
#       callback_func: the function that will be called on button click
class BiggerButton(QPushButton):
    def __init__(self, label_text, callback_func):
        super().__init__(label_text)
        self.callback_func = callback_func
        self.clicked.connect(self.callback_func)
        self.setStyleSheet("height: 80px; width: 200px; max-width: 100px; max-height: 80px; color: %s" % (MAIN_COLOR))

#   Class: TextEditLabel
#
#   A widget class that holds a label and a text edit,
#   and putting the text passed in on a label
#   Parameters:
#       label_text: the text placed on the label
class TextEditLabel(QWidget):
    def __init__(self, label_text, height):
        super().__init__()
        self.label_text = label_text
        self.height = height
        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        self.label = AnimatedLabel(self.label_text)
        self.edit = QTextEdit()
        self.edit.setFixedHeight(self.height)
        self.edit.setTabChangesFocus(True)

        self.layout.addWidget(self.label, 0,0,1,1)
        self.layout.addWidget(self.edit, 0,1,1,1)
        self.setLayout(self.layout)
        self.setFixedHeight(self.height + 18)

    def getText(self):
        return self.edit.toPlainText()
    def clearEdit(self):
        self.edit.clear()


#   Class: TextEditLabel
#
#   A widget class that holds a label and a spin box,
#   and putting the text passed in on a label
#   Parameters:
#       label_text: the text placed on the label

class SpinBoxLabel(QWidget):
    def __init__(self, label_text):
        super().__init__()
        self.label_text = label_text
        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        self.label = AnimatedLabel(self.label_text)
        self.edit = QDoubleSpinBox()
        self.edit.setFixedHeight(27)
        self.edit.setRange(0, 100000000)
        self.edit.setPrefix("$")
        self.edit.setDecimals(2)

        self.layout.addWidget(self.label, 0,0,1,1)
        self.layout.addWidget(self.edit, 0,1,1,1)
        self.setLayout(self.layout)
        self.setFixedHeight(45)

    def getValue(self):
        return self.edit.value()
    def clearEdit(self):
        self.edit.clear()

#   Class:  LabelDropDown
#
#   A class that defines a widget that has a label and a drop down list
#   allowing picking of a string in a passed in list
#   Parameters:
#       label_text: text placed on the label
#       combo_list: list of strings holding the options
class LabelDropDown(QWidget):
    def __init__(self, label_text, combo_list):
        super().__init__()
        self.label_text = label_text
        self.combo_list = combo_list
        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        self.label = AnimatedLabel(self.label_text)
        self.label.setStyleSheet("color: %s" % MAIN_COLOR)
        self.label.setFont(QFont(FONT))
        self.combo = QComboBox()
        self.combo.addItems(self.combo_list)
        self.combo.setStyleSheet("color: %s" % MAIN_COLOR)
        self.combo.setFont(QFont(FONT))
        self.layout.addWidget(self.label, 0,0,1,1)
        self.layout.addWidget(self.combo, 0,1,1,1)
        self.setLayout(self.layout)
        self.setFixedHeight(45)

    def getText(self):
        return self.combo.currentText()

#       Class: ErrorDialog
#
#       A class that defines an modal dialog describing an error
#       Parameters:
#           label_text: the label that describes the error
class ErrorDialog(QDialog):
    def __init__(self, label_text):
        super().__init__()
        self.setWindowFlags(Qt.Window |
                            Qt.CustomizeWindowHint |
                            Qt.WindowTitleHint |
                            Qt.WindowCloseButtonHint |
                            Qt.WindowStaysOnTopHint)
        self.label_text = label_text
        self.initUI()

    def initUI(self):
        self.setModal(True)
        self.error_label = QLabel(self.label_text)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.error_label)
        self.setWindowTitle("Error")
        self.setLayout(self.layout)
        self.setFixedSize(300, 100)
