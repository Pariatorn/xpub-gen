#!/usr/bin/env python3
"""
BSV Address Derivation Tool
A user-friendly script to derive BSV addresses from an extended public key (xpub)
using the official BSV SDK for Python.

Requirements:
    pip install bsv-sdk

Usage:
    python bsv_address_generator.py
"""

import json
import os
import random
import sys
from decimal import ROUND_DOWN, Decimal

try:
    from bsv.hd import Xpub
except ImportError:
    print("Error: BSV SDK not found. Please install it using:")
    print("pip install bsv-sdk")
    sys.exit(1)

# Global constants following BSV protocol and best practices
BSV_DUST_LIMIT = 546  # satoshis - BSV dust limit
SATOSHIS_PER_BSV = 100000000  # 1 BSV = 100,000,000 satoshis
MAX_BSV_AMOUNT = 1000000  # 1 million BSV maximum
MAX_ADDRESSES_WARNING = 1000  # Warning threshold for large address generation
MAX_DERIVATION_INDEX = 2147483647  # BIP32 max non-hardened derivation index (2^31 - 1)
DERIVATION_STATE_FILE = "derivation_state.json"  # File to track derivation state


def print_banner():
    """Print a nice banner for the tool."""
    banner = """
╔══════════════════════════════════════════╗
║         BSV Address Derivation Tool      ║
║      Using Official BSV SDK for Python   ║
╚══════════════════════════════════════════╝
    """
    print(banner)


def save_derivation_state(xpub_fingerprint, last_index, base_path):
    """Save the last derivation state to avoid redundancies."""
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
    """Load the last derivation state."""
    try:
        if os.path.exists(DERIVATION_STATE_FILE):
            with open(DERIVATION_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load derivation state: {e}")
    return None


def get_xpub_fingerprint(xpub_str):
    """Generate a simple fingerprint for the xpub to track state."""
    return hash(xpub_str) % 1000000


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


def get_starting_index(xpub_str, base_path):
    """Get the starting index for derivation, considering previous state."""
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


def validate_derivation_limits(start_index, count):
    """Validate that derivation won't exceed BIP32 limits."""
    end_index = start_index + count - 1

    if end_index > MAX_DERIVATION_INDEX:
        print("Error: Derivation limit exceeded!")
        print(f"Maximum derivation index: {MAX_DERIVATION_INDEX:,}")
        print(f"Requested end index: {end_index:,}")
        print(
            f"You can derive {MAX_DERIVATION_INDEX - start_index + 1:,} more addresses from index {start_index}"
        )
        return False

    if end_index > MAX_DERIVATION_INDEX * 0.9:  # Warning at 90% of limit
        print("Warning: Approaching derivation limit!")
        print(f"End index will be: {end_index:,}")
        print(f"Maximum possible index: {MAX_DERIVATION_INDEX:,}")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != "y":
            return False

    return True


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

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()

        if choice == "1":
            return "equal"
        elif choice == "2":
            return "random"
        else:
            print("Invalid choice. Please enter 1 or 2.")


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


def distribute_amounts_equal(total_amount, address_count):
    """Distribute amount equally across addresses."""
    amount_per_address = total_amount / address_count
    # Round down to 8 decimal places (satoshi precision)
    amount_per_address = amount_per_address.quantize(
        Decimal("0.00000001"), rounding=ROUND_DOWN
    )

    amounts = [amount_per_address] * address_count

    # Handle any remaining dust by adding to the first address
    distributed_total = sum(amounts)
    remainder = total_amount - distributed_total
    if remainder > 0:
        amounts[0] += remainder

    return amounts


def distribute_amounts_random(total_amount, address_count, min_amount, max_amount):
    """Distribute amount randomly within specified range."""
    amounts = []
    remaining = total_amount

    for i in range(address_count - 1):
        # Calculate maximum possible for this address (leaving enough for remaining addresses)
        remaining_addresses = address_count - i - 1
        max_for_remaining = remaining - (min_amount * remaining_addresses)

        # Actual maximum for this address
        actual_max = min(max_amount, max_for_remaining)
        actual_min = min_amount

        if actual_max <= actual_min:
            amount = actual_min
        else:
            # Generate random amount within range
            random_factor = Decimal(str(random.random()))
            amount = actual_min + (actual_max - actual_min) * random_factor
            # Round to satoshi precision
            amount = amount.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)

        amounts.append(amount)
        remaining -= amount

    # Last address gets the remainder
    amounts.append(remaining)

    # Verify total matches (should be exact due to decimal arithmetic)
    if sum(amounts) != total_amount:
        # Adjust the last amount if there's a tiny discrepancy
        amounts[-1] = total_amount - sum(amounts[:-1])

    return amounts


def derive_addresses(xpub_str, count, base_path, start_index=0):
    """Derive addresses from the extended public key."""
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

        # First derive the base path if it has multiple levels (e.g., "0/0" or "44/0/0")
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


def save_addresses_option(addresses):
    """Ask user if they want to save addresses to a file."""
    if not addresses:
        return

    save = (
        input(
            f"\nWould you like to save these {len(addresses)} addresses to a file? (y/n): "
        )
        .strip()
        .lower()
    )

    if save == "y":
        # Default filename with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"bsv_addresses_{timestamp}.txt"

        filename = input(f"Enter filename (default: {default_filename}): ").strip()
        if not filename:
            filename = default_filename

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("BSV Addresses Derived from Extended Public Key\n")
                f.write("=" * 50 + "\n")
                f.write(
                    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"Total addresses: {len(addresses)}\n\n")

                for addr in addresses:
                    f.write(f"Index: {addr['index']}\n")
                    f.write(f"Path: {addr['path']}\n")
                    f.write(f"Address: {addr['address']}\n")
                    f.write("-" * 30 + "\n")

            print(f"✓ Addresses saved to: {filename}")

        except Exception as e:
            print(f"Error saving file: {e}")


def save_addresses_csv(addresses, amounts):
    """Save addresses with amounts to CSV format compatible with Electrum SV."""
    if not addresses:
        return

    save = (
        input(
            f"\nWould you like to save these {len(addresses)} addresses with amounts to CSV (Electrum SV format)? (y/n): "
        )
        .strip()
        .lower()
    )

    if save == "y":
        # Default filename with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"bsv_addresses_amounts_{timestamp}.csv"

        filename = input(f"Enter CSV filename (default: {default_filename}): ").strip()
        if not filename:
            filename = default_filename

        try:
            with open(filename, "w", encoding="utf-8") as f:
                # Write header comment (Electrum SV will ignore it)
                f.write("# BSV Addresses with Amounts - Electrum SV Compatible\n")
                f.write(
                    f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"# Total addresses: {len(addresses)}\n")
                f.write(f"# Total amount: {sum(amounts)} BSV\n")

                # Write address,amount pairs
                for addr, amount in zip(addresses, amounts):
                    f.write(f"{addr['address']},{amount}\n")

            print(f"✓ CSV saved to: {filename}")
            print(f"✓ Total amount distributed: {sum(amounts)} BSV")

        except Exception as e:
            print(f"Error saving CSV file: {e}")


def main():
    """Main function to run the address derivation tool."""
    print_banner()

    try:
        # Get extended public key
        xpub = get_xpub_input()

        # Get number of addresses to derive
        count = get_derivation_count()

        # Get derivation path
        base_path = get_derivation_path()

        # Get starting index (considering previous derivations)
        start_index = get_starting_index(xpub, base_path)

        # Derive addresses
        addresses = derive_addresses(xpub, count, base_path, start_index)

        if addresses:
            print(f"\n✓ Successfully derived {len(addresses)} addresses!")

            # Option to save to txt file
            save_addresses_option(addresses)

            # Option to save to CSV with amounts
            csv_choice = (
                input(
                    "\nWould you like to create a CSV with amounts for Electrum SV? (y/n): "
                )
                .strip()
                .lower()
            )

            if csv_choice == "y":
                # Get total BSV amount
                total_amount = get_bsv_amount()

                # Get distribution mode
                distribution_mode = get_distribution_mode()

                # Generate amounts based on distribution mode
                if distribution_mode == "equal":
                    amounts = distribute_amounts_equal(total_amount, len(addresses))
                    print(f"\n✓ Equal distribution: {amounts[0]} BSV per address")
                else:  # random
                    min_amount, max_amount = get_random_distribution_params(
                        total_amount, len(addresses)
                    )
                    amounts = distribute_amounts_random(
                        total_amount, len(addresses), min_amount, max_amount
                    )
                    print(
                        f"\n✓ Random distribution between {min_amount} - {max_amount} BSV per address"
                    )

                # Display amounts summary
                print("\nAmount distribution summary:")
                print(f"Total amount: {total_amount} BSV")
                print(f"Distributed amount: {sum(amounts)} BSV")
                print(f"Min amount: {min(amounts)} BSV")
                print(f"Max amount: {max(amounts)} BSV")
                print(f"Average amount: {sum(amounts) / len(amounts)} BSV")

                # Save to CSV
                save_addresses_csv(addresses, amounts)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    print("\nThank you for using BSV Address Derivation Tool!")


if __name__ == "__main__":
    main()
