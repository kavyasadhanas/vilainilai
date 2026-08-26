from api.core.database import Base, engine, SessionLocal
from database import models


# Create tables
Base.metadata.create_all(bind=engine)


# Insert initial market costs
db = SessionLocal()

try:
    if db.query(models.MarketCost).count() == 0:

        db.add_all([
            models.MarketCost(
                market_id=1,
                transport_cost_per_kg=1.5,
                commission_per_kg=0.5,
                expected_loss_per_kg=0.3
            ),
            models.MarketCost(
                market_id=2,
                transport_cost_per_kg=3.0,
                commission_per_kg=0.5,
                expected_loss_per_kg=0.3
            )
        ])

        db.commit()

finally:
    db.close()


print("VilaiNilai database created successfully.")