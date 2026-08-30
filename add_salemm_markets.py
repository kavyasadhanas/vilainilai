from api.core.database import SessionLocal
from database.models import Market


MARKETS = [
    {
        "name": "Attayampatti(Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.5319,
        "longitude": 78.0508,
    },
    {
        "name": "Hasthampatti(Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.6764,
        "longitude": 78.1581,
    },
    {
        "name": "Sooramangalam(Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.6710,
        "longitude": 78.1200,
    },
    {
        "name": "Thammampatti (Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.4413,
        "longitude": 78.4887,
    },
    {
        "name": "Athur(Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.5859,
        "longitude": 78.0067,
    },
    {
        "name": "Ammapet(Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.5860,
        "longitude": 78.1580,
    },
    {
        "name": "Mettur(Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.7867,
        "longitude": 77.8006,
    },
    {
        "name": "Mecheri(Uzhavar Sandhai)",
        "district": "Salem",
        "latitude": 11.8365,
        "longitude": 77.9590,
    },
    {
        "name": "Edapadi (Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.5862,
        "longitude": 77.8380,
    },
    {
        "name": "Elampillai(Uzhavar Sandhai )",
        "district": "Salem",
        "latitude": 11.6060,
        "longitude": 78.0050,
    },
]


db = SessionLocal()

try:

    added = 0
    skipped = 0

    for item in MARKETS:

        existing = (
            db.query(Market)
            .filter(
                Market.name == item["name"]
            )
            .first()
        )

        if existing:

            print(
                f"SKIP: {item['name']} already exists "
                f"(id={existing.id})"
            )

            skipped += 1
            continue


        market = Market(
            name=item["name"],
            district=item["district"],
            latitude=item["latitude"],
            longitude=item["longitude"],
        )

        db.add(market)

        print(
            f"ADD: {item['name']}"
        )

        added += 1


    db.commit()

    print()
    print(
        f"Done. Added={added}, Skipped={skipped}"
    )

finally:

    db.close()  