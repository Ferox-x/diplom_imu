import math
import time

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries

from constant import DELAY


class PlotMeta:
    """
    Класс для метаданных графика.

    Содержит информацию о заголовке и метке оси y графика.
    """

    def __init__(self, title, y_title, ceil):
        self.title = title
        self.y_title = y_title
        self.ceil = ceil


class RealTimePlot(QWidget):
    """
    Виджет для от ображения графика в реальном времени.

    Принимает данные, обновляет график и отображает его.
    """

    def __init__(self, parent, get_data, meta):
        self.meta: PlotMeta = meta
        self.get_data = get_data
        self.time_x = 0
        self.max_x = 0
        self.max_y = 0
        super().__init__(parent)

        # Создание серии данных и настройка графика
        self.series_x = QLineSeries()
        self.series_y = QLineSeries()
        self.series_z = QLineSeries()

        self.series_x.setObjectName(f"{self.meta.title} X")
        self.series_y.setObjectName(f"{self.meta.title} Y")
        self.series_z.setObjectName(f"{self.meta.title} Z")

        self.series_x.setName("X")
        self.series_y.setName("Y")
        self.series_z.setName("Z")

        self.chart = QChart()

        self.chart.addSeries(self.series_x)
        self.chart.addSeries(self.series_y)
        self.chart.addSeries(self.series_z)

        self.chart.createDefaultAxes()
        self.chart.setTitle(self.meta.title)

        self.chart.axisY().setTitleText(self.meta.y_title)
        self.chart.axisX().setTitleText('Время, c',)

        self.chart.axisY().setRange(
            -self.meta.ceil,
            self.meta.ceil,
        )

        # Создание объекта QChartView
        self.chartView = QChartView(self.chart)

        # Размещение объекта QChartView в макете окна
        layout = QVBoxLayout()
        layout.addWidget(self.chartView)
        self.setLayout(layout)

        # Настройка параметров окна
        self.setWindowTitle("Real-time Plot")
        self.setGeometry(100, 100, 800, 600)
        self.show()

    def update_data(self, data):
        """
        Обновляет график данными.

        Принимает данные и добавляет их в график.
        """
        self.time_x += DELAY / 100

        # Генерация случайных данных и добавление их в серию
        x = self.series_x.count()
        self.series_x.append(self.time_x, data[0])
        self.series_y.append(self.time_x, data[1])
        self.series_z.append(self.time_x, data[2])
        max_point = max(
            self.get_max(self.series_x.points()),
            self.get_max(self.series_y.points()),
            self.get_max(self.series_z.points()),
        )
        min_point = min(
            self.get_min(self.series_x.points()),
            self.get_min(self.series_y.points()),
            self.get_min(self.series_z.points()),
        )

        # Динамическое обновление графика
        self.chart.axisY().setRange(
            math.ceil(min_point / self.meta.ceil) * self.meta.ceil - (self.meta.ceil),
            math.ceil(max_point / self.meta.ceil) * self.meta.ceil + (self.meta.ceil),
        )
        if x > 50:
            self.series_x.removePoints(0, 2)
            self.series_y.removePoints(0, 2)
            self.series_z.removePoints(0, 2)

        second_frame = 3
        if self.time_x - second_frame < 0:
            self.chart.axisX().setRange(0, self.time_x)
        else:
            self.chart.axisX().setRange(self.time_x - second_frame,
                                        self.time_x)
        # изменение положения графика на оси x
        self.chartView.chart().scroll(3, 0)

    @staticmethod
    def get_max(points: [QPointF]):
        """
        Возвращает максимальное значение y из списка точек.

        Принимает список точек QPointF и возвращает максимальное значение y.
        """
        return max([_.y() for _ in points])

    @staticmethod
    def get_min(points: [QPointF]):
        """
        Возвращает минимальное значение y из списка точек.

        Принимает список точек QPointF и возвращает минимальное значение y.
        """
        return min([_.y() for _ in points])
