from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtGui import QIcon

from metal2f0.ui.single_tab import SingleTab
from metal2f0.ui.batch_tab import BatchTab


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowIcon(
            QIcon(":/icons/metal2f0.svg")
        )
        self.setWindowTitle("Metal2F0")
        self.resize(900, 650)

        tabs = QTabWidget()

        tabs.addTab(
            SingleTab(),
            "Single",
        )

        tabs.addTab(
            BatchTab(),
            "Batch",
        )

        self.setCentralWidget(tabs)