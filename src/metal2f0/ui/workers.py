from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from metal2f0.processing.batch import BatchResult, process_batch
from metal2f0.processing.processor import process


class MaterialWorker(QObject):
    finished = Signal()
    failed = Signal(str)

    def __init__(
        self,
        base_color_path: Path,
        metal_path: Path,
        diffuse_path: Path,
        f0_path: Path,
        metal_channel: int,
        specularity: float,
    ) -> None:
        super().__init__()

        self.base_color_path = base_color_path
        self.metal_path = metal_path
        self.diffuse_path = diffuse_path
        self.f0_path = f0_path
        self.metal_channel = metal_channel
        self.specularity = specularity

    @Slot()
    def run(self) -> None:
        try:
            process(
                base_color_path = self.base_color_path,
                metal_path = self.metal_path,
                diffuse_path = self.diffuse_path,
                f0_path = self.f0_path,
                metal_channel=self.metal_channel,
                specularity=self.specularity,
            )
        except Exception as exc:
            self.failed.emit(str(exc))
        else:
            self.finished.emit()


class BatchWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        directory: Path,
        base_color_pattern: str,
        metal_pattern: str,
        diffuse_postfix: str,
        f0_postfix: str,
        metal_channel: int,
        specularity: float,
        overwrite: bool,
    ) -> None:
        super().__init__()

        self.directory = directory
        self.base_color_pattern = base_color_pattern
        self.metal_pattern = metal_pattern
        self.diffuse_postfix = diffuse_postfix
        self.f0_postfix = f0_postfix
        self.metal_channel = metal_channel
        self.specularity = specularity
        self.overwrite = overwrite

    @Slot()
    def run(self) -> None:
        try:
            result = process_batch(
                directory = self.directory,
                base_color_pattern = self.base_color_pattern,
                metal_pattern = self.metal_pattern,
                diffuse_postfix = self.diffuse_postfix,
                f0_postfix = self.f0_postfix,
                metal_channel=self.metal_channel,
                specularity=self.specularity,
                overwrite=self.overwrite,
            )
        except Exception as exc:
            self.failed.emit(str(exc))
        else:
            self.finished.emit(result)
