from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class InfoDialog(QDialog):
    def __init__(self, title: str, content: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle(title)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(content)
        layout.addWidget(buttons)


class InfoButton(QToolButton):
    def __init__(self, title: str, content_factory, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setText("?")
        self.setFixedSize(24, 24)
        self.setAutoRaise(True)

        self.clicked.connect(
            lambda: InfoDialog(
                title,
                content_factory(),
                self,
            ).exec(),
        )

class SpecularityInfoButton(InfoButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Specularity",
            self._create_content,
            parent,
        )

    @staticmethod
    def _create_content() -> QWidget:
        widget = QWidget()

        layout = QVBoxLayout(widget)

        text = QLabel("Specularity defines the dielectric F0 reflectance used for non-metallic surfaces. " \
        "0.04 corresponds to approximately 4% reflectance at normal incidence, which is a good default value."
        )
        text.setWordWrap(True)
        layout.addWidget(text)

        reference = QLabel('More info: <a href="https://physicallybased.info/">Physically Based - The PBR values database</a>')
        reference.setOpenExternalLinks(True)

        layout.addWidget(reference)

        return widget