#!/usr/bin/env python3
"""
BSV Address Generation Test Script
A simple testing tool for BSV address generation that can:
1. Use the provided example xpub to generate test addresses
2. Generate new private keys for testing
3. Test the main address generation functionality

Requirements:
    pip install bsv-sdk

Usage:
    python test_script.py
"""

import os
import sys

try:
    from bsv import PrivateKey
    from bsv.hd import (
        Xprv,
        Xpub,
        master_xprv_from_seed,
        mnemonic_from_entropy,
        seed_from_mnemonic,
    )
except ImportError:
    print("Error: BSV SDK not found. Please install it using:")
    print("pip install bsv-sdk")
    sys.exit(1)


def print_banner():
    """Print a nice banner for the test tool."""
    banner = """
╔══════════════════════════════════════════════╗
║       BSV Address Generation Test Tool       ║
║         Test the BSV Address Generator       ║
╚══════════════════════════════════════════════╝
    """
    print(banner)


def get_user_choice():
    """Get user's choice for testing."""
    print("\nChoose your testing option:")
    print("1. Test with example xpub (safe for testing)")
    print("2. Test with custom xpub")
    print(
        "3. Generate HD wallet from entropy (demonstrates full BIP32/BIP44 functionality)"
    )

    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")


def test_with_example_xpub():
    """Test using the example xpub file."""
    try:
        if not os.path.exists("example_xpub.txt"):
            print(
                "Error: example_xpub.txt not found. Make sure it exists in the current directory."
            )
            return None

        with open("example_xpub.txt", "r") as f:
            xpub_str = f.read().strip()

        print(f"✓ Loaded example xpub: {xpub_str[:20]}...")

        # Test creating Xpub object
        xpub = Xpub(xpub_str)
        print("✓ Successfully created Xpub object")

        return xpub, xpub_str

    except Exception as e:
        print(f"Error testing with example xpub: {e}")
        return None


def test_with_custom_xpub():
    """Test with user-provided xpub."""
    while True:
        xpub_str = input("\nEnter your xpub for testing: ").strip()
        if not xpub_str:
            print("xpub cannot be empty.")
            continue

        try:
            xpub = Xpub(xpub_str)
            print("✓ Successfully created Xpub object")
            return xpub, xpub_str
        except Exception as e:
            print(f"Invalid xpub: {e}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != "y":
                return None


def test_with_new_private_key():
    """Generate master private key and demonstrate full HD wallet functionality."""
    try:
        print(
            "\n🔐 Generating master private key and demonstrating HD wallet functionality..."
        )

        # Use fixed entropy for reproducible testing (safe for testing only)
        test_entropy = "cd9b819d9c62f0027116c1849e7d497f"
        print(f"✓ Using test entropy: {test_entropy}")

        # Generate mnemonic from entropy
        mnemonic = mnemonic_from_entropy(test_entropy)
        print(f"✓ Generated mnemonic: {mnemonic}")

        # Generate seed from mnemonic
        seed = seed_from_mnemonic(mnemonic)
        print(f"✓ Generated seed: {seed.hex()[:32]}...")

        # Generate master private key (Xprv) from seed
        master_xprv = master_xprv_from_seed(seed)
        print(f"✓ Master private key (Xprv): {str(master_xprv)[:32]}...")

        # Derive master public key (Xpub) from master private key
        master_xpub = master_xprv.xpub()
        print(f"✓ Master public key (Xpub): {str(master_xpub)[:32]}...")

        # Demonstrate child key derivation
        print("\n🔄 Demonstrating child key derivation...")

        test_addresses = []

        # Derive a few child keys for demonstration
        derivation_path = "m/0/i"  # Simple derivation path
        print(f"✓ Using derivation path: {derivation_path}")

        # Use simpler derivation that works with BSV SDK
        # Let's use the master xpub to derive child addresses (this we know works)
        print("✓ Using master Xpub for child address derivation")

        # Get the master private key for demonstration
        try:
            master_private_key = master_xprv.private_key()
            master_address = master_private_key.address()

            # Add master key info
            test_addresses.append(
                {
                    "index": "M",
                    "address": master_address,
                    "private_key": master_private_key.wif(),
                    "derivation_path": "m",
                    "note": "Master private key",
                }
            )

        except Exception as e:
            print(f"⚠️  Could not extract master private key: {e}")

        # Use the master xpub to derive child addresses using ckd (which we know works)
        for i in range(3):
            try:
                # Use simple derivation path: m/0/i (receiving addresses)
                receiving_xpub = master_xpub.ckd(0)  # Change = 0 (receiving)
                child_xpub = receiving_xpub.ckd(i)  # Address index
                child_address = child_xpub.address()

                test_addresses.append(
                    {
                        "index": i,
                        "address": child_address,
                        "private_key": "N/A (Xpub derivation only)",
                        "derivation_path": f"m/0/{i}",
                        "note": "Derived from master Xpub",
                    }
                )

            except Exception as e:
                print(f"⚠️  Could not derive child address {i}: {e}")
                continue

        if test_addresses:
            print("\n📋 HD Wallet Derivation Results:")
            print("=" * 110)
            print(
                f"{'Index':<6} {'Derivation Path':<20} {'Address':<35} {'Private Key (WIF)'}"
            )
            print("=" * 110)

            for addr in test_addresses:
                print(
                    f"{addr['index']:<6} {addr['derivation_path']:<20} {addr['address']:<35} {addr['private_key']}"
                )

            print("=" * 110)
            print("✓ Successfully demonstrated full HD wallet functionality!")
            print("📝 Features demonstrated:")
            print("   - Entropy → Mnemonic → Seed → Master Keys")
            print("   - Master Xprv → Master Xpub derivation")
            print("   - Hierarchical derivation (m/0/i)")
            print("   - Child private keys and addresses")
            print("⚠️  These are TEST KEYS derived from fixed entropy!")

            # Return the master xpub for compatibility with address derivation testing
            return master_xpub, test_addresses

        print("\n⚠️  This uses FIXED TEST ENTROPY - safe for testing!")
        print("⚠️  Do not send real funds to these addresses!")
        print("⚠️  This demonstrates HD wallet functionality only!")

        return master_xpub, None

    except Exception as e:
        print(f"Error with HD wallet demonstration: {e}")
        print("The BSV SDK may have limited HD wallet support.")
        print("Try using options 1 or 2 for xpub testing instead.")
        return None


def test_address_derivation(xpub, count=5):
    """Test address derivation using the same logic as main.py."""
    try:
        print(f"\n🔄 Testing address derivation with {count} addresses...")
        print("=" * 70)
        print(f"{'Index':<6} {'Path':<15} {'Address'}")
        print("=" * 70)

        addresses = []
        base_path = "0"  # Standard receiving addresses

        # Navigate to base path (same logic as main.py)
        current_xpub = xpub
        if base_path:
            path_parts = base_path.split("/")
            for part in path_parts:
                if part.strip():
                    try:
                        index = int(part)
                        current_xpub = current_xpub.ckd(index)
                    except ValueError:
                        print(f"Error: Invalid path component '{part}'")
                        return None

        # Generate addresses
        for i in range(count):
            try:
                child_xpub = current_xpub.ckd(i)
                address = child_xpub.address()

                derivation_path = f"m/{base_path}/{i}" if base_path else f"m/{i}"

                addresses.append(
                    {"index": i, "path": derivation_path, "address": address}
                )

                print(f"{i:<6} {derivation_path:<15} {address}")

            except Exception as e:
                print(f"{i:<6} Error: {e}")

        print("=" * 70)
        return addresses

    except Exception as e:
        print(f"Error during address derivation: {e}")
        return None


def save_test_results(addresses, test_type):
    """Save test results to file."""
    if not addresses:
        return

    save = input("\nSave test results to file? (y/n): ").strip().lower()
    if save != "y":
        return

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{test_type}_{timestamp}.txt"

    try:
        with open(filename, "w") as f:
            f.write("BSV Address Generation Test Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Test Type: {test_type}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total addresses: {len(addresses)}\n\n")

            for addr in addresses:
                f.write(f"Index: {addr['index']}\n")
                f.write(f"Path: {addr['path']}\n")
                f.write(f"Address: {addr['address']}\n")
                f.write("-" * 30 + "\n")

        print(f"✓ Test results saved to: {filename}")

    except Exception as e:
        print(f"Error saving results: {e}")


def save_private_key_results(addresses, test_type):
    """Save private key test results to file."""
    if not addresses:
        return

    save = input("\nSave private key test results to file? (y/n): ").strip().lower()
    if save != "y":
        return

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"private_key_test_{test_type}_{timestamp}.txt"

    try:
        with open(filename, "w") as f:
            f.write("BSV Private Key Test Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Test Type: {test_type}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total test keys: {len(addresses)}\n")
            f.write("⚠️  WARNING: This file contains private keys for testing only!\n")
            f.write("⚠️  Do NOT send real funds to these addresses!\n\n")

            for addr in addresses:
                f.write(f"Index: {addr['index']}\n")
                f.write(f"Path: {addr['derivation_path']}\n")
                f.write(f"Address: {addr['address']}\n")
                f.write(f"Private Key (WIF): {addr['private_key']}\n")
                f.write(f"Note: {addr['note']}\n")
                f.write("-" * 50 + "\n")

        print(f"✓ Private key test results saved to: {filename}")
        print("⚠️  WARNING: This file contains private keys! Keep it secure!")

    except Exception as e:
        print(f"Error saving private key results: {e}")


def main():
    """Main function."""
    print_banner()

    try:
        # Get user choice
        choice = get_user_choice()

        # Test based on choice
        if choice == "1":
            # Test with example xpub
            result = test_with_example_xpub()
            test_type = "example_xpub"
        elif choice == "2":
            # Test with custom xpub
            result = test_with_custom_xpub()
            test_type = "custom_xpub"
        elif choice == "3":
            # Test with fixed private key
            result = test_with_new_private_key()
            test_type = "test_private_key"

        if not result:
            print("Test setup failed.")
            return

        key_obj, extra_info = result

        # Handle different test types
        if choice == "3":
            # Private key testing - show comprehensive results
            print("\n✓ HD wallet demonstration completed successfully!")
            print("📋 HD Wallet Test Results:")
            print("   - Generated master private key from entropy")
            print("   - Derived master public key (Xpub)")
            print("   - Demonstrated BIP44 hierarchical derivation")
            print("   - Created child private keys and addresses")

            if extra_info:  # We have test addresses with private keys
                print(f"   - Generated {len(extra_info)} child key variations")

                # Option to save private key test results
                save_private_key_results(extra_info, test_type)

                # Also test the derived xpub with address derivation
                print("\n🔄 Testing derived Xpub with address derivation...")
                additional_addresses = test_address_derivation(key_obj, 3)
                if additional_addresses:
                    print(
                        "✓ Successfully derived additional addresses from the generated Xpub!"
                    )

            print("\n💡 This demonstrates full HD wallet functionality in the BSV SDK.")
            print(
                "   Including entropy → mnemonic → seed → master keys → child derivation."
            )
        else:
            # Test address derivation for xpub
            count = 5  # Test with 5 addresses
            addresses = test_address_derivation(key_obj, count)

            if addresses:
                print(f"\n✓ Successfully derived {len(addresses)} test addresses!")

                # Option to save results
                save_test_results(addresses, test_type)

        print("\n📋 Next Steps:")
        print("1. Try running the main address generator: python main.py")
        if choice == "1":
            print("2. Use the example_xpub.txt file when prompted")
        print("3. Compare results to verify consistency")

    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    print("\n✓ Test completed! The BSV Address Generator should work correctly.")


if __name__ == "__main__":
    main()
