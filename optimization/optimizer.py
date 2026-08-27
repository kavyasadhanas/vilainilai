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


if __name__ == "__main__":
    # Test: a STORE option that looks tempting on paper (higher raw price)
    # but should lose value once risk-adjusted, especially for a LOW risk farmer
    options = [
        DestinationOption(
            id="market_a", kind="MARKET",
            price_per_kg=26, transport_cost_per_kg=1, commission_per_kg=0.5
        ),
        DestinationOption(
            id="store", kind="STORE",
            price_per_kg=32, days_to_realize=3, storage_cost_per_kg_day=0.3
        ),
    ]

    print("=== LOW risk farmer ===")
    result_low = optimize_allocation(500, options, risk_preference="LOW")
    for d in result_low["details"]:
        print(d)
    print("Total:", result_low["total_expected_return"])

    print("\n=== HIGH risk farmer ===")
    result_high = optimize_allocation(500, options, risk_preference="HIGH")
    for d in result_high["details"]:
        print(d)
    print("Total:", result_high["total_expected_return"])