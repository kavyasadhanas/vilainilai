def make_decision(
    offer_price,
    reservation_price
):

    negotiation_limit = (
        reservation_price * 0.90
    )

    if offer_price >= reservation_price:

        decision = "ACCEPT"

        counteroffer = None

    elif offer_price >= negotiation_limit:

        decision = "NEGOTIATE"

        counteroffer = (
            reservation_price * 1.04
        )

    else:

        decision = "REJECT"

        counteroffer = None

    return {

        "decision": decision,

        "offer_price":
        round(offer_price, 2),

        "reservation_price":
        round(reservation_price, 2),

        "counteroffer":
        round(counteroffer, 2)
        if counteroffer
        else None,

        "price_difference":
        round(
            offer_price
            - reservation_price,
            2
        )
    }