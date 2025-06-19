"""
User input handlers for BSV address generator.
Handles all user input validation and processing.
"""

import os
from decimal import Decimal

from config import (
    BSV_DUST_LIMIT, 
    SATOSHIS_PER_BSV, 
    MAX_BSV_AMOUNT, 
    MAX_ADDRESSES_WARNING
)
from ..utils.state_manager import get_starting_index


def get_xpub_input():
    """Get the extended public key from user input or file."""
    print("\nChoose input method:")
    print("1. Enter xpub directly")
    print("2. Load xpub from file")

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()

        if choice == "1":
            return get_xpub_direct()
        elif choice == "2":
            return get_xpub_from_file()
        else:
            print("Invalid choice. Please enter 1 or 2.")


def get_xpub_direct():
    """Get xpub directly from user input."""
    while True:
        xpub = input("\nEnter your extended public key (xpub): ").strip()

        if not xpub:
            print("Error: xpub cannot be empty.")
            continue

        if not xpub.startswith(("xpub", "tpub")):
            print("Warning: This doesn't look like a standard extended public key.")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm != "y":
                continue

        return xpub


def get_xpub_from_file():
    """Get xpub from a file."""
    while True:
        file_path = input("\nEnter the path to your xpub file: ").strip()

        if not file_path:
            print("Error: File path cannot be empty.")
            continue

        # Expand user path (~)
        file_path = os.path.expanduser(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                print(f"Error: File '{file_path}' is empty.")
                continue

            # Handle multiple lines - take the first non-empty line
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            if lines:
                xpub = lines[0]
                if len(lines) > 1:
                    print(
                        f"Note: File contains multiple lines. Using first line: {xpub[:20]}..."
                    )
                return xpub
            else:
                print(f"Error: No valid content found in '{file_path}'.")
                continue

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            continue
        except PermissionError:
            print(f"Error: Permission denied reading '{file_path}'.")
            continue
        except Exception as e:
            print(f"Error reading file: {e}")
            continue


def get_derivation_count():
    """Get the number of addresses to derive."""
    while True:
        try:
            count = input(
                "\nHow many addresses would you like to derive? (default: 10): "
            ).strip()

            if not count:
                return 10

            count = int(count)

            if count <= 0:
                print("Error: Number must be greater than 0.")
                continue
            elif count > MAX_ADDRESSES_WARNING:
                confirm = (
                    input(
                        f"Warning: Generating {count} addresses. This might take a while. Continue? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if confirm != "y":
                    continue

            return count

        except ValueError:
            print("Error: Please enter a valid number.")


def get_derivation_path():
    """Get the derivation path from user."""
    print("\nDerivation path options:")
    print("1. Standard receiving addresses (m/0/i)")
    print("2. Standard change addresses (m/1/i)")
    print("3. Custom path")

    while True:
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()

        if choice == "1":
            return "0"
        elif choice == "2":
            return "1"
        elif choice == "3":
            custom_path = input(
                "Enter custom derivation path (e.g., '0/0' or '44/0/0'): "
            ).strip()
            if custom_path:
                return custom_path
            print("Error: Custom path cannot be empty.")
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def get_bsv_amount():
    """Get the total BSV amount to distribute across addresses."""
    while True:
        try:
            amount_str = input(
                "\nEnter total BSV amount to distribute (e.g., 1.5): "
            ).strip()

            if not amount_str:
                print("Error: Amount cannot be empty.")
                continue

            amount = Decimal(amount_str)

            if amount <= 0:
                print("Error: Amount must be greater than 0.")
                continue

            # Check maximum BSV limit
            if amount > MAX_BSV_AMOUNT:
                print(f"Error: Amount exceeds maximum limit of {MAX_BSV_AMOUNT:,} BSV.")
                continue

            # Convert to satoshis to check minimum (dust limit)
            satoshis = int(amount * SATOSHIS_PER_BSV)
            if satoshis < BSV_DUST_LIMIT:
                min_bsv = Decimal(BSV_DUST_LIMIT) / SATOSHIS_PER_BSV
                print(
                    f"Error: Amount too small. Minimum is {min_bsv} BSV ({BSV_DUST_LIMIT} satoshis)."
                )
                continue

            return amount

        except (ValueError, ArithmeticError):
            print("Error: Please enter a valid number.")


def get_distribution_mode():
    """Get the distribution mode for amounts."""
    print("\nAmount distribution options:")
    print("1. Equal distribution (split amount equally)")
    print("2. Random distribution (specify min/max range)")
    print("3. 🤖 Smart random distribution (automatic optimal bounds)")
    
    while True:
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            return "equal"
        elif choice == "2":
            return "random"
        elif choice == "3":
            return "smart_random"
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def display_optimal_bounds_preview(total_amount, address_count):
    """
    Display preview of optimal bounds calculation.
    
    Args:
        total_amount (Decimal): Total BSV amount
        address_count (int): Number of addresses
        
    Returns:
        tuple: (min_amount, max_amount, distribution_info)
    """
    from ..core.distribution import calculate_optimal_random_bounds
    
    min_amount, max_amount, distribution_info = calculate_optimal_random_bounds(
        total_amount, address_count
    )
    
    print("\n🤖 Smart Random Distribution Analysis:")
    print("=" * 50)
    print(f"Average amount per address: {distribution_info['average_amount']} BSV")
    print(f"Optimal range: {min_amount} - {max_amount} BSV")
    print(f"Variation range: {distribution_info['variation_range']} BSV")
    print(f"Variation: {distribution_info['variation_percent']:.1f}% of average")
    print(f"Min bound: {distribution_info['min_percent_of_avg']:.1f}% of average")
    print(f"Max bound: {distribution_info['max_percent_of_avg']:.1f}% of average")
    print("=" * 50)
    
    return min_amount, max_amount, distribution_info


def get_random_distribution_params(total_amount, address_count):
    """Get parameters for random distribution."""
    print(
        f"\nRandom distribution for {total_amount} BSV across {address_count} addresses"
    )
    
    # Minimum amount (must be > BSV_DUST_LIMIT)
    min_dust_bsv = Decimal(BSV_DUST_LIMIT) / SATOSHIS_PER_BSV
    
    while True:
        try:
            min_str = input(
                f"Enter minimum amount per address (min: {min_dust_bsv} BSV): "
            ).strip()
            min_amount = Decimal(min_str)
            
            min_sats = int(min_amount * SATOSHIS_PER_BSV)
            if min_sats <= BSV_DUST_LIMIT:
                print(
                    f"Error: Minimum amount must be greater than {min_dust_bsv} BSV ({BSV_DUST_LIMIT} satoshis)."
                )
                continue
                
            break
        except (ValueError, ArithmeticError):
            print("Error: Please enter a valid number.")
    
    # Maximum amount (must be < total_amount)
    while True:
        try:
            max_str = input("Enter maximum amount per address (e.g., 0.1): ").strip()
            max_amount = Decimal(max_str)
            
            if max_amount >= total_amount:
                print(
                    f"Error: Maximum amount must be less than total amount ({total_amount} BSV)."
                )
                continue
            
            if max_amount <= min_amount:
                print(
                    f"Error: Maximum amount must be greater than minimum amount ({min_amount} BSV)."
                )
                continue
                
            # Check if it's possible to distribute with these constraints
            min_total = min_amount * address_count
            if min_total > total_amount:
                print(
                    f"Error: Minimum total ({min_total} BSV) exceeds available amount ({total_amount} BSV)."
                )
                continue
                
            break
        except (ValueError, ArithmeticError):
            print("Error: Please enter a valid number.")
    
    return min_amount, max_amount


def get_smart_random_confirmation(total_amount, address_count):
    """
    Get confirmation for smart random distribution and show preview.
    
    Args:
        total_amount (Decimal): Total BSV amount
        address_count (int): Number of addresses
        
    Returns:
        tuple: (confirmed, min_amount, max_amount, distribution_info) or (False, None, None, None)
    """
    min_amount, max_amount, distribution_info = display_optimal_bounds_preview(
        total_amount, address_count
    )
    
    print("\nThis smart distribution will:")
    print("✅ Ensure truly random amounts across all addresses")
    print("✅ Prevent excessive remainder in the last address")  
    print("✅ Maintain reasonable variation while respecting constraints")
    print("✅ Automatically handle dust limit compliance")
    
    confirmed = get_user_confirmation("Use these optimal bounds for random distribution?")
    
    if confirmed:
        return True, min_amount, max_amount, distribution_info
    else:
        return False, None, None, None


def get_user_confirmation(message):
    """Get yes/no confirmation from user."""
    choice = input(f"{message} (y/n): ").strip().lower()
    return choice == "y" 