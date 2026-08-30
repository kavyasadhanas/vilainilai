import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

import {
  getHarvest,
  getMarketRecommendation
} from "../services/api";

import "./Dashboard.css";


function HarvestPlanner() {

  const [searchParams] =
    useSearchParams();

  const navigate =
    useNavigate();

  const harvestId =
    searchParams.get("harvest_id");


  /* =======================================================
     STATE
  ======================================================= */

  const [harvest, setHarvest] =
    useState(null);

  const [recommendation, setRecommendation] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD SELECTED HARVEST
  ======================================================= */

  useEffect(() => {

    async function loadHarvestPlanner() {

      try {

        setLoading(true);
        setError("");


        if (!harvestId) {

          throw new Error(
            "No harvest was selected. Please select a harvest from My Crops."
          );

        }


        /* -------------------------------------------------
           LOAD EXACT HARVEST
        ------------------------------------------------- */

        const harvestData =
          await getHarvest(
            harvestId
          );


        if (!harvestData) {

          throw new Error(
            "Selected harvest could not be found."
          );

        }


        setHarvest(
          harvestData
        );


        /* -------------------------------------------------
           MARKET RECOMMENDATION
        ------------------------------------------------- */

        const recommendationData =
          await getMarketRecommendation(

            harvestData.crop,

            harvestData.variety ||
            "Deshi",

            harvestData.quantity_kg

          );


        setRecommendation(
          recommendationData
        );


      } catch (err) {

        console.error(
          "Harvest Planner error:",
          err
        );

        setError(
          err.message ||
          "Unable to load harvest planning data."
        );


      } finally {

        setLoading(false);

      }

    }


    loadHarvestPlanner();

  }, [harvestId]);


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading harvest planner...
          </h2>

          <p>
            Fetching harvest information and
            market recommendation.
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
            Unable to load harvest planner
          </h2>

          <p>
            {error}
          </p>

          <button
            className="primary-button"
            onClick={() =>
              navigate("/my-crops")
            }
          >
            Go to My Crops
          </button>

        </div>

      </div>
    );

  }


  /* =======================================================
     EMPTY
  ======================================================= */

  if (!harvest) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            No harvest found
          </h2>

          <p>
            There is no harvest available
            for planning.
          </p>

          <button
            className="primary-button"
            onClick={() =>
              navigate("/my-crops")
            }
          >
            Go to My Crops
          </button>

        </div>

      </div>
    );

  }


  /* =======================================================
     DATA
  ======================================================= */

  const alternatives =
    recommendation?.alternatives || [];


  const predictedPrice =
    recommendation?.predicted_price_per_kg;


  const netPrice =
    recommendation?.net_price_per_kg;


  const expectedReturn =
    recommendation?.expected_return;


  const advantage =
    recommendation?.advantage_over_next_best;


  return (
    <div className="dashboard-page">


      {/* =================================================
          PAGE HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          Harvest Planner
        </h1>

        <p>
          Review the recommended selling strategy
          for your selected harvest.
        </p>

        <p className="fairdeal-harvest-info">

          Harvest #{harvest.id} •{" "}
          {harvest.crop} •{" "}
          {harvest.variety || "Deshi"} •{" "}
          {Number(
            harvest.quantity_kg || 0
          ).toLocaleString()} kg

        </p>

      </section>


      {/* =================================================
          HARVEST SUMMARY
      ================================================= */}

      <section className="stats-grid">


        <div className="stat-card">

          <div className="stat-icon">
            🌱
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Crop
            </span>

            <span className="stat-value">
              {harvest.crop}
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            🌾
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Variety
            </span>

            <span className="stat-value">
              {harvest.variety || "Deshi"}
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            ⚖️
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Quantity
            </span>

            <span className="stat-value">

              {Number(
                harvest.quantity_kg || 0
              ).toLocaleString()}
              {" "}kg

            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            ⭐
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Quality
            </span>

            <span className="stat-value">
              {harvest.quality || "-"}
            </span>

          </div>

        </div>

      </section>


      {/* =================================================
          HARVEST DETAILS
      ================================================= */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
              Harvest Details
            </h2>

            <p>
              Information recorded for this harvest.
            </p>

          </div>

        </div>


        <div className="recommendation-stats">


          <div>

            <span>
              Harvest ID
            </span>

            <strong>
              #{harvest.id}
            </strong>

          </div>


          <div>

            <span>
              Harvest Date
            </span>

            <strong>
              {harvest.harvest_date || "-"}
            </strong>

          </div>


          <div>

            <span>
              Shelf Life
            </span>

            <strong>

              {harvest.shelf_life_days != null
                ? `${harvest.shelf_life_days} days`
                : "-"
              }

            </strong>

          </div>


          <div>

            <span>
              Farmer ID
            </span>

            <strong>
              {harvest.farmer_id || "-"}
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          RECOMMENDED MARKET
      ================================================= */}

      {recommendation && (

        <section
          className="dashboard-card recommendation-card"
          style={{
            marginTop: "18px"
          }}
        >

          <div className="recommendation-header">

            <div>

              <span className="best-choice">
                RECOMMENDED MARKET
              </span>

              <h3>
                {recommendation.recommended_market_name}
              </h3>

            </div>

            <span className="recommendation-icon">
              📍
            </span>

          </div>


          <div className="recommendation-stats">


            <div>

              <span>
                Predicted Price
              </span>

              <strong>

                ₹
                {predictedPrice != null
                  ? Number(
                      predictedPrice
                    ).toFixed(2)
                  : "-"
                }
                /kg

              </strong>

            </div>


            <div>

              <span>
                Net Price
              </span>

              <strong>

                ₹
                {netPrice != null
                  ? Number(
                      netPrice
                    ).toFixed(2)
                  : "-"
                }
                /kg

              </strong>

            </div>


            <div>

              <span>
                Expected Return
              </span>

              <strong>

                ₹
                {expectedReturn != null
                  ? Number(
                      expectedReturn
                    ).toLocaleString()
                  : "-"
                }

              </strong>

            </div>


            <div>

              <span>
                Advantage
              </span>

              <strong>

                ₹
                {advantage != null
                  ? Number(
                      advantage
                    ).toLocaleString()
                  : "0"
                }

              </strong>

            </div>

          </div>


          <p className="recommendation-reason">
            {recommendation.reason}
          </p>

        </section>

      )}


      {/* =================================================
          MARKET COMPARISON
      ================================================= */}

      {alternatives.length > 0 && (

        <section
          className="dashboard-card"
          style={{
            marginTop: "18px"
          }}
        >

          <div className="card-header">

            <div>

              <h2>
                Market Comparison
              </h2>

              <p>
                Compare the available destinations
                for this harvest.
              </p>

            </div>

          </div>


          <div className="buyer-offer-list">

            {alternatives.map(
              (market) => {

                const isBest =
                  market.market_id ===
                  recommendation.recommended_market_id;


                return (

                  <div
                    className="buyer-offer"
                    key={
                      market.market_id
                    }
                  >


                    {/* MARKET */}

                    <div>

                      <strong>
                        {market.market_name}
                      </strong>

                      <span>
                        {market.district || "-"}
                      </span>

                      {isBest && (

                        <span className="best-choice">
                          BEST
                        </span>

                      )}

                    </div>


                    {/* PRICE */}

                    <div>

                      <strong>

                        ₹
                        {Number(
                          market.predicted_price_per_kg
                        ).toFixed(2)}
                        /kg

                      </strong>

                      <span>
                        Predicted
                      </span>

                    </div>


                    {/* NET */}

                    <div>

                      <strong>

                        ₹
                        {Number(
                          market.net_price_per_kg
                        ).toFixed(2)}
                        /kg

                      </strong>

                      <span>
                        Net price
                      </span>

                    </div>


                    {/* RETURN */}

                    <div>

                      <strong>

                        ₹
                        {Number(
                          market.expected_return
                        ).toLocaleString()}

                      </strong>

                      <span>
                        Expected return
                      </span>

                    </div>

                  </div>

                );

              }
            )}

          </div>

        </section>

      )}


      {/* =================================================
          NEXT DECISION
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
              Decision Tools
            </h2>

            <p>
              Explore detailed analysis for this harvest.
            </p>

          </div>

        </div>


        <div className="decision-tools-grid">


          <button
            className="decision-tool-card"
            onClick={() =>
              navigate(
                `/storage-planner?harvest_id=${harvest.id}`
              )
            }
          >

            <span className="decision-tool-icon">
              🏠
            </span>

            <span>

              <strong>
                Storage
              </strong>

              <small>
                Compare selling now vs storage
              </small>

            </span>

            <span className="decision-tool-arrow">
              →
            </span>

          </button>


          <button
            className="decision-tool-card"
            onClick={() =>
              navigate(
                `/what-if?harvest_id=${harvest.id}`
              )
            }
          >

            <span className="decision-tool-icon">
              🔄
            </span>

            <span>

              <strong>
                What-If
              </strong>

              <small>
                Test different market conditions
              </small>

            </span>

            <span className="decision-tool-arrow">
              →
            </span>

          </button>


          <button
            className="decision-tool-card"
            onClick={() =>
              navigate(
                `/map?harvest_id=${harvest.id}`
              )
            }
          >

            <span className="decision-tool-icon">
              📍
            </span>

            <span>

              <strong>
                Market Map
              </strong>

              <small>
                View distance and transport costs
              </small>

            </span>

            <span className="decision-tool-arrow">
              →
            </span>

          </button>


          <button
            className="decision-tool-card"
            onClick={() =>
              navigate("/fairdeal")
            }
          >

            <span className="decision-tool-icon">
              🤝
            </span>

            <span>

              <strong>
                FairDeal
              </strong>

              <small>
                Review buyer negotiation options
              </small>

            </span>

            <span className="decision-tool-arrow">
              →
            </span>

          </button>

        </div>

      </section>


    </div>
  );
}


export default HarvestPlanner;