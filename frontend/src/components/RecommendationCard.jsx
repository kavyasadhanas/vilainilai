function RecommendationCard({ recommendation }) {
  if (!recommendation) {
    return (
      <div className="dashboard-card recommendation-card">
        <div className="card-header">
          <h2>Recommended Action</h2>
        </div>

        <p className="no-data">
          No market recommendation available.
        </p>
      </div>
    );
  }

  const bestMarket = recommendation.alternatives?.[0];

  const expectedReturn =
    recommendation.expected_return != null
      ? Number(recommendation.expected_return).toLocaleString()
      : "-";

  const advantage =
    recommendation.advantage_over_next_best != null
      ? Number(
          recommendation.advantage_over_next_best
        ).toLocaleString()
      : "-";

  const marketPrice =
    bestMarket?.market_price_per_kg != null
      ? bestMarket.market_price_per_kg
      : "-";

  const transportCost =
    bestMarket?.transport_cost_per_kg != null
      ? bestMarket.transport_cost_per_kg
      : "-";

  const commission =
    Number(bestMarket?.commission_per_kg || 0);

  const expectedLoss =
    Number(bestMarket?.expected_loss_per_kg || 0);

  const otherCosts =
    (commission + expectedLoss).toFixed(2);

  const netPrice =
    bestMarket?.net_price_per_kg != null
      ? bestMarket.net_price_per_kg
      : "-";

  return (
    <div className="dashboard-card recommendation-card">

      {/* Header */}
      <div className="card-header recommendation-header">

        <div>
          <h2>Recommended Action</h2>

          <span className="best-choice">
            Best Choice
          </span>
        </div>

        <div className="recommendation-icon">
          📈
        </div>

      </div>


      {/* Recommendation */}
      <h3>
        {recommendation.recommendation || "No recommendation"}
      </h3>


      {/* Expected Return */}
      <div className="expected-return">

        <span>
          Expected Net Return
        </span>

        <strong>
          ₹{expectedReturn}
        </strong>

        <p>
          ₹{advantage} more than next best option
        </p>

      </div>


      {/* Recommendation Statistics */}
      <div className="recommendation-stats">

        <div>
          <span>
            Expected Price
          </span>

          <strong>
            ₹{marketPrice}/kg
          </strong>
        </div>


        <div>
          <span>
            Transport Cost
          </span>

          <strong>
            ₹{transportCost}/kg
          </strong>
        </div>


        <div>
          <span>
            Other Costs
          </span>

          <strong>
            ₹{otherCosts}/kg
          </strong>
        </div>


        <div>
          <span>
            Net Return
          </span>

          <strong>
            ₹{netPrice}/kg
          </strong>
        </div>

      </div>


      {/* Reason */}
      <p className="recommendation-reason">
        {recommendation.reason ||
          "This option currently provides the best expected return."}
      </p>


      {/* Button */}
      <button className="primary-button recommendation-button">
        View Full Recommendation
        <span>→</span>
      </button>

    </div>
  );
}

export default RecommendationCard;