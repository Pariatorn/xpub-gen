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

import os
import sys

try:
    from bsv.hd import Xpub
except ImportError:
    print("Error: BSV SDK not found. Please install it using:")
    print("pip install bsv-sdk")
    sys.exit(1)


def print_banner():
    """Print a nice banner for the tool."""
    banner = """
╔══════════════════════════════════════════╗
║         BSV Address Derivation Tool      ║
║      Using Official BSV SDK for Python   ║
╚══════════════════════════════════════════╝
    """
    print(banner)


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
            elif count > 1000:
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


def derive_addresses(xpub_str, count, base_path):
    """Derive addresses from the extended public key."""
    try:
        # Create Xpub object
        xpub = Xpub(xpub_str)

        addresses = []

        print(f"\nDeriving {count} addresses...")
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
            try:
                # Derive child key at index i
                child_xpub = current_xpub.ckd(i)
                address = child_xpub.address()

                # Construct full derivation path for display
                if base_path:
                    derivation_path = f"m/{base_path}/{i}"
                else:
                    derivation_path = f"m/{i}"

                addresses.append(
                    {"index": i, "path": derivation_path, "address": address}
                )

                print(f"{i:<8} {derivation_path:<19} {address}")

            except Exception as e:
                print(f"{i:<8} Error deriving child {i}: {e}")

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

        # Derive addresses
        addresses = derive_addresses(xpub, count, base_path)

        if addresses:
            print(f"\n✓ Successfully derived {len(addresses)} addresses!")

            # Option to save to file
            save_addresses_option(addresses)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    print("\nThank you for using BSV Address Derivation Tool!")


if __name__ == "__main__":
    main()
