def check_decision_breakpoint(
    current_price,
    expected_price,
    spoilage_percentage,
    alternative_return,
    current_strategy_return
):

    reasons = []

    if current_price < expected_price * 0.90:

        reasons.append(
            "Market price dropped more than 10% below expectation."
        )

    if spoilage_percentage > 8:

        reasons.append(
            "Spoilage risk is above 8%."
        )

    if alternative_return > current_strategy_return:

        reasons.append(
            "Another strategy now gives a higher expected return."
        )

    if len(reasons) > 0:

        return {

            "reoptimize": True,

            "status":
            "BREAKPOINT TRIGGERED",

            "reasons": reasons
        }

    else:

        return {

            "reoptimize": False,

            "status":
            "CURRENT STRATEGY STILL OPTIMAL",

            "reasons":
            [
                "No major market change detected."
            ]
        }