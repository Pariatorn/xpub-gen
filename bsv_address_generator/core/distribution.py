"""
Amount distribution logic for BSV addresses.
Handles equal and random distribution of BSV amounts across addresses.
"""

import random
from decimal import ROUND_DOWN, Decimal

from config import BSV_DUST_LIMIT, SATOSHI_PRECISION, SATOSHIS_PER_BSV


def is_above_dust_limit(amount):
    """
    Check if an amount is above the BSV dust limit.

    Args:
        amount (Decimal): Amount to check

    Returns:
        bool: True if amount is above dust limit
    """
    dust_limit_bsv = Decimal(BSV_DUST_LIMIT) / SATOSHIS_PER_BSV
    return amount > dust_limit_bsv


def get_minimum_viable_amount():
    """
    Get the minimum viable amount (dust limit + small buffer).

    Returns:
        Decimal: Minimum viable amount in BSV
    """
    dust_limit_bsv = Decimal(BSV_DUST_LIMIT) / SATOSHIS_PER_BSV
    return dust_limit_bsv * Decimal("1.1")  # 10% buffer above dust limit


def calculate_optimal_address_count(total_amount, max_addresses=None):
    """
    Calculate the optimal number of addresses for a given total amount.

    Args:
        total_amount (Decimal): Total BSV amount to distribute
        max_addresses (int, optional): Maximum number of addresses allowed

    Returns:
        int: Optimal number of addresses
    """
    min_viable_amount = get_minimum_viable_amount()

    # Calculate maximum possible addresses that can receive viable amounts
    max_possible = int(total_amount / min_viable_amount)

    if max_addresses is not None:
        return min(max_possible, max_addresses)

    return max_possible


def validate_distribution_feasibility(total_amount, address_count, min_amount=None):
    """
    Validate if distribution is feasible with given parameters.

    Args:
        total_amount (Decimal): Total BSV amount
        address_count (int): Number of addresses
        min_amount (Decimal, optional): Minimum amount per address

    Returns:
        tuple: (is_feasible, error_message, suggested_address_count)
    """
    min_viable = get_minimum_viable_amount()

    # Use provided min_amount or minimum viable amount
    effective_min = max(min_amount or min_viable, min_viable)

    # Check if we have enough total amount
    min_total_required = effective_min * address_count

    if min_total_required > total_amount:
        # Calculate how many addresses we can actually support
        suggested_count = calculate_optimal_address_count(total_amount)

        return (
            False,
            f"Cannot distribute {total_amount} BSV across {address_count} addresses. "
            f"Minimum required: {min_total_required} BSV. "
            f"Suggested address count: {suggested_count}",
            suggested_count,
        )

    return True, None, address_count


def calculate_optimal_random_bounds(total_amount, address_count):
    """
    Calculate optimal min/max bounds for random distribution.

    This algorithm ensures:
    1. True randomness across all addresses
    2. No excessive remainder for the last address
    3. Reasonable variation in amounts
    4. Compliance with dust limits

    Args:
        total_amount (Decimal): Total BSV amount to distribute
        address_count (int): Number of addresses

    Returns:
        tuple: (min_amount, max_amount, distribution_info)
    """
    # First validate if distribution is feasible
    is_feasible, error_msg, suggested_count = validate_distribution_feasibility(
        total_amount, address_count
    )

    if not is_feasible:
        # Use suggested count instead
        address_count = suggested_count

    # Calculate average amount per address
    avg_amount = total_amount / address_count

    # Minimum bound: always above dust limit
    min_viable = get_minimum_viable_amount()
    min_from_avg = avg_amount * Decimal("0.25")  # 25% of average
    min_amount = max(min_viable, min_from_avg)

    # Maximum bound: ensure we can distribute without excessive remainder
    # Use 175% of average, but ensure constraints are satisfied
    max_amount = avg_amount * Decimal("1.75")

    # Validate and adjust bounds
    min_amount, max_amount = _validate_and_adjust_bounds(
        total_amount, address_count, min_amount, max_amount, avg_amount
    )

    # Calculate distribution statistics
    variation_range = max_amount - min_amount
    variation_percent = (variation_range / avg_amount) * 100

    distribution_info = {
        "average_amount": avg_amount,
        "variation_range": variation_range,
        "variation_percent": variation_percent,
        "min_percent_of_avg": (min_amount / avg_amount) * 100,
        "max_percent_of_avg": (max_amount / avg_amount) * 100,
        "dust_limit_bsv": min_viable,
        "feasible_address_count": address_count,
        "original_address_count": address_count,
    }

    return min_amount, max_amount, distribution_info


def _validate_and_adjust_bounds(
    total_amount, address_count, min_amount, max_amount, avg_amount
):
    """
    Validate and adjust bounds to ensure distribution is possible.

    Args:
        total_amount (Decimal): Total BSV amount
        address_count (int): Number of addresses
        min_amount (Decimal): Proposed minimum amount
        max_amount (Decimal): Proposed maximum amount
        avg_amount (Decimal): Average amount per address

    Returns:
        tuple: (adjusted_min_amount, adjusted_max_amount)
    """
    # Ensure minimum total can be satisfied
    min_total_required = min_amount * address_count

    if min_total_required > total_amount:
        # Reduce min_amount to make distribution possible
        min_amount = (
            total_amount * Decimal("0.8") / address_count
        )  # Use 80% to leave buffer
        print(f"ℹ️  Adjusted minimum amount to {min_amount} BSV to fit total amount")

    # More sophisticated max amount calculation to prevent excessive last address
    # Calculate what the worst-case last address would get
    # If we give max_amount to (n-1) addresses, what's left for the last?
    worst_case_for_others = max_amount * (address_count - 1)
    worst_case_remainder = total_amount - worst_case_for_others

    # The last address should not get more than 2x the max_amount
    acceptable_max_remainder = max_amount * Decimal("2.0")

    if worst_case_remainder > acceptable_max_remainder:
        # Reduce max_amount so the last address doesn't get too much
        # We want: total - (max_amount * (n-1)) <= 2 * max_amount
        # Solving: max_amount * (n-1) >= total - 2 * max_amount
        # max_amount * (n-1 + 2) >= total
        # max_amount >= total / (n+1)
        conservative_max = total_amount / (address_count + 1)

        # Use this conservative max, but ensure it's not too restrictive
        max_amount = min(max_amount, conservative_max * Decimal("1.3"))  # 30% buffer
        print(
            (
                f"ℹ️  Adjusted maximum amount to {max_amount} BSV to prevent excessive "
                "last address"
            )
        )

    # Ensure we still have enough room for minimum amounts
    adjusted_min_total = min_amount * (address_count - 1)  # Leave last address flexible
    if adjusted_min_total >= total_amount:
        # Further reduce min_amount
        min_amount = (
            total_amount * Decimal("0.6") / address_count
        )  # Use 60% for conservative approach
        print(f"ℹ️  Further adjusted minimum amount to {min_amount} BSV")

    # Final safety check: ensure max > min with reasonable margin
    if max_amount <= min_amount * Decimal("1.1"):  # At least 10% difference
        # Create a balanced range around the average
        spread = avg_amount * Decimal("0.3")  # 30% spread
        min_amount = avg_amount - spread
        max_amount = avg_amount + spread

        # Ensure min is positive and above dust
        dust_limit_bsv = Decimal(BSV_DUST_LIMIT) / SATOSHIS_PER_BSV
        min_amount = max(min_amount, dust_limit_bsv * Decimal("1.1"))

        print(
            (
                f"ℹ️  Created balanced range around average: {min_amount} - "
                f"{max_amount} BSV"
            )
        )

    return min_amount, max_amount


def distribute_amounts_equal(total_amount, address_count):
    """
    Distribute amount equally across addresses.
    Automatically reduces address count if needed to respect dust limits.

    Args:
        total_amount (Decimal): Total BSV amount to distribute
        address_count (int): Requested number of addresses

    Returns:
        tuple: (amounts_list, actual_address_count_used)
    """
    # Validate feasibility and get optimal address count
    is_feasible, error_msg, suggested_count = validate_distribution_feasibility(
        total_amount, address_count
    )

    # Use the feasible address count
    actual_count = suggested_count

    if actual_count != address_count:
        print(
            (
                f"ℹ️  Reduced address count from {address_count} to {actual_count} "
                "to respect dust limits"
            )
        )

    # Calculate amount per address
    amount_per_address = total_amount / actual_count

    # Round down to satoshi precision
    amount_per_address = amount_per_address.quantize(
        Decimal(SATOSHI_PRECISION), rounding=ROUND_DOWN
    )

    amounts = [amount_per_address] * actual_count

    # Handle any remaining dust by adding to the first address
    distributed_total = sum(amounts)
    remainder = total_amount - distributed_total
    if remainder > 0:
        amounts[0] += remainder

    return amounts, actual_count


def distribute_amounts_random(total_amount, address_count, min_amount, max_amount):
    """
    Distribute amount randomly within specified range.
    Ensures all amounts are above dust limit and no negative amounts.

    Args:
        total_amount (Decimal): Total BSV amount to distribute
        address_count (int): Number of addresses
        min_amount (Decimal): Minimum amount per address
        max_amount (Decimal): Maximum amount per address

    Returns:
        tuple: (amounts_list, actual_address_count_used)
    """
    # Ensure min_amount is above dust limit
    min_viable = get_minimum_viable_amount()
    min_amount = max(min_amount, min_viable)

    # Validate feasibility
    is_feasible, error_msg, suggested_count = validate_distribution_feasibility(
        total_amount, address_count, min_amount
    )

    # Use the feasible address count
    actual_count = suggested_count

    if actual_count != address_count:
        print(
            f"ℹ️  Reduced address count from {address_count} to {actual_count} "
            "for random distribution"
        )

    # Recalculate max_amount if needed to ensure feasibility
    avg_amount = total_amount / actual_count
    if max_amount > avg_amount * Decimal("2.0"):
        max_amount = avg_amount * Decimal("1.8")  # Conservative maximum
        print(
            (
                f"ℹ️  Adjusted maximum amount to {max_amount} BSV to ensure "
                "feasible distribution"
            )
        )

    amounts = []
    remaining = total_amount

    for i in range(actual_count - 1):
        # Calculate maximum possible for this address (leaving enough for remaining)
        remaining_addresses = actual_count - i - 1
        max_for_remaining = remaining - (min_amount * remaining_addresses)

        # Actual maximum for this address
        actual_max = min(max_amount, max_for_remaining)
        actual_min = min_amount

        # Ensure we have a valid range
        if actual_max <= actual_min:
            amount = actual_min
        else:
            # Generate random amount within range
            random_factor = Decimal(str(random.random()))
            amount = actual_min + (actual_max - actual_min) * random_factor
            # Round to satoshi precision
            amount = amount.quantize(Decimal(SATOSHI_PRECISION), rounding=ROUND_DOWN)

        amounts.append(amount)
        remaining -= amount

    # Last address gets the remainder - ensure it's above dust limit
    final_amount = remaining
    if final_amount < min_viable:
        # Redistribute some amount from previous addresses
        needed = min_viable - final_amount
        for i in range(len(amounts) - 1, -1, -1):
            if amounts[i] > min_amount + needed:
                amounts[i] -= needed
                final_amount += needed
                break

    amounts.append(final_amount)

    # Final validation - ensure no negative or dust amounts
    for i, amount in enumerate(amounts):
        if amount < min_viable:
            print(
                f"⚠️  Warning: Address {i} amount {amount} below minimum viable amount"
            )

    return amounts, actual_count


def distribute_amounts_random_smart(
    total_amount, address_count, min_amount, max_amount
):
    """
    Improved random distribution that prevents excessive last address amounts.
    Includes dust limit protection and negative amount prevention.

    Args:
        total_amount (Decimal): Total BSV amount to distribute
        address_count (int): Number of addresses
        min_amount (Decimal): Minimum amount per address
        max_amount (Decimal): Maximum amount per address

    Returns:
        tuple: (amounts_list, actual_address_count_used)
    """
    # Ensure min_amount is above dust limit
    min_viable = get_minimum_viable_amount()
    min_amount = max(min_amount, min_viable)

    # Validate feasibility
    is_feasible, error_msg, suggested_count = validate_distribution_feasibility(
        total_amount, address_count, min_amount
    )

    # Use the feasible address count
    actual_count = suggested_count

    if actual_count != address_count:
        print(
            (
                f"ℹ️  Reduced address count from {address_count} to {actual_count} "
                "for smart distribution"
            )
        )

    amounts = []
    remaining = total_amount

    # Calculate target amount for last address (should be within reasonable bounds)
    target_last_amount = max_amount * Decimal("1.1")  # Allow 10% over max

    for i in range(actual_count):
        remaining_addresses = actual_count - i

        if remaining_addresses == 1:
            # Last address gets whatever is left (ensure it's above dust limit)
            final_amount = remaining
            if final_amount < min_viable:
                # This shouldn't happen with proper validation, but safety check
                final_amount = min_viable
            amounts.append(final_amount)
            break

        # Calculate constraints for this address
        min_for_remaining = min_amount * (remaining_addresses - 1)
        max_available = remaining - min_for_remaining

        # Also consider what we want to leave for the last address
        if remaining_addresses == 2:  # Next to last address
            max_to_leave_reasonable = min(
                target_last_amount, max_amount * Decimal("1.5")
            )
            max_available = min(max_available, remaining - max_to_leave_reasonable)

        # Determine bounds for this specific address
        actual_min = min_amount
        actual_max = min(max_amount, max_available)

        # Ensure we have a valid range
        if actual_max <= actual_min:
            amount = actual_min
        else:
            # Generate random amount within range
            random_factor = Decimal(str(random.random()))
            amount = actual_min + (actual_max - actual_min) * random_factor
            # Round to satoshi precision
            amount = amount.quantize(Decimal(SATOSHI_PRECISION), rounding=ROUND_DOWN)

        amounts.append(amount)
        remaining -= amount

    return amounts, actual_count


def distribute_amounts_random_optimal(total_amount, address_count):
    """
    Distribute amount randomly using automatically calculated optimal bounds.
    Includes automatic address count optimization.

    Args:
        total_amount (Decimal): Total BSV amount to distribute
        address_count (int): Requested number of addresses

    Returns:
        tuple: (amounts_list, distribution_info)
    """
    min_amount, max_amount, distribution_info = calculate_optimal_random_bounds(
        total_amount, address_count
    )

    # Get the actual feasible address count
    actual_count = distribution_info["feasible_address_count"]

    # Use the improved smart distribution algorithm
    amounts, final_count = distribute_amounts_random_smart(
        total_amount, actual_count, min_amount, max_amount
    )

    # Add actual distribution statistics
    distribution_info.update(
        {
            "actual_min": min(amounts),
            "actual_max": max(amounts),
            "actual_avg": sum(amounts) / len(amounts),
            "min_bound_used": min_amount,
            "max_bound_used": max_amount,
            "final_address_count": final_count,
        }
    )

    return amounts, distribution_info


def validate_distribution_params(total_amount, address_count, min_amount, max_amount):
    """
    Validate distribution parameters.

    Args:
        total_amount (Decimal): Total BSV amount
        address_count (int): Number of addresses
        min_amount (Decimal): Minimum amount per address
        max_amount (Decimal): Maximum amount per address

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check dust limit compliance
    min_viable = get_minimum_viable_amount()
    if min_amount < min_viable:
        return (
            False,
            f"Minimum amount must be at least {min_viable} BSV (above dust limit).",
        )

    # Check if minimum is greater than maximum
    if max_amount <= min_amount:
        return (
            False,
            f"Maximum amount must be greater than minimum amount ({min_amount} BSV).",
        )

    # Check if maximum amount exceeds total
    if max_amount >= total_amount:
        return (
            False,
            f"Maximum amount must be less than total amount ({total_amount} BSV).",
        )

    # Use the comprehensive feasibility check
    is_feasible, error_msg, suggested_count = validate_distribution_feasibility(
        total_amount, address_count, min_amount
    )

    if not is_feasible:
        return False, error_msg

    # Check if maximum total is less than available amount
    max_total = max_amount * address_count
    if max_total < total_amount:
        return (
            False,
            (
                f"Maximum total ({max_total} BSV) is less than total amount "
                f"({total_amount} BSV)."
            ),
        )

    return True, None


def analyze_distribution_quality(amounts, min_bound, max_bound, total_amount):
    """
    Analyze the quality of a distribution.

    Args:
        amounts (list): List of distributed amounts
        min_bound (Decimal): Minimum bound used
        max_bound (Decimal): Maximum bound used
        total_amount (Decimal): Total amount distributed

    Returns:
        dict: Distribution quality metrics
    """
    actual_min = min(amounts)
    actual_max = max(amounts)
    actual_avg = sum(amounts) / len(amounts)

    # Calculate variation coefficient (standard deviation / mean)
    variance = sum((amount - actual_avg) ** 2 for amount in amounts) / len(amounts)
    std_dev = variance.sqrt()
    variation_coefficient = std_dev / actual_avg

    # Check if last address got excessive amount
    last_amount = amounts[-1]
    excessive_last = last_amount > max_bound * Decimal("1.2")  # 20% over max

    # Count addresses within bounds
    within_bounds = sum(
        1 for amount in amounts[:-1] if min_bound <= amount <= max_bound
    )
    bound_compliance = within_bounds / (len(amounts) - 1) * 100  # Exclude last address

    return {
        "actual_min": actual_min,
        "actual_max": actual_max,
        "actual_avg": actual_avg,
        "std_deviation": std_dev,
        "variation_coefficient": float(variation_coefficient),
        "excessive_last_address": excessive_last,
        "bound_compliance_percent": float(bound_compliance),
        "total_distributed": sum(amounts),
        "distribution_accuracy": abs(sum(amounts) - total_amount)
        < Decimal("0.00000001"),
    }


def create_address_batches(addresses, amounts, max_bsv_per_batch, randomize=False):
    """
    Split addresses and amounts into batches based on maximum BSV per batch.

    Enhanced with variable batch sizes for improved privacy.

    Args:
        addresses (list): List of address dictionaries
        amounts (list): List of corresponding amounts
        max_bsv_per_batch (Decimal): Maximum BSV amount per batch
        randomize (bool): Whether to randomize order for privacy

    Returns:
        list: List of batch dictionaries with addresses, amounts, and metadata
    """
    import random
    from decimal import Decimal

    if len(addresses) != len(amounts):
        raise ValueError("Addresses and amounts lists must have equal length")

    # Combine addresses and amounts for easier processing
    combined_data = list(zip(addresses, amounts))

    # Randomize for privacy if requested
    if randomize:
        combined_data = combined_data.copy()
        random.shuffle(combined_data)

    batches = []
    current_batch_addresses = []
    current_batch_amounts = []
    current_batch_total = Decimal("0")
    batch_number = 1

    for address, amount in combined_data:
        # Enhanced privacy: Use variable batch size instead of always max
        # Create target batch size between 60%-95% of maximum (with some randomness)
        if len(current_batch_addresses) == 0:
            # First item in new batch - calculate variable target size
            privacy_factor = Decimal(str(0.6 + (random.random() * 0.35)))  # 60-95%
            current_target_size = max_bsv_per_batch * privacy_factor
        else:
            # Use the target size we calculated when starting this batch
            pass

        # Check if adding this amount would exceed the target (not max) for privacy
        would_exceed_target = current_batch_total + amount > current_target_size
        # But still respect the absolute maximum as a hard limit
        would_exceed_max = current_batch_total + amount > max_bsv_per_batch

        # Decide whether to start a new batch
        should_start_new_batch = len(current_batch_addresses) > 0 and (
            would_exceed_target or would_exceed_max
        )

        if should_start_new_batch:
            # Save current batch
            batches.append(
                {
                    "batch_number": batch_number,
                    "addresses": current_batch_addresses.copy(),
                    "amounts": current_batch_amounts.copy(),
                    "total_amount": current_batch_total,
                    "address_count": len(current_batch_addresses),
                }
            )

            # Start new batch with new variable target size
            current_batch_addresses = []
            current_batch_amounts = []
            current_batch_total = Decimal("0")
            batch_number += 1

            # Calculate new target size for privacy variation
            privacy_factor = Decimal(str(0.6 + (random.random() * 0.35)))  # 60-95%
            current_target_size = max_bsv_per_batch * privacy_factor

        # Add to current batch
        current_batch_addresses.append(address)
        current_batch_amounts.append(amount)
        current_batch_total += amount

    # Add final batch if not empty
    if current_batch_addresses:
        batches.append(
            {
                "batch_number": batch_number,
                "addresses": current_batch_addresses,
                "amounts": current_batch_amounts,
                "total_amount": current_batch_total,
                "address_count": len(current_batch_addresses),
            }
        )

    return batches


def analyze_batch_distribution(batches, total_amount):
    """
    Analyze the batch distribution and provide statistics.

    Args:
        batches (list): List of batch dictionaries
        total_amount (Decimal): Total amount being distributed

    Returns:
        dict: Distribution analysis statistics
    """
    from decimal import Decimal

    if not batches:
        return {}

    batch_amounts = [batch["total_amount"] for batch in batches]
    batch_counts = [batch["address_count"] for batch in batches]

    analysis = {
        "total_batches": len(batches),
        "total_addresses": sum(batch_counts),
        "total_amount_distributed": sum(batch_amounts),
        "min_batch_amount": min(batch_amounts),
        "max_batch_amount": max(batch_amounts),
        "avg_batch_amount": sum(batch_amounts) / len(batches),
        "min_addresses_per_batch": min(batch_counts),
        "max_addresses_per_batch": max(batch_counts),
        "avg_addresses_per_batch": sum(batch_counts) / len(batches),
        "distribution_accuracy": abs(sum(batch_amounts) - total_amount)
        < Decimal("0.00000001"),
    }

    return analysis
