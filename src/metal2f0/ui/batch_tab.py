from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QDoubleSpinBox,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import QThread

from metal2f0.ui.workers import BatchWorker, BatchResult
from metal2f0.ui.info_button import SpecularityInfoButton

class BatchTab(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.directory_edit = QLineEdit()

        self.base_color_pattern_edit = QLineEdit("*_bc.png")
        self.metal_pattern_edit = QLineEdit("*_orm.png")
        self.diffuse_postfix_edit = QLineEdit("_diffuse.png")
        self.f0_postfix_edit = QLineEdit("_spec.png")

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

        self.overwrite_check = QCheckBox("Overwrite existing files")

        self.start_button = QPushButton("Start Batch")
        self.start_button.clicked.connect(self._start_batch)

        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)

        self._build_ui()

    def _build_ui(self) -> None:
        input_group = QGroupBox("Input")
        input_form = QFormLayout(input_group)
        input_form.addRow("Base directory", self._directory_row())
        input_form.addRow("BaseColor pattern", self.base_color_pattern_edit)
        input_form.addRow("Metal pattern", self.metal_pattern_edit)
        input_form.addRow("Metal channel", self.metal_channel_combo)

        output_group = QGroupBox("Output")
        output_form = QFormLayout(output_group)
        output_form.addRow("Diffuse postfix", self.diffuse_postfix_edit)
        output_form.addRow("F0 / Specular postfix", self.f0_postfix_edit)

        options_group = QGroupBox("Options")
        options_form = QFormLayout(options_group)
        specularity_widget = QWidget()
        specularity_layout = QHBoxLayout(specularity_widget)
        specularity_layout.setContentsMargins(0, 0, 0, 0)
        specularity_layout.addWidget(self.specularity_spin)
        specularity_layout.addWidget(SpecularityInfoButton())
        specularity_layout.addStretch()
        options_form.addRow("Specularity", specularity_widget)
        options_form.addRow("Overwrite", self.overwrite_check)

        layout = QVBoxLayout(self)
        layout.addWidget(input_group)
        layout.addWidget(output_group)
        layout.addWidget(options_group)
        layout.addWidget(self.start_button)
        layout.addWidget(self.output_edit)

    def _directory_row(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.directory_edit)

        button = QPushButton("Browse...")
        button.clicked.connect(self._browse_directory)
        layout.addWidget(button)

        return widget

    def _browse_directory(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select base directory")

        if path:
            self.directory_edit.setText(path)

    def metal_channel(self) -> int:
        return self.metal_channel_combo.currentIndex()

    def specularity(self) -> float:
        return self.specularity_spin.value()
    
    def _start_batch(self) -> None:
        try:
            directory = Path(self.directory_edit.text())

            if not directory.is_dir():
                raise ValueError("Base directory does not exist.")

            self.start_button.setEnabled(False)
            self.output_edit.clear()

            self.thread = QThread(self)

            self.worker = BatchWorker(
                directory,
                self.base_color_pattern_edit.text(),
                self.metal_pattern_edit.text(),
                self.diffuse_postfix_edit.text(),
                self.f0_postfix_edit.text(),
                self.metal_channel(),
                self.specularity(),
                self.overwrite_check.isChecked(),
            )

            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self._batch_finished)
            self.worker.failed.connect(self._batch_failed)
            self.worker.finished.connect(self.thread.quit)
            self.worker.failed.connect(self.thread.quit)
            self.thread.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

        except Exception as exc:
            self._batch_failed(str(exc))

    def _batch_finished(self, result: BatchResult) -> None:
        self.start_button.setEnabled(True)

        self.output_edit.appendPlainText(f"Processed: {len(result.processed)}")
        self.output_edit.appendPlainText(f"Skipped: {len(result.skipped)}")
        self.output_edit.appendPlainText(f"Failed: {len(result.failed)}")
        self.output_edit.appendPlainText("")

        for material in result.processed:
            self.output_edit.appendPlainText(f"✓ {material.key}")
        for skipped in result.skipped:
            self.output_edit.appendPlainText(f"Skipped: {skipped.material.key} — "f"{skipped.reason}")
        for failed in result.failed:
            self.output_edit.appendPlainText(f"Failed: {failed.material.key} — "f"{failed.error}")

        self.thread = None
        self.worker = None

    def _batch_failed(self, message: str) -> None:
        self.start_button.setEnabled(True)
        self.output_edit.appendPlainText(f"Batch failed: {message}")

        self.thread = None
        self.worker = None