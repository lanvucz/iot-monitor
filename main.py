from qtpy import QtWidgets as QW
from guidata.qthelpers import (
    qt_app_context,
    win32_fix_title_bar_background,
)
from qtpy.QtWidgets import (
    QPushButton,
    QGridLayout,
    QGroupBox,
    QPlainTextEdit
)

from plot_monitor import PlotMonitor


APP_NAME = "Sensor Application"
VERSION = "1.0.0"


class MainWindow(QW.QMainWindow):
    """Main Window"""

    def __init__(self):
        super().__init__()
        win32_fix_title_bar_background(self)
        self.plot_widget = None
        self.system_message = None
        self.system_message_layout = None
        self.prepare_system_message()
        self.setup()

    def setup(self):
        """Setup window parameters"""
        # self.setWindowIcon(get_icon("./favicon.ico"))
        # self.setWindowTitle(APP_NAME)
        # self.resize(QC.QSize(800, 600))
        self.plot_widget = PlotMonitor(self)
        # self.setCentralWidget(self.plot_widget)
        main_layout = self.plot_widget.main_layout
        main_layout.addWidget(self.system_message_layout)
        main_frame = QW.QWidget()
        main_frame.setLayout(main_layout)
        self.setCentralWidget(main_frame)

    # # -----------------------------------------------
    def update_message(self, msg):
        self.system_message.appendPlainText(msg)

    # ---------------------------------------------------------------------
    def clear_display(self):
        self.system_message.clear()

    # ---------------------------------------------------------------------
    # @Slot(str, logging.LogRecord)
    # def update_status(self, status):
    #     self.system_message.appendPlainText(status)
    # ---------------------------------------------------------------------

    def prepare_system_message(self):
        log_text_box = QPlainTextEdit()
        log_text_box.setReadOnly(True)

        layout = QGridLayout()
        layout.addWidget(log_text_box, 0, 0, 1, 8)

        # handler = QtHandler(self.update_status)
        # handler = Handler(self)
        # logger.addHandler(handler)
        # # logger.setLevel(logging.INFO)
        # handler.new_record.connect(log_text_box.appendPlainText)

        clear_button = QPushButton('Clear log window')
        layout.addWidget(clear_button, 0, 8)
        clear_button.clicked.connect(self.clear_display)

        msg_layout = QGroupBox("System Message")
        msg_layout.setLayout(layout)

        self.system_message = log_text_box
        self.system_message_layout = msg_layout


# -----------------------------------------------

if __name__ == "__main__":
    with qt_app_context(exec_loop=True):
        window = MainWindow()
        window.show()

# todo csv

