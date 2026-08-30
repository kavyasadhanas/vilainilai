import { useEffect, useState } from "react";

import {
  getFarmerDashboard,
  getStorageAnalysis,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function Alerts() {

  const [dashboard, setDashboard] =
    useState(null);

  const [storage, setStorage] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD ALERT DATA
  ======================================================= */

  useEffect(() => {

    async function loadAlerts() {

      try {

        setLoading(true);
        setError("");

        const [
          dashboardData,
          storageData
        ] = await Promise.all([

          getFarmerDashboard(
            CURRENT_FARMER_ID
          ),

          getStorageAnalysis(
            CURRENT_FARMER_ID
          )

        ]);

        setDashboard(
          dashboardData
        );

        setStorage(
          storageData
        );

      } catch (err) {

        console.error(
          "Alerts loading error:",
          err
        );

        setError(
          err.message ||
          "Unable to load alerts."
        );

      } finally {

        setLoading(false);

      }

    }

    loadAlerts();

  }, []);


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading alerts...
          </h2>

          <p>
            Checking your latest farm decisions
            and important updates.
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
            Unable to load alerts
          </h2>

          <p>
            {error}
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     DATA
  ======================================================= */

  const harvest =
    dashboard?.harvest || null;

  const recommendation =
    dashboard?.recommendation || null;

  const optimization =
    dashboard?.optimization || null;

  const fairdeal =
    dashboard?.fairdeal || null;


  const buyerOffers =
    fairdeal?.buyer_offers || [];


  const pendingOffers =
    buyerOffers.filter(
      (offer) =>
        offer.decision !== "ACCEPT" &&
        offer.decision !== "REJECT"
    );


  const acceptedOffers =
    buyerOffers.filter(
      (offer) =>
        offer.decision === "ACCEPT"
    );


  const rejectedOffers =
    buyerOffers.filter(
      (offer) =>
        offer.decision === "REJECT"
    );


  /* =======================================================
     HARVEST
  ======================================================= */

  const shelfLife =
    Number(
      harvest?.shelf_life_days || 0
    );


  const harvestAlertMessage =
    shelfLife <= 2
      ? `Only ${shelfLife} days of shelf life remain. Consider selling immediately.`
      : shelfLife <= 5
        ? `${shelfLife} days of shelf life remain. Monitor your selling decision closely.`
        : `${shelfLife} days of shelf life are available.`;


  /* =======================================================
     PRICE
  ======================================================= */

  const predictedPrice =
    recommendation
      ? Number(
          recommendation.predicted_price_per_kg || 0
        )
      : null;


  const netPrice =
    recommendation
      ? Number(
          recommendation.net_price_per_kg || 0
        )
      : null;


  /* =======================================================
     OPTIMIZATION
  ======================================================= */

  const totalExpectedReturn =
    Number(
      optimization?.total_expected_return || 0
    );


  const marketAllocation =
    Number(
      storage?.allocated_to_markets_kg || 0
    );


  const buyerAllocation =
    Number(
      storage?.allocated_to_buyers_kg || 0
    );


  const storageAllocation =
    Number(
      storage?.allocated_to_storage_kg || 0
    );


  /* =======================================================
     PAGE
  ======================================================= */

  return (
    <div className="dashboard-page">


      {/* =================================================
          HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          Alerts &amp; Updates
        </h1>

        <p>
          Important updates and decision alerts
          for your farm.
        </p>

        {harvest && (

          <p className="fairdeal-harvest-info">

            Harvest #{harvest.id} •{" "}
            {harvest.crop} •{" "}
            {harvest.variety || "Deshi"} •{" "}
            {Number(
              harvest.quantity_kg || 0
            ).toLocaleString()} kg

          </p>

        )}

      </section>


      {/* =================================================
          IMPORTANT ALERTS
      ================================================= */}

      <section className="dashboard-card alerts-panel">

        <div className="card-header">

          <div>

            <h2>
              Important Alerts
            </h2>

            <p>
              Current alerts based on your farm data.
            </p>

          </div>

        </div>


        <div className="alert-list">


          {/* HARVEST */}

          <div className="alert-list-item">

            <div className="alert-icon">
              ⏳
            </div>

            <div className="alert-list-content">

              <strong>
                Harvest Alert
              </strong>

              <p>
                {harvest
                  ? harvestAlertMessage
                  : "No harvest information is available."
                }
              </p>

            </div>

          </div>


          {/* PRICE */}

          <div className="alert-list-item">

            <div className="alert-icon">
              📈
            </div>

            <div className="alert-list-content">

              <strong>
                Market Price
              </strong>

              <p>

                {recommendation
                  ? (
                    <>
                      Predicted price:
                      {" "}
                      ₹
                      {predictedPrice.toFixed(2)}
                      /kg
                      {" • "}
                      Net:
                      {" "}
                      ₹
                      {netPrice.toFixed(2)}
                      /kg
                    </>
                  )
                  : (
                    "Market price information is unavailable."
                  )
                }

              </p>

            </div>

          </div>


          {/* SELLING */}

          <div className="alert-list-item">

            <div className="alert-icon">
              🚚
            </div>

            <div className="alert-list-content">

              <strong>
                Selling Strategy
              </strong>

              <p>

                {recommendation
                  ? (
                    <>
                      Recommended destination:
                      {" "}
                      {recommendation.recommended_market_name}
                    </>
                  )
                  : (
                    "Selling strategy is unavailable."
                  )
                }

              </p>

            </div>

          </div>


          {/* STORAGE */}

          <div className="alert-list-item">

            <div className="alert-icon">
              🏠
            </div>

            <div className="alert-list-content">

              <strong>
                Storage Decision
              </strong>

              <p>

                {storage
                  ? (
                    <>
                      Current strategy:
                      {" "}
                      <strong>
                        {storage.decision}
                      </strong>
                      {" • "}
                      Storage:
                      {" "}
                      {storageAllocation.toLocaleString()}
                      {" "}kg
                    </>
                  )
                  : (
                    "Storage analysis is unavailable."
                  )
                }

              </p>

            </div>

          </div>


        </div>

      </section>


      {/* =================================================
          DECISION INTELLIGENCE
      ================================================= */}

      <section
        className="dashboard-card"
        style={{
          marginTop: "18px"
        }}
      >

        <div className="card-header">

          <div>

            <h2>
              Decision Intelligence
            </h2>

            <p>
              Signals from the current decision pipeline.
            </p>

          </div>

        </div>


        <div className="alerts-grid">


          {/* BEST MARKET */}

          <div className="alert-card">

            <div className="alert-icon">
              🟢
            </div>

            <div>

              <strong>
                Best Market
              </strong>

              <p>

                {recommendation
                  ? (
                    <>
                      {recommendation.recommended_market_name}
                      {" "}with expected return of ₹
                      {Number(
                        recommendation.expected_return || 0
                      ).toLocaleString()}.
                    </>
                  )
                  : (
                    "Market recommendation is unavailable."
                  )
                }

              </p>

            </div>

          </div>


          {/* OPTIMIZATION */}

          <div className="alert-card">

            <div className="alert-icon">
              🎯
            </div>

            <div>

              <strong>
                Optimization
              </strong>

              <p>

                {optimization
                  ? (
                    <>
                      Expected return:
                      {" "}
                      ₹
                      {totalExpectedReturn.toLocaleString()}.
                      {" "}
                      {marketAllocation.toLocaleString()}
                      kg to markets and
                      {" "}
                      {buyerAllocation.toLocaleString()}
                      kg to buyers.
                    </>
                  )
                  : (
                    "Optimization result is unavailable."
                  )
                }

              </p>

            </div>

          </div>


          {/* FAIRDEAL */}

          <div className="alert-card">

            <div className="alert-icon">
              🤝
            </div>

            <div>

              <strong>
                FairDeal
              </strong>

              <p>

                {fairdeal
                  ? (
                    <>
                      Reservation price:
                      {" "}
                      ₹
                      {Number(
                        fairdeal.reservation_price || 0
                      ).toFixed(2)}
                      /kg.
                      {" "}
                      Best alternative:
                      {" "}
                      {fairdeal.best_alternative || "-"}.
                    </>
                  )
                  : (
                    "FairDeal information is unavailable."
                  )
                }

              </p>

            </div>

          </div>


          {/* BUYERS */}

          <div className="alert-card">

            <div className="alert-icon">
              💬
            </div>

            <div>

              <strong>
                Buyer Offers
              </strong>

              <p>

                {buyerOffers.length === 0
                  ? "No buyer offers are currently available."
                  : (
                    <>
                      {buyerOffers.length} offer
                      {buyerOffers.length !== 1
                        ? "s"
                        : ""
                      }:
                      {" "}
                      {acceptedOffers.length} accepted,
                      {" "}
                      {pendingOffers.length} pending/negotiating,
                      {" "}
                      {rejectedOffers.length} rejected.
                    </>
                  )
                }

              </p>

            </div>

          </div>


        </div>

      </section>


      {/* =================================================
          BUYER OFFER DETAILS
      ================================================= */}

      {buyerOffers.length > 0 && (

        <section
          className="dashboard-card"
          style={{
            marginTop: "18px"
          }}
        >

          <div className="card-header">

            <div>

              <h2>
                Buyer Offer Alerts
              </h2>

              <p>
                Current FairDeal evaluation of buyer offers.
              </p>

            </div>

          </div>


          <div className="buyer-offer-list">

            {buyerOffers.map(
              (offer) => (

                <div
                  className="buyer-offer"
                  key={
                    offer.buyer_offer_id
                  }
                >

                  {/* BUYER */}

                  <div>

                    <strong>
                      {offer.buyer_name ||
                        `Buyer #${offer.buyer_id}`}
                    </strong>

                    <span>
                      Offer #{offer.buyer_offer_id}
                    </span>

                  </div>


                  {/* OFFER */}

                  <div>

                    <strong>

                      ₹
                      {Number(
                        offer.offer_price || 0
                      ).toFixed(2)}
                      /kg

                    </strong>

                    <span>

                      {Number(
                        offer.offered_quantity_kg || 0
                      ).toLocaleString()}
                      {" "}kg

                    </span>

                  </div>


                  {/* DECISION */}

                  <div>

                    <strong>

                      {offer.decision === "ACCEPT"
                        ? "✓ ACCEPT"
                        : offer.decision === "NEGOTIATE"
                          ? "↔ NEGOTIATE"
                          : "✕ REJECT"
                      }

                    </strong>

                    <span>

                      Reservation ₹
                      {Number(
                        offer.reservation_price || 0
                      ).toFixed(2)}
                      /kg

                    </span>

                  </div>


                  {/* DIFFERENCE */}

                  <div>

                    <span>
                      Difference
                    </span>

                    <strong>

                      {offer.price_difference >= 0
                        ? "+"
                        : ""
                      }

                      ₹
                      {Number(
                        offer.price_difference || 0
                      ).toFixed(2)}
                      /kg

                    </strong>

                  </div>

                </div>

              )
            )}

          </div>

        </section>

      )}


      {/* =================================================
          WEATHER
      ================================================= */}

      <section
        className="dashboard-card"
        style={{
          marginTop: "18px"
        }}
      >

        <div className="market-insight">

          <div className="insight-icon">
            🌦️
          </div>

          <div>

            <strong>
              Weather Alerts
            </strong>

            <p>
              Weather-based alerts are currently
              prepared for integration. The current
              alert system does not retrieve live
              weather data.
            </p>

          </div>

        </div>

      </section>


    </div>
  );
}


export default Alerts;