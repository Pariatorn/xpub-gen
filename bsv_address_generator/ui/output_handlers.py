"""
Output handlers for BSV address generator.
Handles display formatting and file operations.
"""

from datetime import datetime


def print_banner():
    """Print a nice banner for the tool."""
    banner = """
╔══════════════════════════════════════════╗
║         BSV Address Derivation Tool      ║
║      Using Official BSV SDK for Python   ║
╚══════════════════════════════════════════╝
    """
    print(banner)


def display_distribution_summary(
    total_amount,
    amounts,
    distribution_mode,
    min_amount=None,
    max_amount=None,
    distribution_info=None,
):
    """
    Display summary of amount distribution.

    Args:
        total_amount (Decimal): Total BSV amount
        amounts (list): List of amounts per address
        distribution_mode (str): 'equal', 'random', or 'smart_random'
        min_amount (Decimal, optional): Minimum amount for random distribution
        max_amount (Decimal, optional): Maximum amount for random distribution
        distribution_info (dict, optional): Distribution analysis information
    """
    if distribution_mode == "equal":
        print(f"\n✓ Equal distribution: {amounts[0]} BSV per address")
    elif distribution_mode == "smart_random":
        print("\n🤖 Smart random distribution completed!")
        print(f"✓ Bounds used: {min_amount} - {max_amount} BSV per address")

        if distribution_info:
            print(
                f"✓ Target variation: {distribution_info.get('variation_percent', 0):.1f}% of average"
            )

            # Display quality metrics if available
            if "actual_min" in distribution_info:
                actual_variation = (
                    (distribution_info["actual_max"] - distribution_info["actual_min"])
                    / distribution_info["actual_avg"]
                ) * 100
                print(f"✓ Achieved variation: {actual_variation:.1f}% of average")
    else:  # regular random
        print(
            f"\n✓ Random distribution between {min_amount} - {max_amount} BSV per address"
        )

    print("\nAmount distribution summary:")
    print(f"Total amount: {total_amount} BSV")
    print(f"Distributed amount: {sum(amounts)} BSV")
    print(f"Min amount: {min(amounts)} BSV")
    print(f"Max amount: {max(amounts)} BSV")
    print(f"Average amount: {sum(amounts) / len(amounts)} BSV")

    # Additional analysis for smart random distribution
    if (
        distribution_mode == "smart_random"
        and distribution_info
        and "actual_min" in distribution_info
    ):
        display_distribution_quality_analysis(
            amounts, min_amount, max_amount, distribution_info
        )


def display_distribution_quality_analysis(
    amounts, min_bound, max_bound, distribution_info
):
    """
    Display detailed quality analysis of the distribution.

    Args:
        amounts (list): List of distributed amounts
        min_bound (Decimal): Minimum bound used
        max_bound (Decimal): Maximum bound used
        distribution_info (dict): Distribution analysis information
    """
    from ..core.distribution import analyze_distribution_quality

    quality_metrics = analyze_distribution_quality(
        amounts, min_bound, max_bound, sum(amounts)
    )

    print("\n📊 Distribution Quality Analysis:")
    print("-" * 40)
    print(f"Variation coefficient: {quality_metrics['variation_coefficient']:.3f}")
    print(f"Bound compliance: {quality_metrics['bound_compliance_percent']:.1f}%")

    if quality_metrics["excessive_last_address"]:
        print("⚠️  Last address received excessive amount")
    else:
        print("✅ Last address amount within reasonable bounds")

    if quality_metrics["distribution_accuracy"]:
        print("✅ Distribution accuracy: Perfect")
    else:
        print("⚠️  Minor rounding discrepancy detected")


def save_addresses_to_txt(addresses):
    """
    Ask user if they want to save addresses to a TXT file.

    Args:
        addresses (list): List of address dictionaries

    Returns:
        str: Filename if saved, None otherwise
    """
    if not addresses:
        return None

    save = (
        input(
            f"\nWould you like to save these {len(addresses)} addresses to a file? (y/n): "
        )
        .strip()
        .lower()
    )

    if save == "y":
        # Default filename with timestamp
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
            return filename

        except Exception as e:
            print(f"Error saving file: {e}")
            return None

    return None


def save_addresses_to_csv(
    addresses, amounts, distribution_mode="random", distribution_info=None
):
    """
    Save addresses with amounts to CSV format compatible with Electrum SV.

    Args:
        addresses (list): List of address dictionaries
        amounts (list): List of amounts per address
        distribution_mode (str): Distribution mode used
        distribution_info (dict, optional): Distribution information

    Returns:
        str: Filename if saved, None otherwise
    """
    if not addresses:
        return None

    save = (
        input(
            f"\nWould you like to save these {len(addresses)} addresses with amounts to CSV (Electrum SV format)? (y/n): "
        )
        .strip()
        .lower()
    )

    if save == "y":
        # Default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"bsv_addresses_amounts_{timestamp}.csv"

        filename = input(f"Enter CSV filename (default: {default_filename}): ").strip()
        if not filename:
            filename = default_filename

        try:
            with open(filename, "w", encoding="utf-8") as f:
                # Write address,amount pairs
                for addr, amount in zip(addresses, amounts):
                    f.write(f"{addr['address']},{amount}\n")

            print(f"✓ CSV saved to: {filename}")
            print(f"✓ Total amount distributed: {sum(amounts)} BSV")

            if distribution_mode == "smart_random":
                print("✓ Smart distribution metadata included in CSV comments")

            return filename

        except Exception as e:
            print(f"Error saving CSV file: {e}")
            return None

    return None


def display_success_message(address_count):
    """Display success message after derivation."""
    print(f"\n✓ Successfully derived {address_count} addresses!")


def display_error_message(error_msg):
    """Display formatted error message."""
    print(f"\n❌ Error: {error_msg}")


def display_warning_message(warning_msg):
    """Display formatted warning message."""
    print(f"\n⚠️  Warning: {warning_msg}")


def display_completion_message():
    """Display final completion message."""
    print("\nThank you for using BSV Address Derivation Tool!")


def ask_csv_creation():
    """Ask if user wants to create a CSV with amounts."""
    return (
        input("\nWould you like to create a CSV with amounts for Electrum SV? (y/n): ")
        .strip()
        .lower()
        == "y"
    )


def display_smart_distribution_benefits():
    """Display benefits of smart random distribution."""
    print("\n🎯 Smart Random Distribution Benefits:")
    print("• Automatically calculates optimal min/max bounds")
    print("• Prevents last address from getting excessive amounts")
    print("• Ensures true randomness across all addresses")
    print("• Maintains reasonable variation while respecting constraints")
    print("• Handles dust limit compliance automatically")
    print("• Provides distribution quality analysis")
    print()


def display_distribution_preview(
    distribution_mode, min_amount=None, max_amount=None, distribution_info=None
):
    """
    Display a preview of the distribution that will be generated.

    Args:
        distribution_mode (str): Distribution mode
        min_amount (Decimal, optional): Minimum amount
        max_amount (Decimal, optional): Maximum amount
        distribution_info (dict, optional): Distribution information
    """
    print(f"\n📋 Distribution Preview ({distribution_mode}):")
    print("-" * 40)

    if distribution_mode == "equal":
        print("• All addresses will receive exactly the same amount")
        print("• Remainder (if any) will be added to the first address")
    elif distribution_mode == "smart_random":
        if distribution_info:
            print(
                f"• Average amount per address: {distribution_info['average_amount']} BSV"
            )
            print(f"• Random range: {min_amount} - {max_amount} BSV")
            print(
                f"• Expected variation: {distribution_info['variation_percent']:.1f}% of average"
            )
            print("• Smart bounds prevent excessive last address amounts")
    else:  # regular random
        print(f"• Random amounts between {min_amount} - {max_amount} BSV")
        print("• Last address gets remaining amount")
        print("• Manual bounds (may cause distribution issues)")

    print("-" * 40)
