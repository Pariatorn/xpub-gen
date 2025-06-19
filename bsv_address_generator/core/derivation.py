"""
Core derivation logic for BSV address generation.
Handles address derivation, validation, and BIP32 operations.
"""

try:
    from bsv.hd import Xpub
except ImportError:
    raise ImportError("BSV SDK not found. Please install it using: pip install bsv-sdk")

from config import MAX_DERIVATION_INDEX, DERIVATION_WARNING_THRESHOLD
from ..utils.state_manager import save_derivation_state, get_xpub_fingerprint


def validate_derivation_limits(start_index, count):
    """
    Validate that derivation won't exceed BIP32 limits.
    
    Args:
        start_index (int): Starting derivation index
        count (int): Number of addresses to derive
        
    Returns:
        bool: True if within limits, False otherwise
    """
    end_index = start_index + count - 1
    
    if end_index > MAX_DERIVATION_INDEX:
        print("Error: Derivation limit exceeded!")
        print(f"Maximum derivation index: {MAX_DERIVATION_INDEX:,}")
        print(f"Requested end index: {end_index:,}")
        print(
            f"You can derive {MAX_DERIVATION_INDEX - start_index + 1:,} more addresses from index {start_index}"
        )
        return False
    
    if end_index > MAX_DERIVATION_INDEX * DERIVATION_WARNING_THRESHOLD:
        print("Warning: Approaching derivation limit!")
        print(f"End index will be: {end_index:,}")
        print(f"Maximum possible index: {MAX_DERIVATION_INDEX:,}")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != "y":
            return False
    
    return True


def derive_addresses(xpub_str, count, base_path, start_index=0):
    """
    Derive addresses from the extended public key.
    
    Args:
        xpub_str (str): Extended public key string
        count (int): Number of addresses to derive
        base_path (str): Base derivation path
        start_index (int): Starting index for derivation
        
    Returns:
        list: List of address dictionaries or None on error
    """
    try:
        # Validate derivation limits before proceeding
        if not validate_derivation_limits(start_index, count):
            return None
            
        # Create Xpub object
        xpub = Xpub(xpub_str)
        addresses = []

        print(f"\nDeriving {count} addresses starting from index {start_index}...")
        print("=" * 80)
        print(f"{'Index':<8} {'Derivation Path':<20} {'Address'}")
        print("=" * 80)

        # First derive the base path if it has multiple levels
        path_parts = base_path.split("/")
        current_xpub = xpub

        # Derive through each part of the base path
        for part in path_parts:
            if part.strip():  # Skip empty parts
                try:
                    index = int(part)
                    current_xpub = current_xpub.ckd(index)
                except ValueError:
                    print(f"Error: Invalid path component '{part}'. Must be a number.")
                    return None

        # Derive addresses
        for i in range(count):
            actual_index = start_index + i
            try:
                # Derive child key at actual index
                child_xpub = current_xpub.ckd(actual_index)
                address = child_xpub.address()

                # Construct full derivation path for display
                if base_path:
                    derivation_path = f"m/{base_path}/{actual_index}"
                else:
                    derivation_path = f"m/{actual_index}"

                addresses.append(
                    {"index": actual_index, "path": derivation_path, "address": address}
                )

                print(f"{actual_index:<8} {derivation_path:<19} {address}")

            except Exception as e:
                print(f"{actual_index:<8} Error deriving child {actual_index}: {e}")

        # Save derivation state
        if addresses:
            last_index = addresses[-1]["index"]
            xpub_fingerprint = get_xpub_fingerprint(xpub_str)
            save_derivation_state(xpub_fingerprint, last_index, base_path)

        return addresses

    except Exception as e:
        print(f"\nError processing extended public key: {e}")
        print("Please check that your xpub is valid and properly formatted.")
        return None 