"""
State management for BSV address generator.
Handles persistence of derivation state to avoid redundancies.
"""

import hashlib
import json
import os

from config import DERIVATION_STATE_FILE


def get_xpub_fingerprint(xpub_str):
    """
    Generate a stable fingerprint for the xpub to track state.
    
    Uses SHA-256 hash for consistent results across Python sessions,
    unlike the built-in hash() function which is randomized for security.
    
    Args:
        xpub_str (str): Extended public key string
        
    Returns:
        int: Stable hash-based fingerprint (6 digits)
    """
    # Create SHA-256 hash of the xpub string
    sha256_hash = hashlib.sha256(xpub_str.encode('utf-8')).hexdigest()
    
    # Convert hex to integer and reduce modulo 1000000 for 6-digit fingerprint
    fingerprint = int(sha256_hash, 16) % 1000000
    
    return fingerprint


def save_derivation_state(xpub_fingerprint, last_index, base_path):
    """
    Save the last derivation state to avoid redundancies.
    
    Args:
        xpub_fingerprint (int): Fingerprint of the xpub
        last_index (int): Last derived index
        base_path (str): Base derivation path
    """
    state = {
        "xpub_fingerprint": xpub_fingerprint,
        "last_index": last_index,
        "base_path": base_path,
    }
    try:
        with open(DERIVATION_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Warning: Could not save derivation state: {e}")


def load_derivation_state():
    """
    Load the last derivation state.
    
    Returns:
        dict: Derivation state or None if not found/error
    """
    try:
        if os.path.exists(DERIVATION_STATE_FILE):
            with open(DERIVATION_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load derivation state: {e}")
    return None


def check_previous_state(xpub_str, base_path):
    """
    Check if there's a previous derivation state for the given xpub and path.
    
    This function only checks for state existence without user interaction,
    maintaining separation of concerns.
    
    Args:
        xpub_str (str): Extended public key string
        base_path (str): Base derivation path
        
    Returns:
        dict: Dictionary with state information or None if no matching state
        Format: {
            'exists': bool,
            'last_index': int,
            'fingerprint': int,
            'can_continue': bool
        }
    """
    state = load_derivation_state()
    xpub_fingerprint = get_xpub_fingerprint(xpub_str)
    
    if (
        state
        and state.get("xpub_fingerprint") == xpub_fingerprint
        and state.get("base_path") == base_path
    ):
        return {
            'exists': True,
            'last_index': state.get("last_index", 0),
            'fingerprint': xpub_fingerprint,
            'can_continue': True
        }
    
    return {
        'exists': False,
        'last_index': 0,
        'fingerprint': xpub_fingerprint,
        'can_continue': False
    }


def clear_derivation_state():
    """Clear the derivation state file."""
    try:
        if os.path.exists(DERIVATION_STATE_FILE):
            os.remove(DERIVATION_STATE_FILE)
            print("✓ Derivation state cleared.")
    except Exception as e:
        print(f"Warning: Could not clear derivation state: {e}")


def get_state_info():
    """
    Get information about current derivation state.
    
    Returns:
        dict: State information or None
    """
    state = load_derivation_state()
    if state:
        return {
            "last_index": state.get("last_index", 0),
            "base_path": state.get("base_path", ""),
            "xpub_fingerprint": state.get("xpub_fingerprint", 0)
        }
    return None 