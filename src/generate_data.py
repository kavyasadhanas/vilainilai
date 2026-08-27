import pandas as pd
import numpy as np
import os


np.random.seed(42)


def generate_market_data():

    os.makedirs("data", exist_ok=True)

    crops = ["Tomato"]
    markets = [
        "Koyambedu",
        "Madurai",
        "Coimbatore",
        "Salem",
        "Trichy"
    ]

    records = []

    for day in range(30):

        for market in markets:

            base_price = np.random.uniform(22, 32)

            forecast_price = (
                base_price
                + np.random.uniform(-2, 4)
            )

            transport_cost = np.random.uniform(
                0.5, 3
            )

            commission = np.random.uniform(
                0.2, 1
            )

            storage_cost = np.random.uniform(
                0.2, 0.8
            )

            spoilage_percentage = np.random.uniform(
                2, 10
            )

            demand_score = np.random.randint(
                50, 100
            )

            records.append({
                "day": day + 1,
                "crop": "Tomato",
                "market": market,
                "current_price": round(
                    base_price, 2
                ),
                "forecast_price": round(
                    forecast_price, 2
                ),
                "transport_cost_per_kg": round(
                    transport_cost, 2
                ),
                "commission_per_kg": round(
                    commission, 2
                ),
                "storage_cost_per_kg": round(
                    storage_cost, 2
                ),
                "spoilage_percentage": round(
                    spoilage_percentage, 2
                ),
                "demand_score": demand_score
            })

    df = pd.DataFrame(records)

    df.to_csv(
        "data/synthetic_market_data.csv",
        index=False
    )

    print(
        "Synthetic market data created successfully!"
    )

    return df


def generate_buyer_offers():

    buyers = [
        "Local Trader",
        "ABC Processor",
        "Wholesale Buyer",
        "Retail Distributor"
    ]

    records = []

    for buyer in buyers:

        for i in range(10):

            offer_price = np.random.uniform(
                20, 35
            )

            quantity = np.random.choice(
                [100, 200, 300, 400, 500]
            )

            records.append({

                "buyer": buyer,

                "offer_price": round(
                    offer_price, 2
                ),

                "quantity": quantity

            })

    df = pd.DataFrame(records)

    df.to_csv(
        "data/synthetic_buyer_offers.csv",
        index=False
    )

    print(
        "Synthetic buyer offers created successfully!"
    )

    return df


if __name__ == "__main__":

    generate_market_data()

    generate_buyer_offers()