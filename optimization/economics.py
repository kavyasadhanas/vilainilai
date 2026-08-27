from optimization.inputs import DestinationOption


def calculate_net_price_per_kg(option: DestinationOption) -> float:
    """
    Net price the farmer actually receives per kg, after
    transport, commission, spoilage loss, and (if storing)
    the cost of storage over the waiting period.
    """

    # Spoilage reduces the effective price you get
    price_after_loss = option.price_per_kg * (1 - option.expected_loss_pct)

    net_price = (
        price_after_loss
        - option.transport_cost_per_kg
        - option.commission_per_kg
    )

    # If this involves waiting/storing, subtract storage cost
    # accumulated over the number of days
    if option.days_to_realize > 0:
        total_storage_cost = (
            option.storage_cost_per_kg_day * option.days_to_realize
        )
        net_price -= total_storage_cost

    return round(net_price, 2)


def calculate_expected_return(option: DestinationOption, quantity_kg: float) -> float:
    """
    Total expected money the farmer gets if they send
    `quantity_kg` to this destination.
    """
    net_price = calculate_net_price_per_kg(option)
    return round(net_price * quantity_kg, 2)


if __name__ == "__main__":
    # Quick manual test
    test_option = DestinationOption(
        id="market_1",
        kind="MARKET",
        price_per_kg=25,
        transport_cost_per_kg=1.5,
        commission_per_kg=0.5,
        expected_loss_pct=0.05
    )

    print("Net price per kg:", calculate_net_price_per_kg(test_option))
    print("Expected return for 500kg:", calculate_expected_return(test_option, 500))