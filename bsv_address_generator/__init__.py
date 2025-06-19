"""
BSV Address Derivation Tool Package
A user-friendly package to derive BSV addresses from extended public keys.
"""

__version__ = "2.1.0"
__author__ = "BSV Address Generator"

from .core.derivation import derive_addresses, validate_derivation_limits
from .core.distribution import (
    distribute_amounts_equal, 
    distribute_amounts_random,
    distribute_amounts_random_optimal,
    calculate_optimal_random_bounds
)
from .ui.input_handlers import (
    get_xpub_input, 
    get_derivation_count, 
    get_derivation_path,
    get_smart_random_confirmation
)
from .ui.output_handlers import save_addresses_to_txt, save_addresses_to_csv
from .utils.state_manager import save_derivation_state, load_derivation_state

__all__ = [
    "derive_addresses",
    "validate_derivation_limits",
    "distribute_amounts_equal", 
    "distribute_amounts_random",
    "distribute_amounts_random_optimal",
    "calculate_optimal_random_bounds",
    "get_xpub_input",
    "get_derivation_count",
    "get_derivation_path",
    "get_smart_random_confirmation",
    "save_addresses_to_txt",
    "save_addresses_to_csv",
    "save_derivation_state",
    "load_derivation_state",
] 