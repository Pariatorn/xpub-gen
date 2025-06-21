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


def display_batch_analysis(batch_analysis):
    """
    Display batch distribution analysis.

    Args:
        batch_analysis (dict): Batch analysis statistics
    """
    print("\n📊 Batch Distribution Analysis:")
    print("-" * 50)
    print(f"Total batches created: {batch_analysis['total_batches']}")
    print(f"Total addresses: {batch_analysis['total_addresses']}")
    print(f"Total amount distributed: {batch_analysis['total_amount_distributed']} BSV")
    print()
    print("Batch amount distribution:")
    print(f"• Min batch amount: {batch_analysis['min_batch_amount']} BSV")
    print(f"• Max batch amount: {batch_analysis['max_batch_amount']} BSV")
    print(f"• Average batch amount: {batch_analysis['avg_batch_amount']:.8f} BSV")
    print()
    print("Addresses per batch:")
    print(f"• Min addresses: {batch_analysis['min_addresses_per_batch']}")
    print(f"• Max addresses: {batch_analysis['max_addresses_per_batch']}")
    print(f"• Average addresses: {batch_analysis['avg_addresses_per_batch']:.1f}")

    if batch_analysis["distribution_accuracy"]:
        print("✅ Distribution accuracy: Perfect")
    else:
        print("⚠️  Minor rounding discrepancy detected")

    print("-" * 50)


def save_batch_files(batches, base_filename, distribution_mode, randomized=False):
    """
    Save batch files to a subdirectory.

    Args:
        batches (list): List of batch dictionaries
        base_filename (str): Base filename (without extension)
        distribution_mode (str): Distribution mode used
        randomized (bool): Whether addresses were randomized

    Returns:
        tuple: (success: bool, subdirectory_path: str, saved_files: list)
    """
    import os
    from datetime import datetime

    if not batches:
        return False, None, []

    # Create subdirectory name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    subdir_name = f"{base_filename}_batches_{timestamp}"

    try:
        # Create subdirectory
        os.makedirs(subdir_name, exist_ok=True)

        saved_files = []

        # Create batch info file
        info_filename = os.path.join(subdir_name, "batch_info.txt")
        with open(info_filename, "w", encoding="utf-8") as f:
            f.write("BSV Address Batch Processing Information\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Distribution mode: {distribution_mode}\n")
            f.write(
                f"Address randomization: {'Enabled' if randomized else 'Disabled'}\n"
            )
            f.write(f"Total batches: {len(batches)}\n")
            f.write(
                f"Total addresses: {sum(batch['address_count'] for batch in batches)}\n"
            )
            f.write(
                f"Total amount: {sum(batch['total_amount'] for batch in batches)} BSV\n\n"
            )

            f.write("Batch Summary:\n")
            f.write("-" * 30 + "\n")
            for batch in batches:
                f.write(f"Batch {batch['batch_number']:02d}: ")
                f.write(f"{batch['address_count']} addresses, ")
                f.write(f"{batch['total_amount']} BSV\n")

        saved_files.append(info_filename)

        # Save individual batch CSV files
        for batch in batches:
            batch_filename = os.path.join(
                subdir_name,
                f"batch_{batch['batch_number']:02d}_{batch['total_amount']:.8f}_BSV.csv",
            )

            with open(batch_filename, "w", encoding="utf-8") as f:
                # Write address,amount pairs
                for addr, amount in zip(batch["addresses"], batch["amounts"]):
                    f.write(f"{addr['address']},{amount}\n")

            saved_files.append(batch_filename)

        return True, subdir_name, saved_files

    except Exception as e:
        print(f"Error creating batch files: {e}")
        return False, None, []


def display_batch_completion_message(success, subdir_path, saved_files, batch_count):
    """
    Display completion message for batch processing.

    Args:
        success (bool): Whether batch creation was successful
        subdir_path (str): Path to the subdirectory
        saved_files (list): List of saved file paths
        batch_count (int): Number of batches created
    """
    if success:
        print("\n✅ Batch Processing Complete!")
        print(f"✓ Created {batch_count} batch files in subdirectory: {subdir_path}")
        print("✓ Batch info file: batch_info.txt")
        print(f"✓ Total files created: {len(saved_files)}")
        print("\nBatch files are ready for independent processing!")

        if batch_count > 10:
            print(f"💡 Tip: Use 'ls {subdir_path}/' to view all batch files")
    else:
        print("\n❌ Batch processing failed!")
        print("The main CSV file is still available.")


def ask_batch_processing_after_csv():
    """Ask if user wants to enable batch processing after CSV creation."""
    return (
        input("\nWould you like to split this CSV into multiple batch files? (y/n): ")
        .strip()
        .lower()
        == "y"
    )
