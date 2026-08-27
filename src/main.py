import pandas as pd
import os

from reservation_price import (
    find_best_alternative,
    calculate_reservation_price
)

from negotiation_engine import (
    make_decision
)

from breakpoint_engine import (
    check_decision_breakpoint
)

from what_if import (
    run_what_if
)

from explainability import (
    generate_explanation
)


def main():

    print("\n🌾 VILAINILAI")
    print(
        "FairDeal AI & Decision Intelligence"
    )

    print(
        "\nLoading synthetic market data..."
    )

    market_df = pd.read_csv(
        "data/synthetic_market_data.csv"
    )

    buyer_df = pd.read_csv(
        "data/synthetic_buyer_offers.csv"
    )

    # Use latest day
    latest_day = market_df["day"].max()

    latest_market_data = market_df[
        market_df["day"] == latest_day
    ]

    # Farmer harvest quantity
    quantity = 400

    # Risk preference
    risk_preference = "medium"

    print(
        f"\nFarmer Quantity: {quantity} kg"
    )

    print(
        f"Risk Preference: {risk_preference}"
    )

    # --------------------------------
    # STEP 1: Find best alternative
    # --------------------------------

    best_alternative, alternatives = (
        find_best_alternative(
            latest_market_data,
            quantity
        )
    )

    print("\n📊 MARKET ALTERNATIVES")

    print(
        alternatives[
            [
                "market",
                "forecast_price",
                "net_price_per_kg",
                "expected_net_return"
            ]
        ]
    )

    # --------------------------------
    # STEP 2: Reservation Price
    # --------------------------------

    reservation_result = (
        calculate_reservation_price(
            best_alternative,
            quantity,
            risk_preference
        )
    )

    reservation_price = (
        reservation_result[
            "reservation_price"
        ]
    )

    print(
        "\n💰 RESERVATION PRICE"
    )

    print(
        f"Best Alternative Market: "
        f"{reservation_result['best_market']}"
    )

    print(
        f"Minimum Acceptable Price: "
        f"₹{reservation_price}/kg"
    )

    # --------------------------------
    # STEP 3: Evaluate Buyer Offers
    # --------------------------------

    results = []

    print("\n🤝 FAIRDEAL BUYER OFFERS")

    for _, buyer in buyer_df.iterrows():

        offer_price = buyer[
            "offer_price"
        ]

        decision_result = make_decision(
            offer_price,
            reservation_price
        )

        explanation = generate_explanation(
            decision_result,
            reservation_result
        )

        results.append({

            "buyer":
            buyer["buyer"],

            "quantity":
            buyer["quantity"],

            "offer_price":
            offer_price,

            "reservation_price":
            reservation_price,

            "decision":
            decision_result["decision"],

            "counteroffer":
            decision_result["counteroffer"],

            "explanation":
            explanation
        })

    results_df = pd.DataFrame(
        results
    )

    print(
        results_df[
            [
                "buyer",
                "offer_price",
                "reservation_price",
                "decision",
                "counteroffer"
            ]
        ]
    )

    # Save results
    results_df.to_csv(
        "data/fairdeal_results.csv",
        index=False
    )

    # --------------------------------
    # STEP 4: Breakpoint Engine
    # --------------------------------

    sample_market = (
        latest_market_data.iloc[0]
    )

    breakpoint_result = (
        check_decision_breakpoint(

            current_price=
            sample_market["current_price"],

            expected_price=
            sample_market["forecast_price"],

            spoilage_percentage=
            sample_market[
                "spoilage_percentage"
            ],

            alternative_return=
            best_alternative[
                "expected_net_return"
            ],

            current_strategy_return=
            best_alternative[
                "expected_net_return"
            ] * 0.90
        )
    )

    print("\n🚨 DECISION BREAKPOINT")

    print(
        breakpoint_result
    )

    # --------------------------------
    # STEP 5: What-If Analysis
    # --------------------------------

    first_offer = buyer_df.iloc[0]

    what_if_result = run_what_if(

        original_offer=
        first_offer["offer_price"],

        reservation_price=
        reservation_price,

        price_change_percent=-5,

        transport_change=1,

        spoilage_change=0.5
    )

    print("\n🔮 WHAT-IF ANALYSIS")

    print(
        what_if_result
    )

    print(
        "\n✅ FairDeal AI completed successfully!"
    )


if __name__ == "__main__":

    main()