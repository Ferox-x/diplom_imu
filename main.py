from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer

from constant import DELAY
from src.serial_port import SerialPortInterface
from widgets.real_time_plot import RealTimePlot, PlotMeta


class UIWindow(SerialPortInterface):

    def __init__(self):
        super().__init__()

    def setup(self, window):
        """Метод инициализирует объекты и расставляет их по координатам."""
        # Параметры главного окна
        window.setObjectName("window")
        window.setEnabled(True)
        window.resize(900, 914)
        window.setMinimumSize(QtCore.QSize(900, 500))
        window.setMaximumSize(QtCore.QSize(1000, 1221))
        self.central_widget = QtWidgets.QWidget(window)
        self.central_widget.setMinimumSize(QtCore.QSize(900, 1200))
        self.central_widget.setObjectName("central_widget")

        # Консоль
        self.console_label = QtWidgets.QLabel(self.central_widget)
        self.console_label.setGeometry(QtCore.QRect(10, 560, 161, 16))
        self.console_label.setObjectName("console_label")
        self.console = QtWidgets.QTextEdit(self.central_widget)
        self.console.setGeometry(QtCore.QRect(10, 580, 320, 300))
        self.console.setTabChangesFocus(False)
        self.console.setReadOnly(True)
        self.console.setObjectName("console")

        window.setCentralWidget(self.central_widget)
        # Меню бар
        self.menubar = QtWidgets.QMenuBar(window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        window.setMenuBar(self.menubar)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.set_up_graphics()
        self.set_up_combo_boxes()

        self.translate_ui(window)
        QtCore.QMetaObject.connectSlotsByName(window)

        self.refresh.clicked.connect(self.update_ports)

        self.update_ports()
    
    def set_up_graphics(self):
        """Метод инициалзации и расположений графиков"""
        # График ускорения
        accel_meta = PlotMeta('Ускорение', 'м/с^2', 10)
        self.graphics_accel = RealTimePlot(self.central_widget, self, accel_meta)
        self.graphics_accel.setGeometry(QtCore.QRect(330, 0, 581, 300))
        self.graphics_accel.setObjectName("graphics_accel")
        # График гироскопа
        gyro_meta = PlotMeta('Гироскоп', 'Угол, Градусы', 60)
        self.graphics_gyro = RealTimePlot(self.central_widget, self, gyro_meta)
        self.graphics_gyro.setGeometry(QtCore.QRect(330, 290, 581, 300))
        self.graphics_gyro.setObjectName("graphics_gyro")
        # График магнитного поля
        mag_meta = PlotMeta('Магнитное поле', 'H, Тл', 20)
        self.graphics_mag = RealTimePlot(self.central_widget, self, mag_meta)
        self.graphics_mag.setGeometry(QtCore.QRect(330, 590, 581, 300))
        self.graphics_mag.setObjectName("graphics_mag")
    
    def set_up_combo_boxes(self):
        """Метод инициалзации и выпадающих списков"""
        # Выбор порта
        self.comboBox_ports = QtWidgets.QComboBox(self.central_widget)
        self.comboBox_ports.setGeometry(QtCore.QRect(10, 20, 231, 21))
        self.comboBox_ports.setObjectName("comboBox_ports")
        self.comboBox_ports.addItem("")
        # Кнопка обновить порты
        self.refresh = QtWidgets.QPushButton(self.central_widget)
        self.refresh.setGeometry(QtCore.QRect(250, 20, 75, 23))
        self.refresh.setObjectName("refresh")

    def update_data(self):
        try:
            self.get_data_from_port()
        except Exception as e:
            self.console.append(
                f"{e}"
            )

    def translate_ui(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("window", "MPU6500"))
        self.console.setHtml(_translate("window",
                                        "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                        "p, li { white-space: pre-wrap; }\n"
                                        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                                        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.comboBox_ports.setItemText(0, _translate("window",
                                                      "Выберети COM PORT"))
        self.refresh.setText(_translate("window", "Обновить"))
        self.console_label.setText(
            _translate("window", "Консоль"))
        self.menu.setTitle(_translate("window", "Файл"))
        self.menu_2.setTitle(_translate("window", "Инфо"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = UIWindow()
    ui.setup(window)
    window.show()
    timer = QTimer()
    timer.timeout.connect(ui.update_data)
    timer.start(DELAY)
    timer = QTimer()
    timer.timeout.connect(ui.update_data)
    timer.start(DELAY)

    sys.exit(app.exec_())
