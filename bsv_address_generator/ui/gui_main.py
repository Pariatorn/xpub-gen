"""
BSV Address Generator - PyQt6 GUI Main Window
A user-friendly graphical interface for the BSV address generator.
"""

import sys
from decimal import Decimal
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import bsv_address_generator.ui.input_handlers as input_handlers
import bsv_address_generator.ui.output_handlers as output_handlers
from config import APP_VERSION

# Import core functionality
from ..core.distribution import (
    distribute_amounts_equal,
    distribute_amounts_random,
    distribute_amounts_random_optimal,
)
from ..utils.state_manager import check_previous_state
from .widgets.input_panel import InputPanel
from .widgets.results_panel import ResultsPanel
from .workers.generation_worker import AddressGenerationWorker


class BSVAddressGeneratorGUI(QMainWindow):
    """Main GUI window for BSV Address Generator."""

    def __init__(self):
        super().__init__()
        self.addresses = []
        self.amounts = []
        self.distribution_info = None
        self.worker_thread = None

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"BSV Address Generator v{APP_VERSION}")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # Create header
        self.create_header(main_layout)

        # Create main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Input controls (with fixed width container)
        left_container = QWidget()
        left_container.setMaximumWidth(380)
        left_container.setMinimumWidth(350)
        left_container_layout = QVBoxLayout(left_container)
        left_container_layout.setContentsMargins(0, 0, 0, 0)

        self.input_panel = InputPanel()
        left_container_layout.addWidget(self.input_panel)
        splitter.addWidget(left_container)

        # Right panel - Results
        self.results_panel = ResultsPanel()
        splitter.addWidget(self.results_panel)

        # Set splitter proportions and constraints
        splitter.setStretchFactor(0, 0)  # Fixed size for left panel
        splitter.setStretchFactor(1, 1)  # Expandable right panel
        splitter.setSizes([350, 850])  # Set initial sizes

        # Status bar
        self.statusBar().showMessage("Ready to generate addresses")

    def create_header(self, parent_layout):
        """Create application header."""
        header = QFrame()
        header.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2c3e50, stop: 1 #34495e);
                border-bottom: 2px solid #e74c3c;
                padding: 8px;
                max-height: 45px;
                min-height: 45px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)

        title = QLabel("BSV Address Generator")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title.setStyleSheet("color: white; margin: 0px; padding: 0px;")

        # BSV Symbol in the center
        bsv_symbol = QLabel("₿")
        bsv_symbol.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        bsv_symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bsv_symbol.setStyleSheet(
            """
            color: #f39c12;
            margin: 0px;
            padding: 0px;
            background: transparent;
            border: none;
        """
        )

        subtitle = QLabel("Generate addresses from xpub")
        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        subtitle.setStyleSheet(
            "color: #bdc3c7; font-size: 10px; margin: 0px; padding: 0px;"
        )

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(bsv_symbol)
        header_layout.addStretch()
        header_layout.addWidget(subtitle)
        parent_layout.addWidget(header)

    def setup_connections(self):
        """Setup signal/slot connections."""
        # Button connections
        self.input_panel.paste_btn.clicked.connect(self.paste_xpub)
        self.input_panel.load_file_btn.clicked.connect(self.load_xpub_file)
        self.input_panel.clear_xpub_btn.clicked.connect(self.clear_xpub)

        self.input_panel.path_combo.currentTextChanged.connect(self.on_path_changed)
        self.input_panel.dist_mode.currentTextChanged.connect(
            self.on_distribution_mode_changed
        )

        self.input_panel.preview_btn.clicked.connect(self.preview_distribution)
        self.input_panel.generate_btn.clicked.connect(self.generate_addresses)

        self.results_panel.save_txt_btn.clicked.connect(self.save_txt)
        self.results_panel.save_csv_btn.clicked.connect(self.save_csv)
        self.results_panel.batch_export_btn.clicked.connect(self.batch_export)

        # Auto-update random bounds when amount changes
        self.input_panel.bsv_amount.valueChanged.connect(self.update_random_bounds)
        self.input_panel.address_count.valueChanged.connect(self.update_random_bounds)

    def load_example_xpub(self):
        """Load example xpub if available."""
        example_file = Path("example_xpub.txt")
        if example_file.exists():
            try:
                with open(example_file, "r") as f:
                    xpub = f.read().strip()
                    self.input_panel.xpub_input.setPlainText(xpub)
            except Exception:
                pass  # Silently ignore if can't load example

    def paste_xpub(self):
        """Paste XPUB from clipboard."""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.input_panel.xpub_input.setPlainText(text)

    def load_xpub_file(self):
        """Load XPUB from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load XPUB File", "", "Text files (*.txt);;All files (*.*)"
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    # Handle multiple lines - take first non-empty line
                    lines = [
                        line.strip() for line in content.split("\n") if line.strip()
                    ]
                    if lines:
                        self.input_panel.xpub_input.setPlainText(lines[0])
                    else:
                        QMessageBox.warning(
                            self, "Error", "No valid content found in file."
                        )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def clear_xpub(self):
        """Clear XPUB input."""
        self.input_panel.xpub_input.clear()

    def on_path_changed(self):
        """Handle derivation path selection change."""
        show_custom = self.input_panel.path_combo.currentText() == "Custom path"
        self.input_panel.custom_path_input.setVisible(show_custom)

    def on_distribution_mode_changed(self):
        """Handle distribution mode change."""
        mode = self.input_panel.dist_mode.currentText()
        show_params = (
            "Random distribution" in mode and mode != "Smart random distribution"
        )
        self.input_panel.random_params_widget.setVisible(show_params)

        if not show_params:
            self.update_random_bounds()

    def update_random_bounds(self):
        """Update random distribution bounds based on total amount and address count."""
        if self.input_panel.dist_mode.currentText() == "Random distribution":
            total = Decimal(str(self.input_panel.bsv_amount.value()))
            count = self.input_panel.address_count.value()

            if count > 0:
                avg = total / count
                # Set reasonable defaults
                min_val = float(avg * Decimal("0.1"))  # 10% of average
                max_val = float(avg * Decimal("2.0"))  # 200% of average

                # Ensure minimum is above dust limit
                dust_limit_bsv = 0.00000546  # 546 satoshis in BSV
                min_val = max(min_val, dust_limit_bsv)

                self.input_panel.min_amount.setValue(min_val)
                self.input_panel.max_amount.setValue(max_val)

    def get_derivation_path(self):
        """Get the selected derivation path."""
        path_text = self.input_panel.path_combo.currentText()
        if "receiving" in path_text:
            return "0"
        elif "change" in path_text:
            return "1"
        else:  # Custom path
            return self.input_panel.custom_path_input.text().strip()

    def validate_inputs(self):
        """Validate all input fields."""
        return input_handlers.validate_inputs(self, self.input_panel)

    def preview_distribution(self):
        """Preview the distribution without generating addresses."""
        if not self.validate_inputs():
            return

        total_amount = Decimal(str(self.input_panel.bsv_amount.value()))
        count = self.input_panel.address_count.value()
        mode = self.input_panel.dist_mode.currentText()

        preview_text = "Distribution Preview\n"
        preview_text += "=" * 50 + "\n\n"
        preview_text += f"Total BSV Amount: {total_amount} BSV\n"
        preview_text += f"Number of Addresses: {count}\n"
        preview_text += f"Distribution Mode: {mode}\n\n"

        try:
            if mode == "Equal distribution":
                amounts = distribute_amounts_equal(total_amount, count)
                preview_text += f"Amount per address: {amounts[0]} BSV\n"

            elif mode == "Random distribution":
                min_amt = Decimal(str(self.input_panel.min_amount.value()))
                max_amt = Decimal(str(self.input_panel.max_amount.value()))
                preview_text += f"Random range: {min_amt} - {max_amt} BSV\n"
                preview_text += f"Average amount: {total_amount / count} BSV\n"

            elif mode == "Smart random distribution":
                from ..core.distribution import calculate_optimal_random_bounds

                min_amt, max_amt, dist_info = calculate_optimal_random_bounds(
                    total_amount, count
                )
                preview_text += f"Optimal range: {min_amt:.8f} - {max_amt:.8f} BSV\n"
                preview_text += (
                    f"Average amount: {dist_info['average_amount']:.8f} BSV\n"
                )
                preview_text += f"Variation: {dist_info['variation_percent']:.1f}%\n"

            self.results_panel.preview_text.setPlainText(preview_text)
            self.results_panel.results_tabs.setCurrentIndex(0)  # Switch to preview tab

        except Exception as e:
            QMessageBox.critical(
                self, "Preview Error", f"Failed to create preview: {str(e)}"
            )

    def generate_addresses(self):
        """Generate addresses using worker thread."""
        if not self.validate_inputs():
            return

        # Disable generate button and show progress
        self.input_panel.generate_btn.setEnabled(False)
        self.input_panel.progress_bar.setVisible(True)
        self.input_panel.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage("Generating addresses...")

        # Get parameters
        xpub = self.input_panel.xpub_input.toPlainText().strip()
        count = self.input_panel.address_count.value()
        base_path = self.get_derivation_path()

        # Determine starting index
        start_index = 0

        # Check if user manually set a starting index
        manual_index = self.input_panel.manual_start_index.value()
        if manual_index > 0:
            start_index = manual_index
            self.statusBar().showMessage(
                f"Starting from manually set index: {start_index}"
            )
        else:
            # Check for previous state only if manual index is 0 (auto mode)
            state_info = check_previous_state(xpub, base_path)
            if state_info["can_continue"]:
                reply = QMessageBox.question(
                    self,
                    "Continue Previous Generation?",
                    (
                        "Found previous derivation state (last index: "
                        f"{state_info['last_index']}).\n"
                        "Continue from where you left off?"
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    start_index = state_info["last_index"] + 1

        # Start worker thread
        self.worker_thread = AddressGenerationWorker(
            xpub, count, base_path, start_index
        )
        self.worker_thread.generation_completed.connect(self.on_generation_completed)
        self.worker_thread.error_occurred.connect(self.on_generation_error)
        self.worker_thread.start()

    def on_generation_completed(self, addresses):
        """Handle completed address generation."""
        self.addresses = addresses

        # Generate amounts based on distribution mode
        total_amount = Decimal(str(self.input_panel.bsv_amount.value()))
        mode = self.input_panel.dist_mode.currentText()

        try:
            if mode == "Equal distribution":
                self.amounts = distribute_amounts_equal(total_amount, len(addresses))

            elif mode == "Random distribution":
                min_amt = Decimal(str(self.input_panel.min_amount.value()))
                max_amt = Decimal(str(self.input_panel.max_amount.value()))
                self.amounts = distribute_amounts_random(
                    total_amount, len(addresses), min_amt, max_amt
                )

            elif mode == "Smart random distribution":
                self.amounts, self.distribution_info = (
                    distribute_amounts_random_optimal(total_amount, len(addresses))
                )

            # Update table
            self.update_addresses_table()

            # Switch to addresses tab
            self.results_panel.results_tabs.setCurrentIndex(1)

            self.statusBar().showMessage(
                f"Successfully generated {len(addresses)} addresses"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Distribution Error", f"Failed to distribute amounts: {str(e)}"
            )

        finally:
            # Re-enable UI
            self.input_panel.generate_btn.setEnabled(True)
            self.input_panel.progress_bar.setVisible(False)

    def on_generation_error(self, error_message):
        """Handle generation error."""
        QMessageBox.critical(
            self, "Generation Error", f"Failed to generate addresses: {error_message}"
        )

        # Re-enable UI
        self.input_panel.generate_btn.setEnabled(True)
        self.input_panel.progress_bar.setVisible(False)
        self.statusBar().showMessage("Address generation failed")

    def update_addresses_table(self):
        """Update the addresses table with generated data."""
        if not self.addresses or not self.amounts:
            return

        self.results_panel.addresses_table.setRowCount(len(self.addresses))

        for i, (addr_info, amount) in enumerate(zip(self.addresses, self.amounts)):
            self.results_panel.addresses_table.setItem(
                i, 0, QTableWidgetItem(str(addr_info["index"]))
            )
            self.results_panel.addresses_table.setItem(
                i, 1, QTableWidgetItem(addr_info["address"])
            )
            self.results_panel.addresses_table.setItem(
                i, 2, QTableWidgetItem(f"{amount:.8f}")
            )

        # Resize columns to content
        self.results_panel.addresses_table.resizeColumnsToContents()

    def save_txt(self):
        """Save addresses to TXT file."""
        output_handlers.save_txt(self, self.addresses)

    def save_csv(self):
        """Save addresses with amounts to CSV file."""
        output_handlers.save_csv(self, self.addresses, self.amounts)

    def batch_export(self):
        """Export addresses in batches."""
        output_handlers.batch_export(self, self.addresses, self.amounts)


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)

    # Set application icon
    # Create an assets directory in the project root and place your icon file there.
    icon_path = Path(__file__).parent.parent.parent / "assets/app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    app.setApplicationName("BSV Address Generator")
    app.setOrganizationName("BSV Tools")

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = BSVAddressGeneratorGUI()
    window.load_example_xpub()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
