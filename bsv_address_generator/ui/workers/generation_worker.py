from PyQt6.QtCore import QThread, pyqtSignal

from ...core.derivation import derive_addresses


class AddressGenerationWorker(QThread):
    """Worker thread for address generation to prevent UI freezing."""

    progress_updated = pyqtSignal(int)
    generation_completed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, xpub, count, base_path, start_index=0):
        super().__init__()
        self.xpub = xpub
        self.count = count
        self.base_path = base_path
        self.start_index = start_index

    def run(self):
        try:
            addresses = derive_addresses(
                self.xpub, self.count, self.base_path, self.start_index
            )
            if addresses:
                self.generation_completed.emit(addresses)
            else:
                self.error_occurred.emit("Failed to generate addresses")
        except Exception as e:
            self.error_occurred.emit(str(e))
