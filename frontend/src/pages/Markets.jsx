import { useEffect, useState } from "react";
import {
  useSearchParams,
  useNavigate
} from "react-router-dom";

import {
  getHarvest,
  getFarmerHarvests,
  getMarketRecommendation,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function Markets() {

  const [searchParams] =
    useSearchParams();

  const navigate =
    useNavigate();


  const selectedHarvestId =
    searchParams.get("harvest_id");


  /* =======================================================
     STATE
  ======================================================= */

  const [harvest, setHarvest] =
    useState(null);

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD HARVEST + MARKET RECOMMENDATION
  ======================================================= */

  useEffect(() => {

    async function loadMarkets() {

      try {

        setLoading(true);
        setError("");


        let selectedHarvest;


        /* -------------------------------------------------
           SELECTED HARVEST
        ------------------------------------------------- */

        if (selectedHarvestId) {

          selectedHarvest =
            await getHarvest(
              selectedHarvestId
            );

        } else {

          const harvests =
            await getFarmerHarvests(
              CURRENT_FARMER_ID
            );


          if (
            !Array.isArray(harvests) ||
            harvests.length === 0
          ) {

            throw new Error(
              "No harvest records found for this farmer."
            );

          }


          selectedHarvest =
            harvests[0];

        }


        if (!selectedHarvest) {

          throw new Error(
            "Unable to determine the selected harvest."
          );

        }


        setHarvest(
          selectedHarvest
        );


        /* -------------------------------------------------
           MARKET RECOMMENDATION
        ------------------------------------------------- */

        const recommendation =
          await getMarketRecommendation(

            selectedHarvest.crop,

            selectedHarvest.variety ||
            "Deshi",

            selectedHarvest.quantity_kg

          );


        setData(
          recommendation
        );


      } catch (err) {

        console.error(
          "Market loading error:",
          err
        );

        setError(
          err.message ||
          "Unable to load market data."
        );


      } finally {

        setLoading(false);

      }

    }


    loadMarkets();

  }, [selectedHarvestId]);


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading market information...
          </h2>

          <p>
            Calculating market prices and
            expected returns.
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
            Unable to load markets
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

  if (!data || !harvest) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            No market data available
          </h2>

          <p>
            There is no harvest available for
            market analysis.
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     DATA
  ======================================================= */

  const alternatives =
    data.alternatives || [];


  return (
    <div className="dashboard-page">


      {/* =================================================
          PAGE HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          Market Comparison
        </h1>

        <p>
          Compare predicted prices and expected
          returns for your selected harvest.
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
            📦
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
          BEST MARKET
      ================================================= */}

      <section
        className="dashboard-card recommendation-card"
      >

        <div className="recommendation-header">

          <div>

            <span className="best-choice">
              BEST MARKET
            </span>

            <h3>
              {data.recommended_market_name}
            </h3>

          </div>

          <span className="recommendation-icon">
            ✓
          </span>

        </div>


        <div className="recommendation-stats">


          <div>

            <span>
              Predicted Price
            </span>

            <strong>

              ₹
              {Number(
                data.predicted_price_per_kg
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
                data.net_price_per_kg
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
                data.expected_return
              ).toLocaleString()}

            </strong>

          </div>


          <div>

            <span>
              Advantage
            </span>

            <strong>

              ₹
              {Number(
                data.advantage_over_next_best || 0
              ).toLocaleString()}

            </strong>

          </div>

        </div>


        <p className="recommendation-reason">
          {data.reason}
        </p>

      </section>


      {/* =================================================
          AVAILABLE MARKETS
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
              Available Markets
            </h2>

            <p>
              ML-predicted prices, costs and
              estimated net returns.
            </p>

          </div>

        </div>


        {alternatives.length === 0 ? (

          <div className="dashboard-state">

            <h2>
              No market alternatives
            </h2>

            <p>
              No market comparison data is
              available for this harvest.
            </p>

          </div>

        ) : (

          <div className="market-table">


            {/* =============================================
                TABLE HEADER
            ============================================= */}

            <div className="market-table-header">

              <span>
                Market
              </span>

              <span>
                District
              </span>

              <span>
                Predicted
              </span>

              <span>
                Net/kg
              </span>

              <span>
                Return
              </span>

            </div>


            {/* =============================================
                MARKET ROWS
            ============================================= */}

            {alternatives.map(
              (market) => {

                const isBest =
                  market.market_id ===
                  data.recommended_market_id;


                return (

                  <div
                    key={
                      market.market_id
                    }
                    className={
                      isBest
                        ? "market-row best-market"
                        : "market-row"
                    }
                  >


                    {/* MARKET */}

                    <div>

                      <strong>
                        {market.market_name}
                      </strong>

                      {isBest && (

                        <span
                          className="best-choice"
                          style={{
                            display: "inline-flex",
                            marginTop: "4px"
                          }}
                        >
                          BEST
                        </span>

                      )}

                    </div>


                    {/* DISTRICT */}

                    <span>
                      {market.district || "-"}
                    </span>


                    {/* PREDICTED */}

                    <span>

                      ₹
                      {Number(
                        market.predicted_price_per_kg
                      ).toFixed(2)}

                    </span>


                    {/* NET */}

                    <span>

                      ₹
                      {Number(
                        market.net_price_per_kg
                      ).toFixed(2)}

                    </span>


                    {/* RETURN */}

                    <strong>

                      ₹
                      {Number(
                        market.expected_return
                      ).toLocaleString()}

                    </strong>

                  </div>

                );

              }
            )}

          </div>

        )}

      </section>


      {/* =================================================
          COST & RETURN BREAKDOWN
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
              Cost &amp; Return Breakdown
            </h2>

            <p>
              Costs considered before calculating
              your expected net return.
            </p>

          </div>

        </div>


        <div className="buyer-offer-list">

          {alternatives.map(
            (market) => (

              <div
                className="buyer-offer"
                key={
                  `cost-${market.market_id}`
                }
              >


                {/* MARKET */}

                <div>

                  <strong>
                    {market.market_name}
                  </strong>

                  <span>
                    Transport
                  </span>

                  <span>
                    Commission
                  </span>

                </div>


                {/* COSTS */}

                <div>

                  <strong>

                    ₹
                    {Number(
                      market.transport_cost_per_kg || 0
                    ).toFixed(2)}
                    /kg

                  </strong>

                  <span>

                    ₹
                    {Number(
                      market.commission_per_kg || 0
                    ).toFixed(2)}
                    /kg

                  </span>

                </div>


                {/* LOSS */}

                <div>

                  <strong>

                    ₹
                    {Number(
                      market.expected_loss_per_kg || 0
                    ).toFixed(2)}
                    /kg

                  </strong>

                  <span>
                    Expected loss
                  </span>

                </div>


                {/* NET PRICE */}

                <div>

                  <strong>

                    ₹
                    {Number(
                      market.net_price_per_kg || 0
                    ).toFixed(2)}
                    /kg

                  </strong>

                  <span>
                    Net price
                  </span>

                </div>

              </div>

            )
          )}

        </div>

      </section>


    </div>
  );
}


export default Markets;