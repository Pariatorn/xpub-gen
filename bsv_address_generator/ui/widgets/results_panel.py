from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ResultsPanel(QWidget):
    """Widget for displaying results and export options."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

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
