import pandas as pd


def find_best_alternative(
    market_df,
    quantity
):

    alternatives = []

    for _, row in market_df.iterrows():

        # Expected selling price
        expected_price = row[
            "forecast_price"
        ]

        # Total cost
        total_cost = (
            row["transport_cost_per_kg"]
            + row["commission_per_kg"]
            + row["storage_cost_per_kg"]
        )

        # Price after costs
        net_price = (
            expected_price
            - total_cost
        )

        # Spoilage adjustment
        usable_quantity = (
            quantity
            * (
                1
                - row[
                    "spoilage_percentage"
                ] / 100
            )
        )

        # Final expected return
        expected_net_return = (
            net_price
            * usable_quantity
        )

        alternatives.append({

            "market": row["market"],

            "forecast_price":
            round(expected_price, 2),

            "net_price_per_kg":
            round(net_price, 2),

            "expected_net_return":
            round(expected_net_return, 2),

            "spoilage_percentage":
            row["spoilage_percentage"]
        })

    alternatives_df = pd.DataFrame(
        alternatives
    )

    best = alternatives_df.loc[
        alternatives_df[
            "expected_net_return"
        ].idxmax()
    ]

    return best, alternatives_df


def calculate_reservation_price(
    best_alternative,
    quantity,
    risk_preference="medium"
):

    alternative_value_per_kg = (
        best_alternative[
            "expected_net_return"
        ]
        / quantity
    )

    risk_adjustments = {
        "low": 0.02,
        "medium": 0.05,
        "high": 0.10
    }

    risk_factor = risk_adjustments.get(
        risk_preference.lower(),
        0.05
    )

    risk_adjustment = (
        alternative_value_per_kg
        * risk_factor
    )

    reservation_price = (
        alternative_value_per_kg
        + risk_adjustment
    )

    return {

        "best_market":
        best_alternative["market"],

        "alternative_value_per_kg":
        round(
            alternative_value_per_kg,
            2
        ),

        "risk_adjustment":
        round(
            risk_adjustment,
            2
        ),

        "reservation_price":
        round(
            reservation_price,
            2
        )
    }