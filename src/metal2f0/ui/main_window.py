from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtGui import QIcon, QAction, QKeySequence

from metal2f0.ui.single_tab import SingleTab
from metal2f0.ui.batch_tab import BatchTab
from metal2f0.ui.about_dialog import AboutDialog
from metal2f0.ui.third_party_licenses_dialog import ThirdPartyLicensesDialog


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
        self._create_menu_bar()


    def _create_menu_bar(self):
        file_menu = self.menuBar().addMenu("&File")

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = self.menuBar().addMenu("&Help")

        licenses_action = QAction("Third-Party Licenses", self)
        licenses_action.triggered.connect(self._show_third_party_licenses)
        help_menu.addAction(licenses_action)

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_third_party_licenses(self):
        dialog = ThirdPartyLicensesDialog(self)
        dialog.exec()

    def _show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()