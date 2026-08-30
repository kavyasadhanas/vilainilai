import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getFarmerHistory,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function History() {

  const navigate =
    useNavigate();


  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD HISTORY
  ======================================================= */

  useEffect(() => {

    async function loadHistory() {

      try {

        setLoading(true);
        setError("");

        const result =
          await getFarmerHistory(
            CURRENT_FARMER_ID
          );

        setData(
          result
        );

      } catch (err) {

        console.error(
          "History loading error:",
          err
        );

        setError(
          err.message ||
          "Unable to load history."
        );

      } finally {

        setLoading(false);

      }

    }


    loadHistory();

  }, []);


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading history...
          </h2>

          <p>
            Fetching your previous decisions.
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     ERROR
  ======================================================= */

  if (error) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state error-state">

          <h2>
            Unable to load history
          </h2>

          <p>
            {error}
          </p>

        </div>

      </div>
    );

  }


  if (!data) {
    return null;
  }


  /* =======================================================
     HISTORY DATA
  ======================================================= */

  const history =
    Array.isArray(data.history)
      ? data.history
      : [];


  /* =======================================================
     SUMMARY
  ======================================================= */

  const totalQuantity =
    history.reduce(
      (total, item) =>
        total +
        Number(
          item.quantity_kg || 0
        ),
      0
    );


  const recordedDecisions =
    history.filter(
      item =>
        item.recommendation_id !== null
    ).length;


  const totalExpectedReturn =
    history.reduce(
      (total, item) =>
        total +
        Number(
          item.expected_return || 0
        ),
      0
    );


  return (
    <div className="dashboard-page">


      {/* =================================================
          HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          History
        </h1>

        <p>
          Review your previous harvests and
          decision records.
        </p>

      </section>


      {/* =================================================
          SUMMARY
      ================================================= */}

      <section className="stats-grid">


        <div className="stat-card">

          <div className="stat-icon">
            🌱
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Harvest Records
            </span>

            <span className="stat-value">
              {history.length}
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            📦
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Total Harvested
            </span>

            <span className="stat-value">
              {totalQuantity.toLocaleString()} kg
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            📋
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Recorded Decisions
            </span>

            <span className="stat-value">
              {recordedDecisions}
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            💰
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Recorded Expected Return
            </span>

            <span className="stat-value">
              ₹
              {totalExpectedReturn.toLocaleString()}
            </span>

          </div>

        </div>

      </section>


      {/* =================================================
          HISTORY
      ================================================= */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
              Decision History
            </h2>

            <p>
              Previous harvest decisions and
              supporting analysis.
            </p>

          </div>

        </div>


        {history.length === 0 ? (

          <div className="dashboard-state">

            <h2>
              No history available
            </h2>

            <p>
              Your harvest and decision history
              will appear here.
            </p>

            <button
              className="primary-button"
              onClick={() =>
                navigate("/dashboard")
              }
            >
              Add Harvest
            </button>

          </div>

        ) : (

          <div className="history-list">

            {history.map(
              (item) => {

                const optimization =
                  item.optimization;

                const fairdeal =
                  item.fairdeal;

                const storage =
                  optimization?.storage;

                const allocations =
                  optimization?.allocations || {};


                return (

                  <article
                    className="history-item"
                    key={
                      item.harvest_id
                    }
                  >


                    {/* =================================
                        HEADER
                    ================================= */}

                    <div className="history-item-header">

                      <div>

                        <span className="best-choice">
                          HARVEST #{item.harvest_id}
                        </span>

                        <h3>

                          {item.crop}
                          {" — "}
                          {item.variety}

                        </h3>

                        <p>
                          Harvested on{" "}
                          {item.harvest_date}
                        </p>

                      </div>


                      <div className="history-action">

                        <strong>
                          {item.action ||
                            "Not recorded"}
                        </strong>

                      </div>

                    </div>


                    {/* =================================
                        HARVEST INFORMATION
                    ================================= */}

                    <div className="history-info-grid">


                      <div>

                        <span>
                          Quantity
                        </span>

                        <strong>

                          {Number(
                            item.quantity_kg || 0
                          ).toLocaleString()}
                          {" "}kg

                        </strong>

                      </div>


                      <div>

                        <span>
                          Quality
                        </span>

                        <strong>
                          {item.quality || "-"}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Shelf Life
                        </span>

                        <strong>

                          {item.shelf_life_days != null
                            ? `${item.shelf_life_days} days`
                            : "-"
                          }

                        </strong>

                      </div>


                      <div>

                        <span>
                          Decision
                        </span>

                        <strong>
                          {item.action ||
                            "Not recorded"}
                        </strong>

                      </div>

                    </div>


                    {/* =================================
                        MARKET DECISION
                    ================================= */}

                    {item.recommendation_id && (

                      <div className="history-section">

                        <h4>
                          Market Decision
                        </h4>

                        <div className="history-analysis-grid">


                          <div>

                            <span>
                              Destination
                            </span>

                            <strong>
                              {item.destination || "-"}
                            </strong>

                          </div>


                          <div>

                            <span>
                              Predicted Price
                            </span>

                            <strong>

                              ₹
                              {Number(
                                item.predicted_price_per_kg || 0
                              ).toFixed(2)}
                              /kg

                            </strong>

                          </div>


                          <div>

                            <span>
                              Net Price
                            </span>

                            <strong>

                              ₹
                              {Number(
                                item.net_price_per_kg || 0
                              ).toFixed(2)}
                              /kg

                            </strong>

                          </div>


                          <div>

                            <span>
                              Expected Return
                            </span>

                            <strong>

                              ₹
                              {Number(
                                item.expected_return || 0
                              ).toLocaleString()}

                            </strong>

                          </div>

                        </div>

                      </div>

                    )}


                    {/* =================================
                        OPTIMIZATION
                    ================================= */}

                    {optimization && (

                      <div className="history-section">

                        <h4>
                          Optimization
                        </h4>

                        <div className="history-analysis-grid">


                          <div>

                            <span>
                              Risk Preference
                            </span>

                            <strong>
                              {optimization.risk_preference || "-"}
                            </strong>

                          </div>


                          <div>

                            <span>
                              Optimized Return
                            </span>

                            <strong>

                              ₹
                              {Number(
                                optimization.total_expected_return || 0
                              ).toLocaleString()}

                            </strong>

                          </div>


                          <div>

                            <span>
                              Market Allocation
                            </span>

                            <strong>

                              {Number(
                                allocations.market_1 || 0
                              ).toLocaleString()}
                              {" "}kg

                            </strong>

                          </div>


                          <div>

                            <span>
                              Storage Allocation
                            </span>

                            <strong>

                              {Number(
                                allocations.store || 0
                              ).toLocaleString()}
                              {" "}kg

                            </strong>

                          </div>

                        </div>


                        {storage && (

                          <div className="history-mini-grid">


                            <div>

                              <span>
                                Future Price
                              </span>

                              <strong>

                                ₹
                                {Number(
                                  storage.expected_future_price_per_kg || 0
                                ).toFixed(2)}
                                /kg

                              </strong>

                            </div>


                            <div>

                              <span>
                                Storage Capacity
                              </span>

                              <strong>

                                {Number(
                                  storage.storage_capacity_kg || 0
                                ).toLocaleString()}
                                {" "}kg

                              </strong>

                            </div>


                            <div>

                              <span>
                                Storage Period
                              </span>

                              <strong>

                                {storage.days_to_wait || 0}
                                {" "}days

                              </strong>

                            </div>

                          </div>

                        )}

                      </div>

                    )}


                    {/* =================================
                        FAIRDEAL
                    ================================= */}

                    {fairdeal && (

                      <div className="history-section">

                        <h4>
                          FairDeal
                        </h4>

                        <div className="history-analysis-grid">


                          <div>

                            <span>
                              Best Alternative
                            </span>

                            <strong>
                              {fairdeal.best_alternative || "-"}
                            </strong>

                          </div>


                          <div>

                            <span>
                              Risk Preference
                            </span>

                            <strong>
                              {fairdeal.risk_preference || "-"}
                            </strong>

                          </div>


                          <div>

                            <span>
                              Reservation Price
                            </span>

                            <strong>

                              ₹
                              {Number(
                                fairdeal.reservation_price || 0
                              ).toFixed(2)}
                              /kg

                            </strong>

                          </div>


                          <div>

                            <span>
                              Buyer Offers
                            </span>

                            <strong>

                              {fairdeal.buyer_offers?.length || 0}

                            </strong>

                          </div>

                        </div>

                      </div>

                    )}


                    {/* =================================
                        EXPLANATION
                    ================================= */}

                    {item.explanation && (

                      <div className="market-insight">

                        <div className="insight-icon">
                          💡
                        </div>

                        <div>

                          <strong>
                            Why this decision?
                          </strong>

                          <p>
                            {item.explanation}
                          </p>

                        </div>

                      </div>

                    )}


                    {!item.recommendation_id && (

                      <div className="fairdeal-empty">

                        <strong>
                          No decision recorded
                        </strong>

                        <p>
                          This harvest has been stored
                          in the system, but no finalized
                          recommendation has been recorded.
                        </p>

                      </div>

                    )}

                  </article>

                );

              }
            )}

          </div>

        )}

      </section>

    </div>
  );
}


export default History;