from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from metal2f0 import __version__

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About metal2f0")
        self.setModal(True)

        layout = QVBoxLayout(self)

        icon = QLabel()
        icon.setPixmap(QPixmap(":/icons/metal2f0.svg")
                       .scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation,)
                       )
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("<h2>metal2f0</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        description = QLabel("Convert textures from metallic-roughness workflow into specular workflow<br><br>"
            f"Version {__version__}<br><br>"
            "Copyright © 2026 Tobias Wink<br><br>"
            "Licensed under the MIT License."
        )
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)