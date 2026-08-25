from digital_twin import (
    FarmerState,
    HarvestState,
    DigitalTwin
)


print("\n" + "=" * 65)
print("VILAINILAI - DIGITAL TWIN TEST")
print("=" * 65)


# ============================================================
# CREATE FARMER
# ============================================================

farmer = FarmerState(
    farmer_id="F001",
    location="Salem",
    risk_preference="MEDIUM"
)


# ============================================================
# CREATE HARVEST
# ============================================================

harvest = HarvestState(
    crop="Tomato",
    variety="Tomato",
    quantity_kg=1000,
    quality="Grade A",
    harvest_date="2026-08-25",
    remaining_shelf_life_days=4,
    storage_capacity_kg=500,
    storage_cost_per_kg_day=0.50
)


# ============================================================
# CREATE DIGITAL TWIN
# ============================================================

twin = DigitalTwin(
    farmer=farmer,
    harvest=harvest
)


# ============================================================
# UPDATE MARKET STATE
# ============================================================

twin.update_market_state(
    current_price=25.0,
    forecast_price=28.0,
    demand_direction="INCREASING",
    shock_status="NORMAL",
    market="Salem Uzhavar Sandhai"
)


# ============================================================
# ADD BUYER OFFER
# ============================================================

twin.add_buyer_offer(
    buyer_name="Local Trader",
    price_per_kg=24.0,
    quantity_kg=400
)


# ============================================================
# DISPLAY STATE
# ============================================================

print("\nCURRENT DIGITAL TWIN STATE")
print("-" * 65)

print(
    twin.get_state()
)


# ============================================================
# OPTIMIZER INPUT
# ============================================================

print("\nOPTIMIZER INPUT")
print("-" * 65)

print(
    twin.get_optimizer_input()
)


# ============================================================
# SIMULATE SALE
# ============================================================

print("\nRecording sale of 200 kg...")

twin.record_sale(
    200
)

print(
    f"Remaining harvest: "
    f"{twin.harvest.quantity_kg} kg"
)


# ============================================================
# SIMULATE TIME
# ============================================================

print("\nAdvancing time by 1 day...")

twin.advance_time(
    1
)

print(
    f"Remaining shelf life: "
    f"{twin.harvest.remaining_shelf_life_days} days"
)


# ============================================================
# FINAL STATE
# ============================================================

print("\nFINAL DIGITAL TWIN STATE")
print("-" * 65)

print(
    twin.get_state()
)


print("\n" + "=" * 65)
print("DIGITAL TWIN TEST COMPLETED")
print("=" * 65)