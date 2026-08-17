from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import QThread

from metal2f0.ui.workers import MaterialWorker
from metal2f0.ui.info_button import SpecularityInfoButton


class SingleTab(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.base_color_edit = QLineEdit()
        self.metal_edit = QLineEdit()
        self.diffuse_edit = QLineEdit()
        self.f0_edit = QLineEdit()

        self.metal_channel_combo = QComboBox()
        self.metal_channel_combo.addItems(
            [
                "Red",
                "Green",
                "Blue",
                "Alpha",
            ]
        )
        self.metal_channel_combo.setCurrentIndex(2)
        self.metal_channel_combo.setFixedWidth(120)

        self.specularity_spin = QDoubleSpinBox()
        self.specularity_spin.setRange(0.0, 1.0)
        self.specularity_spin.setDecimals(2)
        self.specularity_spin.setSingleStep(0.01)
        self.specularity_spin.setValue(0.04)
        self.specularity_spin.setFixedWidth(120)

        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self._convert)

        self._build_ui()

    def _build_ui(self) -> None:
        input_group = QGroupBox("Input")
        input_form = QFormLayout(input_group)

        input_form.addRow(
            "BaseColor",
            self._file_row(self.base_color_edit, self._browse_base_color)
        )

        input_form.addRow(
            "Metal",
            self._file_row(self.metal_edit, self._browse_metal)
        )

        input_form.addRow(
            "Metal channel",
            self.metal_channel_combo
        )

        output_group = QGroupBox("Output")
        output_form = QFormLayout(output_group)

        output_form.addRow(
            "Diffuse Albedo",
            self._file_row(self.diffuse_edit, self._browse_diffuse)
        )

        output_form.addRow(
            "F0 / Specular",
            self._file_row(self.f0_edit, self._browse_f0)
        )

        specularity_widget = QWidget()

        specularity_layout = QHBoxLayout(specularity_widget)
        specularity_layout.setContentsMargins(0, 0, 0, 0)

        specularity_layout.addWidget(self.specularity_spin)
        specularity_layout.addWidget(SpecularityInfoButton())
        specularity_layout.addStretch()

        output_form.addRow("Specularity", specularity_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(input_group)
        layout.addWidget(output_group)
        layout.addWidget(self.convert_button)
        layout.addStretch()

    @staticmethod
    def _file_row(edit: QLineEdit, browse_callback) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(edit)

        button = QPushButton("Browse...")
        button.clicked.connect(browse_callback)

        layout.addWidget(button)

        return widget

    def _browse_base_color(self) -> None:
        self._browse_input(self.base_color_edit)

    def _browse_metal(self) -> None:
        self._browse_input(self.metal_edit)

    def _browse_diffuse(self) -> None:
        self._browse_output(self.diffuse_edit)

    def _browse_f0(self) -> None:
        self._browse_output(self.f0_edit)

    @staticmethod
    def _browse_input(edit: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Select image",
            "",
            "Images (*.png *.tga *.exr);;All files (*)",
        )

        if path:
            edit.setText(path)

    @staticmethod
    def _browse_output(edit: QLineEdit) -> None:
        path, _ = QFileDialog.getSaveFileName(
            None,
            "Select output image",
            "",
            "PNG (*.png);;TGA (*.tga);;OpenEXR (*.exr)",
        )

        if path:
            edit.setText(path)

    def metal_channel(self) -> int:
        return self.metal_channel_combo.currentIndex()

    def specularity(self) -> float:
        return self.specularity_spin.value()

    def _convert(self) -> None:
        try:
            base_color = Path(self.base_color_edit.text())
            metal = Path(self.metal_edit.text())
            diffuse = Path(self.diffuse_edit.text())
            f0 = Path(self.f0_edit.text())

            if not base_color.is_file():
                raise ValueError("BaseColor file does not exist.")

            if not metal.is_file():
                raise ValueError("Metal file does not exist.")

            self.convert_button.setEnabled(False)

            self.thread = QThread(self)

            self.worker = MaterialWorker(
                base_color,
                metal,
                diffuse,
                f0,
                self.metal_channel(),
                self.specularity(),
            )

            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self._conversion_finished)
            self.worker.failed.connect(self._conversion_failed)
            self.worker.finished.connect(self.thread.quit)
            self.worker.failed.connect(self.thread.quit)
            self.thread.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

        except Exception as exc:
            self._conversion_failed(str(exc))

    def _conversion_finished(self) -> None:
        self.convert_button.setEnabled(True)

        self.thread = None
        self.worker = None

    def _conversion_failed(self, message: str) -> None:
        self.convert_button.setEnabled(True)

        self.thread = None
        self.worker = None
