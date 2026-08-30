import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getFarmerDashboard,
  getFarmer,
  updateFarmer,
  createHarvest,
  getMarketRecommendation,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function Dashboard() {

  const navigate =
    useNavigate();


  /* =======================================================
     EXISTING DASHBOARD DATA
  ======================================================= */

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =======================================================
     FORM STATE
  ======================================================= */

  const [crop, setCrop] =
    useState("Tomato");

  const [variety, setVariety] =
    useState("Deshi");

  const [quantity, setQuantity] =
    useState("");

  const [location, setLocation] =
    useState("Dindigul, Tamil Nadu");

  const [harvestDate, setHarvestDate] =
    useState("");

  const [quality, setQuality] =
    useState("Grade A");

  const [storageFacility, setStorageFacility] =
    useState("Available");

  /*
    NEW:
    Farmer-entered physical storage capacity.
  */
  const [storageCapacity, setStorageCapacity] =
    useState("");

  const [riskPreference, setRiskPreference] =
    useState("MEDIUM");


  /* =======================================================
     ANALYSIS STATE
  ======================================================= */

  const [analysisResult, setAnalysisResult] =
    useState(null);

  const [analyzing, setAnalyzing] =
    useState(false);

  const [analysisError, setAnalysisError] =
    useState("");


  /* =======================================================
     LOAD DASHBOARD DATA
  ======================================================= */

  useEffect(() => {

    async function loadDashboard() {

      try {

        setLoading(true);
        setError("");


        const [
          dashboardResult,
          farmerResult
        ] = await Promise.all([

          getFarmerDashboard(
            CURRENT_FARMER_ID
          ),

          getFarmer(
            CURRENT_FARMER_ID
          )

        ]);


        setData(
          dashboardResult
        );


        /* -----------------------------------------------
           PREFILL FROM CURRENT HARVEST
        ------------------------------------------------ */

        const currentHarvest =
          dashboardResult?.harvest;


        if (currentHarvest) {

          setCrop(
            currentHarvest.crop ||
            "Tomato"
          );


          setVariety(
            currentHarvest.variety ||
            "Deshi"
          );


          setQuantity(
            String(
              currentHarvest.quantity_kg ?? ""
            )
          );


          setQuality(
            currentHarvest.quality ||
            "Grade A"
          );


          setHarvestDate(
            currentHarvest.harvest_date ||
            ""
          );

        }


        /* -----------------------------------------------
           FARMER PROFILE
        ------------------------------------------------ */

        if (farmerResult) {

          setLocation(
            farmerResult.location ||
            "Dindigul, Tamil Nadu"
          );


          setRiskPreference(
            farmerResult.risk_preference ||
            "MEDIUM"
          );


          /*
            NEW:
            Load the farmer's existing storage capacity.
          */

          const farmerCapacity =
            Number(
              farmerResult.storage_capacity_kg
              ?? 0
            );


          setStorageCapacity(
            farmerCapacity > 0
              ? String(farmerCapacity)
              : ""
          );


          /*
            If the farmer has no storage capacity,
            treat storage facility as unavailable.
          */

          if (
            farmerCapacity <= 0
          ) {

            setStorageFacility(
              "Not Available"
            );

          } else {

            setStorageFacility(
              "Available"
            );

          }

        }


        /* -----------------------------------------------
           DEFAULT DATE
        ------------------------------------------------ */

        if (
          !currentHarvest?.harvest_date
        ) {

          const today =
            new Date();


          const localDate =
            new Date(
              today.getTime() -
              today.getTimezoneOffset() *
                60000
            )
              .toISOString()
              .split("T")[0];


          setHarvestDate(
            localDate
          );

        }

      } catch (err) {

        console.error(
          "Dashboard loading error:",
          err
        );


        setError(
          err.message ||
          "Unable to load dashboard data."
        );

      } finally {

        setLoading(false);

      }

    }


    loadDashboard();

  }, []);


  /* =======================================================
     STORAGE FACILITY CHANGE
  ======================================================= */

  function handleStorageFacilityChange(
    event
  ) {

    const value =
      event.target.value;


    setStorageFacility(
      value
    );


    /*
      When storage is unavailable,
      capacity must be zero/empty.
    */

    if (
      value === "Not Available"
    ) {

      setStorageCapacity(
        ""
      );

    }

  }


  /* =======================================================
     STORAGE CAPACITY CHANGE
  ======================================================= */

  function handleStorageCapacityChange(
    event
  ) {

    const value =
      event.target.value;


    /*
      Allow the user to temporarily
      clear the field while typing.
    */

    if (value === "") {

      setStorageCapacity(
        ""
      );

      return;

    }


    const numericValue =
      Number(value);


    if (
      !Number.isFinite(
        numericValue
      )
    ) {

      return;

    }


    /*
      Never allow negative capacity.
    */

    if (
      numericValue < 0
    ) {

      return;

    }


    setStorageCapacity(
      value
    );

  }


  /* =======================================================
     ANALYZE MARKET
  ======================================================= */

  async function handleAnalyzeMarket(
    event
  ) {

    event.preventDefault();


    setAnalysisError("");


    const quantityNumber =
      Number(quantity);


    const storageCapacityNumber =
      Number(
        storageCapacity
      );


    /* =====================================================
       VALIDATION
    ===================================================== */

    if (!crop.trim()) {

      setAnalysisError(
        "Please select a crop."
      );

      return;

    }


    if (!variety.trim()) {

      setAnalysisError(
        "Please select a variety."
      );

      return;

    }


    if (
      !Number.isFinite(
        quantityNumber
      ) ||
      quantityNumber <= 0
    ) {

      setAnalysisError(
        "Please enter a valid quantity."
      );

      return;

    }


    if (!harvestDate) {

      setAnalysisError(
        "Please select the harvest date."
      );

      return;

    }


    /* =====================================================
       STORAGE VALIDATION
    ===================================================== */

    if (
      storageFacility === "Available"
    ) {

      if (
        !Number.isFinite(
          storageCapacityNumber
        ) ||
        storageCapacityNumber <= 0
      ) {

        setAnalysisError(
          "Please enter your available storage capacity."
        );

        return;

      }


      if (
        storageCapacityNumber >
        quantityNumber
      ) {

        setAnalysisError(
          "Storage capacity cannot exceed the harvest quantity."
        );

        return;

      }

    }


    try {

      setAnalyzing(true);


      /* ===================================================
         GET CURRENT FARMER
      =================================================== */

      const farmer =
        await getFarmer(
          CURRENT_FARMER_ID
        );


      /* ===================================================
         DETERMINE STORAGE CAPACITY TO SAVE
      =================================================== */

      const capacityToSave =
        storageFacility === "Available"
          ? storageCapacityNumber
          : 0;


      /* ===================================================
         SAVE FARMER PROFILE
      =================================================== */

      await updateFarmer(

        CURRENT_FARMER_ID,

        {

          name:
            farmer.name,

          location:
            location,

          risk_preference:
            riskPreference,

          storage_capacity_kg:
            capacityToSave

        }

      );


      /* ===================================================
         CHECK EXISTING HARVEST
      =================================================== */

      const existingHarvest =
        data?.harvest || null;


      let selectedHarvest =
        existingHarvest;


      const harvestChanged =
        !existingHarvest ||
        existingHarvest.crop !== crop ||
        (
          existingHarvest.variety ||
          ""
        ) !== variety ||
        Number(
          existingHarvest.quantity_kg ||
          0
        ) !== quantityNumber ||
        (
          existingHarvest.quality ||
          ""
        ) !== quality ||
        (
          existingHarvest.harvest_date ||
          ""
        ) !== harvestDate;


      /* ===================================================
         CREATE NEW HARVEST ONLY WHEN NEEDED
      =================================================== */

      if (harvestChanged) {

        selectedHarvest =
          await createHarvest({

            farmer_id:
              CURRENT_FARMER_ID,

            crop:
              crop,

            variety:
              variety,

            quantity_kg:
              quantityNumber,

            quality:
              quality,

            harvest_date:
              harvestDate,

            shelf_life_days:
              5

          });

      }


      /* ===================================================
         MARKET ANALYSIS
      =================================================== */

      const recommendation =
        await getMarketRecommendation(

          crop,

          variety,

          quantityNumber

        );


      setAnalysisResult(
        recommendation
      );


      /* ===================================================
         GO TO SELECTED HARVEST
      =================================================== */

      navigate(
        `/harvest-planner?harvest_id=${selectedHarvest.id}`
      );


    } catch (err) {

      console.error(
        "Market analysis error:",
        err
      );


      setAnalysisError(
        err.message ||
        "Unable to save harvest and analyze the market."
      );

    } finally {

      setAnalyzing(false);

    }

  }


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading your dashboard...
          </h2>

          <p>
            Preparing your harvest decision workspace.
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
            Unable to load dashboard
          </h2>

          <p>
            {error}
          </p>

          <button
            className="primary-button"
            onClick={() =>
              window.location.reload()
            }
          >
            Try Again
          </button>

        </div>

      </div>
    );

  }


  /* =======================================================
     CURRENT HARVEST
  ======================================================= */

  const harvest =
    data?.harvest || null;


  /* =======================================================
     INPUT SUMMARY VALUES
  ======================================================= */

  const quantityNumber =
    Number(
      quantity || 0
    );


  const summaryCrop =
    crop || "-";


  const summaryQuantity =
    quantityNumber > 0
      ? `${quantityNumber.toLocaleString()} kg`
      : "-";


  const summaryStorageCapacity =
    storageFacility === "Available" &&
    Number(storageCapacity) > 0
      ? `${Number(
          storageCapacity
        ).toLocaleString()} kg`
      : "Not available";


  /* =======================================================
     PAGE
  ======================================================= */

  return (
    <div className="dashboard-page">


      {/* =================================================
          WELCOME
      ================================================= */}

      <section
        className="welcome-section dashboard-welcome"
      >

        <div>

          <h1>
            Welcome, Farmer! 🌱
          </h1>

          <p>
            Enter your harvest details to get the
            best market decision.
          </p>

        </div>

      </section>


      {/* =================================================
          DASHBOARD INPUT AREA
      ================================================= */}

      <section className="dashboard-input-layout">


        {/* =================================================
            LEFT — FARMER & HARVEST DETAILS
        ================================================= */}

        <div className="dashboard-card harvest-input-card">


          {/* ---------------------------------------------
              CARD HEADER
          --------------------------------------------- */}

          <div className="input-card-header">

            <div className="input-step">
              1
            </div>


            <div>

              <h2>
                Farmer &amp; Harvest Details
              </h2>

              <p>
                Provide accurate details to get
                better recommendations.
              </p>

            </div>


            <div className="input-card-icon">
              👨‍🌾
            </div>

          </div>


          {/* ---------------------------------------------
              FORM
          --------------------------------------------- */}

          <form
            onSubmit={
              handleAnalyzeMarket
            }
          >


            {/* =========================================
                INPUT GRID
            ========================================= */}

            <div className="input-form-grid">


              {/* -----------------------------------------
                  CROP
              ----------------------------------------- */}

              <div className="form-field">

                <label>
                  Crop <span>*</span>
                </label>

                <select
                  value={crop}
                  onChange={(event) =>
                    setCrop(
                      event.target.value
                    )
                  }
                >

                  <option value="Tomato">
                    🍃 Tomato
                  </option>

                </select>

              </div>


              {/* -----------------------------------------
                  QUANTITY
              ----------------------------------------- */}

              <div className="form-field">

                <label>
                  Quantity (in kg) <span>*</span>
                </label>

                <div className="input-with-suffix">

                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={quantity}
                    onChange={(event) =>
                      setQuantity(
                        event.target.value
                      )
                    }
                    required
                  />

                  <span>
                    kg
                  </span>

                </div>

              </div>


              {/* -----------------------------------------
                  VARIETY
              ----------------------------------------- */}

              <div className="form-field">

                <label>
                  Variety
                </label>

                <select
                  value={variety}
                  onChange={(event) =>
                    setVariety(
                      event.target.value
                    )
                  }
                >

                  <option value="Deshi">
                    Deshi
                  </option>

                  <option value="Hybrid">
                    Hybrid
                  </option>

                  <option value="Local">
                    Local
                  </option>

                </select>

              </div>


              {/* =======================================
              DISTRICT
              ======================================== */}

              <div className="form-field">

                <label>
                  District <span>*</span>
                </label>

                <select
                  value={location}
                  onChange={(event) =>
                    setLocation(
                      event.target.value
                    )
                  }
                >

                <option value="Salem, Tamil Nadu">
                  📍 Salem
                </option>

                <option value="Dindigul, Tamil Nadu">
                  📍 Dindigul
                </option>

                <option value="Madurai, Tamil Nadu">
                  📍 Madurai
                </option>

                <option value="Coimbatore, Tamil Nadu">
                  📍 Coimbatore
                </option>

                <option value="Erode, Tamil Nadu">
                  📍 Erode
                </option>

                <option value="Namakkal, Tamil Nadu">
                  📍 Namakkal
                </option>

                <option value="Karur, Tamil Nadu">
                  📍 Karur
                </option>

                <option value="Theni, Tamil Nadu">
                  📍 Theni
                </option>

                <option value="Dharmapuri, Tamil Nadu">
                  📍 Dharmapuri
                </option>

                <option value="Krishnagiri, Tamil Nadu">
                  📍 Krishnagiri
                </option>

                <option value="Tiruchirappalli, Tamil Nadu">
                  📍 Tiruchirappalli
                </option>

                <option value="Thanjavur, Tamil Nadu">
                  📍 Thanjavur
                </option>

                <option value="Virudhunagar, Tamil Nadu">
                  📍 Virudhunagar
                </option>

                <option value="Cuddalore, Tamil Nadu">
                  📍 Cuddalore
                </option>

              </select>

            </div>

              {/* -----------------------------------------
                  HARVEST DATE
              ----------------------------------------- */}

              <div className="form-field">

                <label>
                  Harvest Date <span>*</span>
                </label>

                <input
                  type="date"
                  value={harvestDate}
                  onChange={(event) =>
                    setHarvestDate(
                      event.target.value
                    )
                  }
                  required
                />

              </div>


              {/* -----------------------------------------
                  QUALITY
              ----------------------------------------- */}

              <div className="form-field">

                <label>
                  Quality Grade
                </label>

                <select
                  value={quality}
                  onChange={(event) =>
                    setQuality(
                      event.target.value
                    )
                  }
                >

                  <option value="Grade A">
                    🛡 Grade A
                  </option>

                  <option value="Grade B">
                    Grade B
                  </option>

                  <option value="Grade C">
                    Grade C
                  </option>

                </select>

              </div>


              {/* -----------------------------------------
                  STORAGE FACILITY
              ----------------------------------------- */}

              <div className="form-field">

                <label>
                  Storage Facility
                </label>

                <select
                  value={storageFacility}
                  onChange={
                    handleStorageFacilityChange
                  }
                >

                  <option value="Available">
                    🏠 Available
                  </option>

                  <option value="Not Available">
                    Not Available
                  </option>

                </select>

              </div>


              {/* -----------------------------------------
                  STORAGE CAPACITY
              ----------------------------------------- */}

              <div className="form-field">

                <label>
                  Storage Capacity (kg)
                </label>

                <div className="input-with-suffix">

                  <input
                    type="number"
                    min="0"
                    max={
                      quantityNumber > 0
                        ? quantityNumber
                        : undefined
                    }
                    step="1"
                    value={storageCapacity}
                    onChange={
                      handleStorageCapacityChange
                    }
                    disabled={
                      storageFacility ===
                      "Not Available"
                    }
                    placeholder={
                      storageFacility ===
                      "Not Available"
                        ? "No storage"
                        : "Enter capacity"
                    }
                  />

                  <span>
                    kg
                  </span>

                </div>


                <small
                  style={{
                    display: "block",
                    marginTop: "5px",
                    color: "#52736b",
                    fontSize: "11px"
                  }}
                >
                  Maximum: harvest quantity
                </small>

              </div>

            </div>


            {/* =========================================
                RISK PREFERENCE
            ========================================= */}

            <div className="form-field full-width-field">

              <label>
                Risk Preference
              </label>

              <select
                value={riskPreference}
                onChange={(event) =>
                  setRiskPreference(
                    event.target.value
                  )
                }
              >

                <option value="LOW">
                  Conservative — prioritize lower risk
                </option>

                <option value="MEDIUM">
                  Moderate — balance between price &amp; time
                </option>

                <option value="HIGH">
                  Aggressive — prioritize higher returns
                </option>

              </select>

            </div>


            {/* =========================================
                EXPLANATION
            ========================================= */}

            <div className="form-info-box">

              <div className="form-info-icon">
                i
              </div>

              <div>

                <strong>
                  Why these details?
                </strong>

                <p>
                  These details help our AI analyze
                  market trends and provide the best
                  selling decision for you.
                </p>

              </div>

            </div>


            {/* =========================================
                ERROR
            ========================================= */}

            {analysisError && (

              <div
                className="form-error-box"
              >
                {analysisError}
              </div>

            )}


            {/* =========================================
                ANALYZE BUTTON
            ========================================= */}

            <div className="form-action">

              <button
                type="submit"
                className="primary-button analyze-button"
                disabled={analyzing}
              >

                {analyzing
                  ? "Analyzing..."
                  : "Analyze Market"
                }

                <span>
                  →
                </span>

              </button>

            </div>

          </form>

        </div>


        {/* =================================================
            RIGHT — INPUT SUMMARY
        ================================================= */}

        <aside className="dashboard-card input-summary-card">


          {/* ---------------------------------------------
              SUMMARY HEADER
          --------------------------------------------- */}

          <div className="summary-header">

            <div className="summary-icon">
              ▣
            </div>

            <h2>
              Input Summary
            </h2>

          </div>


          {/* ---------------------------------------------
              SUMMARY ITEMS
          --------------------------------------------- */}

          <div className="summary-list">


            {/* CROP */}

            <div className="summary-item">

              <span className="summary-item-icon">
                🍃
              </span>

              <div>

                <span>
                  Crop
                </span>

                <strong>
                  {summaryCrop}
                </strong>

              </div>

            </div>


            {/* QUANTITY */}

            <div className="summary-item">

              <span className="summary-item-icon">
                ⚖
              </span>

              <div>

                <span>
                  Quantity
                </span>

                <strong>
                  {summaryQuantity}
                </strong>

              </div>

            </div>


            {/* LOCATION */}

            <div className="summary-item">

              <span className="summary-item-icon">
                📍
              </span>

              <div>

                <span>
                  Location
                </span>

                <strong>
                  {location || "-"}
                </strong>

              </div>

            </div>


            {/* HARVEST DATE */}

            <div className="summary-item">

              <span className="summary-item-icon">
                📅
              </span>

              <div>

                <span>
                  Harvest Date
                </span>

                <strong>
                  {harvestDate || "-"}
                </strong>

              </div>

            </div>


            {/* QUALITY */}

            <div className="summary-item">

              <span className="summary-item-icon">
                🛡
              </span>

              <div>

                <span>
                  Quality Grade
                </span>

                <strong>
                  {quality}
                </strong>

              </div>

            </div>


            {/* STORAGE */}

            <div className="summary-item">

              <span className="summary-item-icon">
                🏠
              </span>

              <div>

                <span>
                  Storage
                </span>

                <strong>
                  {storageFacility}
                </strong>

              </div>

            </div>


            {/* NEW: STORAGE CAPACITY */}

            <div className="summary-item">

              <span className="summary-item-icon">
                📦
              </span>

              <div>

                <span>
                  Storage Capacity
                </span>

                <strong>
                  {summaryStorageCapacity}
                </strong>

              </div>

            </div>


            {/* RISK */}

            <div className="summary-item">

              <span className="summary-item-icon">
                ◔
              </span>

              <div>

                <span>
                  Risk Preference
                </span>

                <strong>
                  {riskPreference === "LOW"
                    ? "Conservative"
                    : riskPreference === "HIGH"
                      ? "Aggressive"
                      : "Moderate"
                  }
                </strong>

              </div>

            </div>

          </div>


          {/* ---------------------------------------------
              READY MESSAGE
          --------------------------------------------- */}

          <div className="summary-ready-box">

            <div className="summary-ready-icon">
              ↗
            </div>

            <div>

              <strong>
                Ready to analyze!
              </strong>

              <p>
                Click "Analyze Market" to get
                price prediction and best market
                options.
              </p>

            </div>

          </div>

        </aside>

      </section>


      {/* =================================================
          CURRENT HARVEST STATUS
      ================================================= */}

      {harvest && (

        <section
          className="dashboard-card current-harvest-strip"
        >

          <div>

            <span>
              Current saved harvest
            </span>

            <strong>
              #{harvest.id} •{" "}
              {harvest.crop} •{" "}
              {harvest.variety || variety} •{" "}
              {Number(
                harvest.quantity_kg || 0
              ).toLocaleString()} kg
            </strong>

          </div>


          <button
            className="view-all"
            type="button"
            onClick={() =>
              navigate(
                `/harvest-planner?harvest_id=${harvest.id}`
              )
            }
          >
            Open Harvest Planner →
          </button>

        </section>

      )}


      {/* =================================================
          ANALYSIS PREVIEW
      ================================================= */}

      {analysisResult && (

        <section
          className="dashboard-card"
          style={{
            marginTop: "18px"
          }}
        >

          <div className="card-header">

            <div>

              <h2>
                Market Analysis
              </h2>

              <p>
                Initial recommendation for the entered harvest.
              </p>

            </div>

          </div>


          <div className="recommendation-stats">

            <div>

              <span>
                Recommended Market
              </span>

              <strong>
                {
                  analysisResult
                    .recommended_market_name ||
                  "-"
                }
              </strong>

            </div>


            <div>

              <span>
                Predicted Price
              </span>

              <strong>
                ₹
                {Number(
                  analysisResult
                    .predicted_price_per_kg || 0
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
                  analysisResult
                    .net_price_per_kg || 0
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
                  analysisResult
                    .expected_return || 0
                ).toLocaleString()}
              </strong>

            </div>

          </div>

        </section>

      )}

    </div>
  );
}


export default Dashboard;