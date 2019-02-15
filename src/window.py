import sys, os

from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QVBoxLayout, QStackedWidget, QLabel, QDockWidget, QGraphicsOpacityEffect, QDialog, QMessageBox
from PySide2.QtCore import Slot, Qt, QPropertyAnimation, QEasingCurve, QJsonDocument, QFile, QIODevice, Property
from PySide2.QtGui import QCloseEvent
from classes import *

MAIN_COLOR = "#336699"


#       Class: MainWindow
#
#       A QMainWindow child class that extends the functionality of QMainWindow.
#       Holds a QStackWidget on the central widget, and docks a next and previous
#       button that will cycle through the stacked widget.
#       Parameters:
#           stack_widgets: A list of widgets placed on the QStackWidget
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setObjectName("Main")
        self.setStyleSheet("QMainWindow#Main{background-color:white}")
        self.curr_page = 0
        self.title = 'CashTrack'
        self.left = 100
        self.top = 100
        self.width = 1280
        self.height = 960
        self.stack_widgets = []
        self.stack_widgets.append(FrontPage(parent=self))
        self.stack_widgets.append(SignInPage(parent=self))
        self.stack_widgets.append(CalendarPage(parent=self))
        self.bar = BarChartPage(parent=self)
        self.stack_widgets.append(self.bar)
        self.pie = PieChartPage(parent=self)
        self.stack_widgets.append(self.pie)
        self.num_pages = len(self.stack_widgets)
        self.curr_widget = self.stack_widgets[0]
        self.curr_user = None
        self.saveDialog = None
        self.changes_saved = False
        self.initUI()

    def closeEvent(self, event):

        if self.curr_user != None and self.changes_saved != True:
            ret = QMessageBox.warning(self, "Save?", "Do you want to save?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            if ret == QMessageBox.Save:
                self.finishSave()
                self.pie.destroy()
                self.bar.destroy()
                event.accept()
            elif ret == QMessageBox.Discard:
                self.pie.destroy()
                self.bar.destroy()
                event.accept()
                super(MainWindow, self).closeEvent(event)
            elif ret == QMessageBox.Cancel:
                event.ignore()
        else:
            event.accept()
            super(MainWindow, self).closeEvent(event)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #stacked widget to hold all the pages
        self.pageStack = QStackedWidget(self)

        #the stacked widgets are all widgets passed to the
        #constructor of the mainwindow class  and will be cyclable
        for x in range(len(self.stack_widgets)):
            self.pageStack.addWidget(self.stack_widgets[x])
        self.setCentralWidget(self.pageStack)

        #adds a dock widget to the bottom containing a next button
        self.buttonDockWidget = QDockWidget()
        self.buttonDockWidget.setStyleSheet("QPushButton {color: %s}" % (MAIN_COLOR))
        self.buttonDockWidget.setAllowedAreas(Qt.BottomDockWidgetArea)

        #adding a widget that holds the button allows for layout in the dock
        #area
        self.buttonWidget = QWidget()
        self.dockLayout = QGridLayout()

        self.nextButton = BaseButton("Next", self.cycle_forward)
        self.prevButton = BaseButton("Prev", self.cycle_back)
        self.prevButton.hide()
        self.prevButton.setEnabled(False)

        self.dockLayout.addWidget(self.prevButton, 0, 0)
        self.dockLayout.addWidget(self.nextButton, 0, 1)
        self.dockLayout.setAlignment(Qt.AlignRight)
        self.buttonWidget.setLayout(self.dockLayout)

        #put the the forward and backward button
        #on the widget that will be put on the dock
        self.buttonDockWidget.setWidget(self.buttonWidget)
        self.buttonDockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)

        #put empty widget on the title bar to make it empty
        self.buttonDockWidget.setTitleBarWidget(QWidget())
        self.addDockWidget(Qt.BottomDockWidgetArea, self.buttonDockWidget)

        self.saveButtonWidget = QWidget()
        self.saveButtonWidgetLayout = QVBoxLayout()
        self.saveButtonWidgetLayout.setAlignment(Qt.AlignLeft)
        self.saveButton = BaseButton("Save", self.save)
        self.saveButtonWidgetLayout.addWidget(self.saveButton)
        self.saveButtonWidget.setLayout(self.saveButtonWidgetLayout)

        self.saveButtonDockWidget = QDockWidget()
        self.saveButtonDockWidget.setAllowedAreas(Qt.TopDockWidgetArea)
        self.saveButtonDockWidget.setTitleBarWidget(QWidget())
        self.saveButtonDockWidget.setWidget(self.saveButtonWidget)
        self.addDockWidget(Qt.TopDockWidgetArea, self.saveButtonDockWidget)
        self.saveButton.hide()

        self.menu_bar = self.menuBar()

        self.show()
        self.fade_in(self.buttonWidget, 2000)

    def fade_in(self, widget, duration):
        self.effect = QGraphicsOpacityEffect(self)
        widget.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.InBack)
        self.anim.start()

    def fade_out(self, widget, duration, endFunc):
        self.effect = QGraphicsOpacityEffect(self)
        widget.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)

        #out back describes an easing function that deccelerates slowly to zero
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()
        #connecting a function to the end of the fade out can be used to
        #transition out of the animation to the next phase
        self.anim.finished.connect(endFunc)

    @Slot()
    def cycle_forward(self):
        self.curr_page+=1
        if self.curr_page == 3:
            self.prevButton.show()
            self.prevButton.setEnabled(True)
        if self.curr_page == 2:
            self.saveButton.show()
        if not self.curr_page >= 2:
            self.nextButton.setEnabled(False)
            self.prevButton.setEnabled(False)
        elif self.curr_page == self.num_pages - 1:
            self.nextButton.setEnabled(False)
            self.prevButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(True)
            self.prevButton.setEnabled(True)
        self.fade_out(self.curr_widget, 500, self.finishedNext)
        self.curr_widget = self.stack_widgets[self.curr_page]

    @Slot()
    def cycle_back(self):
        self.curr_page -= 1
        if self.curr_page == 2:
            self.prevButton.setEnabled(False)
            self.nextButton.setEnabled(True)
        else:
            self.prevButton.setEnabled(True)
            self.nextButton.setEnabled(True)
        self.fade_out(self.curr_widget, 500, self.finishedNext)
        self.curr_widget = self.stack_widgets[self.curr_page]

    @Slot()
    def finishedNext(self):
        self.fade_in(self.curr_widget, 1000)
        self.pageStack.setCurrentIndex(self.curr_page)

    @Slot()
    def save(self):
        self.saveDialog = QDialog()
        self.saveDialog.setWindowFlags(Qt.Window |
                            Qt.CustomizeWindowHint |
                            Qt.WindowTitleHint |
                            Qt.WindowCloseButtonHint |
                            Qt.WindowStaysOnTopHint)
        self.saveDialog.setWindowTitle("Saving")
        self.saveDialog.setFixedSize(300, 100)
        self.saveDialog.setModal(True)
        self.saveLayout = QGridLayout()
        self.saveLayout.setAlignment(Qt.AlignCenter)
        self.saveLabel = QLabel("Save username %s?" % (self.username))
        self.saveButton = BaseButton("Okay", self.finishSave)
        self.saveLayout.addWidget(self.saveLabel)
        self.saveLayout.addWidget(self.saveButton)
        self.saveDialog.setLayout(self.saveLayout)

        self.saveDialog.show()

    @Slot()
    def finishSave(self):
        if self.saveDialog != None:
            self.saveDialog.hide()
            del self.saveDialog
            self.saveDialog = None
        saveDocument = QJsonDocument(self.dataDoc)
        saveFile = QFile()
        saveFile.setFileName("./assets/data.json")
        saveFile.open(QIODevice.WriteOnly)
        saveFile.write(saveDocument.toJson())
        saveFile.close()
        self.changes_saved = True

    def resetNext(self):
        self.nextButton.setEnabled(True)

    #called from the sign in page widget to set the current user object
    def setUser(self, user, username, dataDoc):
        self.changes_saved = True
        self.curr_user = user
        self.username = username
        self.dataDoc = dataDoc

    def setChangesSaved(self, val):
        self.changes_saved = val

if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = MainWindow()

    sys.exit(app.exec_())
