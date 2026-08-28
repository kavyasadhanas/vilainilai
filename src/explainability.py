def generate_explanation(
    decision_result,
    reservation_result
):

    decision = decision_result[
        "decision"
    ]

    offer = decision_result[
        "offer_price"
    ]

    reservation = decision_result[
        "reservation_price"
    ]

    best_market = reservation_result[
        "best_market"
    ]

    if decision == "ACCEPT":

        explanation = (
            f"The offer of ₹{offer}/kg is "
            f"higher than your minimum acceptable "
            f"price of ₹{reservation}/kg. "
            f"Therefore, accepting this offer is "
            f"economically better than the best "
            f"alternative market strategy."
        )

    elif decision == "NEGOTIATE":

        counteroffer = decision_result[
            "counteroffer"
        ]

        explanation = (
            f"The offer of ₹{offer}/kg is slightly "
            f"below your minimum acceptable price of "
            f"₹{reservation}/kg. "
            f"The best alternative is {best_market}. "
            f"Try negotiating at approximately "
            f"₹{counteroffer}/kg."
        )

    else:

        explanation = (
            f"The offer of ₹{offer}/kg is significantly "
            f"below your minimum acceptable price of "
            f"₹{reservation}/kg. "
            f"Selling through {best_market} is expected "
            f"to provide a better economic return."
        )

    return explanation