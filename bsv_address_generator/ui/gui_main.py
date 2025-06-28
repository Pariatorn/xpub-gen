"""
BSV Address Generator - PyQt6 GUI Main Window
A user-friendly graphical interface for the BSV address generator.
"""

import os
import sys
from decimal import Decimal
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import core functionality
from ..core.derivation import derive_addresses
from ..core.distribution import (
    create_address_batches,
    distribute_amounts_equal,
    distribute_amounts_random,
    distribute_amounts_random_optimal,
)
from ..utils.state_manager import check_previous_state


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
        self.setWindowTitle("BSV Address Generator")
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

        left_panel = self.create_input_panel()
        left_container_layout.addWidget(left_panel)
        splitter.addWidget(left_container)

        # Right panel - Results
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)

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

    def create_input_panel(self):
        """Create the left input panel."""
        # Create scroll area for the input panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # XPUB Input Group
        xpub_group = QGroupBox("1. Extended Public Key (XPUB)")
        xpub_layout = QVBoxLayout(xpub_group)

        # XPUB text field
        self.xpub_input = QTextEdit()
        self.xpub_input.setMaximumHeight(70)
        self.xpub_input.setMinimumHeight(50)
        self.xpub_input.setPlaceholderText("Paste your extended public key here...")
        xpub_layout.addWidget(self.xpub_input)

        # XPUB buttons
        xpub_buttons = QHBoxLayout()
        self.paste_btn = QPushButton("📋 Paste")
        self.load_file_btn = QPushButton("📁 Load from File")
        self.clear_xpub_btn = QPushButton("🗑️ Clear")

        xpub_buttons.addWidget(self.paste_btn)
        xpub_buttons.addWidget(self.load_file_btn)
        xpub_buttons.addWidget(self.clear_xpub_btn)
        xpub_layout.addLayout(xpub_buttons)

        layout.addWidget(xpub_group)

        # Address Count Group
        count_group = QGroupBox("2. Number of Addresses")
        count_layout = QHBoxLayout(count_group)

        self.address_count = QSpinBox()
        self.address_count.setMinimum(1)
        self.address_count.setMaximum(10000)
        self.address_count.setValue(10)

        count_layout.addWidget(QLabel("Generate:"))
        count_layout.addWidget(self.address_count)
        count_layout.addWidget(QLabel("addresses"))
        count_layout.addStretch()

        layout.addWidget(count_group)

        # Starting Index Group
        index_group = QGroupBox("2b. Starting Index (Optional)")
        index_layout = QHBoxLayout(index_group)

        self.manual_start_index = QSpinBox()
        self.manual_start_index.setMinimum(0)
        self.manual_start_index.setMaximum(2147483647)  # BIP32 max index
        self.manual_start_index.setValue(0)
        self.manual_start_index.setSpecialValueText("Auto (continue from last)")

        index_layout.addWidget(QLabel("Start from index:"))
        index_layout.addWidget(self.manual_start_index)
        index_layout.addStretch()

        layout.addWidget(index_group)

        # Derivation Path Group
        path_group = QGroupBox("3. Derivation Path")
        path_layout = QVBoxLayout(path_group)

        self.path_combo = QComboBox()
        self.path_combo.addItems(
            ["Standard receiving (m/0/i)", "Standard change (m/1/i)", "Custom path"]
        )

        self.custom_path_input = QLineEdit()
        self.custom_path_input.setPlaceholderText("e.g., 44/0/0")
        self.custom_path_input.setVisible(False)

        path_layout.addWidget(self.path_combo)
        path_layout.addWidget(self.custom_path_input)

        layout.addWidget(path_group)

        # Distribution Group
        dist_group = QGroupBox("4. BSV Distribution")
        dist_layout = QVBoxLayout(dist_group)

        # Total BSV amount
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Total amount:"))
        self.bsv_amount = QDoubleSpinBox()
        self.bsv_amount.setMinimum(0.00000001)
        self.bsv_amount.setMaximum(1000000.0)
        self.bsv_amount.setDecimals(8)
        self.bsv_amount.setValue(1.0)
        amount_layout.addWidget(self.bsv_amount)
        amount_layout.addWidget(QLabel("BSV"))
        amount_layout.addStretch()
        dist_layout.addLayout(amount_layout)

        # Distribution mode
        self.dist_mode = QComboBox()
        self.dist_mode.addItems(
            ["Equal distribution", "Random distribution", "Smart random distribution"]
        )
        dist_layout.addWidget(QLabel("Distribution mode:"))
        dist_layout.addWidget(self.dist_mode)

        # Random distribution parameters
        self.random_params_widget = QWidget()
        random_layout = QGridLayout(self.random_params_widget)

        random_layout.addWidget(QLabel("Min amount:"), 0, 0)
        self.min_amount = QDoubleSpinBox()
        self.min_amount.setMinimum(0.00000001)
        self.min_amount.setMaximum(1000000.0)
        self.min_amount.setDecimals(8)
        self.min_amount.setValue(0.01)
        random_layout.addWidget(self.min_amount, 0, 1)
        random_layout.addWidget(QLabel("BSV"), 0, 2)

        random_layout.addWidget(QLabel("Max amount:"), 1, 0)
        self.max_amount = QDoubleSpinBox()
        self.max_amount.setMinimum(0.00000001)
        self.max_amount.setMaximum(1000000.0)
        self.max_amount.setDecimals(8)
        self.max_amount.setValue(0.1)
        random_layout.addWidget(self.max_amount, 1, 1)
        random_layout.addWidget(QLabel("BSV"), 1, 2)

        self.random_params_widget.setVisible(False)
        dist_layout.addWidget(self.random_params_widget)

        layout.addWidget(dist_group)

        # Create a fixed button area that doesn't scroll
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(10, 5, 10, 10)

        # Preview button
        self.preview_btn = QPushButton("🔍 Preview Distribution")
        self.preview_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                border: 2px solid #2980b9;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #5dade2, stop: 1 #3498db);
                border: 2px solid #3498db;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #21618c);
            }
        """
        )
        button_layout.addWidget(self.preview_btn)

        # Generate button
        self.generate_btn = QPushButton("🚀 Generate Addresses")
        self.generate_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #229954);
                color: white;
                border: 2px solid #229954;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2ecc71, stop: 1 #27ae60);
                border: 2px solid #27ae60;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #229954, stop: 1 #1e8449);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
                border: 2px solid #95a5a6;
            }
        """
        )
        button_layout.addWidget(self.generate_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        button_layout.addWidget(self.progress_bar)

        layout.addWidget(button_container)

        layout.addStretch()

        # Set the panel as the scroll area's widget
        scroll_area.setWidget(panel)
        return scroll_area

    def create_results_panel(self):
        """Create the right results panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Results tabs
        self.results_tabs = QTabWidget()

        # Preview tab
        self.preview_tab = QWidget()
        preview_layout = QVBoxLayout(self.preview_tab)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Distribution preview will appear here...")
        preview_layout.addWidget(self.preview_text)

        self.results_tabs.addTab(self.preview_tab, "📊 Preview")

        # Addresses tab
        self.addresses_tab = QWidget()
        addresses_layout = QVBoxLayout(self.addresses_tab)

        self.addresses_table = QTableWidget()
        self.addresses_table.setColumnCount(3)
        self.addresses_table.setHorizontalHeaderLabels(
            ["Index", "Address", "Amount (BSV)"]
        )
        addresses_layout.addWidget(self.addresses_table)

        # Export buttons
        export_layout = QHBoxLayout()
        self.save_txt_btn = QPushButton("💾 Save TXT")
        self.save_csv_btn = QPushButton("📊 Save CSV")
        self.batch_export_btn = QPushButton("📦 Batch Export")

        export_layout.addWidget(self.save_txt_btn)
        export_layout.addWidget(self.save_csv_btn)
        export_layout.addWidget(self.batch_export_btn)
        export_layout.addStretch()

        addresses_layout.addLayout(export_layout)

        self.results_tabs.addTab(self.addresses_tab, "📍 Addresses")

        layout.addWidget(self.results_tabs)

        return panel

    def setup_connections(self):
        """Setup signal/slot connections."""
        # Button connections
        self.paste_btn.clicked.connect(self.paste_xpub)
        self.load_file_btn.clicked.connect(self.load_xpub_file)
        self.clear_xpub_btn.clicked.connect(self.clear_xpub)

        self.path_combo.currentTextChanged.connect(self.on_path_changed)
        self.dist_mode.currentTextChanged.connect(self.on_distribution_mode_changed)

        self.preview_btn.clicked.connect(self.preview_distribution)
        self.generate_btn.clicked.connect(self.generate_addresses)

        self.save_txt_btn.clicked.connect(self.save_txt)
        self.save_csv_btn.clicked.connect(self.save_csv)
        self.batch_export_btn.clicked.connect(self.batch_export)

        # Auto-update random bounds when amount changes
        self.bsv_amount.valueChanged.connect(self.update_random_bounds)
        self.address_count.valueChanged.connect(self.update_random_bounds)

    def load_example_xpub(self):
        """Load example xpub if available."""
        example_file = Path("example_xpub.txt")
        if example_file.exists():
            try:
                with open(example_file, "r") as f:
                    xpub = f.read().strip()
                    self.xpub_input.setPlainText(xpub)
            except Exception:
                pass  # Silently ignore if can't load example

    def paste_xpub(self):
        """Paste XPUB from clipboard."""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.xpub_input.setPlainText(text)

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
                        self.xpub_input.setPlainText(lines[0])
                    else:
                        QMessageBox.warning(
                            self, "Error", "No valid content found in file."
                        )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def clear_xpub(self):
        """Clear XPUB input."""
        self.xpub_input.clear()

    def on_path_changed(self):
        """Handle derivation path selection change."""
        show_custom = self.path_combo.currentText() == "Custom path"
        self.custom_path_input.setVisible(show_custom)

    def on_distribution_mode_changed(self):
        """Handle distribution mode change."""
        mode = self.dist_mode.currentText()
        show_params = (
            "Random distribution" in mode and mode != "Smart random distribution"
        )
        self.random_params_widget.setVisible(show_params)

        if not show_params:
            self.update_random_bounds()

    def update_random_bounds(self):
        """Update random distribution bounds based on total amount and address count."""
        if self.dist_mode.currentText() == "Random distribution":
            total = Decimal(str(self.bsv_amount.value()))
            count = self.address_count.value()

            if count > 0:
                avg = total / count
                # Set reasonable defaults
                min_val = float(avg * Decimal("0.1"))  # 10% of average
                max_val = float(avg * Decimal("2.0"))  # 200% of average

                # Ensure minimum is above dust limit
                dust_limit_bsv = 0.00000546  # 546 satoshis in BSV
                min_val = max(min_val, dust_limit_bsv)

                self.min_amount.setValue(min_val)
                self.max_amount.setValue(max_val)

    def get_derivation_path(self):
        """Get the selected derivation path."""
        path_text = self.path_combo.currentText()
        if "receiving" in path_text:
            return "0"
        elif "change" in path_text:
            return "1"
        else:  # Custom path
            return self.custom_path_input.text().strip()

    def validate_inputs(self):
        """Validate all input fields."""
        # Check XPUB
        xpub = self.xpub_input.toPlainText().strip()
        if not xpub:
            QMessageBox.warning(
                self, "Validation Error", "Please enter an extended public key."
            )
            return False

        if not xpub.startswith(("xpub", "tpub")):
            reply = QMessageBox.question(
                self,
                "Warning",
                "This doesn't look like a standard extended public key. Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return False

        # Check custom path if selected
        if self.path_combo.currentText() == "Custom path":
            custom_path = self.custom_path_input.text().strip()
            if not custom_path:
                QMessageBox.warning(
                    self, "Validation Error", "Please enter a custom derivation path."
                )
                return False

        # Check random distribution bounds
        if self.dist_mode.currentText() == "Random distribution":
            min_val = self.min_amount.value()
            max_val = self.max_amount.value()

            if min_val >= max_val:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Minimum amount must be less than maximum amount.",
                )
                return False

        return True

    def preview_distribution(self):
        """Preview the distribution without generating addresses."""
        if not self.validate_inputs():
            return

        total_amount = Decimal(str(self.bsv_amount.value()))
        count = self.address_count.value()
        mode = self.dist_mode.currentText()

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
                min_amt = Decimal(str(self.min_amount.value()))
                max_amt = Decimal(str(self.max_amount.value()))
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

            self.preview_text.setPlainText(preview_text)
            self.results_tabs.setCurrentIndex(0)  # Switch to preview tab

        except Exception as e:
            QMessageBox.critical(
                self, "Preview Error", f"Failed to create preview: {str(e)}"
            )

    def generate_addresses(self):
        """Generate addresses using worker thread."""
        if not self.validate_inputs():
            return

        # Disable generate button and show progress
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage("Generating addresses...")

        # Get parameters
        xpub = self.xpub_input.toPlainText().strip()
        count = self.address_count.value()
        base_path = self.get_derivation_path()

        # Determine starting index
        start_index = 0

        # Check if user manually set a starting index
        manual_index = self.manual_start_index.value()
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
                    f"Found previous derivation state (last index: {state_info['last_index']}).\nContinue from where you left off?",
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
        total_amount = Decimal(str(self.bsv_amount.value()))
        mode = self.dist_mode.currentText()

        try:
            if mode == "Equal distribution":
                self.amounts = distribute_amounts_equal(total_amount, len(addresses))

            elif mode == "Random distribution":
                min_amt = Decimal(str(self.min_amount.value()))
                max_amt = Decimal(str(self.max_amount.value()))
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
            self.results_tabs.setCurrentIndex(1)

            self.statusBar().showMessage(
                f"Successfully generated {len(addresses)} addresses"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Distribution Error", f"Failed to distribute amounts: {str(e)}"
            )

        finally:
            # Re-enable UI
            self.generate_btn.setEnabled(True)
            self.progress_bar.setVisible(False)

    def on_generation_error(self, error_message):
        """Handle generation error."""
        QMessageBox.critical(
            self, "Generation Error", f"Failed to generate addresses: {error_message}"
        )

        # Re-enable UI
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Address generation failed")

    def update_addresses_table(self):
        """Update the addresses table with generated data."""
        if not self.addresses or not self.amounts:
            return

        self.addresses_table.setRowCount(len(self.addresses))

        for i, (addr_info, amount) in enumerate(zip(self.addresses, self.amounts)):
            self.addresses_table.setItem(
                i, 0, QTableWidgetItem(str(addr_info["index"]))
            )
            self.addresses_table.setItem(i, 1, QTableWidgetItem(addr_info["address"]))
            self.addresses_table.setItem(i, 2, QTableWidgetItem(f"{amount:.8f}"))

        # Resize columns to content
        self.addresses_table.resizeColumnsToContents()

    def save_txt(self):
        """Save addresses to TXT file."""
        if not self.addresses:
            QMessageBox.warning(self, "No Data", "Please generate addresses first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Addresses (TXT)", "addresses.txt", "Text files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, "w") as f:
                    for addr_info in self.addresses:
                        f.write(f"{addr_info['address']}\n")

                QMessageBox.information(
                    self, "Success", f"Addresses saved to {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Save Error", f"Failed to save file: {str(e)}"
                )

    def save_csv(self):
        """Save addresses with amounts to CSV file."""
        if not self.addresses or not self.amounts:
            QMessageBox.warning(
                self, "No Data", "Please generate addresses with distribution first."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Addresses & Amounts (CSV)",
            "addresses_amounts.csv",
            "CSV files (*.csv)",
        )

        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write("address,amount\n")
                    for addr_info, amount in zip(self.addresses, self.amounts):
                        f.write(f"{addr_info['address']},{amount:.8f}\n")

                QMessageBox.information(
                    self, "Success", f"Addresses and amounts saved to {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Save Error", f"Failed to save file: {str(e)}"
                )

    def batch_export(self):
        """Export addresses in batches."""
        if not self.addresses or not self.amounts:
            QMessageBox.warning(
                self, "No Data", "Please generate addresses with distribution first."
            )
            return

        # Simple batch export dialog (can be enhanced later)
        max_bsv_per_batch, ok = QInputDialog.getDouble(
            self,
            "Batch Export",
            "Maximum BSV per batch file:",
            value=10.0,
            min=0.1,
            max=100000.0,
            decimals=8,
        )

        if not ok:
            return

        try:
            batches = create_address_batches(
                self.addresses,
                self.amounts,
                Decimal(str(max_bsv_per_batch)),
                randomize=True,  # Default to randomized for privacy
            )

            if not batches:
                QMessageBox.warning(self, "Batch Error", "Failed to create batches.")
                return

            # Choose directory to save batches
            dir_path = QFileDialog.getExistingDirectory(
                self, "Choose Directory for Batch Files"
            )
            if not dir_path:
                return

            # Save batch files
            for i, batch in enumerate(batches):
                batch_file = os.path.join(dir_path, f"batch_{i + 1:03d}.csv")
                with open(batch_file, "w") as f:
                    f.write("address,amount\n")
                    for addr_info, amount in zip(batch["addresses"], batch["amounts"]):
                        f.write(f"{addr_info['address']},{amount:.8f}\n")

            total_amount = sum(sum(batch["amounts"]) for batch in batches)
            QMessageBox.information(
                self,
                "Batch Export Complete",
                f"Created {len(batches)} batch files in {dir_path}\n"
                f"Total amount distributed: {total_amount:.8f} BSV",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Batch Export Error", f"Failed to create batches: {str(e)}"
            )


def main():
    """Main function to run the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("BSV Address Generator")
    app.setOrganizationName("BSV Tools")

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = BSVAddressGeneratorGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
