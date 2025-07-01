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
MAX_ADDRESS_COUNT = 10000  # Maximum number of addresses that can be generated at once

# GUI Default Values
DEFAULT_ADDRESS_COUNT = 10  # Default number of addresses to generate
DEFAULT_BSV_AMOUNT = 1.0  # Default BSV amount to distribute
DEFAULT_MIN_RANDOM_AMOUNT = 0.01  # Default minimum amount for random distribution
DEFAULT_MAX_RANDOM_AMOUNT = 0.1  # Default maximum amount for random distribution

# Batch Export Configuration
MIN_BATCH_REASONABLE = (
    0.001  # Minimum reasonable batch size (0.001 BSV ~180x dust limit)
)
DEFAULT_BATCH_SIZE = 10.0  # Default maximum BSV per batch file
MAX_BATCH_SIZE = 100000.0  # Maximum allowable batch size
BATCH_MIN_MULTIPLIER = 10  # Multiplier for minimum distribution amount (10x)

# File Paths
DERIVATION_STATE_FILE = "derivation_state.json"  # File to track derivation state

# Derivation Warnings
DERIVATION_WARNING_THRESHOLD = 0.95  # Warning at 95% of maximum derivation index

# Decimal Precision
SATOSHI_PRECISION = "0.00000001"  # 8 decimal places for satoshi precision

# Version
APP_VERSION = "1.0.0"
