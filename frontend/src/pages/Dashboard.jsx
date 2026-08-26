import { useEffect, useState } from "react";

import { getFarmerDashboard } from "../services/api";

import StatCard from "../components/StatCard";
import CropOverview from "../components/CropOverview";
import RecommendationCard from "../components/RecommendationCard";
import MarketComparison from "../components/MarketComparison";
import "./Dashboard.css";

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const result = await getFarmerDashboard(1);

        setData(result);
      } catch (err) {
        console.error("Dashboard loading error:", err);
        setError(err.message || "Unable to load dashboard data.");
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  /* =========================
     LOADING STATE
  ========================= */

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-state">
          <h2>Loading your dashboard...</h2>
          <p>Please wait while we fetch your farm information.</p>
        </div>
      </div>
    );
  }

  /* =========================
     ERROR STATE
  ========================= */

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-state error-state">
          <h2>Unable to load dashboard</h2>
          <p>{error}</p>

          <button
            className="primary-button"
            onClick={() => window.location.reload()}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  /* =========================
     EMPTY STATE
  ========================= */

  if (!data) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-state">
          <h2>No dashboard data available</h2>
          <p>We couldn't find information for this farmer.</p>
        </div>
      </div>
    );
  }

  const harvest = data.harvest;
  const recommendation = data.recommendation;
  const alternatives = recommendation?.alternatives || [];

  return (
    <div className="dashboard-page">

      {/* =========================
          WELCOME SECTION
      ========================= */}

      <section className="welcome-section">
        <h1>
          Good morning, Kavya <span>👋</span>
        </h1>

        <p>
          Let's plan the best for your harvest today.
        </p>
      </section>


      {/* =========================
          STAT CARDS
      ========================= */}

      <section className="stats-grid">

        <StatCard
          icon="🌱"
          label="Active Crop"
          value={harvest?.crop || "-"}
        />

        <StatCard
          icon="⚖️"
          label="Quantity"
          value={
            harvest?.quantity_kg != null
              ? `${harvest.quantity_kg.toLocaleString()} kg`
              : "-"
          }
        />

        <StatCard
          icon="📅"
          label="Harvest Date"
          value={harvest?.harvest_date || "-"}
        />

        <StatCard
          icon="👨‍🌾"
          label="Farmer ID"
          value={data.farmer_id ?? "-"}
        />

      </section>


      {/* =========================
          MAIN DASHBOARD GRID
      ========================= */}

      <section className="dashboard-grid">

        {/* Crop Overview */}

        <CropOverview
          harvest={harvest}
        />


        {/* Recommendation */}

        <RecommendationCard
          recommendation={recommendation}
        />


        {/* Market Comparison */}

        <MarketComparison
          alternatives={alternatives}
        />


        {/* =========================
            STORE OR SELL
        ========================= */}

        <div className="dashboard-card store-card">

          <div className="card-header">
            <div>
              <h2>Store or Sell?</h2>

              <p>
                Based on current market conditions
              </p>
            </div>
          </div>


          <div className="store-content">

            <div className="store-option">
              <span>Storage Cost</span>

              <strong>
                ₹3,200
              </strong>
            </div>


            <div className="store-option">
              <span>Expected Return After Storage</span>

              <strong>
                ₹
                {recommendation?.expected_return != null
                  ? (
                      recommendation.expected_return + 1300
                    ).toLocaleString()
                  : "-"
                }
              </strong>
            </div>


            <div className="store-option">
              <span>Additional Profit</span>

              <strong className="positive">
                ₹1,300
              </strong>
            </div>


            <div className="store-option">
              <span>Spoilage Risk</span>

              <strong className="risk-medium">
                ● Medium
              </strong>
            </div>

          </div>


          <div className="store-recommendation">

            <div>
              <span>Recommendation</span>

              <strong>
                SELL NOW
              </strong>
            </div>

            <span className="recommendation-icon">
              ✓
            </span>

          </div>


          <button className="primary-button">
            View Storage Analysis
            <span>→</span>
          </button>

        </div>

      </section>


      {/* =========================
          ALERTS & UPDATES
      ========================= */}

      <section className="alerts-section">

        <div className="section-heading">
          <h2>Alerts &amp; Updates</h2>

          <button className="view-all">
            View All →
          </button>
        </div>


        <div className="alerts-grid">

          {/* Weather Alert */}

          <div className="alert-card weather-alert">

            <div className="alert-icon">
              🌧️
            </div>

            <div>
              <strong>
                Rain Alert
              </strong>

              <p>
                Moderate rain expected in the region.
                Plan your harvest accordingly.
              </p>
            </div>

          </div>


          {/* Market Alert */}

          <div className="alert-card market-alert">

            <div className="alert-icon">
              📈
            </div>

            <div>
              <strong>
                Market Trend
              </strong>

              <p>
                {harvest?.crop || "Crop"} prices are
                showing positive movement.
              </p>
            </div>

          </div>


          {/* Transport Alert */}

          <div className="alert-card transport-alert">

            <div className="alert-icon">
              🚚
            </div>

            <div>
              <strong>
                Transport Update
              </strong>

              <p>
                Transport availability is normal
                across nearby markets.
              </p>
            </div>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Dashboard;