from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QTextBrowser, QVBoxLayout


class ThirdPartyLicensesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Third-Party Licenses")
        self.resize(650, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        description = QLabel(
            "metal2f0 uses the following third-party software. "
            "For complete license and copyright information, "
            "please refer to the official project documentation."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(
            """
            <h3>NumPy</h3>
            <p>
                Version: 2.5.2<br>
                License: BSD-3-Clause
            </p>
            <p>
                <a href="https://numpy.org/doc/stable/license.html">
                    NumPy license information
                </a>
            </p>

            <h3>OpenImageIO</h3>
            <p>
                Version: 3.1.16.0<br>
                License: Apache License 2.0
            </p>
            <p>
                <a href="https://github.com/AcademySoftwareFoundation/OpenImageIO/blob/main/LICENSE.md">
                    OpenImageIO license information
                </a>
            </p>

            <h3>PySide6 / Qt for Python</h3>
            <p>
                Version: 6.11.1<br>
                License: LGPLv3
            </p>
            <p>
                <a href="https://doc.qt.io/qtforpython-6/licenses.html">
                    Qt for Python license information
                </a>
            </p>
            <p>
                <a href="https://doc.qt.io/qt-6/licenses-used-in-qt.html">
                    Qt third-party components
                </a>
            </p>
            """
        )
        layout.addWidget(browser)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)