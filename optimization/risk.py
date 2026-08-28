from optimization.inputs import DestinationOption


# How much we discount an option's return based on farmer's risk appetite
# and how uncertain that option is (waiting/storing = more uncertain than selling today)
RISK_PENALTY_PER_DAY = {
    "LOW": 0.10,        # risk-averse farmer: heavily penalize waiting
    "MEDIUM": 0.04,      # moderate: some penalty
    "HIGH": 0.01,        # risk-tolerant: barely penalizes waiting
}


def get_risk_adjusted_price(option: DestinationOption, net_price_per_kg: float, risk_preference: str) -> float:
    """
    Reduce the net price of an option based on how many days out
    it is (more uncertainty = more risk) and the farmer's risk
    tolerance. Selling today (days_to_realize == 0) has no penalty.
    """

    risk_preference = risk_preference.upper()
    penalty_rate = RISK_PENALTY_PER_DAY.get(risk_preference, RISK_PENALTY_PER_DAY["MEDIUM"])

    if option.days_to_realize == 0:
        return net_price_per_kg

    penalty = net_price_per_kg * penalty_rate * option.days_to_realize
    risk_adjusted_price = net_price_per_kg - penalty

    return round(risk_adjusted_price, 2)


if __name__ == "__main__":
    # Manual test: same net price, but waiting 3 days
    net_price = 28.0

    for pref in ["LOW", "MEDIUM", "HIGH"]:
        adjusted = get_risk_adjusted_price(
            option=DestinationOption(id="store", kind="STORE", price_per_kg=30, days_to_realize=3),
            net_price_per_kg=net_price,
            risk_preference=pref
        )
        print(f"{pref} risk farmer, 3-day wait: ₹{net_price} -> risk-adjusted ₹{adjusted}")