import { useEffect, useState } from "react";

import {
  useSearchParams,
  useNavigate
} from "react-router-dom";

import {
  getHarvestStorageAnalysis,
  getFarmerHarvests,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function StoragePlanner() {

  const [searchParams] =
    useSearchParams();

  const navigate =
    useNavigate();


  const requestedHarvestId =
    searchParams.get(
      "harvest_id"
    );


  /* =======================================================
     STATE
  ======================================================= */

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD STORAGE ANALYSIS
  ======================================================= */

  useEffect(() => {

    async function loadStorageAnalysis() {

      try {

        setLoading(true);
        setError("");


        let selectedHarvestId =
          requestedHarvestId;


        /* =================================================
           NO HARVEST ID
           → USE LATEST FARMER HARVEST
        ================================================= */

        if (!selectedHarvestId) {

          const harvests =
            await getFarmerHarvests(
              CURRENT_FARMER_ID
            );


          if (
            !Array.isArray(harvests) ||
            harvests.length === 0
          ) {

            throw new Error(
              "No harvest records found. Please add a harvest from the Dashboard."
            );

          }


          /*
            getFarmerHarvests() already returns
            harvests ordered newest first.
          */

          selectedHarvestId =
            harvests[0].id;

        }


        /* =================================================
           LOAD STORAGE ANALYSIS
        ================================================= */

        const result =
          await getHarvestStorageAnalysis(
            selectedHarvestId
          );


        if (!result) {

          throw new Error(
            "No storage analysis was returned."
          );

        }


        setData(
          result
        );


      } catch (err) {

        console.error(
          "Storage Planner error:",
          err
        );

        setError(
          err.message ||
          "Unable to load storage analysis."
        );


      } finally {

        setLoading(false);

      }

    }


    loadStorageAnalysis();

  }, [requestedHarvestId]);


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading storage analysis...
          </h2>

          <p>
            Comparing immediate selling with
            future storage returns.
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
            Unable to load storage analysis
          </h2>

          <p>
            {error}
          </p>

          <button
            className="primary-button"
            onClick={() =>
              navigate("/dashboard")
            }
          >
            Go to Dashboard
          </button>

        </div>

      </div>
    );

  }


  /* =======================================================
     EMPTY
  ======================================================= */

  if (!data) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            No storage analysis available
          </h2>

          <p>
            No optimization result was returned.
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     DATA
  ======================================================= */

  const storage =
    data.storage || {};

  const storeAnalysis =
    data.store_analysis || {};

  const decision =
    data.decision || "UNKNOWN";


  const totalHarvest =
    Number(
      data.total_harvest_kg || 0
    );


  const marketAllocation =
    Number(
      data.allocated_to_markets_kg || 0
    );


  const buyerAllocation =
    Number(
      data.allocated_to_buyers_kg || 0
    );


  const storageAllocation =
    Number(
      data.allocated_to_storage_kg || 0
    );


  const futurePrice =
    storage.expected_future_price_per_kg != null
      ? Number(
          storage.expected_future_price_per_kg
        )
      : null;


  const netStoragePrice =
    storeAnalysis.net_price_per_kg != null
      ? Number(
          storeAnalysis.net_price_per_kg
        )
      : null;


  const riskAdjustedPrice =
    storeAnalysis.risk_adjusted_price_per_kg != null
      ? Number(
          storeAnalysis.risk_adjusted_price_per_kg
        )
      : null;


  return (
    <div className="dashboard-page">


      {/* =================================================
          PAGE HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          Storage Planner
        </h1>

        <p>
          Decide whether selling now or storing
          your harvest gives the better return.
        </p>

        <p className="fairdeal-harvest-info">

          Harvest #{data.harvest_id} •{" "}
          {data.crop || "-"} •{" "}
          {data.variety || "-"} •{" "}
          {totalHarvest.toLocaleString()} kg

        </p>

      </section>


      {/* =================================================
          SUMMARY
      ================================================= */}

      <section className="stats-grid">


        <div className="stat-card">

          <div className="stat-icon">
            📦
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Total Harvest
            </span>

            <span className="stat-value">
              {totalHarvest.toLocaleString()} kg
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            🏠
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Storage Capacity
            </span>

            <span className="stat-value">
              {Number(
                storage.storage_capacity_kg || 0
              ).toLocaleString()} kg
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            📈
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Future Predicted Price
            </span>

            <span className="stat-value">

              {futurePrice != null
                ? `₹${futurePrice.toFixed(2)}/kg`
                : "-"
              }

            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            🎯
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Current Decision
            </span>

            <span className="stat-value">
              {decision}
            </span>

          </div>

        </div>

      </section>


      {/* =================================================
          MAIN DECISION
      ================================================= */}

      <section className="dashboard-card recommendation-card">

        <div className="recommendation-header">

          <div>

            <span className="best-choice">
              OPTIMAL STRATEGY
            </span>

            <h3>
              {decision}
            </h3>

          </div>

          <span className="recommendation-icon">
            ✓
          </span>

        </div>


        <div className="expected-return">

          <span>
            Total Expected Return
          </span>

          <strong>

            ₹
            {Number(
              data.total_expected_return || 0
            ).toLocaleString()}

          </strong>

          <p>
            Based on risk-adjusted optimization.
          </p>

        </div>


        <div className="recommendation-stats">

          <div>

            <span>
              Reference Market
            </span>

            <strong>
              {storage.reference_market || "-"}
            </strong>

          </div>


          <div>

            <span>
              Waiting Period
            </span>

            <strong>
              {storage.days_to_wait ?? "-"} days
            </strong>

          </div>


          <div>

            <span>
              Storage Cost
            </span>

            <strong>

              ₹
              {storage.storage_cost_per_kg_day != null
                ? Number(
                    storage.storage_cost_per_kg_day
                  ).toFixed(2)
                : "-"
              }
              /kg/day

            </strong>

          </div>


          <div>

            <span>
              Risk Preference
            </span>

            <strong>
              {data.risk_preference || "-"}
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          HARVEST ALLOCATION
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
              Harvest Allocation
            </h2>

            <p>
              How the optimizer has allocated this harvest.
            </p>

          </div>

        </div>


        <div className="recommendation-stats">


          <div>

            <span>
              Total Harvest
            </span>

            <strong>
              {totalHarvest.toLocaleString()} kg
            </strong>

          </div>


          <div>

            <span>
              Markets
            </span>

            <strong>
              {marketAllocation.toLocaleString()} kg
            </strong>

          </div>


          <div>

            <span>
              Buyers
            </span>

            <strong>
              {buyerAllocation.toLocaleString()} kg
            </strong>

          </div>


          <div>

            <span>
              Storage
            </span>

            <strong>
              {storageAllocation.toLocaleString()} kg
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          STORAGE ECONOMICS
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
              Storage Economics
            </h2>

            <p>
              Financial impact of waiting before selling.
            </p>

          </div>

        </div>


        <div className="recommendation-stats">


          <div>

            <span>
              Expected Future Price
            </span>

            <strong>

              {futurePrice != null
                ? `₹${futurePrice.toFixed(2)}/kg`
                : "-"
              }

            </strong>

          </div>


          <div>

            <span>
              Net Storage Price
            </span>

            <strong>

              {netStoragePrice != null
                ? `₹${netStoragePrice.toFixed(2)}/kg`
                : "-"
              }

            </strong>

          </div>


          <div>

            <span>
              Risk-Adjusted Price
            </span>

            <strong>

              {riskAdjustedPrice != null
                ? `₹${riskAdjustedPrice.toFixed(2)}/kg`
                : "-"
              }

            </strong>

          </div>


          <div>

            <span>
              Allocated to Storage
            </span>

            <strong>
              {storageAllocation.toLocaleString()} kg
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          WHY THIS DECISION
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
              Why This Decision?
            </h2>

            <p>
              Explanation of the optimizer result.
            </p>

          </div>

        </div>


        <div className="form-info-box">

          <div className="form-info-icon">
            i
          </div>

          <div>

            {decision === "SELL NOW" ? (

              <>
                <strong>
                  Selling now is currently preferred.
                </strong>

                <p>
                  The storage option is less attractive
                  after considering future price, storage
                  cost, expected loss and risk adjustment.
                </p>
              </>

            ) : (

              <>
                <strong>
                  Storage is currently preferred.
                </strong>

                <p>
                  The future risk-adjusted return is
                  currently more attractive than
                  immediate selling.
                </p>
              </>

            )}

          </div>

        </div>

      </section>


    </div>
  );
}


export default StoragePlanner;