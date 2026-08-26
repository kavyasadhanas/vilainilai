function MarketComparison({ alternatives }) {
  if (!alternatives || alternatives.length === 0) {
    return (
      <div className="dashboard-card market-comparison">
        <div className="card-header">
          <div>
            <h2>Where Should You Sell?</h2>
            <p>Compare markets and choose the best return</p>
          </div>
        </div>

        <p className="no-data">
          No market data available.
        </p>
      </div>
    );
  }

  const bestMarket = alternatives[0];

  return (
    <div className="dashboard-card market-comparison">

      {/* Header */}
      <div className="card-header">
        <div>
          <h2>Where Should You Sell?</h2>

          <p>
            Compare markets and choose the best return
          </p>
        </div>
      </div>

      {/* Market Table */}
      <div className="market-table">

        {/* Table Header */}
        <div className="market-table-header">
          <span>Market</span>
          <span>Price (₹)</span>
          <span>Transport (₹)</span>
          <span>Net Return (₹)</span>
        </div>

        {/* Market Rows */}
        {alternatives.map((market, index) => {
          const marketPrice =
            market.market_price_per_kg != null
              ? market.market_price_per_kg
              : "-";

          const transportCost =
            market.transport_cost_per_kg != null
              ? market.transport_cost_per_kg
              : "-";

          const expectedReturn =
            market.expected_return != null
              ? Number(
                  market.expected_return
                ).toLocaleString()
              : "-";

          return (
            <div
              className={`market-row ${
                index === 0 ? "best-market" : ""
              }`}
              key={
                market.market_id ??
                `${market.market_name}-${index}`
              }
            >
              <strong>
                {market.market_name || "Unknown Market"}
              </strong>

              <span>
                ₹{marketPrice}
              </span>

              <span>
                ₹{transportCost}
              </span>

              <span>
                ₹{expectedReturn}
              </span>
            </div>
          );
        })}
      </div>

      {/* Best Market Insight */}
      <div className="market-insight">
        <span className="insight-icon">
          ↗
        </span>

        <div>
          <strong>
            {bestMarket.market_name ||
              "Best available market"}
          </strong>

          <p>
            gives you the highest net return
            among the available markets.
          </p>
        </div>
      </div>

    </div>
  );
}

export default MarketComparison;