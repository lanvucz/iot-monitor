from datetime import datetime
from qtpy.QtWidgets import (
    QWidget, QMessageBox, QInputDialog, QPushButton,
    QComboBox, QGridLayout, QFormLayout,
    QLabel, QGroupBox, QVBoxLayout,
    QPlainTextEdit
)
from qtpy.QtCore import (
    QSize, QTimer
)
from qwt import (
    QwtPlot,
    QwtPlotCurve,
    QwtPlotItem,
)
from guidata.qthelpers import (
    add_actions,
    create_action,
)

from qtpy.QtGui import (QColor, QPen)
from utils import enumerate_serial_ports, get_item_from_queue, get_all_from_queue
from serial_port_monitor import SerialPortMonitor
import queue
from db import SensorDatabase
# from message_log import logger


class PlotMonitor(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setContentsMargins(10, 10, 10, 10)
        parent.setWindowTitle('Sensor Realtime Monitor')
        parent.resize(QSize(800, 600))

        self.port = ""
        self.com_port_name = None
        self.baurate = 9600
        self.available_ports = None
        self.button_connect = None
        self.button_disconnect = None
        self.com_box = None
        self.Com_ComboBox = None
        self.measurement_ComboBox = None
        self.measurements = {"Rosný bod (D)": "D",
                             "Suchá teplota (T)": "T",
                             "Relativní vlhkost (H)": "H",
                             "Měrná vlhkost (M)": "M",
                             "Absolutní vlhkost (A)": "A"}

        self.statusBar = parent.statusBar
        self.menuBar = parent.menuBar
        self.update_message = parent.update_message

        self.monitor_active = False  # on/off monitor state
        self.start_measurement_action = None
        self.stop_measurement_action = None
        self.com_data_queue = None
        self.com_error_queue = None
        self.com_monitor = None
        self.plot = None
        self.curve = None
        self.plot_xy_value = [[], []]
        self.plot_ymin = None
        self.plot_ymax = None
        self.button_plot_clear = None
        self.plot_groupbox = None
        self.sensorDB = None
        self.timer = QTimer()
        self.time_interval = 10000  # miliseconds
        self.system_message = None
        self.system_message_layout = None
        self.create_configuration_layout()
        self.create_status_bar()
        # self.create_plot_layout()
        self.prepare_db()
        self.create_menu_bar()
        self.set_actions_enable_state()
        self.prepare_plot_box()
        # self.prepare_system_message()
        self.main_layout = self.create_main_frame()

    # ---------------------------------------------------------------------

    def create_status_bar(self):
        """Create status bar"""
        # self.statusBar().addWidget(self.status_text, 1)
        # self.status_text = QLabel('Monitor idle')
        status = self.statusBar()
        status.showMessage("Welcome to Sensor Realtime Monitor", 5000)

    # ---------------------------------------------------------------------

    # def debug_message(self, message, ):
    #     status = self.statusBar()
    #     status.showMessage(message, 5000)
    #
    # # ---------------------------------------------------------------------
    #
    # def status_message(self, message):
    #     status = self.statusBar()
    #     status.showMessage(message)

    # ---------------------------------------------------------------------

    def create_menu_bar(self):
        """Create menu"""
        file_menu = self.menuBar().addMenu("File")
        select_port_action = create_action(self,
                                           "Select COM &Port...",
                                           shortcut="Ctrl+P",
                                           triggered=self.on_select_port,
                                           tip="Select a COM port")
        # quit_action = create_action(
        #     self,
        #     "Quit",
        #     shortcut="Ctrl+Q",
        #     icon=get_std_icon("DialogCloseButton"),
        #     tip="Quit application",
        #     triggered=self.close,
        # )
        self.start_measurement_action = create_action(
            self,
            "Start",
            shortcut="Ctrl+S",
            triggered=self.on_start_measurement,
            tip="Start the data monitor")
        self.stop_measurement_action = create_action(
            self,
            "Stop",
            shortcut="Ctrl+T",
            triggered=self.on_stop_measurement,
            tip="Stop the data monitor")

        self.start_measurement_action.setEnabled(False)
        self.stop_measurement_action.setEnabled(False)

        add_actions(file_menu, (select_port_action,
                                self.start_measurement_action,
                                self.stop_measurement_action,
                                ))
        # None,
        # quit_action))

    # ----------------------------------------------------------------------

    def set_actions_enable_state(self):
        if not self.get_com_port():
            start_enable = stop_enable = False
        else:
            start_enable = not self.monitor_active
            stop_enable = self.monitor_active

        self.start_measurement_action.setEnabled(start_enable)
        self.stop_measurement_action.setEnabled(stop_enable)
        self.button_connect.setEnabled(start_enable)
        self.button_disconnect.setEnabled(stop_enable)

    # ----------------------------------------------------------------
    def on_select_port(self):
        print("on_select_port")
        ports = enumerate_serial_ports()
        if len(ports) == 0:
            self.update_message('No serial ports found!!!')
            QMessageBox.critical(self, 'No ports', 'No serial ports found')
            return
        item, ok = QInputDialog.getItem(self, 'Select a port', 'Serial port:', ports, 0, False)
        if ok and item:
            com_index = self.Com_ComboBox.findText(item)
            if com_index == -1:
                self.fill_ports_combobox()
                self.Com_ComboBox.setCurrentText(item)
            else:
                self.Com_ComboBox.setCurrentIndex(com_index)
            self.set_actions_enable_state()

    # ----------------------------------------------------------------
    def get_com_port(self):
        return self.Com_ComboBox.currentText()

    # ----------------------------------------------------------------

    def fill_ports_combobox(self):
        """ Purpose: rescan the serial port com and update the combobox
        """
        self.Com_ComboBox.clear()
        self.available_ports = enumerate_serial_ports()
        for value in self.available_ports:
            self.Com_ComboBox.addItem(value)
        # self.Com_ComboBox.currentIndexChanged.connect(self.set_actions_enable_state)

    # ----------------------------------------------------------------------
    def on_change_measurement_attribute(self):
        self.plot_xy_value = [[], []]
        self.plot.setAxisTitle(QwtPlot.yLeft, self.get_measured_curve_description())
        self.curve.setData(self.plot_xy_value[0], self.plot_xy_value[1])

    # ----------------------------------------------------------------------

    def create_configuration_layout(self):
        self.button_connect = QPushButton("Start")
        self.button_connect.clicked.connect(self.on_start_measurement)
        self.button_disconnect = QPushButton("Stop")
        self.button_disconnect.clicked.connect(self.on_stop_measurement)
        # self.button_disconnect.setEnabled(False)

        self.Com_ComboBox = QComboBox()
        self.fill_ports_combobox()

        v_layout = QGridLayout()

        # v_layout.addWidget(self.Com_ComboBox, 0, 0, 1, 1)
        v_layout.addWidget(self.button_connect, 0, 1)
        v_layout.addWidget(self.button_disconnect, 1, 1)

        comp_port = QFormLayout()
        comp_port.addRow(QLabel("COMP PORT: "), self.Com_ComboBox)
        v_layout.addLayout(comp_port, 0, 0)

        self.measurement_ComboBox = QComboBox()
        for m in self.measurements:
            self.measurement_ComboBox.addItem(m)
        self.measurement_ComboBox.currentIndexChanged.connect(self.on_change_measurement_attribute)
        m_layout = QFormLayout()
        m_layout.addRow(QLabel("Measure: "), self.measurement_ComboBox)
        v_layout.addLayout(m_layout, 1, 0)

        self.com_box = QGroupBox("Configuration")
        self.com_box.setLayout(v_layout)

    # ---------------------------------------------------------------------

    def prepare_plot_box(self):
        """
        Purpose:   create the pyqwt plot
        Return:    return a list containing the plot and the list of the curves
        """
        plot = QwtPlot(self)
        plot.setAxisTitle(QwtPlot.xBottom, 'Time [m]')
        # plot.setAutoReplot()
        # plot.enableAutoRange(enable=True)
        # plot.setAxisScale(QwtPlot.xBottom, 0, 10, 1)
        plot.setAxisTitle(QwtPlot.yLeft, self.get_measured_curve_description())
        # plot.setAxisScale(QwtPlot.yLeft, YMIN, YMAX, (YMAX - YMIN) / 10)
        plot.replot()

        curve = QwtPlotCurve('')
        curve.setRenderHint(QwtPlotItem.RenderAntialiased)
        pen = QPen(QColor('red'))
        pen.setWidth(2)
        curve.setPen(pen)
        curve.attach(plot)
        # curve.setData(x,y)

        plot_layout = QGridLayout()
        # plot_layout.addWidget(plot, 0, 0, 8, 7)

        plot_layout.addWidget(plot, 0, 0, 8, 8)

        # self.button_plot_clear = QPushButton("Clear screen")
        # self.button_plot_clear.clicked.connect(self.clear_screen)
        # plot_layout.addWidget(self.button_plot_clear, 0, 8)

        self.plot_groupbox = QGroupBox('Measurement')
        self.plot_groupbox.setLayout(plot_layout)
        self.plot = plot
        self.curve = curve

    # ---------------------------------------------------------------------
    # def update_message(self, msg):
    #     logger.info(msg)

    # # ---------------------------------------------------------------------
    #
    # def update_message(self, msg):
    #     self.system_message.appendPlainText(msg)
    #
    # # ---------------------------------------------------------------------
    # def clear_display(self):
    #     self.system_message.clear()
    #
    # # ---------------------------------------------------------------------
    # def prepare_system_message(self):
    #     log_text_box = QPlainTextEdit()
    #     log_text_box.setReadOnly(True)
    #
    #     layout = QGridLayout()
    #     layout.addWidget(log_text_box, 0, 0, 1, 8)
    #
    #     clear_button = QPushButton('Clear log window')
    #     layout.addWidget(clear_button, 0, 8)
    #     clear_button.clicked.connect(self.clear_display)
    #
    #     msg_layout = QGroupBox("System Message")
    #     msg_layout.setLayout(layout)
    #
    #     self.system_message = log_text_box
    #     self.system_message_layout = msg_layout

    # ---------------------------------------------------------------------
    def get_measured_curve_description(self):
        return self.measurement_ComboBox.currentText()

    # ---------------------------------------------------------------------

    def get_measured_unit(self):
        curve_description = self.get_measured_curve_description()
        return self.measurements[curve_description]

    # ---------------------------------------------------------------------
    def prepare_db(self):
        self.sensorDB = SensorDatabase(self)

    # ---------------------------------------------------------------------
    def get_time_interval(self):
        # 5 seconds before
        value = int(self.time_interval / 1000 - 5)
        if value <= 0:
            return int(self.time_interval / 1000)
        else:
            return value

    # ---------------------------------------------------------------------

    def on_start_measurement(self):
        self.com_data_queue = queue.Queue()
        self.com_error_queue = queue.Queue()
        self.port = self.get_com_port()

        self.com_monitor = SerialPortMonitor(self.com_data_queue,
                                             self.com_error_queue,
                                             self.port,
                                             self.get_measured_unit(),
                                             self.get_time_interval()
                                             )
        self.com_monitor.start()
        com_error = get_item_from_queue(self.com_error_queue)
        if com_error is not None:
            QMessageBox.critical(self, 'Monitor error', com_error)
            self.com_monitor = None

        self.monitor_active = True
        self.set_actions_enable_state()
        self.Com_ComboBox.setEnabled(False)
        self.measurement_ComboBox.setEnabled(False)
        self.sensorDB.start_measurement()
        self.timer.start(self.time_interval)
        self.timer.timeout.connect(self.update_screen)
        self.update_message("Start measurement")
        # self.status_message("Monitor running")

    # ---------------------------------------------------------------------

    def on_stop_measurement(self):
        if self.com_monitor is not None:
            self.com_monitor.join(1000)
            self.com_monitor = None

        self.monitor_active = False
        self.set_actions_enable_state()
        self.Com_ComboBox.setEnabled(True)
        self.measurement_ComboBox.setEnabled(True)
        self.sensorDB.stop_measurement()
        self.timer.stop()
        self.update_message("Stop measurement")
        # self.status_message("Monitor idle")

    # -------------------------------------------------------------------

    def clear_screen(self):
        print("clear_screen TODO")

    # ---------------------------------------------------------------------
    def parse_data(self, data):
        # data = [ (data, timestamp, time_from_start)]
        result = []
        # for d in data:
        d = data[-1]
        if d[0]:
            value = d[0].strip()
            address = value[1:3]
            type = value[3:4]
            y = float(value[5:])
            timestamp = d[1]
            x = round(d[2] / 60., 3)
            result.append({"type": type, "address": address, "x": x, "y": y, "timestamp": timestamp})
        return result

    # ---------------------------------------------------------------------
    def save_value_to_db(self, data=[]):
        if len(data) > 0:
            result = []
            for d in data:
                result.append({
                    "timestamp": d["timestamp"],
                    "H": (d["type"] == "H" and d["y"]) or None,
                    "D": (d["type"] == "D" and d["y"]) or None,
                    "T": (d["type"] == "T" and d["y"]) or None,
                    "M": (d["type"] == "M" and d["y"]) or None,
                    "A": (d["type"] == "A" and d["y"]) or None,
                    "sensor": str(d["address"]),
                    ## datetime format %Y-%m-%dT%H:%M:%S%z
                    "time": datetime.fromtimestamp(d["timestamp"]).astimezone().isoformat(timespec='seconds')
                })
            self.sensorDB.insert_sensor_record(result)

    # ---------------------------------------------------------------------
    def update_screen(self):
        data = list(get_all_from_queue(self.com_data_queue))
        if len(data) > 0:
            self.update_message(data[-1][0])
            result = self.parse_data(data)
            if len(result) > 0:
                for d in result:
                    self.plot_xy_value[0].append(d["x"])
                    self.plot_xy_value[1].append(d["y"])
                    if not self.plot_ymin or d["y"] < self.plot_ymin:
                        self.plot_ymin = d["y"] - 0.1 * d["y"]
                    if not self.plot_ymax or d["y"] > self.plot_ymax:
                        self.plot_ymax = d["y"] + 0.1 * d["y"]
                self.curve.setData(self.plot_xy_value[0], self.plot_xy_value[1])
                self.save_value_to_db(result)
                self.plot.setAxisScale(QwtPlot.xBottom, self.plot_xy_value[0][0], self.plot_xy_value[0][-1])
                self.plot.setAxisScale(QwtPlot.yLeft, self.plot_ymin, self.plot_ymax)

                self.plot.replot()

    # ---------------------------------------------------------------------

    def create_main_frame(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.com_box)
        main_layout.addWidget(self.plot_groupbox)
        # main_layout.addWidget(self.system_message_layout)
        main_layout.addStretch(1)
        return main_layout
