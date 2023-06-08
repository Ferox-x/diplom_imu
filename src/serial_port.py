from serial import Serial
import serial.tools.list_ports
from constant import PORT_SPEED
from src.core import InitMainWindow


class SerialPortInterface(InitMainWindow):
    """
    Класс для взаимодействия с последовательным портом.

    Наследуется от класса InitMainWindow.
    """

    def update_ports(self):
        """
        Обновляет список доступных портов.

        Закрывает текущий открытый порт и сбрасывает состояние форматирования данных.
        Очищает выпадающий список портов и добавляет в него доступные порты.
        Подключает обработчик события изменения выбранного порта.
        Выводит сообщение об успешном обновлении портов в консоль.
        """
        if self.serial_port:
            self.serial_port.close()
            self.data_formatter.set_initial_state()
        try:
            self.comboBox_ports.currentIndexChanged.disconnect(
                self.connect_serial)
        except TypeError as _ex:
            pass
        self.comboBox_ports.clear()
        self.comboBox_ports.addItem("Выберите COM PORT")
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBox_ports.addItem(str(port))
        self.comboBox_ports.currentIndexChanged.connect(self.connect_serial)
        self.console.append("Порты обновлены")

    def connect_serial(self):
        """
        Подключается к выбранному порту.

        Закрывает предыдущий открытый порт, если он существует.
        Создает объект Serial для выбранного порта с заданной скоростью.
        Сбрасывает буферы ввода и вывода.
        Устанавливает таймаут в 0.
        Выводит сообщение об успешном подключении порта в консоль.
        """
        try:
            port = self.comboBox_ports.currentText().split()[0]
            if self.serial_port is not None and self.serial_port.isOpen():
                self.serial_port.close()
            self.serial_port = Serial(port, PORT_SPEED)
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
            self.serial_port.timeout = 0
            self.console.append("Порт подключён")
        except Exception as _ex:
            self.console.append(_ex)

    def disconnect_serial(self):
        """
        Отключает открытый порт.
        """
        self.serial_port.close()

    def get_data_from_port(self):
        """
        Получает данные с порта.

        Если порт открыт и существует, считывает строку данных с порта в кодировке utf-8.
        Если данные присутствуют, форматирует их в соответствии с текущим состоянием форматирования.
        Выводит данные в консоль.
        """
        try:
            if self.serial_port is not None and self.serial_port.isOpen():
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    if self.data_formatter.has_init:
                        self.data_formatter.parse_data(data)

                    elif self.data_formatter.has_in_process:
                        if self.data_formatter.parse_data(data):
                            accel_data = self.data_formatter.get_accel_data()
                            if accel_data:
                                self.graphics_accel.update_data(accel_data)
                            gyro_data = self.data_formatter.get_gyro_data()
                            if gyro_data:
                                self.graphics_gyro.update_data(gyro_data)
                            if self.data_formatter.has_magnetometer:
                                mag_data = self.data_formatter.get_mag_data()
                                if mag_data:
                                    self.graphics_mag.update_data(mag_data)
                    self.console.append(data)
        except serial.SerialException as e:
            self.console.append(
                f"Ошибка при попытке читать последовательный порт: {e}"
            )
            self.disconnect_serial()
