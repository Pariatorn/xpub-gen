"""
State management for BSV address generator.
Handles persistence of derivation state to avoid redundancies.
"""

import json
import os

from config import DERIVATION_STATE_FILE


def get_xpub_fingerprint(xpub_str):
    """
    Generate a simple fingerprint for the xpub to track state.
    
    Args:
        xpub_str (str): Extended public key string
        
    Returns:
        int: Simple hash-based fingerprint
    """
    return hash(xpub_str) % 1000000


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


def get_starting_index(xpub_str, base_path):
    """
    Get the starting index for derivation, considering previous state.
    
    Args:
        xpub_str (str): Extended public key string
        base_path (str): Base derivation path
        
    Returns:
        int: Starting index for derivation
    """
    state = load_derivation_state()
    xpub_fingerprint = get_xpub_fingerprint(xpub_str)
    
    if (
        state
        and state.get("xpub_fingerprint") == xpub_fingerprint
        and state.get("base_path") == base_path
    ):
        last_index = state.get("last_index", 0)
        print("\nFound previous derivation state.")
        print(f"Last derived index was: {last_index}")
        
        choice = (
            input("Do you want to continue from the last index? (y/n): ")
            .strip()
            .lower()
        )
        if choice == "y":
            return last_index + 1
    
    return 0


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