#!/usr/bin/env python3
"""
BSV Address Derivation Tool - Refactored Version
A clean, modular script to derive BSV addresses from extended public keys.

Requirements:
    pip install bsv-sdk

Usage:
    python main_refactored.py
"""

# Import our modular components
from bsv_address_generator.core.derivation import derive_addresses
from bsv_address_generator.core.distribution import (
    analyze_batch_distribution,
    create_address_batches,
    distribute_amounts_equal,
    distribute_amounts_random,
    distribute_amounts_random_optimal,
)
from bsv_address_generator.ui.input_handlers import (
    get_batch_randomization_preference,
    get_bsv_amount,
    get_derivation_count,
    get_derivation_path,
    get_distribution_mode,
    get_max_bsv_per_batch,
    get_random_distribution_params,
    get_smart_random_confirmation,
    get_starting_index,
    get_xpub_input,
)
from bsv_address_generator.ui.output_handlers import (
    ask_batch_processing_after_csv,
    ask_csv_creation,
    display_batch_analysis,
    display_batch_completion_message,
    display_completion_message,
    display_distribution_summary,
    display_smart_distribution_benefits,
    display_success_message,
    print_banner,
    save_addresses_to_csv,
    save_addresses_to_txt,
    save_batch_files,
)
from bsv_address_generator.utils.state_manager import (
    update_derivation_state_for_actual_usage,
)


def handle_address_truncation(addresses, actual_count, original_count, xpub, base_path):
    """
    Helper function to handle address list truncation and derivation state updates.

    Args:
        addresses: List of address dictionaries
        actual_count: Number of addresses actually used
        original_count: Original number of addresses generated
        xpub: Extended public key
        base_path: Derivation path

    Returns:
        Possibly truncated list of addresses
    """
    if actual_count < original_count:
        addresses = addresses[:actual_count]
        update_derivation_state_for_actual_usage(xpub, base_path, addresses)
    return addresses


def main():
    """Main function to run the address derivation tool."""
    print_banner()

    try:
        # Step 1: Get extended public key
        xpub = get_xpub_input()

        # Step 2: Get number of addresses to derive
        count = get_derivation_count()

        # Step 3: Get derivation path
        base_path = get_derivation_path()

        # Step 4: Get starting index (considering previous derivations)
        start_index = get_starting_index(xpub, base_path)

        # Step 5: Derive addresses
        addresses = derive_addresses(xpub, count, base_path, start_index)

        if addresses:
            display_success_message(len(addresses))

            # Step 6: Save to TXT file (optional)
            save_addresses_to_txt(addresses)

            # Step 7: Create CSV with amounts (optional)
            if ask_csv_creation():
                # Get total BSV amount
                total_amount = get_bsv_amount()

                # Get distribution mode
                distribution_mode = get_distribution_mode()

                # Initialize variables
                amounts = None
                distribution_info = None
                min_amount = None
                max_amount = None

                # Generate amounts based on distribution mode
                if distribution_mode == "equal":
                    amounts, actual_count = distribute_amounts_equal(
                        total_amount, len(addresses)
                    )
                    # Update addresses list if count was reduced
                    addresses = handle_address_truncation(
                        addresses, actual_count, len(addresses), xpub, base_path
                    )
                    display_distribution_summary(
                        total_amount, amounts, distribution_mode
                    )

                elif distribution_mode == "smart_random":
                    # Show benefits and get confirmation
                    display_smart_distribution_benefits()
                    confirmed, min_amount, max_amount, distribution_info = (
                        get_smart_random_confirmation(total_amount, len(addresses))
                    )

                    if confirmed:
                        amounts, distribution_info = distribute_amounts_random_optimal(
                            total_amount, len(addresses)
                        )
                        # Update addresses list if count was reduced
                        final_count = distribution_info.get(
                            "final_address_count", len(addresses)
                        )
                        addresses = handle_address_truncation(
                            addresses, final_count, len(addresses), xpub, base_path
                        )
                        min_amount = distribution_info["min_bound_used"]
                        max_amount = distribution_info["max_bound_used"]

                        display_distribution_summary(
                            total_amount,
                            amounts,
                            distribution_mode,
                            min_amount,
                            max_amount,
                            distribution_info,
                        )
                    else:
                        print(
                            (
                                "Smart distribution cancelled. "
                                "Falling back to manual random distribution."
                            )
                        )
                        min_amount, max_amount = get_random_distribution_params(
                            total_amount, len(addresses)
                        )
                        amounts, actual_count = distribute_amounts_random(
                            total_amount, len(addresses), min_amount, max_amount
                        )
                        # Update addresses list if count was reduced
                        addresses = handle_address_truncation(
                            addresses, actual_count, len(addresses), xpub, base_path
                        )
                        distribution_mode = "random"  # Update mode for display
                        display_distribution_summary(
                            total_amount,
                            amounts,
                            distribution_mode,
                            min_amount,
                            max_amount,
                        )

                else:  # random distribution
                    min_amount, max_amount = get_random_distribution_params(
                        total_amount, len(addresses)
                    )
                    amounts, actual_count = distribute_amounts_random(
                        total_amount, len(addresses), min_amount, max_amount
                    )
                    # Update addresses list if count was reduced
                    addresses = handle_address_truncation(
                        addresses, actual_count, len(addresses), xpub, base_path
                    )
                    display_distribution_summary(
                        total_amount, amounts, distribution_mode, min_amount, max_amount
                    )

                # Save to CSV if amounts were generated
                if amounts:
                    main_csv_filename = save_addresses_to_csv(
                        addresses, amounts, distribution_mode, distribution_info
                    )

                    # Step 8: Batch processing (optional)
                    if main_csv_filename and ask_batch_processing_after_csv():
                        # Get batch processing parameters
                        max_bsv_per_batch = get_max_bsv_per_batch()

                        # Ask about randomization for privacy (only for random modes)
                        randomize_batches = get_batch_randomization_preference(
                            distribution_mode
                        )

                        # Create batches
                        print("\n🔄 Creating batch files...")
                        batches = create_address_batches(
                            addresses, amounts, max_bsv_per_batch, randomize_batches
                        )

                        if batches:
                            # Analyze batch distribution
                            batch_analysis = analyze_batch_distribution(
                                batches, total_amount
                            )
                            display_batch_analysis(batch_analysis)

                            # Extract base filename from main CSV
                            base_filename = (
                                main_csv_filename.replace(".csv", "")
                                if main_csv_filename.endswith(".csv")
                                else main_csv_filename
                            )

                            # Save batch files
                            success, subdir_path, saved_files = save_batch_files(
                                batches,
                                base_filename,
                                distribution_mode,
                                randomize_batches,
                            )

                            # Display completion message
                            display_batch_completion_message(
                                success, subdir_path, saved_files, len(batches)
                            )
                        else:
                            print("❌ Failed to create batches.")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    display_completion_message()


if __name__ == "__main__":
    main()
