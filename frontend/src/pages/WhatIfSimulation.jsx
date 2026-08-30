import { useEffect, useState } from "react";

import {
  useSearchParams,
  useNavigate
} from "react-router-dom";

import {
  getHarvest,
  getFarmer,
  getFarmerHarvests,
  simulateWhatIf,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function WhatIfSimulation() {

  const [searchParams] =
    useSearchParams();

  const navigate =
    useNavigate();


  const selectedHarvestId =
    searchParams.get(
      "harvest_id"
    );


  /* =======================================================
     STATE
  ======================================================= */

  const [harvest, setHarvest] =
    useState(null);

  const [farmer, setFarmer] =
    useState(null);

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [simulating, setSimulating] =
    useState(false);

  const [error, setError] =
    useState("");


  /* =======================================================
     SCENARIO CONTROLS
  ======================================================= */

  const [priceChange, setPriceChange] =
    useState(0);

  const [transportChange, setTransportChange] =
    useState(0);

  const [storageCapacity, setStorageCapacity] =
    useState("");

  const [spoilageRisk, setSpoilageRisk] =
    useState(0);


  /* =======================================================
     LOAD FARMER + HARVEST
  ======================================================= */

  useEffect(() => {

    async function loadData() {

      try {

        setLoading(true);
        setError("");


        /* ================================================
           LOAD FARMER PROFILE
        ================================================ */

        const farmerData =
          await getFarmer(
            CURRENT_FARMER_ID
          );


        setFarmer(
          farmerData
        );


        /* ================================================
           SELECT HARVEST
        ================================================ */

        let selectedHarvest;


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
              "No harvest records found."
            );

          }


          /*
            Harvests are already ordered newest first.
          */

          selectedHarvest =
            harvests[0];

        }


        setHarvest(
          selectedHarvest
        );


        /* ================================================
           DEFAULT STORAGE CAPACITY
           USE FARMER'S ACTUAL CAPACITY
        ================================================ */

        const farmerStorageCapacity =
          Number(
            farmerData.storage_capacity_kg || 0
          );


        const harvestQuantity =
          Number(
            selectedHarvest.quantity_kg || 0
          );


        /*
          A farmer cannot store more than:
          1. their physical storage capacity
          2. the current harvest quantity
        */

        const defaultStorageCapacity =
          Math.min(
            farmerStorageCapacity,
            harvestQuantity
          );


        setStorageCapacity(
          String(
            defaultStorageCapacity
          )
        );


      } catch (err) {

        console.error(
          "What-if loading error:",
          err
        );


        setError(
          err.message ||
          "Unable to load harvest and farmer data."
        );

      } finally {

        setLoading(false);

      }

    }


    loadData();

  }, [selectedHarvestId]);


  /* =======================================================
     RUN SIMULATION
  ======================================================= */

  async function handleSimulation() {

    if (!harvest) {
      return;
    }


    const harvestQuantity =
      Number(
        harvest.quantity_kg || 0
      );


    const farmerStorageCapacity =
      Number(
        farmer?.storage_capacity_kg || 0
      );


    const requestedStorageCapacity =
      Number(
        storageCapacity
      );


    /* ================================================
       VALIDATE STORAGE CAPACITY
    ================================================ */

    if (
      requestedStorageCapacity < 0
    ) {

      setError(
        "Storage capacity cannot be negative."
      );

      return;

    }


    if (
      requestedStorageCapacity >
      farmerStorageCapacity
    ) {

      setError(
        `Storage capacity cannot exceed your actual capacity of ${farmerStorageCapacity.toLocaleString()} kg.`
      );

      return;

    }


    if (
      requestedStorageCapacity >
      harvestQuantity
    ) {

      setError(
        `Storage capacity cannot exceed the harvest quantity of ${harvestQuantity.toLocaleString()} kg.`
      );

      return;

    }


    try {

      setSimulating(true);
      setError("");


      const simulationResult =
        await simulateWhatIf(

          CURRENT_FARMER_ID,

          {
            harvest_id:
              harvest.id,

            price_change_pct:
              Number(
                priceChange
              ),

            transport_change_per_kg:
              Number(
                transportChange
              ),

            storage_capacity_kg:
              requestedStorageCapacity,

            spoilage_risk_pct:
              Number(
                spoilageRisk
              )
          }

        );


      setResult(
        simulationResult
      );


    } catch (err) {

      console.error(
        "What-if simulation error:",
        err
      );


      setError(
        err.message ||
        "Unable to run simulation."
      );

    } finally {

      setSimulating(false);

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
            Loading What-If Simulation...
          </h2>

          <p>
            Preparing your current harvest
            for scenario analysis.
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     ERROR
  ======================================================= */

  if (error && !harvest) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state error-state">

          <h2>
            Unable to load simulation
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


  if (!harvest) {
    return null;
  }


  /* =======================================================
     VALUES
  ======================================================= */

  const harvestQuantity =
    Number(
      harvest.quantity_kg || 0
    );


  const actualStorageCapacity =
    Number(
      farmer?.storage_capacity_kg || 0
    );


  const currentPlan =
    result?.current_plan;

  const simulatedPlan =
    result?.simulated_plan;


  const currentReturn =
    Number(
      currentPlan?.total_expected_return || 0
    );


  const simulatedReturn =
    Number(
      simulatedPlan?.total_expected_return || 0
    );


  const profitDifference =
    Number(
      result?.profit_difference || 0
    );


  const profitChangePercent =
    Number(
      result?.profit_change_percent || 0
    );


  const isImprovement =
    profitDifference > 0;


  const isReduction =
    profitDifference < 0;


  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <div className="dashboard-page">


      {/* =================================================
          HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          What-If Simulation
        </h1>

        <p>
          Test different market and storage
          conditions before making a decision.
        </p>

        <p className="fairdeal-harvest-info">

          Harvest #{harvest.id} •{" "}
          {harvest.crop} •{" "}
          {harvest.variety || "Deshi"} •{" "}
          {harvestQuantity.toLocaleString()} kg

        </p>

      </section>


      {/* =================================================
          SCENARIO CONTROLS
      ================================================= */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
              Scenario Controls
            </h2>

            <p>
              Change assumptions and simulate a
              new optimal selling strategy.
            </p>

          </div>

        </div>


        <div className="whatif-controls-grid">


          {/* PRICE */}

          <div className="form-field">

            <label>
              Price Change (%)
            </label>

            <input
              type="number"
              step="1"
              min="-100"
              max="100"
              value={priceChange}
              onChange={(event) =>
                setPriceChange(
                  event.target.value
                )
              }
            />

          </div>


          {/* TRANSPORT */}

          <div className="form-field">

            <label>
              Transport Change (₹/kg)
            </label>

            <input
              type="number"
              step="0.5"
              value={transportChange}
              onChange={(event) =>
                setTransportChange(
                  event.target.value
                )
              }
            />

          </div>


          {/* STORAGE */}

          <div className="form-field">

            <label>
              Storage Capacity (kg)
            </label>

            <input
              type="number"
              min="0"
              max={
                Math.min(
                  actualStorageCapacity,
                  harvestQuantity
                )
              }
              step="1"
              value={storageCapacity}
              onChange={(event) =>
                setStorageCapacity(
                  event.target.value
                )
              }
            />

            <small
              style={{
                display: "block",
                marginTop: "5px",
                fontSize: "10px",
                color: "#52736b"
              }}
            >
              Actual capacity:{" "}
              {actualStorageCapacity.toLocaleString()}
              {" "}kg
            </small>

          </div>


          {/* SPOILAGE */}

          <div className="form-field">

            <label>
              Additional Spoilage Risk (%)
            </label>

            <input
              type="number"
              min="0"
              max="100"
              step="1"
              value={spoilageRisk}
              onChange={(event) =>
                setSpoilageRisk(
                  event.target.value
                )
              }
            />

          </div>


        </div>


        <div className="whatif-action">

          <button
            className="primary-button"
            onClick={
              handleSimulation
            }
            disabled={simulating}
          >

            {simulating
              ? "Simulating..."
              : "Simulate"
            }

          </button>

        </div>


        {error && (

          <div className="form-error-box">

            {error}

          </div>

        )}

      </section>


      {/* =================================================
          RESULTS
      ================================================= */}

      {result && (

        <>


          {/* =============================================
              SIMULATION RESULT
          ============================================= */}

          <section
            className="dashboard-card"
            style={{
              marginTop: "18px"
            }}
          >

            <div className="card-header">

              <div>

                <h2>
                  Simulation Result
                </h2>

                <p>
                  Current plan compared with the
                  simulated scenario.
                </p>

              </div>

            </div>


            <div className="recommendation-stats">


              <div>

                <span>
                  Current Return
                </span>

                <strong>
                  ₹
                  {currentReturn.toLocaleString()}
                </strong>

              </div>


              <div>

                <span>
                  Simulated Return
                </span>

                <strong>
                  ₹
                  {simulatedReturn.toLocaleString()}
                </strong>

              </div>


              <div>

                <span>
                  Difference
                </span>

                <strong
                  className={
                    isImprovement
                      ? "whatif-positive"
                      : isReduction
                        ? "whatif-negative"
                        : ""
                  }
                >

                  {profitDifference >= 0
                    ? "+"
                    : ""
                  }

                  ₹
                  {profitDifference.toLocaleString()}

                </strong>

              </div>


              <div>

                <span>
                  Change
                </span>

                <strong
                  className={
                    isImprovement
                      ? "whatif-positive"
                      : isReduction
                        ? "whatif-negative"
                        : ""
                  }
                >

                  {profitChangePercent >= 0
                    ? "+"
                    : ""
                  }

                  {profitChangePercent.toFixed(2)}
                  %

                </strong>

              </div>

            </div>


            <p className="recommendation-reason">

              {isImprovement
                ? "The simulated conditions improve the expected return."
                : isReduction
                  ? "The simulated conditions reduce the expected return."
                  : "The simulated conditions produce the same expected return."
              }

            </p>

          </section>


          {/* =============================================
              ALLOCATION COMPARISON
          ============================================= */}

          <section
            className="dashboard-card"
            style={{
              marginTop: "18px"
            }}
          >

            <div className="card-header">

              <div>

                <h2>
                  Allocation Comparison
                </h2>

                <p>
                  How the harvest would be allocated
                  under each scenario.
                </p>

              </div>

            </div>


            <div className="whatif-allocation-grid">


              <div className="whatif-comparison-card">

                <h3>
                  Current Plan
                </h3>


                <div>

                  <span>
                    Markets
                  </span>

                  <strong>

                    {Number(
                      currentPlan
                        ?.allocation_summary
                        ?.market_kg || 0
                    ).toLocaleString()}
                    {" "}kg

                  </strong>

                </div>


                <div>

                  <span>
                    Buyers
                  </span>

                  <strong>

                    {Number(
                      currentPlan
                        ?.allocation_summary
                        ?.buyer_kg || 0
                    ).toLocaleString()}
                    {" "}kg

                  </strong>

                </div>


                <div>

                  <span>
                    Storage
                  </span>

                  <strong>

                    {Number(
                      currentPlan
                        ?.allocation_summary
                        ?.storage_kg || 0
                    ).toLocaleString()}
                    {" "}kg

                  </strong>

                </div>

              </div>


              <div className="whatif-comparison-card">

                <h3>
                  Simulated Plan
                </h3>


                <div>

                  <span>
                    Markets
                  </span>

                  <strong>

                    {Number(
                      simulatedPlan
                        ?.allocation_summary
                        ?.market_kg || 0
                    ).toLocaleString()}
                    {" "}kg

                  </strong>

                </div>


                <div>

                  <span>
                    Buyers
                  </span>

                  <strong>

                    {Number(
                      simulatedPlan
                        ?.allocation_summary
                        ?.buyer_kg || 0
                    ).toLocaleString()}
                    {" "}kg

                  </strong>

                </div>


                <div>

                  <span>
                    Storage
                  </span>

                  <strong>

                    {Number(
                      simulatedPlan
                        ?.allocation_summary
                        ?.storage_kg || 0
                    ).toLocaleString()}
                    {" "}kg

                  </strong>

                </div>

              </div>


            </div>

          </section>


          {/* =============================================
              SIMULATED STRATEGY
          ============================================= */}

          <section
            className="dashboard-card"
            style={{
              marginTop: "18px"
            }}
          >

            <div className="card-header">

              <div>

                <h2>
                  Simulated Strategy
                </h2>

                <p>
                  Detailed destination allocation.
                </p>

              </div>

            </div>


            <div className="buyer-offer-list">

              {(
                simulatedPlan?.details || []
              ).map(
                (detail) => (

                  <div
                    className="buyer-offer"
                    key={
                      detail.destination_id
                    }
                  >

                    {/* =================================
                        DESTINATION NAME
                    ================================= */}

                    <div>

                      <strong>
                        {
                          detail.destination_name ||
                          detail.destination_id
                        }
                      </strong>

                      <span>
                        {detail.kind}
                      </span>

                    </div>


                    {/* =================================
                        QUANTITY / PRICE
                    ================================= */}

                    <div>

                      <strong>

                        {Number(
                          detail.allocated_kg || 0
                        ).toLocaleString()}

                        {" "}kg

                      </strong>

                      <span>

                        ₹
                        {Number(
                          detail.risk_adjusted_price_per_kg || 0
                        ).toFixed(2)}

                        /kg

                      </span>

                    </div>


                    {/* =================================
                        EXPECTED RETURN
                    ================================= */}

                    <div>

                      <strong>

                        ₹
                        {Number(
                          detail.expected_return || 0
                        ).toLocaleString()}

                      </strong>

                      <span>
                        Expected return
                      </span>

                    </div>

                  </div>

                )
              )}

            </div>

          </section>


        </>

      )}

    </div>
  );
}


export default WhatIfSimulation;