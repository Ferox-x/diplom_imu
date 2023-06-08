from PyQt5 import QtWidgets
from serial import Serial

from widgets.real_time_plot import RealTimePlot


class InitMainWindow:
    """
    Класс для инициализации главного окна приложения.

    Содержит переменные инициализации виджетов и объектов.
    """

    def __init__(self):
        self.comboBox_sensor: QtWidgets.QComboBox | None = None
        self.comboBox_speed: QtWidgets.QComboBox | None = None
        self.comboBox_ports: QtWidgets.QComboBox | None = None
        self.refresh: QtWidgets.QPushButton | None = None
        self.graphics_accel: RealTimePlot | None = None
        self.graphics_gyro: RealTimePlot | None = None
        self.graphics_mag: RealTimePlot | None = None
        self.menu: QtWidgets.QMenu | None = None
        self.menu_2: QtWidgets.QMenu | None = None
        self.menubar: QtWidgets.QMenuBar | None = None
        self.used_sensor: QtWidgets.QLabel | None = None
        self.speed_label: QtWidgets.QLabel | None = None
        self.console_label: QtWidgets.QLabel | None = None
        self.console: QtWidgets.QTextEdit | None = None
        self.central_widget = None
        self.serial_port: Serial | None = None
        self.data_formatter = DataFormatter()


class DataFormatter:
    """
    Класс для форматирования данных.

    Определяет состояние данных и выполняет их форматирование и разбор.
    """

    init_state = 0
    in_process = 1

    def __init__(self):
        self.state = self.init_state
        self.magnetometer = False
        self.temperature = False
        self.accel_data = [0, 0, 0]
        self.gyro_data = [0, 0, 0]
        self.mag_data = [0, 0, 0]
        self.temp_data = 0
        self.parsed_data = []

    def set_initial_state(self):
        """
        Устанавливает начальное состояние данных.
        """
        self.__init__()

    @property
    def has_magnetometer(self):
        """
        Проверяет наличие магнетометра.

        Возвращает True, если магнетометр присутствует, иначе False.
        """
        return self.magnetometer

    @property
    def has_temperature(self):
        """
        Проверяет наличие температуры.

        Возвращает True, если температура присутствует, иначе False.
        """
        return self.temperature

    @property
    def has_init(self):
        """
        Проверяет состояние данных.

        Возвращает True, если состояние данных равно init_state, иначе False.
        """
        if self.state == self.init_state:
            return True
        return False

    @property
    def has_in_process(self):
        """
        Проверяет состояние данных.

        Возвращает True, если состояние данных равно in_process, иначе False.
        """
        if self.state == self.in_process:
            return True
        return False

    def parse_data(self, data: str):
        """
        Разбирает и форматирует данные.

        Принимает строку данных и разбирает ее в соответствии с текущим состоянием данных.
        """
        if data:
            if self.has_init:
                self.parse_init_state(data)
            elif self.has_in_process:
                split_data = data.split()
                if len(split_data) != self.count_digits:
                    return False
                self.parsed_data = split_data
            return True

    @property
    def count_digits(self):
        count = 6
        if self.has_magnetometer:
            count += 3
        # if self.has_temperature:
        #     count += 1
        return count

    def parse_init_state(self, string):
        """
        Разбирает и форматирует данные в начальном состоянии.

        Принимает строку данных и устанавливает соответствующие значения состояния данных.
        """
        if string == 'Magnetometer True':
            self.magnetometer = True
        if string == 'Temperature True':
            self.temperature = True
        if string == 'Start':
            self.state = self.in_process
        self.parsed_data = string

    def get_accel_data(self):
        """
        Возвращает отформатированные данные акселерометра.

        Возвращает список значений акселерометра в метрах в секунду в квадрате.
        """
        if self.has_in_process:
            try:
                return [
                    float(self.parsed_data[0]) * 9.8,
                    float(self.parsed_data[1]) * 9.8,
                    float(self.parsed_data[2]) * 9.8,
                ]
            except (ValueError, IndexError):
                print("Акселерометр: неправильная дата", self.parsed_data)

    def get_gyro_data(self):
        """
        Возвращает отформатированные данные гироскопа.

        Возвращает список значений гироскопа.
        """
        if self.has_in_process:
            try:
                return [
                    float(self.parsed_data[3]),
                    float(self.parsed_data[4]),
                    float(self.parsed_data[5]),
                ]
            except (ValueError, IndexError):
                print("Гироскоп: неправильная дата", self.parsed_data)

    def get_mag_data(self):
        """
        Возвращает отформатированные данные магнетометра.

        Возвращает список значений магнетометра.
        """
        if self.has_in_process and self.has_magnetometer:
            try:
                return [
                    float(self.parsed_data[6]),
                    float(self.parsed_data[7]),
                    float(self.parsed_data[8]),
                ]
            except (ValueError, IndexError):
                print("Магнитометр: неправильная дата")

    def get_temp(self):
        """
        Возвращает отформатированные данные температуры.

        Возвращает значение температуры.
        """
        if self.has_in_process and self.has_temperature:
            try:
                if self.has_magnetometer:
                    return float(self.parsed_data[9])
                return float(self.parsed_data[6])
            except (ValueError, IndexError):
                print("Температура: неправильная дата")
