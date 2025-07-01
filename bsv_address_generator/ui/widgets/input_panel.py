from decimal import Decimal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import (
    BSV_DUST_LIMIT,
    DEFAULT_ADDRESS_COUNT,
    DEFAULT_BSV_AMOUNT,
    DEFAULT_MAX_RANDOM_AMOUNT,
    DEFAULT_MIN_RANDOM_AMOUNT,
    MAX_ADDRESS_COUNT,
    MAX_BSV_AMOUNT,
    MAX_DERIVATION_INDEX,
    SATOSHIS_PER_BSV,
)


class InputPanel(QScrollArea):
    """Widget for all user inputs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Calculate dust limit in BSV for minimum values
        self.dust_limit_bsv = Decimal(BSV_DUST_LIMIT) / SATOSHIS_PER_BSV
        # Use dust limit + small buffer for minimum GUI values
        self.min_bsv_amount = float(self.dust_limit_bsv * Decimal("1.1"))

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
        self.address_count.setMaximum(MAX_ADDRESS_COUNT)
        self.address_count.setValue(DEFAULT_ADDRESS_COUNT)

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
        self.manual_start_index.setMaximum(MAX_DERIVATION_INDEX)
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
        self.bsv_amount.setMinimum(self.min_bsv_amount)  # Use dust limit + buffer
        self.bsv_amount.setMaximum(float(MAX_BSV_AMOUNT))
        self.bsv_amount.setDecimals(8)
        self.bsv_amount.setValue(DEFAULT_BSV_AMOUNT)
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
        self.min_amount.setMinimum(self.min_bsv_amount)  # Use dust limit + buffer
        self.min_amount.setMaximum(float(MAX_BSV_AMOUNT))
        self.min_amount.setDecimals(8)
        self.min_amount.setValue(DEFAULT_MIN_RANDOM_AMOUNT)
        random_layout.addWidget(self.min_amount, 0, 1)
        random_layout.addWidget(QLabel("BSV"), 0, 2)

        random_layout.addWidget(QLabel("Max amount:"), 1, 0)
        self.max_amount = QDoubleSpinBox()
        self.max_amount.setMinimum(self.min_bsv_amount)  # Use dust limit + buffer
        self.max_amount.setMaximum(float(MAX_BSV_AMOUNT))
        self.max_amount.setDecimals(8)
        self.max_amount.setValue(DEFAULT_MAX_RANDOM_AMOUNT)
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

        self.setWidget(panel)
