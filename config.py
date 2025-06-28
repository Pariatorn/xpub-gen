"""
Configuration constants for BSV Address Generator
Contains all global constants and settings following BSV protocol specifications.
"""

# BSV Protocol Constants
BSV_DUST_LIMIT = 546  # satoshis - BSV dust limit
SATOSHIS_PER_BSV = 100000000  # 1 BSV = 100,000,000 satoshis

# Application Limits
MAX_BSV_AMOUNT = 1000000  # 1 million BSV maximum
MAX_ADDRESSES_WARNING = 1000  # Warning threshold for large address generation
MAX_DERIVATION_INDEX = 2147483647  # BIP32 max non-hardened derivation index (2^31 - 1)

# File Paths
DERIVATION_STATE_FILE = "derivation_state.json"  # File to track derivation state

# Derivation Warnings
DERIVATION_WARNING_THRESHOLD = 0.95  # Warning at 95% of maximum derivation index

# Decimal Precision
SATOSHI_PRECISION = "0.00000001"  # 8 decimal places for satoshi precision

# Version
APP_VERSION = "1.0.0"
