import { useEffect, useState } from "react";

import {
  useSearchParams,
  useNavigate
} from "react-router-dom";

import {
  getHarvest,
  getFarmerHarvests,
  getPriceForecast,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function PriceForecast() {

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

  const [forecast, setForecast] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD SELECTED HARVEST + FORECAST
  ======================================================= */

  useEffect(() => {

    async function loadForecast() {

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
           CURRENT ML MARKET
        ------------------------------------------------- */

        /*
          The current forecasting model uses the
          Dindigul ML market for this tomato workflow.
        */

        const market =
          "Dindigul(Uzhavar Sandhai )";

        const district =
          "Dindigul";


        /* -------------------------------------------------
           GENERATE FORECAST
        ------------------------------------------------- */

        const forecastData =
          await getPriceForecast(

            market,

            district,

            selectedHarvest.variety ||
            "Deshi",

            selectedHarvest.quantity_kg

          );


        setForecast(
          forecastData
        );


      } catch (err) {

        console.error(
          "Price forecast error:",
          err
        );

        setError(
          err.message ||
          "Unable to load price forecast."
        );

      } finally {

        setLoading(false);

      }

    }


    loadForecast();

  }, [selectedHarvestId]);


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading price forecast...
          </h2>

          <p>
            The XGBoost model is generating
            the latest prediction.
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
            Unable to load forecast
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

  if (!forecast || !harvest) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            No forecast available
          </h2>

          <p>
            No prediction data was returned.
          </p>

        </div>

      </div>
    );

  }


  return (
    <div className="dashboard-page">


      {/* =================================================
          PAGE HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          Price Forecast
        </h1>

        <p>
          XGBoost-powered tomato price prediction
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
          FORECAST SUMMARY
      ================================================= */}

      <section className="stats-grid">


        {/* Crop */}

        <div className="stat-card">

          <div className="stat-icon">
            🌱
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Crop Variety
            </span>

            <span className="stat-value">

              {harvest.crop}
              {" — "}
              {forecast.variety}

            </span>

          </div>

        </div>


        {/* Market */}

        <div className="stat-card">

          <div className="stat-icon">
            📍
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Market
            </span>

            <span className="stat-value">
              {forecast.market}
            </span>

          </div>

        </div>


        {/* Quantity */}

        <div className="stat-card">

          <div className="stat-icon">
            📦
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Arrival Quantity
            </span>

            <span className="stat-value">

              {Number(
                forecast.arrival_quantity_kg ||
                harvest.quantity_kg ||
                0
              ).toLocaleString()}
              {" "}kg

            </span>

          </div>

        </div>


        {/* Model */}

        <div className="stat-card">

          <div className="stat-icon">
            🤖
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Model
            </span>

            <span className="stat-value">
              XGBoost
            </span>

          </div>

        </div>

      </section>


      {/* =================================================
          MAIN FORECAST
      ================================================= */}

      <section className="dashboard-card recommendation-card">

        <div className="recommendation-header">

          <div>

            <span className="best-choice">
              ML FORECAST
            </span>

            <h3>
              Predicted Tomato Price
            </h3>

          </div>

          <span className="recommendation-icon">
            📈
          </span>

        </div>


        <div className="expected-return">

          <span>
            Predicted Price Per Kilogram
          </span>

          <strong>
            ₹
            {Number(
              forecast.predicted_price_per_kg
            ).toFixed(2)}
          </strong>

          <p>
            Based on historical market features
            and the trained XGBoost model.
          </p>

        </div>


        <div className="recommendation-stats">


          <div>

            <span>
              Market
            </span>

            <strong>
              {forecast.market}
            </strong>

          </div>


          <div>

            <span>
              District
            </span>

            <strong>
              {forecast.district}
            </strong>

          </div>


          <div>

            <span>
              Variety
            </span>

            <strong>
              {forecast.variety}
            </strong>

          </div>


          <div>

            <span>
              Forecast Date
            </span>

            <strong>
              {forecast.prediction_date ||
                "Next available date"}
            </strong>

          </div>

        </div>


        <p className="recommendation-reason">

          The prediction is generated using
          market, district, variety, arrival
          quantity, calendar features and
          historical price features.

        </p>

      </section>


      {/* =================================================
          SELECTED HARVEST
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
              Selected Harvest
            </h2>

            <p>
              Harvest information used for this forecast.
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
              Crop
            </span>

            <strong>
              {harvest.crop}
            </strong>

          </div>


          <div>

            <span>
              Variety
            </span>

            <strong>
              {harvest.variety || "Deshi"}
            </strong>

          </div>


          <div>

            <span>
              Quantity
            </span>

            <strong>

              {Number(
                harvest.quantity_kg || 0
              ).toLocaleString()}
              {" "}kg

            </strong>

          </div>


          <div>

            <span>
              Quality
            </span>

            <strong>
              {harvest.quality || "-"}
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

        </div>

      </section>


      {/* =================================================
          FORECAST INFORMATION
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
              Forecast Information
            </h2>

            <p>
              Inputs used for this prediction.
            </p>

          </div>

        </div>


        <div className="recommendation-stats">


          <div>

            <span>
              Market Dataset
            </span>

            <strong>
              {forecast.market}
            </strong>

          </div>


          <div>

            <span>
              District
            </span>

            <strong>
              {forecast.district}
            </strong>

          </div>


          <div>

            <span>
              Variety
            </span>

            <strong>
              {forecast.variety}
            </strong>

          </div>


          <div>

            <span>
              Quantity
            </span>

            <strong>

              {Number(
                forecast.arrival_quantity_kg ||
                harvest.quantity_kg ||
                0
              ).toLocaleString()}
              {" "}kg

            </strong>

          </div>

        </div>


        {/* =============================================
            MODEL NOTE
        ============================================= */}

        <p
          className="recommendation-reason"
          style={{
            marginTop: "14px"
          }}
        >

          Forecast generated by the
          XGBoost tomato price model.

        </p>

      </section>


    </div>
  );
}


export default PriceForecast;