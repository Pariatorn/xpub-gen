#!/usr/bin/env python3
"""
BSV Address Derivation Tool - Refactored Version
A clean, modular script to derive BSV addresses from extended public keys.

Requirements:
    pip install bsv-sdk

Usage:
    python main_refactored.py
"""

import sys

# Import our modular components
from bsv_address_generator.core.derivation import derive_addresses
from bsv_address_generator.core.distribution import (
    distribute_amounts_equal,
    distribute_amounts_random,
    distribute_amounts_random_optimal,
)
from bsv_address_generator.ui.input_handlers import (
    get_bsv_amount,
    get_derivation_count,
    get_derivation_path,
    get_distribution_mode,
    get_random_distribution_params,
    get_smart_random_confirmation,
    get_starting_index,
    get_xpub_input,
)
from bsv_address_generator.ui.output_handlers import (
    ask_csv_creation,
    display_completion_message,
    display_distribution_preview,
    display_distribution_summary,
    display_smart_distribution_benefits,
    display_success_message,
    print_banner,
    save_addresses_to_csv,
    save_addresses_to_txt,
)


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
                    amounts = distribute_amounts_equal(total_amount, len(addresses))
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
                            "Smart distribution cancelled. Falling back to manual random distribution."
                        )
                        min_amount, max_amount = get_random_distribution_params(
                            total_amount, len(addresses)
                        )
                        amounts = distribute_amounts_random(
                            total_amount, len(addresses), min_amount, max_amount
                        )
                        distribution_mode = "random"  # Update mode for display
                        display_distribution_summary(
                            total_amount,
                            amounts,
                            distribution_mode,
                            min_amount,
                            max_amount,
                        )

                else:  # manual random
                    min_amount, max_amount = get_random_distribution_params(
                        total_amount, len(addresses)
                    )

                    # Show preview of manual distribution
                    display_distribution_preview(
                        distribution_mode, min_amount, max_amount
                    )

                    amounts = distribute_amounts_random(
                        total_amount, len(addresses), min_amount, max_amount
                    )
                    display_distribution_summary(
                        total_amount, amounts, distribution_mode, min_amount, max_amount
                    )

                # Save to CSV if amounts were generated
                if amounts:
                    save_addresses_to_csv(
                        addresses, amounts, distribution_mode, distribution_info
                    )

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    display_completion_message()


if __name__ == "__main__":
    main()
