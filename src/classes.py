import os

from PySide2.QtWidgets import QWidget, QFrame, QGridLayout, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QTextEdit, QCheckBox, QCalendarWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QProgressBar, QRadioButton, QGroupBox
from PySide2.QtCore import QDir, Slot, Qt, QPropertyAnimation, QEasingCurve, QJsonDocument, QFile, QIODevice, Property, QDate
from PySide2.QtGui import QPixmap, QFont, QColor, QTextCharFormat, QBrush, QPen, QPainter
from PySide2.QtCharts import QtCharts

from widgets import *

FONT = "Arial Black"
MAIN_COLOR = "#336699"
SECONDARY_COLOR = "#996633"
ERROR_COLOR = "#FF0000"
PAY_PERIODS = ["Monthly", "Semi-monthly", "Bi-weekly", "Weekly", "Tips"]
INCOME_TYPES = ["Primary Job", "Secondary Job", "Gift"]
EXPENSE_TYPES = ["Personal", "Debt", "Rent", "Mortgage", "Car Insurance", "House Insurance", "Life Insurance", "Health Insurance", "Child Expense", "Gift", "Travel", "Education", "Food", "Restaurant", "Bar", "Grocery", "Car Repair", "Gasoline", "Shopping", "Luxuries", "Entertainment", "Hobbies", "Alcohol", "Tobacco", "Other"]
TIMELINE_OPTIONS = ["","All Time", "Year", "Month"]
TRANSACTION_TYPES = ["", "Incomes", "Expenses", "Net", "Both", "Type", "Keyword"]

#       class: PieChartPage
#
#       A class that defines a widget that will hold a pie chart and options
#       to generate a specific pie chart.
class PieChartPage(QWidget):
    def __init__(self, parent=None):
        super(PieChartPage, self).__init__(parent)
        self.initUI()
        self.curr_user = None
        self.years_choice = None
        self.months_choice = None
        self.days_choice = None
        self.chart = None
        self.series = None

        self.colors = [MAIN_COLOR, SECONDARY_COLOR, "#993366", "#669933", "#333399", "#ECA742", "#F92232", "#17A798","#FF8023", "#94DE00" ,"#8D1EB1", "#99EC20", "#BE006B", "#EDB800", "#733100", "#596E00", "#00473F", "#690018", "#20074E", "#A79C61", "#3E6A61", "#544772", "#A77C61", "#D07DED", "#FFA581", "#79EEBC", "#F6FE81", "#666104"]

    def destroy(self):
        if self.series != None and self.chart != None:
            self.chart.removeSeries(self.series)

    def initUI(self):
        self.layout = QGridLayout()
        self.setStyleSheet("font: %s; color: %s" % (FONT, MAIN_COLOR))
        self.layout.setAlignment(Qt.AlignLeft)
        self.options_holder = QWidget()
        self.options_layout = QGridLayout()
        self.options_layout.setAlignment(Qt.AlignCenter)

        #under chart placeholder
        self.place_hold = QFrame()
        self.place_hold.setFixedSize(700, 202)
        self.place_hold.setStyleSheet("background-color: %s; border-style: inset; border-radius: 10; border-color: %s" % (MAIN_COLOR, MAIN_COLOR))

        self.time_box = QGroupBox()
        self.time_box.setTitle("Time:")
        self.time_box.setFixedSize(350, 195)
        self.time_box.hide()
        self.time_layout = QVBoxLayout()
        self.time_box.setLayout(self.time_layout)

        self.small_place_hold = QFrame()
        self.small_place_hold.setFixedSize(350, 195)
        self.small_place_hold.setStyleSheet("background-color: %s; border-style: inset; border-radius: 10; border-color: %s" % (MAIN_COLOR, MAIN_COLOR))
        self.small_place_hold.hide()

        #time line group box
        self.timeline_options = QGroupBox()
        self.timeline_options.setFixedSize(150, 150)
        self.timeline_layout = QVBoxLayout()
        self.timeline_options.setTitle("Timeline:")

        self.all_time = QRadioButton("All Time")
        self.all_time.setChecked(True)
        self.all_time.toggled.connect(self.disallowTime)
        self.year = QRadioButton("Year")
        self.year.toggled.connect(self.allowTime)
        self.month = QRadioButton("Month")
        self.month.toggled.connect(self.allowTime)
        self.day = QRadioButton("Day")
        self.day.toggled.connect(self.allowTime)

        self.timeline_layout.addWidget(self.all_time)
        self.timeline_layout.addWidget(self.year)
        self.timeline_layout.addWidget(self.month)
        self.timeline_layout.addWidget(self.day)

        self.timeline_options.setLayout(self.timeline_layout)

        #data group box
        self.data_options = QGroupBox()
        self.data_options.setFixedSize(150, 150)
        self.data_layout = QVBoxLayout()
        self.data_options.setTitle("Data:")

        self.income_expense = QRadioButton("Income/Expense")
        self.income_expense.setChecked(True)
        self.income_expense.toggled.connect(self.untoggleAll)
        self.all_types = QRadioButton("All Types")
        self.all_types.toggled.connect(self.toggleAll)
        self.certain_types = QRadioButton("Certain Types")
        self.certain_types.toggled.connect(self.allowToggle)

        self.data_layout.addWidget(self.income_expense)
        self.data_layout.addWidget(self.all_types)
        self.data_layout.addWidget(self.certain_types)

        self.data_options.setLayout(self.data_layout)

        #transaction type group box
        self.type_options = QGroupBox()
        self.type_options.setFixedSize(310, 560)
        self.type_options.setTitle("Types:")
        self.type_layout = QGridLayout()

        self.income_options = QGroupBox()
        self.income_options.setTitle("Income:")
        self.income_layout = QVBoxLayout()
        self.income_options.setLayout(self.income_layout)
        self.income_options.setEnabled(False)


        self.income_checks = []
        for i in range(len(INCOME_TYPES)):
            new_check = QCheckBox(INCOME_TYPES[i])
            self.income_checks.append(new_check)
            self.income_layout.addWidget(new_check)

        self.expense_options = QGroupBox()
        self.expense_options.setTitle("Expense:")
        self.expense_layout = QVBoxLayout()
        self.expense_options.setLayout(self.expense_layout)
        self.expense_options.setEnabled(False)

        self.expense_checks = []
        for i in range(len(EXPENSE_TYPES)):
            new_check = QCheckBox(EXPENSE_TYPES[i])
            self.expense_checks.append(new_check)
            self.expense_layout.addWidget(new_check)

        self.type_layout.addWidget(self.income_options, 0,0,1,1)
        self.type_layout.addWidget(self.expense_options, 0,1,1,1)
        self.type_options.setLayout(self.type_layout)

        #generate button
        self.gen = BaseButton("Generate", self.generateChart)


        self.bar_holder = QWidget()
        self.bar_holder.setFixedSize(150, 40)

        self.bar_layout = QVBoxLayout()
        self.bar = QProgressBar()
        self.bar.setFixedSize(150, 40)
        self.bar.setMinimum(0)
        self.bar.setMaximum(0)
        self.bar.setOrientation(Qt.Horizontal)
        self.bar.hide()
        self.bar_layout.addWidget(self.bar)
        self.bar_holder.setLayout(self.bar_layout)

        self.options_layout.addWidget(self.timeline_options, 0, 0, 1, 1)
        self.options_layout.addWidget(self.data_options, 0, 1, 1, 1)
        self.options_layout.addWidget(self.type_options, 1,0, 1, 2)
        self.options_layout.addWidget(self.gen, 2, 0, 1, 1)
        self.options_layout.addWidget(self.bar_holder, 2, 1, 1, 1)
        self.options_holder.setLayout(self.options_layout)

        #chart holder
        self.chart_holder = QtCharts.QChartView()
        self.chart_holder.setFixedSize(700, 580)
        self.chart_holder.setRenderHint(QPainter.Antialiasing)

        self.layout.addWidget(self.options_holder, 0, 0, 3, 1)
        self.layout.addWidget(self.chart_holder, 0, 1, 2, 2)
        self.layout.addWidget(self.place_hold, 2, 1, 1, 2)
        self.layout.addWidget(self.time_box, 2, 1, 1, 1)
        self.layout.addWidget(self.small_place_hold, 2, 2, 1, 1)
        self.setLayout(self.layout)

    def setCurrUser(self, user):
        self.curr_user = user

    @Slot()
    def toggleAll(self, checked):
        if checked:
            for i in self.income_checks:
                i.setChecked(True)
            for i in self.expense_checks:
                i.setChecked(True)


            self.income_options.setEnabled(False)
            self.expense_options.setEnabled(False)

    @Slot()
    def untoggleAll(self, checked):
        if checked:
            for i in self.income_checks:
                i.setChecked(False)
            for i in self.expense_checks:
                i.setChecked(False)

            self.income_options.setEnabled(False)
            self.expense_options.setEnabled(False)

    @Slot()
    def allowToggle(self, checked):
        if checked:
            self.income_options.setEnabled(True)
            self.expense_options.setEnabled(True)

    @Slot()
    def allowTime(self, checked):
        if self.years_choice != None:
            self.years_choice.hide()
            del self.years_choice
            self.years_choice = None
        if self.months_choice != None:
            self.months_choice.hide()
            del self.months_choice
            self.months_choice = None
        if self.days_choice != None:
            self.days_choice.hide()
            del self.days_choice
            self.days_choice = None

        if checked:
            self.place_hold.hide()
            self.time_box.show()
            self.small_place_hold.show()
        if self.year.isChecked():
            years = list(self.curr_user["transactions"].keys())
            years.sort()
            self.years_choice = LabelDropDown("Year:", years)
            self.time_layout.addWidget(self.years_choice)
        if self.month.isChecked():
            years = list(self.curr_user["transactions"].keys())
            years.sort()
            self.years_choice = LabelDropDown("Year:", years)
            self.years_choice.combo.currentIndexChanged.connect(self.changeMonths)
            self.time_layout.addWidget(self.years_choice)
            if len(years) != 0:
                curr_months = list(self.curr_user["transactions"][self.years_choice.getText()].keys())
                curr_months.sort()
            else:
                curr_months = []
            self.months_choice = LabelDropDown("Month:", curr_months)
            self.time_layout.addWidget(self.months_choice)
        if self.day.isChecked():
            years = list(self.curr_user["transactions"].keys())
            self.years_choice = LabelDropDown("Year:", years)
            self.years_choice.combo.currentIndexChanged.connect(self.changeMonthsAndDays)
            self.time_layout.addWidget(self.years_choice)
            if len(years) != 0:
                curr_months = list(self.curr_user["transactions"][self.years_choice.getText()].keys())
                curr_months.sort()
            else:
                curr_months = []
            self.months_choice = LabelDropDown("Month:", curr_months)
            self.months_choice.combo.currentIndexChanged.connect(self.changeDays)
            self.time_layout.addWidget(self.months_choice)
            if len(curr_months) != 0:
                curr_days = list(self.curr_user["transactions"][self.years_choice.getText()][self.months_choice.getText()].keys())
                curr_days.sort()
            else:
                curr_days = []
            self.days_choice = LabelDropDown("Days:", curr_days)
            self.time_layout.addWidget(self.days_choice)

    @Slot()
    def disallowTime(self, checked):
        if checked:
            self.time_box.hide()
            self.small_place_hold.hide()
            self.place_hold.show()

    @Slot()
    def changeMonths(self, index):
        self.months_choice.combo.clear()
        new_months = list(self.curr_user["transactions"][self.years_choice.getText()].keys())
        new_months.sort()
        self.months_choice.combo.addItems(new_months)

    @Slot()
    def changeMonthsAndDays(self, index):
        self.months_choice.combo.clear()
        new_months = list(self.curr_user["transactions"][self.years_choice.getText()].keys())
        new_months.sort()
        self.months_choice.combo.addItems(new_months)
        self.days_choice.combo.clear()
        new_days = list(self.curr_user["transactions"][self.years_choice.getText()][self.months_choice.getText()].keys())
        new_days.sort()
        self.days_choice.combo.addItems(new_days)

    @Slot()
    def changeDays(self, index):
        self.days_choice.combo.clear()
        if self.months_choice.getText() != "":
            new_days = list(self.curr_user["transactions"][self.years_choice.getText()][self.months_choice.getText()].keys())
            new_days.sort()
            self.days_choice.combo.addItems(new_days)

    @Slot()
    def generateChart(self):

        def gatherData():
            return_data = None

            #data for the all time graph
            if self.all_time.isChecked():
                if self.income_expense.isChecked():
                    return_data = {"title": "All Time - Income/Expense", "data": {"Incomes": 0, "Expenses": 0}}
                    data = self.curr_user["transactions"]
                    for year in data.keys():
                        for month in data[year].keys():
                            for day in data[year][month].keys():
                                self.bar.setValue(self.bar.value() + 1)
                                for income in data[year][month][day]["income"]:
                                    return_data["data"]["Incomes"] += income[0]
                                for expense in data[year][month][day]["expense"]:
                                    return_data["data"]["Expenses"] += expense[0]

                    return_data["data"]["Incomes"] = round(return_data["data"]["Incomes"], 2)
                    return_data["data"]["Expenses"] = round(return_data["data"]["Expenses"], 2)

                else:
                    title = "All Time - "
                    if self.all_types.isChecked():
                        title += "All Types"
                    else:
                        title += "Picked Types"
                    return_data = {"title": title}
                    data = self.curr_user["transactions"]
                    trans_data = {}
                    for x in self.income_checks:
                        if x.isChecked():
                            trans_data[x.text()] = 0
                    for x in self.expense_checks:
                        if x.isChecked():
                            trans_data[x.text()] = 0
                    return_data["data"] = trans_data

                    for year in data.keys():
                        for month in data[year].keys():
                            for day in data[year][month].keys():
                                self.bar.setValue(self.bar.value() + 1)
                                for income in data[year][month][day]["income"]:
                                    if income[1] in return_data["data"].keys():
                                        return_data["data"][income[1]] += income[0]
                                for expense in data[year][month][day]["expense"]:
                                    if expense[1] in return_data["data"].keys():
                                        return_data["data"][expense[1]] += expense[0]

                    for x in return_data["data"].keys():
                        return_data["data"][x] = round(return_data["data"][x], 2)

            elif self.year.isChecked():
                if self.income_expense.isChecked():
                    data = self.curr_user["transactions"]
                    year = self.years_choice.getText()
                    return_data = {"title": "Year %s - Income/Expense" % (year), "data": {"Incomes": 0, "Expenses": 0}}
                    for month in data[year].keys():
                        for day in data[year][month].keys():
                            self.bar.setValue(self.bar.value() + 1)
                            for income in data[year][month][day]["income"]:
                                return_data["data"]["Incomes"] += income[0]
                            for expense in data[year][month][day]["expense"]:
                                return_data["data"]["Expenses"] += expense[0]
                    return_data["data"]["Incomes"] = round(return_data["data"]["Incomes"], 2)
                    return_data["data"]["Expenses"] = round(return_data["data"]["Expenses"], 2)
                else:
                    data = self.curr_user["transactions"]
                    year = self.years_choice.getText()
                    title = "Year %s - " % (year)
                    if self.all_types.isChecked():
                        title += "All Types"
                    else:
                        title += "Picked Types"
                    return_data = {"title": title}

                    trans_data = {}
                    for x in self.income_checks:
                        if x.isChecked():
                            trans_data[x.text()] = 0
                    for x in self.expense_checks:
                        if x.isChecked():
                            trans_data[x.text()] = 0
                    return_data["data"] = trans_data

                    for month in data[year].keys():
                        for day in data[year][month].keys():
                            self.bar.setValue(self.bar.value() + 1)
                            for income in data[year][month][day]["income"]:
                                if income[1] in return_data["data"].keys():
                                    return_data["data"][income[1]] += income[0]
                            for expense in data[year][month][day]["expense"]:
                                if expense[1] in return_data["data"].keys():
                                    return_data["data"][expense[1]] += expense[0]
                    for x in return_data["data"].keys():
                        return_data["data"][x] = round(return_data["data"][x], 2)

            elif self.month.isChecked():
                if self.income_expense.isChecked():
                    data = self.curr_user["transactions"]
                    year = self.years_choice.getText()
                    month = self.months_choice.getText()
                    return_data = {"title": "Month %s/%s - Income/Expense" % (month, year), "data": {"Incomes": 0, "Expenses": 0}}
                    for day in data[year][month].keys():
                        self.bar.setValue(self.bar.value() + 1)
                        for income in data[year][month][day]["income"]:
                            return_data["data"]["Incomes"] += income[0]
                        for expense in data[year][month][day]["expense"]:
                            return_data["data"]["Expenses"] += expense[0]
                    return_data["data"]["Incomes"] = round(return_data["data"]["Incomes"], 2)
                    return_data["data"]["Expenses"] = round(return_data["data"]["Expenses"], 2)
                else:
                    data = self.curr_user["transactions"]
                    year = self.years_choice.getText()
                    month = self.months_choice.getText()
                    title = "Month %s/%s - " % (month, year)
                    if self.all_types.isChecked():
                        title += "All Types"
                    else:
                        title += "Picked Types"
                    return_data = {"title": title}

                    trans_data = {}
                    for x in self.income_checks:
                        if x.isChecked():
                            trans_data[x.text()] = 0
                    for x in self.expense_checks:
                        if x.isChecked():
                            trans_data[x.text()] = 0
                    return_data["data"] = trans_data

                    for day in data[year][month].keys():
                        self.bar.setValue(self.bar.value() + 1)
                        for income in data[year][month][day]["income"]:
                            if income[1] in return_data["data"].keys():
                                return_data["data"][income[1]] += income[0]
                        for expense in data[year][month][day]["expense"]:
                            if expense[1] in return_data["data"].keys():
                                return_data["data"][expense[1]] += expense[0]
                    for x in return_data["data"].keys():
                        return_data["data"][x] = round(return_data["data"][x], 2)

            elif self.day.isChecked():
                if self.income_expense.isChecked():
                    data = self.curr_user["transactions"]
                    year = self.years_choice.getText()
                    month = self.months_choice.getText()
                    day = self.days_choice.getText()

                    return_data = {"title": "Day %s/%s/%s - Income/Expense" % (month, day, year), "data": {"Incomes": 0, "Expenses": 0}}
                    for income in data[year][month][day]["income"]:
                        self.bar.setValue(self.bar.value() + 1)
                        return_data["data"]["Incomes"] += income[0]
                    for expense in data[year][month][day]["expense"]:
                        self.bar.setValue(self.bar.value() + 1)
                        return_data["data"]["Expenses"] += expense[0]
                    return_data["data"]["Incomes"] = round(return_data["data"]["Incomes"], 2)
                    return_data["data"]["Expenses"] = round(return_data["data"]["Expenses"], 2)
                else:
                    data = self.curr_user["transactions"]
                    year = self.years_choice.getText()
                    month = self.months_choice.getText()
                    day = self.days_choice.getText()
                    title = "Day %s/%s/%s - " % (month, day, year)
                    if self.all_types.isChecked():
                        title += "All Types"
                    else:
                        title += "Picked Types"
                    return_data = {"title": title}

                    trans_data = {}
                    for x in self.income_checks:
                        if x.isChecked():
                            trans_data[x.text()] = 0
                    for x in self.expense_checks:
                        if x.isChecked():
                            trans_data[x.text()] = 0
                    return_data["data"] = trans_data

                    for income in data[year][month][day]["income"]:
                        self.bar.setValue(self.bar.value() + 1)
                        if income[1] in return_data["data"].keys():
                            return_data["data"][income[1]] += income[0]
                    for expense in data[year][month][day]["expense"]:
                        self.bar.setValue(self.bar.value() + 1)
                        if expense[1] in return_data["data"].keys():
                            return_data["data"][expense[1]] += expense[0]
                    for x in return_data["data"].keys():
                        return_data["data"][x] = round(return_data["data"][x], 2)

            return return_data

        data = self.showProgress(gatherData)

        if self.chart != None:
            chart = self.chart_holder.chart()
            self.chart.hide()
            self.chart.removeSeries(self.series)
        self.chart = QtCharts.QChart()

        self.series = QtCharts.QPieSeries()
        for key in data["data"].keys():
            if data["data"][key] != 0:
                self.series.append(key, data["data"][key])
        color_count = 0
        for slice in self.series.slices():
            slice.setLabel("%s - $%.2f" % (slice.label(), slice.value()))
            slice.setColor(QColor(self.colors[color_count]))
            color_count += 1
        self.chart.addSeries(self.series)
        self.chart.setTitle(data["title"] + " ---- Total: $%.2f" % (self.series.sum()))
        self.legend = self.chart.legend()
        self.legend.detachFromChart()
        self.legend.setGeometry(10, 20, 200, 1000)
        self.chart_holder.setChart(self.chart)

    def showProgress(self, func, *pargs, **kargs):
        self.bar.show()
        self.bar.setValue(1)
        ret = func(*pargs, **kargs)
        self.bar.hide()
        return ret

#       class: BarChartPage
#
#       A class that defines a widget that will hold a bar chart and options
#       to generate a specific bar chart.
class BarChartPage(QWidget):

    def __init__(self, parent=None):
        super(BarChartPage, self).__init__(parent)
        self.curr_user = None
        self.available_years = None
        self.year_options = None
        self.month_options = None
        self.type_options = None
        self.data_options = None
        self.data_options2 = None
        self.search_edit = None
        self.gen_button = None
        self.cancel_button = None
        self.chart = None
        self.set = None
        self.axisX = None
        self.axisY = None
        self.series = None
        self.curr_row = 0
        self.initUI()

    def destroy(self):
        if self.series != None and self.chart != None:
            self.chart.removeSeries(self.series)

    def initUI(self):
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.options_widget = QFrame()
        self.options_widget.setFixedSize(300, 300)
        self.options_widget.setStyleSheet(".QFrame{border: 3px solid; border-color: %s; border-radius: 10px; border-style:inset;}" % (MAIN_COLOR))

        self.options_layout = QGridLayout()
        self.options_layout.setAlignment(Qt.AlignTop| Qt.AlignLeft)

        self.timeline_options = LabelDropDown("Timeline:", TIMELINE_OPTIONS)
        self.timeline_options.combo.setFocusPolicy(Qt.StrongFocus)
        self.timeline_options.combo.currentIndexChanged.connect(self.timelinePicked)

        self.options_layout.addWidget(self.timeline_options, self.curr_row, 0, 1, 3)
        self.curr_row += 1
        self.options_widget.setLayout(self.options_layout)

        self.chartHolder = QtCharts.QChartView()
        self.chartHolder.setFixedSize(750, 600)
        self.chartHolder.setRubberBand(QtCharts.QChartView.HorizontalRubberBand)

        self.progress_holder = QWidget()
        self.progress_holder.setFixedSize(300, 100)
        self.progress_layout = QVBoxLayout()
        self.progress_holder.setLayout(self.progress_layout)

        self.layout.addWidget(self.options_widget, 0, 0, 1, 1)
        self.layout.addWidget(self.progress_holder, 1, 0, 1, 1)
        self.layout.addWidget(self.chartHolder, 0, 1, 4, 3)


        self.setLayout(self.layout)

    def setCurrUser(self, user):
        self.curr_user = user

    @Slot()
    def timelinePicked(self, index):

        self.available_years = list(self.curr_user["transactions"].keys())
        self.available_years.sort()
        self.available_years.insert(0, "")
        if index == 0:
            self.hideOptions()
        #all time
        elif index == 1:
            self.hideOptions()
            self.type_options = LabelDropDown("Data:", TRANSACTION_TYPES)
            self.options_layout.addWidget(self.type_options, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.type_options.combo.currentIndexChanged.connect(self.dataPicked)
        #by year or month
        elif index == 2 or index == 3:
            self.hideOptions()
            self.year_options = LabelDropDown("Year:", self.available_years)
            self.options_layout.addWidget(self.year_options, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.year_options.combo.currentIndexChanged.connect(self.yearPicked)

    @Slot()
    def yearPicked(self, index):
        if self.gen_button != None:
            self.gen_button.hide()
            del self.gen_button
            self.gen_button = None
        if self.cancel_button != None:
            self.cancel_button.hide()
            del self.cancel_button
            self.cancel_button = None
        if self.data_options2 != None:
            self.data_options2.hide()
            del self.data_options2
            self.data_options2 = None
        if self.data_options != None:
            self.data_options.hide()
            del self.data_options
            self.data_options = None
        if self.search_edit != None:
            self.search_edit.hide()
            del self.search_edit
            self.search_edit = None


        if index == 0:
            return
        if self.timeline_options.getText() == "Year":
            if self.type_options != None:
                self.type_options.hide()
                del self.type_options
                self.type_options = None
            self.type_options = LabelDropDown("Data:", TRANSACTION_TYPES)
            self.options_layout.addWidget(self.type_options, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.type_options.combo.currentIndexChanged.connect(self.dataPicked)
        elif self.timeline_options.getText() == "Month":
            if self.type_options != None:
                self.type_options.hide()
                del self.type_options
                self.type_options = None
            if self.month_options != None:
                self.month_options.hide()
                del self.month_options
                self.month_options = None
            picked_year = self.year_options.getText()
            self.available_months = list(self.curr_user["transactions"][picked_year].keys())
            self.available_months.sort()
            self.available_months.insert(0, "")
            self.month_options = LabelDropDown("Month:", self.available_months)
            self.options_layout.addWidget(self.month_options, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.month_options.combo.currentIndexChanged.connect(self.monthPicked)

    @Slot()
    def monthPicked(self, index):
        if self.gen_button != None:
            self.gen_button.hide()
            del self.gen_button
            self.gen_button = None
        if self.cancel_button != None:
            self.cancel_button.hide()
            del self.cancel_button
            self.cancel_button = None
        if self.data_options2 != None:
            self.data_options2.hide()
            del self.data_options2
            self.data_options2 = None
        if self.data_options != None:
            self.data_options.hide()
            del self.data_options
            self.data_options = None
        if self.search_edit != None:
            self.search_edit.hide()
            del self.search_edit
            self.search_edit = None


        if index == 0:
            return
        else:
            if self.type_options != None:
                self.type_options.hide()
                del self.type_options
                self.type_options = None
            self.type_options = LabelDropDown("Data:", TRANSACTION_TYPES)
            self.options_layout.addWidget(self.type_options, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.type_options.combo.currentIndexChanged.connect(self.dataPicked)

    @Slot()
    def dataPicked(self, index):
        if self.gen_button != None:
            self.gen_button.hide()
            del self.gen_button
            self.gen_button = None
        if self.cancel_button != None:
            self.cancel_button.hide()
            del self.cancel_button
            self.cancel_button = None
        if self.data_options2 != None:
            self.data_options2.hide()
            del self.data_options2
            self.data_options2 = None
        if self.data_options != None:
            self.data_options.hide()
            del self.data_options
            self.data_options = None
        if self.search_edit != None:
            self.search_edit.hide()
            del self.search_edit
            self.search_edit = None
        if self.type_options.combo.currentText() != "Type" and \
           self.type_options.combo.currentText() != "Keyword":
            self.ready()
        else:
            self.data_options = LabelDropDown("I/E:", ["Income", "Expense"])
            self.options_layout.addWidget(self.data_options, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.data_options.combo.currentIndexChanged.connect(self.typePicked)

    @Slot()
    def typePicked(self, index):
        if self.gen_button != None:
            self.gen_button.hide()
            del self.gen_button
            self.gen_button = None
        if self.cancel_button != None:
            self.cancel_button.hide()
            del self.cancel_button
            self.cancel_button = None
        if self.data_options2 != None:
            self.data_options2.hide()
            del self.data_options2
            self.data_options2 = None
        if self.search_edit != None:
            self.search_edit.hide()
            del self.search_edit
            self.search_edit = None

        if self.type_options.combo.currentText() == "Keyword":
            self.search_edit = TextEditLabel("Search:", 28)
            self.options_layout.addWidget(self.search_edit, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.ready()
        elif self.data_options.getText() == "Income":
            self.data_options2 = LabelDropDown("Type:", INCOME_TYPES)
            self.options_layout.addWidget(self.data_options2, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.data_options2.combo.currentIndexChanged.connect(self.ready)
        else:
            self.data_options2 = LabelDropDown("Type:", EXPENSE_TYPES)
            self.options_layout.addWidget(self.data_options2, self.curr_row, 0, 1, 3)
            self.curr_row += 1
            self.data_options2.combo.currentIndexChanged.connect(self.ready)

    def ready(self, hide_gen = True):
        if self.gen_button != None:
            self.gen_button.hide()
            del self.gen_button
            self.gen_button = None
        if self.cancel_button != None:
            self.cancel_button.hide()
            del self.cancel_button
            self.cancel_button = None

        self.gen_button = BaseButton("Generate", self.generateChart)
        self.cancel_button = BaseButton("Cancel", self.hideOptions)
        self.options_layout.addWidget(self.gen_button, self.curr_row, 0, 1, 1)
        self.options_layout.addWidget(self.cancel_button, self.curr_row, 2, 1, 1)
        self.curr_row+=1

    def hideOptions(self):
        self.curr_row = 1
        if self.year_options != None:
            self.year_options.hide()
            del self.year_options
            self.year_options = None
        if self.month_options != None:
            self.month_options.hide()
            del self.month_options
            self.month_options = None
        if self.gen_button != None:
            self.gen_button.hide()
            del self.gen_button
            self.gen_button = None
        if self.cancel_button != None:
            self.cancel_button.hide()
            del self.cancel_button
            self.cancel_button = None
        if self.type_options != None:
            self.type_options.hide()
            del self.type_options
            self.type_options = None
        if self.data_options2 != None:
            self.data_options2.hide()
            del self.data_options2
            self.data_options2 = None
        if self.data_options != None:
            self.data_options.hide()
            del self.data_options
            self.data_options = None
        if self.search_edit != None:
            self.search_edit.hide()
            del self.search_edit
            self.search_edit = None

    @Slot()
    def generateChart(self):
        timeline = self.timeline_options.getText()

        def allTime():
            return_data = None
            if self.type_options.getText() == "Incomes":
                years = []
                months = []
                days = []
                month_totals = []
                keys = list(self.curr_user["transactions"].keys())
                keys.sort()
                for year in keys:
                    years.append(year)
                    for month in self.curr_user["transactions"][year].keys():
                        months.append(month + "/" + year)
                        month_total = 0
                        for day in self.curr_user["transactions"][year][month].keys():
                            self.bar.setValue(self.bar.value() + 1)
                            if len(self.curr_user["transactions"][year][month][day]["income"]) >= 1:
                                days.append(day)
                            for transaction in self.curr_user["transactions"][year][month][day]["income"]:
                                month_total += transaction[0]
                        month_totals.append(round(month_total, 2))
                return_data = {"title": "Incomes", "years": years, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Expenses":
                years = []
                months = []
                days = []
                month_totals = []
                keys = list(self.curr_user["transactions"].keys())
                keys.sort()
                for year in keys:
                    years.append(year)
                    for month in self.curr_user["transactions"][year].keys():
                        months.append(month + "/" + year)
                        month_total = 0
                        for day in self.curr_user["transactions"][year][month].keys():
                            self.bar.setValue(self.bar.value() + 1)
                            if len(self.curr_user["transactions"][year][month][day]["expense"]) >= 1:
                                days.append(day)
                            for transaction in self.curr_user["transactions"][year][month][day]["expense"]:
                                month_total += transaction[0]
                        month_totals.append(round(month_total, 2))
                return_data = {"title": "Expenses","years": years, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Net":
                years = []
                months = []
                days = []
                month_totals = []
                keys = list(self.curr_user["transactions"].keys())
                keys.sort()
                for year in keys:
                    years.append(year)
                    for month in self.curr_user["transactions"][year].keys():
                        months.append(month + "/" + year)
                        month_total = 0
                        for day in self.curr_user["transactions"][year][month].keys():
                            expense_total = 0
                            income_total = 0
                            if len(self.curr_user["transactions"][year][month][day]["expense"]) >= 1 or \
                                len(self.curr_user["transactions"][year][month][day]["income"]) >= 1:
                                days.append(day)
                            for transaction in self.curr_user["transactions"][year][month][day]["expense"]:
                                self.bar.setValue(self.bar.value() + 1)
                                expense_total += transaction[0]
                            for transaction in self.curr_user["transactions"][year][month][day]["income"]:
                                self.bar.setValue(self.bar.value() + 1)
                                income_total += transaction[0]
                            month_total += income_total - expense_total

                        month_totals.append(round(month_total, 2))
                return_data = {"title": "Net (Income - Expense)","years": years, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Both":
                years = []
                months = []
                days = []
                month_totals = []
                keys = list(self.curr_user["transactions"].keys())
                keys.sort()
                for year in keys:
                    years.append(year)
                    for month in self.curr_user["transactions"][year].keys():
                        months.append(month + "/" + year)
                        month_total = [0, 0]
                        for day in self.curr_user["transactions"][year][month].keys():
                            expense_total = 0
                            income_total = 0
                            if len(self.curr_user["transactions"][year][month][day]["expense"]) >= 1 or \
                                len(self.curr_user["transactions"][year][month][day]["income"]) >= 1:
                                days.append(day)
                            for transaction in self.curr_user["transactions"][year][month][day]["expense"]:
                                self.bar.setValue(self.bar.value() + 1)
                                expense_total += transaction[0]
                            for transaction in self.curr_user["transactions"][year][month][day]["income"]:
                                self.bar.setValue(self.bar.value() + 1)
                                income_total += transaction[0]
                            month_total[0] += round(income_total, 2)
                            month_total[1] += round(expense_total, 2)

                        month_totals.append(month_total)
                return_data = {"title": "Income and Expense","years": years, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Type":
                years = []
                months = []
                days = []
                month_totals = []
                search_type = self.data_options2.getText()
                if self.data_options.getText() == "Income":
                    type = "income"
                else:
                    type = "expense"
                keys = list(self.curr_user["transactions"].keys())
                keys.sort()
                for year in keys:
                    years.append(year)
                    for month in self.curr_user["transactions"][year].keys():
                        months.append(month + "/" + year)
                        month_total = 0
                        for day in self.curr_user["transactions"][year][month].keys():
                            total = 0
                            if len(self.curr_user["transactions"][year][month][day][type]) >= 1:
                                days.append(day)
                            for transaction in self.curr_user["transactions"][year][month][day][type]:
                                self.bar.setValue(self.bar.value() + 1)
                                if transaction[1] == search_type:
                                    total += transaction[0]
                            month_total += round(total, 2)

                        month_totals.append(month_total)

                return_data = {"title": search_type,"years": years, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Keyword":
                years = []
                months = []
                days = []
                month_totals = []
                search_type = self.search_edit.getText()
                if self.data_options.getText() == "Income":
                    type = "income"
                else:
                    type = "expense"
                keys = list(self.curr_user["transactions"].keys())
                keys.sort()
                for year in keys:
                    years.append(year)
                    for month in self.curr_user["transactions"][year].keys():
                        months.append(month + "/" + year)
                        month_total = 0
                        for day in self.curr_user["transactions"][year][month].keys():
                            total = 0
                            if len(self.curr_user["transactions"][year][month][day][type]) >= 1:
                                days.append(day)
                            for transaction in self.curr_user["transactions"][year][month][day][type]:
                                self.bar.setValue(self.bar.value() + 1)
                                if search_type.lower() in transaction[2].lower():
                                    total += transaction[0]
                            month_total += round(total, 2)

                        month_totals.append(month_total)

                return_data = {"title": search_type,"years": years, "months": months, "days": days, "month totals": month_totals}


            return return_data

        def byYear(currYear):
            return_data = None
            year = currYear

            if self.type_options.getText() == "Incomes":
                months = []
                month_totals = []
                days = []
                keys = list(self.curr_user["transactions"][year].keys())
                keys.sort()
                for month in keys:
                    months.append(month + "/" + year)
                    month_total = 0
                    for day in self.curr_user["transactions"][year][month].keys():
                        if len(self.curr_user["transactions"][year][month][day]["income"]) >= 1:
                            days.append(day)
                        for transaction in self.curr_user["transactions"][year][month][day]["income"]:
                            self.bar.setValue(self.bar.value() + 1)
                            month_total += transaction[0]
                    month_totals.append(round(month_total, 2))
                return_data = {"title": "Incomes", "years": year, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Expenses":
                months = []
                month_totals = []
                days = []
                keys = list(self.curr_user["transactions"][year].keys())
                keys.sort()
                for month in keys:
                    months.append(month + "/" + year)
                    month_total = 0
                    for day in self.curr_user["transactions"][year][month].keys():
                        if len(self.curr_user["transactions"][year][month][day]["income"]) >= 1:
                            days.append(day)
                        for transaction in self.curr_user["transactions"][year][month][day]["expense"]:
                            self.bar.setValue(self.bar.value() + 1)
                            month_total += transaction[0]
                    month_totals.append(round(month_total, 2))
                return_data = {"title": "Incomes", "years": year, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Net":
                months = []
                days = []
                month_totals = []
                keys = list(self.curr_user["transactions"][year].keys())
                keys.sort()
                for month in keys:
                    months.append(month + "/" + year)
                    month_total = 0
                    for day in self.curr_user["transactions"][year][month].keys():
                        expense_total = 0
                        income_total = 0
                        if len(self.curr_user["transactions"][year][month][day]["expense"]) >= 1 or \
                            len(self.curr_user["transactions"][year][month][day]["income"]) >= 1:
                            days.append(day)
                        for transaction in self.curr_user["transactions"][year][month][day]["expense"]:
                            self.bar.setValue(self.bar.value() + 1)
                            expense_total += transaction[0]
                        for transaction in self.curr_user["transactions"][year][month][day]["income"]:
                            self.bar.setValue(self.bar.value() + 1)
                            income_total += transaction[0]
                        month_total += income_total - expense_total

                    month_totals.append(round(month_total, 2))
                return_data = {"title": "Net (Income - Expense)","years": year, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Both":
                months = []
                days = []
                month_totals = []
                keys = list(self.curr_user["transactions"][year].keys())
                keys.sort()
                for month in keys:
                    months.append(month + "/" + year)
                    month_total = [0, 0]
                    for day in self.curr_user["transactions"][year][month].keys():
                        expense_total = 0
                        income_total = 0
                        if len(self.curr_user["transactions"][year][month][day]["expense"]) >= 1 or \
                            len(self.curr_user["transactions"][year][month][day]["income"]) >= 1:
                            days.append(day)
                        for transaction in self.curr_user["transactions"][year][month][day]["expense"]:
                            self.bar.setValue(self.bar.value() + 1)
                            expense_total += transaction[0]
                        for transaction in self.curr_user["transactions"][year][month][day]["income"]:
                            self.bar.setValue(self.bar.value() + 1)
                            income_total += transaction[0]
                        month_total[0] += round(income_total, 2)
                        month_total[1] += round(expense_total, 2)

                        month_totals.append(month_total)
                return_data = {"title": "Income and Expense","years": year, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Type":
                months = []
                days = []
                month_totals = []
                search_type = self.data_options2.getText()
                if self.data_options.getText() == "Income":
                    type = "income"
                else:
                    type = "expense"
                keys = list(self.curr_user["transactions"][year].keys())
                keys.sort()
                for month in keys:
                    months.append(month + "/" + year)
                    month_total = 0
                    for day in self.curr_user["transactions"][year][month].keys():
                        total = 0
                        if len(self.curr_user["transactions"][year][month][day][type]) >= 1:
                            days.append(day)
                        for transaction in self.curr_user["transactions"][year][month][day][type]:
                            self.bar.setValue(self.bar.value() + 1)
                            if transaction[1] == search_type:
                                total += transaction[0]
                        month_total += round(total, 2)

                    month_totals.append(month_total)

                return_data = {"title": search_type,"years": year, "months": months, "days": days, "month totals": month_totals}
            elif self.type_options.getText() == "Keyword":
                months = []
                days = []
                month_totals = []
                search_type = self.search_edit.getText()
                if self.data_options.getText() == "Income":
                    type = "income"
                else:
                    type = "expense"
                keys = list(self.curr_user["transactions"][year].keys())
                keys.sort()
                for month in keys:
                    months.append(month + "/" + year)
                    month_total = 0
                    for day in self.curr_user["transactions"][year][month].keys():
                        total = 0
                        if len(self.curr_user["transactions"][year][month][day][type]) >= 1:
                            days.append(day)
                        for transaction in self.curr_user["transactions"][year][month][day][type]:
                            self.bar.setValue(self.bar.value() + 1)
                            if search_type.lower() in transaction[2].lower():
                                total += transaction[0]
                        month_total += round(total, 2)

                    month_totals.append(month_total)

                return_data = {"title": search_type,"years": year, "months": months, "days": days, "month totals": month_totals}
            return return_data

        def byMonth(currYear, currMonth):
            return_data = None
            year = currYear
            month = currMonth
            start_date = QDate(int(year), int(month), 1)
            end_date = QDate(int(year), int(month), start_date.daysInMonth())

            if self.type_options.getText() == "Incomes":
                days = []
                day_totals = []
                for day in range(start_date.day(), end_date.day() + 1):
                    days.append(str(day))
                    total = 0
                    if str(day) in self.curr_user["transactions"][year][month].keys():
                        for transaction in self.curr_user["transactions"][year][month][str(day)]["income"]:
                            self.bar.setValue(self.bar.value() + 1)
                            total += transaction[0]
                    day_totals.append(total)
                return_data = {"title": "Incomes", "years": year, "months": month, "days": days, "day totals": day_totals}


            elif self.type_options.getText() == "Expenses":
                days = []
                day_totals = []
                for day in range(start_date.day(), end_date.day() + 1):
                    days.append(str(day))
                    total = 0
                    if str(day) in self.curr_user["transactions"][year][month].keys():
                        for transaction in self.curr_user["transactions"][year][month][str(day)]["expense"]:
                            self.bar.setValue(self.bar.value() + 1)
                            total += transaction[0]
                    day_totals.append(total)
                return_data = {"title": "Expenses", "years": year, "months": month, "days": days, "day totals": day_totals}


            elif self.type_options.getText() == "Net":
                days = []
                day_totals = []
                for day in range(start_date.day(), end_date.day() + 1):
                    days.append(str(day))
                    total = 0
                    expense_total = 0
                    income_total = 0
                    if str(day) in self.curr_user["transactions"][year][month].keys():
                        for transaction in self.curr_user["transactions"][year][month][str(day)]["expense"]:
                            self.bar.setValue(self.bar.value() + 1)
                            expense_total += transaction[0]
                        for transaction in self.curr_user["transactions"][year][month][str(day)]["income"]:
                            self.bar.setValue(self.bar.value() + 1)
                            income_total += transaction[0]
                        total = income_total - expense_total
                    day_totals.append(total)
                return_data = {"title": "Net (Incomes - Expenses)", "years": year, "months": month, "days": days, "day totals": day_totals}

            elif self.type_options.getText() == "Both":
                days = []
                day_totals = []
                for day in range(start_date.day(), end_date.day() + 1):
                    days.append(str(day))
                    day_total = [0,0]
                    income_total = 0
                    expense_total = 0
                    if str(day) in self.curr_user["transactions"][year][month].keys():
                        for transaction in self.curr_user["transactions"][year][month][str(day)]["expense"]:
                            self.bar.setValue(self.bar.value() + 1)
                            expense_total += transaction[0]
                        for transaction in self.curr_user["transactions"][year][month][str(day)]["income"]:
                            self.bar.setValue(self.bar.value() + 1)
                            income_total += transaction[0]
                    day_total[0] += round(income_total, 2)
                    day_total[1] += round(expense_total, 2)

                    day_totals.append(day_total)
                return_data = {"title": "Income/Expense", "years": year, "months": month, "days": days, "day totals": day_totals}

            elif self.type_options.getText() == "Type":
                days = []
                day_totals = []
                search_type = self.data_options2.getText()
                if self.data_options.getText() == "Income":
                    type = "income"
                else:
                    type = "expense"
                for day in range(start_date.day(), end_date.day() + 1):
                    total = 0
                    days.append(str(day))
                    if str(day) in self.curr_user["transactions"][year][month].keys():
                        for transaction in self.curr_user["transactions"][year][month][str(day)][type]:
                            if transaction[1] == search_type:
                                self.bar.setValue(self.bar.value() + 1)
                                total += transaction[0]
                    total = round(total, 2)

                    day_totals.append(total)

                return_data = {"title": search_type, "years": year, "months": month, "days": days, "day totals": day_totals}


            elif self.type_options.getText() == "Keyword":
                days = []
                day_totals = []
                search_type = self.search_edit.getText()
                if self.data_options.getText() == "Income":
                    type = "income"
                else:
                    type = "expense"
                for day in range(start_date.day(), end_date.day() + 1):
                    total = 0
                    days.append(str(day))
                    if str(day) in self.curr_user["transactions"][year][month].keys():
                        for transaction in self.curr_user["transactions"][year][month][str(day)][type]:
                            if search_type.lower() in transaction[2].lower():
                                self.bar.setValue(self.bar.value() + 1)
                                total += transaction[0]
                    total = round(total, 2)
                    day_totals.append(total)

                return_data = {"title": search_type,"years": year, "months": month, "days": days, "day totals": day_totals}
            return return_data

        data = None
        if timeline == "All Time":
            type = self.type_options.getText()
            error = False
            if type == "":
                self.error(self.type_options.label)
                error = True
            if type == "Keyword" and self.search_edit.getText() == "":
                self.error(self.search_edit.label, False)
                error = True
            if error:
                return
            data = self.showProgress(allTime)
            if self.chart != None:
                self.removeChart()
            if type != "Both":
                self.createChart(data)
            elif type == "Both":
                self.createChart(data, type=1)

        elif timeline == "Year":
            #error checking
            year = self.year_options.getText()
            type = self.type_options.getText()
            error = False

            if type == "Keyword" and self.search_edit.getText() == "":
                self.error(self.search_edit.label, False)
                error = True
            if year == "":
                self.error(self.year_options.label)
                error = True
            elif type == "":
                self.error(self.type_options.label)
                error = True
            if error:
                return
            data = self.showProgress(byYear, year)
            if self.chart != None:
                self.removeChart()
            if type != "Both":
                self.createChart(data)
            elif type == "Both":
                self.createChart(data, type=1)

        elif timeline == "Month":
            #error checking
            error = False
            year = self.year_options.getText()
            month = self.month_options.getText()
            type = self.type_options.getText()

            if type == "Keyword" and self.search_edit.getText() == "":
                self.error(self.search_edit.label, False)
                error = True
            if year == "":
                error = True
                self.error(self.year_options.label)
                self.month_options.hide()
            elif month == "":
                error = True
                self.error(self.month_options.label)
            elif type == "":
                self.error(self.type_options.label)
                error = True
            if error:
                return
            data = self.showProgress(byMonth, year, month)
            if self.chart != None:
                self.removeChart()
            if type != "Both":
                self.createChart(data, type=2)
            elif type == "Both":
                self.createChart(data, type=3)

    def createChart(self, data, type = 0):
        if type == 0:
            self.set = QtCharts.QBarSet(data["title"])
            self.set.setColor(QColor(MAIN_COLOR))
            max = 0
            min = 0
            for item in data["month totals"]:
                if item > max:
                    max = item
                if item < min:
                    min = item
                self.set.append(item)
            self.series = QtCharts.QBarSeries()
            self.series.append(self.set)
            self.series.setLabelsFormat("@value")

            self.chart = QtCharts.QChart()
            self.chart.addSeries(self.series)
            self.chart.setTitle(data["title"])
            font = QFont(FONT)
            font.setPixelSize(18)
            self.chart.setTitleFont(font)
            self.chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

            self.axisX = QtCharts.QBarCategoryAxis()
            self.axisX.setCategories(data["months"])
            self.axisY = QtCharts.QValueAxis()
            self.axisY.setRange(min, max)
            self.axisY.setTickCount(20)
            axis_font = QFont(FONT)
            axis_font.setPixelSize(12)
            self.axisX.setLabelsFont(axis_font)
            self.axisY.setLabelsFont(axis_font)

            self.chart.addAxis(self.axisX, Qt.AlignBottom)
            self.series.attachAxis(self.axisX)
            self.chart.addAxis(self.axisY, Qt.AlignLeft)
            self.series.attachAxis(self.axisY)
            self.chart.legend().setAlignment(Qt.AlignBottom)
            self.chartHolder.setChart(self.chart)
            self.chartHolder.setRenderHint(QPainter.Antialiasing)
        elif type == 1:
            self.set1 = QtCharts.QBarSet("Incomes")
            self.set1.setColor(QColor(MAIN_COLOR))
            self.set2 = QtCharts.QBarSet("Expenses")
            self.set2.setColor(QColor(SECONDARY_COLOR))
            max = 0
            for item in data["month totals"]:
                if item[0] > max:
                    max = item[0]
                if item[1] > max:
                    max = item[1]
                self.set1.append(item[0])
                self.set2.append(item[1])
            self.series = QtCharts.QBarSeries()
            self.series.append(self.set1)
            self.series.append(self.set2)

            self.series.setLabelsFormat("@value")

            self.chart = QtCharts.QChart()
            self.chart.addSeries(self.series)
            self.chart.setTitle(data["title"])
            font = QFont(FONT)
            font.setPixelSize(18)
            self.chart.setTitleFont(font)
            self.chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

            self.axisX = QtCharts.QBarCategoryAxis()
            self.axisX.setCategories(data["months"])
            self.axisY = QtCharts.QValueAxis()
            self.axisY.setRange(0, max)
            self.axisY.setTickCount(20)
            axis_font = QFont(FONT)
            axis_font.setPixelSize(12)
            self.axisX.setLabelsFont(axis_font)
            self.axisY.setLabelsFont(axis_font)

            self.chart.addAxis(self.axisX, Qt.AlignBottom)
            self.series.attachAxis(self.axisX)
            self.chart.addAxis(self.axisY, Qt.AlignLeft)
            self.series.attachAxis(self.axisY)
            self.chart.legend().setAlignment(Qt.AlignBottom)
            self.chartHolder.setRenderHint(QPainter.Antialiasing)
            self.chartHolder.setChart(self.chart)
        if type == 2:
            self.set = QtCharts.QBarSet(data["title"])
            self.set.setColor(QColor(MAIN_COLOR))
            max = 0
            min = 0
            for item in data["day totals"]:
                if item > max:
                    max = item
                if item < min:
                    min = item
                self.set.append(item)
            self.series = QtCharts.QBarSeries()
            self.series.append(self.set)

            self.series.setLabelsFormat("@value")


            self.chart = QtCharts.QChart()
            self.chart.addSeries(self.series)
            self.chart.setTitle(data["title"])
            font = QFont(FONT)
            font.setPixelSize(18)
            self.chart.setTitleFont(font)
            self.chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

            self.axisX = QtCharts.QBarCategoryAxis()
            self.axisX.setCategories(data["days"])
            self.axisY = QtCharts.QValueAxis()
            self.axisY.setRange(min, max)
            self.axisY.setTickCount(20)
            axis_font = QFont(FONT)
            axis_font.setPixelSize(12)
            self.axisX.setLabelsFont(axis_font)
            self.axisY.setLabelsFont(axis_font)

            self.chart.addAxis(self.axisX, Qt.AlignBottom)
            self.series.attachAxis(self.axisX)
            self.chart.addAxis(self.axisY, Qt.AlignLeft)
            self.series.attachAxis(self.axisY)
            self.chart.legend().setAlignment(Qt.AlignBottom)
            self.chartHolder.setChart(self.chart)
            self.chartHolder.setRenderHint(QPainter.Antialiasing)
        elif type == 3:
            self.set1 = QtCharts.QBarSet("Incomes")
            self.set1.setColor(QColor(MAIN_COLOR))
            self.set2 = QtCharts.QBarSet("Expenses")
            self.set2.setColor(QColor(SECONDARY_COLOR))
            max = 0
            for item in data["day totals"]:
                if item[0] > max:
                    max = item[0]
                if item[1] > max:
                    max = item[1]
                self.set1.append(item[0])
                self.set2.append(item[1])
            self.series = QtCharts.QBarSeries()
            self.series.append(self.set1)
            self.series.append(self.set2)

            self.series.setLabelsFormat("@value")

            self.chart = QtCharts.QChart()
            self.chart.addSeries(self.series)
            self.chart.setTitle(data["title"])

            font = QFont(FONT)
            font.setPixelSize(18)
            self.chart.setTitleFont(font)
            self.chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

            self.axisX = QtCharts.QBarCategoryAxis()
            self.axisX.setCategories(data["days"])
            self.axisY = QtCharts.QValueAxis()
            self.axisY.setRange(0, max)
            self.axisY.setTickCount(20)
            axis_font = QFont(FONT)
            axis_font.setPixelSize(12)
            self.axisX.setLabelsFont(axis_font)
            self.axisY.setLabelsFont(axis_font)

            self.chart.addAxis(self.axisX, Qt.AlignBottom)
            self.series.attachAxis(self.axisX)
            self.chart.addAxis(self.axisY, Qt.AlignLeft)
            self.series.attachAxis(self.axisY)
            self.chart.legend().setAlignment(Qt.AlignBottom)
            self.chartHolder.setRenderHint(QPainter.Antialiasing)
            self.chartHolder.setChart(self.chart)

    def removeChart(self):
        chart = self.chartHolder.chart()
        del chart

    def showProgress(self, func, *pargs, **kargs):
        self.bar = QProgressBar()
        self.bar.setFixedSize(320, 20)
        self.bar.setMinimum(0)
        self.bar.setMaximum(0)
        self.bar.setOrientation(Qt.Horizontal)
        self.progress_layout.addWidget(self.bar)
        self.bar.show()
        self.bar.setValue(1)
        ret = func(*pargs, **kargs)
        self.bar.hide()
        del self.bar
        self.bar = None
        return ret

    def error(self, widget, hide_gen = True):
        if hide_gen:
            if self.gen_button != None:
                self.gen_button.hide()
                del self.gen_button
                self.gen_button = None
            if self.cancel_button != None:
                self.cancel_button.hide()
                del self.cancel_button
                self.cancel_button = None
        self.occ_error_anim = QPropertyAnimation(widget, b"colorProp")
        self.occ_error_anim.setDuration(3000)
        self.occ_error_anim.setStartValue(QColor(ERROR_COLOR))
        self.occ_error_anim.setEndValue(QColor(MAIN_COLOR))
        self.occ_error_anim.start()

#       class: InfoFrame
#
#       A class that defines a Frame widget that holds a title, table area
#       and buttons that will bring up dialogs to modify the table
#
#       Parameters:
#           label_text: text that will be displayed at the top of the InfoFrame
#                       to describe what the table is
#           header_labels: a list of strings that will be placed on the header
#                          of the table
#           info_type: the type of info being represented by the frame, income
#                      or expense
class InfoFrame(QFrame):
    def __init__(self, label_text, header_labels, info_type,  parent = None,):
        super(InfoFrame, self).__init__(parent)
        self.label_text = label_text
        self.header_labels = header_labels
        self.user_data = None
        self.curr_date = ()
        self.info_type = info_type
        self.initUI()

    def initUI(self):
        self.setFixedSize(300, 600)
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        self.description = QLabel(self)
        self.description.setText(self.label_text)
        self.description.setStyleSheet("border: 2px solid; border-color: %s; border-radius: 10px; border-style:inset; color: %s; font: 8pt %s" % (MAIN_COLOR,MAIN_COLOR,FONT))
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setFixedSize(280, 30)

        self.tableHolder = QWidget(self)
        self.tableLayout = QGridLayout(self.tableHolder)
        self.tableLayout.setAlignment(Qt.AlignCenter)
        self.tableHolder.setFixedSize(280,250)

        #the actual table displaying the data
        self.infoTable = QTableWidget(self.tableHolder)
        self.infoTable.setStyleSheet("color: %s; font: 8pt %s" % (MAIN_COLOR, FONT))
        self.infoTable.setColumnCount(len(self.header_labels))
        self.infoTable.setHorizontalHeaderLabels(self.header_labels)
        self.infoTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.infoTable.setSelectionMode(QAbstractItemView.SingleSelection)

        self.tableLayout.addWidget(self.infoTable, 0, 0, 1, 1)
        self.tableHolder.setLayout(self.tableLayout)

        #total label keeps track of the amount of money held in the current table
        self.totalLabel = QLabel(self)
        self.totalLabel.setStyleSheet("border: 2px solid; border-color: %s; border-radius: 10px; border-style:inset; color: %s; font: 8pt %s" % (MAIN_COLOR,MAIN_COLOR,FONT))
        self.totalLabel.setText("Total: $0.00")
        self.totalLabel.setFixedSize(280, 30)
        self.totalLabel.setAlignment(Qt.AlignCenter)

        #the buttons that will bring up their respective modification widgets
        self.addButton = BaseButton("Add", self.addTransaction)
        self.editButton = BaseButton("Edit", self.editTransaction)
        self.removeButton = BaseButton("Remove", self.removeTransaction)

        self.addEditRemoveHolder = QFrame()
        self.addEditRemoveHolder.setStyleSheet("border: 2px solid; border-color: %s; border-radius: 10px; border-style:inset;" % (MAIN_COLOR))
        self.addEditRemoveHolder.setFixedSize(280, 200)
        self.addEditRemoveLayout = QVBoxLayout()
        self.addEditRemoveHolder.setLayout(self.addEditRemoveLayout)

        self.layout.addWidget(self.description, 0,0,1,3)
        self.layout.addWidget(self.tableHolder, 1,0,1,3)
        self.layout.addWidget(self.totalLabel, 2, 0, 1, 3)
        self.layout.addWidget(self.addButton, 3, 0, 1, 1)
        self.layout.addWidget(self.editButton, 3, 1, 1, 1)
        self.layout.addWidget(self.removeButton, 3, 2, 1, 1)
        self.layout.addWidget(self.addEditRemoveHolder, 4, 0, 1, 3)
        self.setLayout(self.layout)

        self.addWidg = None
        self.editWidg = None
        self.removeWidg = None

    def setUserData(self, user_data, curr_date):
        self.user_data = user_data
        self.curr_date = (curr_date.year(), curr_date.month(), curr_date.day())

        self.updateTable()

    def setDate(self, curr_date):
        self.curr_date = (curr_date.year(), curr_date.month(), curr_date.day())

        if self.addWidg != None:
            self.addWidg.hide()
            del self.addWidg
            self.addWidg = None
        if self.editWidg != None:
            self.editWidg.hide()
            del self.editWidg
            self.editWidg = None
        if self.removeWidg != None:
            self.removeWidg.hide()
            del self.removeWidg
            self.removeWidg = None

        self.setTotal(0)
        self.updateTable()

    def setTotal(self, new_total):
        self.totalLabel.setText("Total: $%.2f" % (new_total))

    def updateTable(self):
        self.infoTable.clearContents()
        self.infoTable.setRowCount(0)
        self.infoTable.setColumnCount(0)
        self.curr_year = str(self.curr_date[0])
        self.curr_month = str(self.curr_date[1])
        self.curr_day = str(self.curr_date[2])


        self.parentWidget().parentWidget().updateTotals(self.curr_year, self.curr_month)

        if self.curr_year in list(self.user_data.keys()) and \
            self.curr_month in list(self.user_data[self.curr_year].keys()) and \
            self.curr_day in list(self.user_data[self.curr_year][self.curr_month].keys()):
            row = 0
            self.type_data = self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type]
            #get each transaction from the current date data that matches the frames
            #info type
            if len(self.type_data) == 0:
                #if there are no income or expenses on the current day, remove it from
                #the user's data object
                if len(self.user_data[self.curr_year][self.curr_month][self.curr_day]["expense"]) == 0 and \
                   len(self.user_data[self.curr_year][self.curr_month][self.curr_day]["income"]) == 0:
                   del self.user_data[self.curr_year][self.curr_month][self.curr_day]

                if(len(self.user_data[self.curr_year][self.curr_month].keys()) == 0):
                    del self.user_data[self.curr_year][self.curr_month]

                if(len(self.user_data[self.curr_year].keys()) == 0):
                    del self.user_data[self.curr_year]
                return

            #only set the edit and remove buttons if there are items that can
            #be edited or removed
            self.editButton.setEnabled(True)
            self.removeButton.setEnabled(True)
            self.infoTable.setRowCount(len(self.type_data))
            self.infoTable.setColumnCount(3)
            self.infoTable.setHorizontalHeaderLabels(self.header_labels)
            self.sum_total = 0.0
            for item in self.type_data:

                amount = item[0]
                self.sum_total+=amount
                type = item[1]
                memo = item[2]

                amount_item = QTableWidgetItem()
                amount_item.setFlags(amount_item.flags() ^ Qt.ItemIsEditable)
                amount_item.setText("%.2f" % (amount))

                type_item = QTableWidgetItem()
                type_item.setFlags(type_item.flags() ^ Qt.ItemIsEditable)
                type_item.setText(type)

                memo_label = QLabel()
                memo_label.setText(memo)
                memo_label.setStyleSheet("color: %s; font: 8pt %s" % (MAIN_COLOR,FONT))

                self.infoTable.setItem(row, 0, amount_item)
                self.infoTable.setItem(row, 1, type_item)
                self.infoTable.setCellWidget(row, 2, memo_label)
                self.infoTable.resizeRowToContents(row)

                row+=1

            self.setTotal(self.sum_total)
            self.infoTable.resizeColumnToContents(2)
        else:
            self.editButton.setEnabled(False)
            self.removeButton.setEnabled(False)


    @Slot()
    def addTransaction(self):

        if self.addWidg != None:
            self.addWidg.hide()
            del self.addWidg
            self.addWidg = None
        if self.editWidg != None:
            self.editWidg.hide()
            del self.editWidg
            self.editWidg = None
        if self.removeWidg != None:
            self.removeWidg.hide()
            del self.removeWidg
            self.removeWidg = None

        self.addWidg = None
        self.editWidg = None

        self.addWidg = AddWidget(self.user_data, self.curr_date, self.info_type)
        self.addEditRemoveLayout.addWidget(self.addWidg)

    @Slot()
    def editTransaction(self):
        if self.addWidg != None:
            self.addWidg.hide()
            del self.addWidg
            self.addWidg = None
        if self.editWidg != None:
            self.editWidg.hide()
            del self.editWidg
            self.editWidg = None
        if self.removeWidg != None:
            self.removeWidg.hide()
            del self.removeWidg
            self.removeWidg = None

        selectionModel = self.infoTable.selectionModel()
        selectedRow = selectionModel.selectedRows()
        if not len(selectedRow) > 0:
            self.error_dialog = ErrorDialog("You must select a row to edit.")
            self.error_dialog.show()
            return

        self.editWidg = EditWidget(self.user_data, self.curr_date, self.info_type, self.infoTable.currentRow())
        self.addEditRemoveLayout.addWidget(self.editWidg)


    @Slot()
    def removeTransaction(self):
        if self.addWidg != None:
            self.addWidg.hide()
            del self.addWidg
            self.addWidg = None
        if self.editWidg != None:
            self.editWidg.hide()
            del self.editWidg
            self.editWidg = None
        if self.removeWidg != None:
            self.removeWidg.hide()
            del self.removeWidg
            self.removeWidg = None

        selectionModel = self.infoTable.selectionModel()
        selectedRow = selectionModel.selectedRows()
        if not len(selectedRow) > 0:
            self.error_dialog = ErrorDialog("You must select a row to remove.")
            self.error_dialog.show()
            return

        self.removeWidg = RemoveWidget(self.user_data, self.curr_date, self.info_type, self.infoTable.currentRow())
        self.addEditRemoveLayout.addWidget(self.removeWidg)

#       class: TransactionCalendar
#
#       A class that extends the QCalendarWidget, overriding the paintCell
#       method to draw a border around a day cell if the user has data pertaining
#       to that cell.
class TransactionCalendar(QCalendarWidget):
    def __init__(self):
        super(TransactionCalendar, self).__init__()
        self.user_data = None
        self.outline_pen = QPen()
        self.outline_pen.setColor(QColor(MAIN_COLOR))
        self.outline_pen.setWidth(4)
        self.brush = QBrush()
        self.brush.setColor(Qt.transparent)

    def setUserData(self, data):
        self.user_data = data

    def paintCell(self, painter, rect, date):

        super(TransactionCalendar, self).paintCell(painter, rect, date)
        if self.user_data != None:
            self.curr_year = str(date.year())
            self.curr_month = str(date.month())
            self.curr_day = str(date.day())

            if self.curr_year in self.user_data.keys():
                if self.curr_month in self.user_data[self.curr_year].keys():
                    if self.curr_day in self.user_data[self.curr_year][self.curr_month].keys():
                        painter.setBrush(self.brush)
                        painter.setPen(self.outline_pen)
                        painter.drawRect(rect.adjusted(0, 0, -1, -1))

#       class: AddWidget
#
#       A class that defines a widget that allows the user to enter data that will
#       be displayed on a day on the calendar. Since this object will be destroyed
#       upon completion, must be passed all the info at instantiation. Will add
#       an entry to the user's data structure.
#
#       Parameters:
#           user_data: the data structure holding transaction data for each day
#           curr_data: a list holding three ints corresponding to [year, month, day]
#           info_type: a string denoting an income or expense information type
class AddWidget(QWidget):
    def __init__(self, user_data, curr_date, info_type):
        super().__init__()
        self.user_data = user_data
        self.curr_date = curr_date
        self.curr_year = str(curr_date[0])
        self.curr_month = str(curr_date[1])
        self.curr_day = str(curr_date[2])
        self.info_type = info_type
        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        self.memo_label = TextEditLabel("Memo: ", 50)
        self.amount_label = SpinBoxLabel("Amount:")
        if self.info_type == "expense":
            self.type_drop = LabelDropDown("Type: ", EXPENSE_TYPES)
        elif self.info_type == "income":
            self.type_drop = LabelDropDown("Type: ", INCOME_TYPES)

        self.okay_button = BaseButton("OK", self.okay)
        self.cancel_button = BaseButton("Cancel", self.cancel)

        self.layout.addWidget(self.amount_label, 0, 0, 1, 2)
        self.layout.addWidget(self.memo_label, 2, 0, 2, 2)
        self.layout.addWidget(self.type_drop, 1, 0, 1, 2)
        self.layout.addWidget(self.okay_button, 4, 0, 1, 1)
        self.layout.addWidget(self.cancel_button, 4, 1, 1, 1)

        self.setLayout(self.layout)

    @Slot()
    def okay(self):
        if self.amount_label.getValue() == 0:
            error = True
            self.amount_error_anim = QPropertyAnimation(self.amount_label.label, b"colorProp")
            self.amount_error_anim.setDuration(3000)
            self.amount_error_anim.setStartValue(QColor(ERROR_COLOR))
            self.amount_error_anim.setEndValue(QColor(MAIN_COLOR))
            self.amount_error_anim.start()
            return
        if self.curr_year in list(self.user_data.keys()) and \
            self.curr_month in list(self.user_data[self.curr_year].keys()) and \
            self.curr_day in list(self.user_data[self.curr_year][self.curr_month].keys()):
            self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type].append([self.amount_label.getValue(), self.type_drop.getText(), self.memo_label.getText()])
        else:
            if self.curr_year not in list(self.user_data.keys()):
                self.user_data[self.curr_year] = {}
            if self.curr_month not in list(self.user_data[self.curr_year].keys()):
                self.user_data[self.curr_year][self.curr_month] = {}
            if self.curr_day not in list(self.user_data[self.curr_year][self.curr_month].keys()):
                self.user_data[self.curr_year][self.curr_month][self.curr_day] = {}
                self.user_data[self.curr_year][self.curr_month][self.curr_day]["expense"] = []
                self.user_data[self.curr_year][self.curr_month][self.curr_day]["income"] = []

            self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type].append([self.amount_label.getValue(), self.type_drop.getText(), self.memo_label.getText()])

        self.parentWidget().parentWidget().updateTable()
        main_window = self.parentWidget().parentWidget().parentWidget().parentWidget().parentWidget().parentWidget()
        main_window.setChangesSaved(False)
        self.cancel()

    @Slot()
    def cancel(self):
        self.hide()

#       class: EditWidget
#
#       A class that defines a widget that allows the user to edit data that will
#       be displayed on a day on the calendar. Since this object will be destroyed
#       upon completion, must be passed all the info at instantiation. Will edit the
#       data from the user's data structure.
#
#       Parameters:
#           user_data: the data structure holding transaction data for each day
#           curr_data: a list holding three ints corresponding to [year, month, day]
#           info_type: a string denoting an income or expense information type
class EditWidget(QWidget):
    def __init__(self, user_data, curr_date, info_type, current_trans):
        super().__init__()
        self.user_data = user_data
        self.curr_date = curr_date
        #json requires string keys, will be used as the keys to hold the data by date
        self.curr_year = str(curr_date[0])
        self.curr_month = str(curr_date[1])
        self.curr_day = str(curr_date[2])
        self.info_type = info_type
        self.current_trans = current_trans

        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        self.memo_label = TextEditLabel("Memo:", 50)
        self.memo_label.edit.setText(self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type][self.current_trans][2])

        self.amount_label = SpinBoxLabel("Amount:")
        self.amount_label.edit.setValue(self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type][self.current_trans][0])
        if self.info_type == "expense":
            self.type_drop = LabelDropDown("Type: ", EXPENSE_TYPES)
        elif self.info_type == "income":
            self.type_drop = LabelDropDown("Type: ", INCOME_TYPES)

        drop_type = self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type][self.current_trans][1]
        index = self.type_drop.combo.findText(drop_type)
        self.type_drop.combo.setCurrentIndex(index)

        self.okay_button = BaseButton("OK", self.okay)
        self.cancel_button = BaseButton("Cancel", self.cancel)

        self.layout.addWidget(self.amount_label, 0, 0, 1, 2)
        self.layout.addWidget(self.memo_label, 2, 0, 2, 2)
        self.layout.addWidget(self.type_drop, 1, 0, 1, 2)
        self.layout.addWidget(self.okay_button, 4, 0, 1, 1)
        self.layout.addWidget(self.cancel_button, 4, 1, 1, 1)
        self.setLayout(self.layout)

    @Slot()
    def okay(self):
        self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type][self.current_trans] = [self.amount_label.getValue(), self.type_drop.getText(), self.memo_label.getText()]
        self.parentWidget().parentWidget().updateTable()
        main_window = self.parentWidget().parentWidget().parentWidget().parentWidget().parentWidget().parentWidget()
        main_window.setChangesSaved(False)
        self.cancel()
    @Slot()
    def cancel(self):
        self.hide()

#       class: RemoveWidget
#
#       A class that defines a widget that allows the user to remove data that will
#       be displayed on a day on the calendar. Since this object will be destroyed
#       upon completion, must be passed all the info at instantiation. Will remove
#       the data from the user's data structure.
#
#       Parameters:
#           user_data: the data structure holding transaction data for each day
#           curr_data: a list holding three ints corresponding to [year, month, day]
#           info_type: a string denoting an income or expense information type
class RemoveWidget(QWidget):
    def __init__(self, user_data, curr_date, info_type, current_trans):
        super().__init__()
        self.user_data = user_data
        self.curr_date = curr_date
        self.curr_year = str(curr_date[0])
        self.curr_month = str(curr_date[1])
        self.curr_day = str(curr_date[2])
        self.info_type = info_type
        self.current_trans = current_trans

        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        self.memo_label = TextEditLabel("Memo:", 50)
        self.memo_label.edit.setText(self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type][self.current_trans][2])
        self.memo_label.edit.setReadOnly(True)

        self.amount_label = SpinBoxLabel("Amount:")
        self.amount_label.edit.setValue(self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type][self.current_trans][0])
        self.amount_label.edit.setReadOnly(True)

        if self.info_type == "expense":
            self.type_drop = LabelDropDown("Type: ", EXPENSE_TYPES)
        elif self.info_type == "income":
            self.type_drop = LabelDropDown("Type: ", INCOME_TYPES)

        drop_type = self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type][self.current_trans][1]
        index = self.type_drop.combo.findText(drop_type)
        self.type_drop.combo.setCurrentIndex(index)
        self.type_drop.combo.setEditable(False)

        self.okay_button = BaseButton("OK", self.okay)
        self.cancel_button = BaseButton("Cancel", self.cancel)

        self.layout.addWidget(self.amount_label, 0, 0, 1, 2)
        self.layout.addWidget(self.memo_label, 2, 0, 2, 2)
        self.layout.addWidget(self.type_drop, 1, 0, 1, 2)
        self.layout.addWidget(self.okay_button, 4, 0, 1, 1)
        self.layout.addWidget(self.cancel_button, 4, 1, 1, 1)
        self.setLayout(self.layout)

    @Slot()
    def okay(self):
        del self.user_data[self.curr_year][self.curr_month][self.curr_day][self.info_type][self.current_trans]
        self.parentWidget().parentWidget().updateTable()
        main_window = self.parentWidget().parentWidget().parentWidget().parentWidget().parentWidget().parentWidget()
        main_window.setChangesSaved(False)
        self.cancel()
    @Slot()
    def cancel(self):
        self.hide()

#   Class: FrontPage
#
#   Defines a QWidget for the front splash screen page. COntains an image and
#   title label.
#   Defines a fade in animation function for fading in some of its own widgets
#   on show
class FrontPage(QWidget):
    def __init__(self, parent = None):
        super(FrontPage, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.l = QVBoxLayout()
        self.l.setAlignment(Qt.AlignHCenter)

        #check if assets folder exists
        if QDir("assets").exists():

            self.img_label = QLabel()
            self.pixmap = QPixmap("./assets/front_page_img.jpg")
            #if the fron page image does not exist, skip adding it
            if self.pixmap.isNull():
                pass
            else:
                self.pixmap = self.pixmap.scaled(800,800, Qt.KeepAspectRatio)
                self.img_label.setPixmap(self.pixmap)
                self.l.addWidget(self.img_label)
        #create it if it does not
        else:
            QDir().mkdir("assets")

        self.setLayout(self.l)

        #dont put the title text on the layout so that it can float above the image
        self.title_label = QLabel(self)
        self.title_label.setStyleSheet("color: %s" % (MAIN_COLOR))
        self.title_label.setLayout(QVBoxLayout())
        self.title_label.setFont(QFont(FONT, 40))
        self.title_label.setText("CashTrack")
        self.title_label.adjustSize()
        self.title_label.move(185, 250)
        self.fade_in(self, 1000)

    def fade_in(self, widget, duration):
        self.effect = QGraphicsOpacityEffect(self)
        widget.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        #in back describes an easing function that accelerates slowly from zero
        self.anim.setEasingCurve(QEasingCurve.InBack)
        self.anim.start()

#   Class: SignInPage
#
#   A class that defines a widget used to sign in to an existing user if one
#   exists, or creates a new user. Stores and draws user data from a Json document
class SignInPage(QWidget):
    def __init__(self, parent=None):
        super(SignInPage, self).__init__(parent)


        file = QFile()
        file.setFileName('./assets/data.json')
        result = file.open(QIODevice.ReadOnly | QIODevice.Text)

        if not result:
            file.open(QIODevice.WriteOnly)
            file.close()
            file.open(QIODevice.ReadOnly | QIODevice.Text)
            val = file.readAll()
        else:
            val = file.readAll()
            file.close()
        self.dataDoc = QJsonDocument.fromJson(val)
        self.dataObject = self.dataDoc.object()
        self.sign_in_widg = QFrame(self)
        self.create_user_widg = QFrame(self)
        self.sign_in_widg.hide()
        self.create_user_widg.hide()
        self.sign_in_widg.setObjectName("Sign")
        self.create_user_widg.setObjectName("Create")
        self.setStyleSheet("QFrame#Sign{border: 3px solid; border-color: %s; border-style: inset; border-radius: 10px}\
                            QFrame#Create{border: 3px solid; border-color: %s; border-style: inset; border-radius: 10px}" % (MAIN_COLOR, MAIN_COLOR))
        self.choose_signin = False
        self.choose_new = False
        self.initUI()

    def initUI(self):
        self.existing_user = BiggerButton("Existing User",self.choiceExist)
        self.new_user = BiggerButton("New User",self.choiceNew)
        self.sign_in_edit = QTextEdit()
        self.sign_in_edit.setFixedSize(100, 26)
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.existing_user, 0, 0)
        if len(list(self.dataObject.keys())) == 0:
            self.existing_user.hide()
        self.layout.addWidget(self.new_user, 0, 1)
        self.setLayout(self.layout)

    @Slot()
    def choiceExist(self):
        self.choose_signin = True
        self.existing_user.hide()
        self.new_user.hide()
        self.sign_in_widg.setFixedSize(400,400)
        self.signin_layout = QGridLayout()
        self.signin_layout.setAlignment(Qt.AlignCenter)
        self.sign_in_label = TextEditLabel("Username:", 27)
        self.signin_layout.addWidget(self.sign_in_label, 0, 0, 1, 2)
        self.sign_in_butt = BaseButton("Sign In", self.sign_in)
        self.signin_layout.addWidget(self.sign_in_butt, 1, 0, 1, 1)
        self.signin_layout.addWidget(BaseButton("Cancel", self.cancel), 1, 1, 1, 1)
        self.sign_in_widg.setLayout(self.signin_layout)
        self.layout.addWidget(self.sign_in_widg, 0, 0, 1, 1)
        self.sign_in_widg.show()

    @Slot()
    def choiceNew(self):
        self.choose_new = True
        self.existing_user.hide()
        self.new_user.hide()
        self.create_user_widg.setFixedSize(400,400)
        self.newuser_layout = QGridLayout()
        self.newuser_layout.setAlignment(Qt.AlignCenter)
        self.username_widg = TextEditLabel("Username:", 27)
        self.name_widg = TextEditLabel("Name:", 27)
        self.occupation_widg = TextEditLabel("Occupation:", 27)

        self.pay_widg = LabelDropDown("Pay-period:", PAY_PERIODS)
        self.create_user_butt = BaseButton("Create", self.create_user)
        self.newuser_layout.addWidget(self.username_widg, 0,0,1,2)
        self.newuser_layout.addWidget(self.name_widg, 1,0,1,2)
        self.newuser_layout.addWidget(self.occupation_widg, 2,0,1,2)
        self.newuser_layout.addWidget(self.pay_widg, 3, 0, 1, 2)
        self.newuser_layout.addWidget(self.create_user_butt, 4, 0)
        self.newuser_layout.addWidget(BaseButton("Cancel", self.cancel), 4, 1)
        self.create_user_widg.setLayout(self.newuser_layout)
        self.layout.addWidget(self.create_user_widg, 0, 0)
        self.create_user_widg.show()

    @Slot()
    def sign_in(self):
        error = False
        if self.sign_in_label.getText().strip() == "":
            error = True
            self.username_error_anim = QPropertyAnimation(self.sign_in_label.label, b"colorProp")
            self.username_error_anim.setDuration(3000)
            self.username_error_anim.setStartValue(QColor(ERROR_COLOR))
            self.username_error_anim.setEndValue(QColor(MAIN_COLOR))
            self.username_error_anim.start()
        elif not self.sign_in_label.getText().strip() in list(self.dataObject.keys()):
            self.error_dialog = ErrorDialog("Username doesn't exist.")
            self.error_dialog.show()
            error = True
        if not error:
            self.username = self.sign_in_label.getText().strip()
            self.curr_user = self.dataObject[self.username]
            self.sign_in_label.clearEdit()
            self.finish()

    @Slot()
    def create_user(self):
        error = False
        if self.username_widg.getText().strip() == "":
            error = True
            self.username_error_anim = QPropertyAnimation(self.username_widg.label, b"colorProp")
            self.username_error_anim.setDuration(3000)
            self.username_error_anim.setStartValue(QColor(ERROR_COLOR))
            self.username_error_anim.setEndValue(QColor(MAIN_COLOR))
            self.username_error_anim.start()
        if self.name_widg.getText().strip() == "":
            error = True
            self.name_error_anim = QPropertyAnimation(self.name_widg.label, b"colorProp")
            self.name_error_anim.setDuration(3000)
            self.name_error_anim.setStartValue(QColor(ERROR_COLOR))
            self.name_error_anim.setEndValue(QColor(MAIN_COLOR))
            self.name_error_anim.start()
        if self.occupation_widg.getText().strip() == "":
            error = True
            self.occ_error_anim = QPropertyAnimation(self.occupation_widg.label, b"colorProp")
            self.occ_error_anim.setDuration(3000)
            self.occ_error_anim.setStartValue(QColor(ERROR_COLOR))
            self.occ_error_anim.setEndValue(QColor(MAIN_COLOR))
            self.occ_error_anim.start()
        if self.username_widg.getText().strip() in list(self.dataObject.keys()):
            self.error_dialog = ErrorDialog("Username already exists.")
            self.error_dialog.show()
            error = True

        if not error:
            new_user_data = {}
            new_user_data["name"] = self.name_widg.getText().strip()
            new_user_data["occupation"] = self.occupation_widg.getText().strip()
            new_user_data["pay period"] = self.pay_widg.getText()
            new_user_data["transactions"] = {}
            currentDate = QDate.currentDate()
            curr_year = currentDate.year()
            curr_month = currentDate.month()
            curr_day = currentDate.day()
            new_user_data["creation date"] = (curr_year, curr_month, curr_day)

            new_user_num = len(list(self.dataObject.keys())) + 1

            #save the new user in the json document save file
            self.username = self.username_widg.getText().strip()
            self.dataObject[self.username] = new_user_data
            saveDocument = QJsonDocument(self.dataObject)
            saveFile = QFile()
            saveFile.setFileName("./assets/data.json")
            saveFile.open(QIODevice.WriteOnly)
            saveFile.write(saveDocument.toJson())
            saveFile.close()

            self.curr_user = new_user_data
            self.name_widg.clearEdit()
            self.occupation_widg.clearEdit()
            self.username_widg.clearEdit()
            self.finish()

    @Slot()
    def cancel(self):
        self.choose_new = False
        self.choose_signin = False
        self.create_user_widg.hide()
        del self.create_user_widg
        self.create_user_widg = QFrame()
        self.sign_in_widg.hide()
        del self.sign_in_widg
        self.sign_in_widg = QFrame()
        self.sign_in_widg.setObjectName("Sign")
        self.create_user_widg.setObjectName("Create")
        if len(list(self.dataObject.keys())) != 0:
            self.existing_user.show()
        self.new_user.show()

    def finish(self):
        #sign in page is on a stacked widget on the main window
        #resets the next button to continue forward
        self.parentWidget().parentWidget().setUser(self.curr_user, self.username, self.dataObject)
        for i in range(2, self.parentWidget().parentWidget().num_pages):
            self.parentWidget().widget(i).setCurrUser(self.curr_user)
        self.parentWidget().parentWidget().cycle_forward()

#       Class: CalendarPage
#
#       A class that defines a widget that will hold a calendar widget to show
#       all transactions
class CalendarPage(QWidget):
    def __init__(self, parent=None):
        super(CalendarPage, self).__init__(parent)
        self.curr_user = None
        self.initUI()
    def initUI(self):
        self.layout = QGridLayout(self)
        self.calendar = TransactionCalendar()

        #setting the color and font of the weekend days on the calendar widget
        self.weekend_format = QTextCharFormat()
        self.weekend_format.setForeground(QBrush(QColor(MAIN_COLOR)))
        self.weekend_format.setFont(QFont(FONT, 10))
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, self.weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, self.weekend_format)

        #setting the color and font of the weekday days on the calendar widget
        self.weekday_format = QTextCharFormat()
        self.weekday_format.setForeground(QBrush(Qt.black))
        self.weekday_format.setFont(QFont(FONT, 10))
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Monday, self.weekday_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Tuesday, self.weekday_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Wednesday, self.weekday_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Thursday, self.weekday_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Friday, self.weekday_format)

        #removes the week number from the calendar
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        #set the properties of the calendar
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setGridVisible(True)
        self.calendar.setFixedSize(500, 600)
        self.calendar.currentPageChanged.connect(self.updateTotals)
        self.nav_bar = self.calendar.findChild(QWidget, "qt_calendar_navigationbar")
        #self.prev_button = self.calendar.findChild(QWidget, "qt_calendar_prevmonth")
        #self.next_button = self.calendar.findChild(QWidget, "qt_calendar_nextmonth")
        self.nav_bar.setObjectName("NAV")
        self.calendar.setStyleSheet("QTableView{selection-background-color: %s} #NAV{background-color: %s; color: white; font: %s}  QToolButton:hover{color:white} QToolButton:pressed{color:%s; background-color:white} " % (MAIN_COLOR, MAIN_COLOR, FONT, MAIN_COLOR))
        self.calendar.selectionChanged.connect(self.changeDate)

        self.seperator = QFrame(self)
        self.seperator.setStyleSheet("color: %s" % (MAIN_COLOR))
        self.seperator.setFrameShape(QFrame.VLine)
        self.seperator.setFrameShadow(QFrame.Raised)

        #information widget used to hold day data
        self.info_widg = QFrame(self)
        self.info_widg.setObjectName("Info")
        self.info_layout = QGridLayout()
        self.info_layout.setAlignment(Qt.AlignTop)

        currentDate = self.calendar.selectedDate()
        self.info_title = QLabel("Transactions: %d/%d/%d" % (currentDate.month(), currentDate.day(), currentDate.year()))
        self.info_title.setAlignment(Qt.AlignCenter)
        self.info_title.setStyleSheet(".QLabel{border: 2px solid; border-color: %s; border-radius: 10px; border-style:inset; color: %s; font: 12pt %s}" % (MAIN_COLOR,MAIN_COLOR,FONT))
        self.info_layout.addWidget(self.info_title, 0,0, 1, 2)

        self.income_frame = InfoFrame("Income", ["Amount", "Type","Memo"], "income", parent = self)
        self.info_layout.addWidget(self.income_frame, 1, 0)
        self.expense_frame = InfoFrame("Expense", ["Amount","Type", "Memo"], "expense", parent = self)

        self.totals_frame = QFrame()
        self.totals_frame.setFixedSize(500, 150)
        self.totals_frame.setStyleSheet("QFrame{border: 3px solid; border-color: %s; border-style: inset; border-radius: 10px}" % (MAIN_COLOR))
        self.totals_layout = QGridLayout()
        self.totals_layout.setAlignment(Qt.AlignCenter)

        self.month_label = QLabel("Month Totals:")
        self.month_label.setStyleSheet("color: %s; font: 12pt %s" % (MAIN_COLOR,FONT))

        self.income_total = QLabel("Total Income: $0.00")
        self.income_total.setAlignment(Qt.AlignCenter)
        self.income_total.setStyleSheet("border: 2px solid; border-color: %s; border-radius: 10px; border-style:inset; color: %s; font: 12pt %s" % (MAIN_COLOR,MAIN_COLOR,FONT))
        self.expense_total = QLabel("Total Expense: $0.00")
        self.expense_total.setAlignment(Qt.AlignCenter)
        self.expense_total.setStyleSheet("border: 2px solid; border-color: %s; border-radius: 10px; border-style:inset; color: %s; font: 12pt %s" % (MAIN_COLOR,MAIN_COLOR,FONT))

        self.totals_layout.addWidget(self.month_label, 0, 1, 1, 1)
        self.totals_layout.addWidget(self.income_total, 1, 0, 1, 3)
        self.totals_layout.addWidget(self.expense_total, 2, 0, 1, 3)
        self.totals_frame.setLayout(self.totals_layout)

        self.info_layout.addWidget(self.expense_frame, 1, 1)
        self.info_widg.setLayout(self.info_layout)
        #add the widgets to the layout
        self.layout.addWidget(self.calendar, 0, 0, 3, 3)
        self.layout.addWidget(self.seperator, 0, 3, 4, 1)
        self.layout.addWidget(self.info_widg,0,4, 4, 1)
        self.layout.addWidget(self.totals_frame, 3,0, 1, 3)

        self.layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.setStyleSheet("QFrame#Info{border: 3px solid; border-color: %s; border-style: inset; border-radius: 10px}" % (MAIN_COLOR))
        self.setLayout(self.layout)

    def setCurrUser(self, user):
        self.curr_user = user
        self.min_date = self.curr_user["creation date"]
        self.min_year = self.min_date[0]
        self.min_month = self.min_date[1]
        self.min_day = self.min_date[2]
        self.calendar.setUserData(self.curr_user["transactions"])
        self.income_frame.setUserData(self.curr_user["transactions"], self.calendar.selectedDate())
        self.expense_frame.setUserData(self.curr_user["transactions"], self.calendar.selectedDate())
        currentDate = self.calendar.selectedDate()
        self.income_frame.setDate(currentDate)
        self.expense_frame.setDate(currentDate)
        self.updateTotals(self.calendar.yearShown(), self.calendar.monthShown())


    @Slot()
    def changeDate(self):
        currentDate = self.calendar.selectedDate()

        #set the date on the label
        self.info_title.setText("Transactions: %d/%d/%d" % (currentDate.month(), currentDate.day(), currentDate.year()))
        date_tuple = (currentDate.year(), currentDate.month(), currentDate.day())

        #set the date on the table widgets
        self.income_frame.setDate(currentDate)
        self.expense_frame.setDate(currentDate)

    def updateTotals(self, year, month):
        transactions = self.curr_user["transactions"]
        year = str(year)
        month = str(month)
        if self.curr_user != None:
            if year in transactions.keys():
                if month in transactions[year]:
                    income_total = 0
                    expense_total = 0
                    for day in (transactions[year][month]).keys():
                        income = transactions[year][month][day]["income"]
                        expense = transactions[year][month][day]["expense"]
                        for x in income:
                            income_total += x[0]
                        for x in expense:
                            expense_total += x[0]
                    self.income_total.setText("Total Income: $%.2f" % (income_total))
                    self.expense_total.setText("Total Expense: $%.2f" % (expense_total))

                else:
                    self.income_total.setText("Total Income: $0.00")
                    self.expense_total.setText("Total Expense: $0.00")
            else:
                self.income_total.setText("Total Income: $0.00")
                self.expense_total.setText("Total Expense: $0.00")
