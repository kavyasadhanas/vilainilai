from ortools.linear_solver import pywraplp

from optimization.inputs import DestinationOption
from optimization.economics import calculate_net_price_per_kg
from optimization.risk import get_risk_adjusted_price


def optimize_allocation(
    harvest_quantity_kg: float,
    options: list[DestinationOption],
    risk_preference: str = "MEDIUM"
) -> dict:
    """
    Decide how many kg of the harvest to send to each destination
    to maximize total risk-adjusted net return.
    """

    solver = pywraplp.Solver.CreateSolver("GLOP")
    if solver is None:
        raise RuntimeError("Could not create OR-Tools solver.")

    # ------------------------------------------------------------
    # Decision variables
    # ------------------------------------------------------------
    allocation_vars = {}

    for option in options:
        upper_bound = option.capacity_kg if option.capacity_kg is not None else harvest_quantity_kg
        allocation_vars[option.id] = solver.NumVar(0, upper_bound, option.id)

    # ------------------------------------------------------------
    # Constraint: total allocated cannot exceed harvest quantity
    # ------------------------------------------------------------
    solver.Add(
        sum(allocation_vars.values()) <= harvest_quantity_kg
    )

    # ------------------------------------------------------------
    # Compute net price, then risk-adjust it, per destination
    # ------------------------------------------------------------
    net_prices = {}
    risk_adjusted_prices = {}

    for option in options:
        net_price = calculate_net_price_per_kg(option)
        net_prices[option.id] = net_price
        risk_adjusted_prices[option.id] = get_risk_adjusted_price(
            option=option,
            net_price_per_kg=net_price,
            risk_preference=risk_preference
        )

    # ------------------------------------------------------------
    # Objective: maximize total risk-adjusted return
    # ------------------------------------------------------------
    solver.Maximize(
        sum(
            allocation_vars[option.id] * risk_adjusted_prices[option.id]
            for option in options
        )
    )

    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL:
        raise RuntimeError("Optimizer did not find an optimal solution.")

    allocations = {
        option_id: round(var.solution_value(), 2)
        for option_id, var in allocation_vars.items()
    }

    details = [
        {
            "destination_id": option.id,
            "kind": option.kind,
            "days_to_realize": option.days_to_realize,
            "net_price_per_kg": net_prices[option.id],
            "risk_adjusted_price_per_kg": risk_adjusted_prices[option.id],
            "allocated_kg": allocations[option.id],
            "expected_return": round(
                allocations[option.id] * risk_adjusted_prices[option.id], 2
            )
        }
        for option in options
    ]

    return {
        "allocations": allocations,
        "total_expected_return": round(solver.Objective().Value(), 2),
        "risk_preference": risk_preference,
        "details": details
    }

from ML.digital_twin.harvest_state import HarvestState
from optimization.strategy_generator import generate_all_options


def get_optimal_strategy(
    harvest: HarvestState,
    risk_preference: str,
    market_price_list: list[dict],
    buyer_offers: list[dict],
    expected_future_price_per_kg: float = None,
    days_to_wait: int = 2
) -> dict:
    """
    THE single entry point for the rest of the team.

    Takes a farmer's harvest + risk preference + available markets/buyers,
    and returns the optimal allocation across all of them.

    This is the function Member 4 (FairDeal) and Member 5 (API) should import:
        from optimization.optimizer import get_optimal_strategy
    """
    options = generate_all_options(
        harvest=harvest,
        market_price_list=market_price_list,
        buyer_offers=buyer_offers,
        expected_future_price_per_kg=expected_future_price_per_kg,
        days_to_wait=days_to_wait
    )

    result = optimize_allocation(
        harvest_quantity_kg=harvest.quantity_kg,
        options=options,
        risk_preference=risk_preference
    )

    return result

if __name__ == "__main__":
    harvest = HarvestState(
        crop="Tomato",
        variety="Local",
        quantity_kg=500,
        quality="Grade A",
        harvest_date="2026-08-25",
        remaining_shelf_life_days=4,
        storage_capacity_kg=200,
        storage_cost_per_kg_day=0.3
    )

    market_price_list = [
        {"id": 1, "name": "Market A", "price_per_kg": 26, "transport_cost_per_kg": 1, "commission_per_kg": 0.5, "expected_loss_per_kg": 0.02},
        {"id": 2, "name": "Market B", "price_per_kg": 29, "transport_cost_per_kg": 3, "commission_per_kg": 0.5, "expected_loss_per_kg": 0.02},
    ]

    buyer_offers = [
        {"id": 7, "offered_price_per_kg": 24, "quantity_kg": 300},
    ]

    result = get_optimal_strategy(
        harvest=harvest,
        risk_preference="MEDIUM",
        market_price_list=market_price_list,
        buyer_offers=buyer_offers,
        expected_future_price_per_kg=32,
        days_to_wait=2
    )

    print("\n=== FINAL RECOMMENDATION ===")
    for d in result["details"]:
        if d["allocated_kg"] > 0:
            print(f"  {d['allocated_kg']} kg -> {d['destination_id']} ({d['kind']}) @ ₹{d['risk_adjusted_price_per_kg']}/kg")

    print(f"\nTotal expected return: ₹{result['total_expected_return']}")