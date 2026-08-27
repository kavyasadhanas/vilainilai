def run_what_if(
    original_offer,
    reservation_price,
    price_change_percent=0,
    transport_change=0,
    spoilage_change=0
):

    new_offer = (
        original_offer
        * (
            1
            + price_change_percent / 100
        )
    )

    new_reservation = (
        reservation_price
        + transport_change
        + spoilage_change
    )

    difference = (
        new_offer
        - new_reservation
    )

    if new_offer >= new_reservation:

        decision = "ACCEPT"

    elif new_offer >= (
        new_reservation * 0.90
    ):

        decision = "NEGOTIATE"

    else:

        decision = "REJECT"

    return {

        "new_offer_price":
        round(new_offer, 2),

        "new_reservation_price":
        round(new_reservation, 2),

        "new_decision":
        decision,

        "difference":
        round(difference, 2)
    }