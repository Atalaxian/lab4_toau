import pickle
import sys
from os import listdir
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QListWidgetItem, \
    QSizePolicy, QTableWidgetItem, QVBoxLayout
from save_load import Ui_Form
from error_window import Ui_widget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from main_window import Ui_MainWindow
from form_params import Ui_Form_Params
from math import log
import random


class NotCalc(Exception):
    def __init__(self):
        super().__init__()


class GraphicMatplotlibWithQt(FigureCanvas):
    def __init__(self, fig):
        self.fig = fig
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class SetParams(QWidget, Ui_Form_Params):
    mysignal = QtCore.pyqtSignal(float, float, float, float, float)
    error_window = None

    def __init__(self, duration, requestion, risk, time_model, time_delivery):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Параметры')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        elem_1 = QTableWidgetItem(str(duration))
        elem_1.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        elem_2 = QTableWidgetItem(str(time_delivery))
        elem_2.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        elem_3 = QTableWidgetItem(str(requestion))
        elem_3.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        elem_4 = QTableWidgetItem(str(risk))
        elem_4.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        elem_5 = QTableWidgetItem(str(time_model))
        elem_5.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.tableWidget.setItem(0, 0, elem_1)
        self.tableWidget.setItem(0, 1, elem_2)
        self.tableWidget.setItem(0, 2, elem_3)
        self.tableWidget.setItem(0, 3, elem_4)
        self.tableWidget.setItem(0, 4, elem_5)
        self.button_apply.clicked.connect(self.send_params)
        self.setMaximumSize(self.width(), self.height())
        self.setMinimumSize(self.width(), self.height())

    @QtCore.pyqtSlot()
    def send_params(self):
        try:
            duration = float(self.tableWidget.item(0, 0).text())
            time_delivery = float(self.tableWidget.item(1, 0).text())
            requestion = float(self.tableWidget.item(2, 0).text())
            risk = float(self.tableWidget.item(3, 0).text())
            time_model = float(self.tableWidget.item(4, 0).text())
        except ValueError:
            self.error_window = ErrorWindow('Ошибка! Введённые значения не могут быть преобразованы в числа.')
            self.error_window.show()
            return
        self.mysignal.emit(duration, requestion, risk, time_model, time_delivery)
        self.close()


class SaveLoad(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Загрузка и сохранение')


class ErrorWindow(QWidget, Ui_widget):
    def __init__(self, log: str):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.error_label.setText(log)
        self.setWindowIcon(QIcon('error_icon.jpg'))


class MainWindow(QMainWindow, Ui_MainWindow):
    flag_params = False
    file_work_ui = None
    error_window = None
    set_paras_window = None
    time_delivery = None
    requestion = None
    duration = None
    risk = None
    time_model = None
    list_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red',
                   'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    toolbar_gant = None
    canvas = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Однопродуктовая задача управления запасами с постоянным уровнем запаса (Вариант №10)')
        self.button_save.clicked.connect(self.save)
        self.button_load.clicked.connect(self.load)
        self.solution.clicked.connect(self.calculate)
        self.button_set_params.clicked.connect(self.set_new_params)
        self.set_params_graph_end.stateChanged.connect(self.setting_graph)

    @QtCore.pyqtSlot()
    def set_new_params(self):
        self.set_paras_window = SetParams(self.duration, self.requestion, self.risk,
                                          self.time_model, self.time_delivery)
        self.set_paras_window.mysignal.connect(self.get_new_params)
        self.set_paras_window.show()

    @QtCore.pyqtSlot(int)
    def setting_graph(self, status: int) -> None:
        if status == 2:
            toolbar = NavigationToolbar(self.canvas, self)
            vertical_layout = QVBoxLayout()
            vertical_layout.setSpacing(0)
            vertical_layout.addWidget(toolbar)
            self.verticalLayout_graph.addLayout(vertical_layout)
        if status == 0:
            layout = self.verticalLayout_graph.takeAt(1)
            self.delete_items_of_layout(layout)

    @QtCore.pyqtSlot(float, float, float, float, float)
    def get_new_params(self, duration, requestion, risk, time_model, time_delivery):
        self.flag_params = True
        self.duration = duration
        self.start_duration.setText(str(duration))
        self.requestion = requestion
        self.start_requestion.setText(str(requestion))
        self.risk = risk
        self.start_risk.setText(str(risk))
        self.time_model = time_model
        self.start_time_model.setText(str(time_model))
        self.time_delivery = time_delivery
        self.start_time_delivery.setText(str(time_delivery))

    def delete_items_of_layout(self, layout) -> None:
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.delete_items_of_layout(item.layout())

    def clear_layout(self, layout) -> None:
        for x in range(layout.count()):
            item = layout.takeAt(0)
            self.delete_items_of_layout(item.layout())

    def clear_data(self) -> None:
        self.delete_items_of_layout(self.verticalLayout_graph)
        if self.canvas is not None:
            plt.close(self.canvas.fig)
            self.canvas = None

    def graphics(self, layout, values: dict, b: float) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Время (t)')
        canvas = GraphicMatplotlibWithQt(fig)
        ax.set_title('Изменение запасов при (M)-политике')
        x_list = list()
        y_list = list()
        for x, y in values.items():
            value = str(x)
            value = value.split(' ')[0]
            value = float(value)
            if value > self.time_model:
                break
            x_list.append(value)
            y_list.append(y)
        ax.plot(x_list, y_list, color='blue', label='Оставшийся запас')
        y_list = [b for x in range(int(self.time_model + 1))]
        x_list = [x for x in range(int(self.time_model + 1))]
        ax.plot(x_list, y_list, color='green', label='Страховой запас')
        ax.set_ylabel('Запасы')
        ax.legend(loc='best')
        self.canvas = canvas
        layout.addWidget(canvas)

    @QtCore.pyqtSlot()
    def calculate(self) -> None:
        self.clear_data()
        if not self.flag_params:
            self.error_window = ErrorWindow('Не введены параметры!')
            self.error_window.show()
            return
        self.tableWidget.setRowCount(0)
        self.set_params_graph_end.setChecked(False)
        b = -(self.requestion * self.time_delivery) * (1 + log(self.risk))
        m = self.requestion * (self.time_delivery + self.duration) + b
        self.result_b_ui.setText('{0:.6}'.format(b))
        self.result_m_ui.setText('{0:.6}'.format(m))
        r = list()
        for x in range(int(self.time_model + 1)):
            r.append(random.expovariate(lambd=1 / self.requestion))
        stocks = list()
        medium_time_delivery = self.time_delivery
        time_stock_app = list()
        order = list()
        flag_stocks = False
        new_ndist = r[0] / 100
        if new_ndist <= 0:
            new_ndist = 0.01
        all_elems = {'0.0': m}
        for y in range(1, int((self.time_model + 1) * 100)):
            x = y / 100
            counter = x
            if int(x) == float(x):
                new_ndist = r[int(x)] / 100
                if new_ndist < 0:
                    new_ndist = 0.01
            if flag_stocks:
                new_elem = all_elems[(str(round(x - 0.01, 2)) + ' stocks')] - new_ndist
            else:
                if (all_elems[str(round(x - 0.01, 2))] - new_ndist) > 0:
                    new_elem = all_elems[str(round(x - 0.01, 2))] - new_ndist
                else:
                    new_elem = 0.0
            flag_stocks = False
            all_elems[str(x)] = new_elem
            if len(stocks) != 0:
                new_my_list = list()
                for elem in stocks:
                    for key, value in elem.items():
                        if key == 0.01:
                            new_elem_with_order = new_elem + value
                            all_elems[(str(x) + ' stocks')] = new_elem_with_order
                            flag_stocks = True
                        else:
                            new_my_list.append({round(key - 0.01, 2): value})
                stocks = new_my_list.copy()
            if counter % self.duration == 0:
                if new_elem < m:
                    if medium_time_delivery < self.duration:
                        time_stock_app.append(x)
                        order.append(m - new_elem)
                        stocks.append({medium_time_delivery: (m - new_elem)})
                    elif medium_time_delivery > self.duration:
                        number = 0
                        for elem in stocks:
                            for value in elem.values():
                                number += value
                        new_order = m - new_elem - number
                        if new_order > 0:
                            stocks.append({medium_time_delivery: new_order})
                            order.append(new_order)
                            time_stock_app.append(x)
                        else:
                            stocks.append({medium_time_delivery: 0.01})
                            time_stock_app.append(x)
                            order.append(0.01)
        self.result_m_ui.setText('{0:.6}'.format(m))
        self.tableWidget.setRowCount(len(time_stock_app))
        for x, elem in enumerate(time_stock_app):
            elem_1 = QTableWidgetItem(str('{0:.6}'.format(elem)))
            elem_1.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            elem_2 = QTableWidgetItem(str('{0:.6}'.format(order[x])))
            elem_2.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(x, 0, elem_1)
            self.tableWidget.setItem(x, 1, elem_2)
        self.graphics(self.verticalLayout_graph, all_elems, b)
        self.set_params_graph_end.setDisabled(False)

    def select_file(self, value_file: QListWidgetItem) -> None:
        vl = value_file.text()
        pathFile = 'saves/' + vl
        file = open(pathFile, "wb")
        pickle.dump(self.time_delivery, file)
        pickle.dump(self.requestion, file)
        pickle.dump(self.duration, file)
        pickle.dump(self.risk, file)
        pickle.dump(self.time_model, file)
        file.close()
        self.file_work_ui.close()

    def load_file(self, value_file: QListWidgetItem) -> None:
        file = value_file.text()
        pathFile = 'saves/' + file
        file = open(pathFile, "rb")
        self.time_delivery = pickle.load(file)
        self.start_time_delivery.setText(str(self.time_delivery))
        self.requestion = pickle.load(file)
        self.start_requestion.setText(str(self.requestion))
        self.duration = pickle.load(file)
        self.start_duration.setText(str(self.duration))
        self.risk = pickle.load(file)
        self.start_risk.setText(str(self.risk))
        self.time_model = pickle.load(file)
        self.start_time_model.setText(str(self.time_model))
        self.file_work_ui.close()
        self.flag_params = True
        self.result_m_ui.setText('')
        self.result_b_ui.setText('')
        self.delete_items_of_layout(self.verticalLayout_graph)
        self.set_params_graph_end.setChecked(False)
        self.set_params_graph_end.setDisabled(True)
        self.tableWidget.setRowCount(0)

    def save(self) -> None:
        if not self.flag_params:
            self.error_window = ErrorWindow('Не введены параметры!')
            self.error_window.show()
            return
        self.file_work_ui = SaveLoad()
        try:
            list_file = listdir(path='saves')
        except FileNotFoundError:
            self.error_window = ErrorWindow('Папка с именем saves не найдена.')
            self.error_window.show()
            return
        self.file_work_ui.groupBox.setTitle("Сохранение")
        self.file_work_ui.listWidget.clear()
        for elem in list_file:
            self.file_work_ui.listWidget.addItem(QListWidgetItem(elem))
        self.file_work_ui.listWidget.itemDoubleClicked.connect(self.select_file)
        self.file_work_ui.show()

    def load(self) -> None:
        self.file_work_ui = SaveLoad()
        try:
            list_file = listdir(path='saves')
        except FileNotFoundError:
            self.error_window = ErrorWindow('Папка с именем saves не найдена.')
            self.error_window.show()
            return
        self.file_work_ui.groupBox.setTitle("Загрузка")
        self.file_work_ui.listWidget.clear()
        for elem in list_file:
            self.file_work_ui.listWidget.addItem(QListWidgetItem(elem))
        self.file_work_ui.listWidget.itemDoubleClicked.connect(self.load_file)
        self.file_work_ui.show()


if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(qapp.exec())
