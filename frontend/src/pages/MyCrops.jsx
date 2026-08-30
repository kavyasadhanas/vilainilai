import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getFarmerHarvests,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function MyCrops() {

  const [harvests, setHarvests] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const navigate =
    useNavigate();


  /* =======================================================
     LOAD HARVESTS
  ======================================================= */

  useEffect(() => {

    async function loadHarvests() {

      try {

        setLoading(true);
        setError("");

        const result =
          await getFarmerHarvests(
            CURRENT_FARMER_ID
          );

        setHarvests(
          Array.isArray(result)
            ? result
            : []
        );

      } catch (err) {

        console.error(
          "My Crops loading error:",
          err
        );

        setError(
          err.message ||
          "Unable to load your crops."
        );

      } finally {

        setLoading(false);

      }

    }

    loadHarvests();

  }, []);


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading your crops...
          </h2>

          <p>
            Fetching your harvest records.
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
            Unable to load crops
          </h2>

          <p>
            {error}
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     SUMMARY
  ======================================================= */

  const totalQuantity =
    harvests.reduce(
      (total, harvest) =>
        total +
        Number(
          harvest.quantity_kg || 0
        ),
      0
    );


  const latestHarvest =
    harvests.length > 0
      ? harvests[0]
      : null;


  /* =======================================================
     PAGE
  ======================================================= */

  return (
    <div className="dashboard-page">


      {/* ===================================================
          HEADER
      =================================================== */}

      <section className="welcome-section">

        <h1>
          My Crops
        </h1>

        <p>
          View and manage your recorded harvests.
        </p>

        <p className="fairdeal-harvest-info">

          Farmer #{CURRENT_FARMER_ID} •{" "}
          {harvests.length} harvest record
          {harvests.length !== 1 ? "s" : ""}

        </p>

      </section>


      {/* ===================================================
          SUMMARY CARDS
      =================================================== */}

      <section className="stats-grid">

        {/* Total Records */}

        <div className="stat-card">

          <div className="stat-icon">
            🌱
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Total Harvest Records
            </span>

            <span className="stat-value">
              {harvests.length}
            </span>

          </div>

        </div>


        {/* Total Quantity */}

        <div className="stat-card">

          <div className="stat-icon">
            📦
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Total Quantity
            </span>

            <span className="stat-value">
              {totalQuantity.toLocaleString()} kg
            </span>

          </div>

        </div>


        {/* Latest Crop */}

        <div className="stat-card">

          <div className="stat-icon">
            🍅
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Latest Crop
            </span>

            <span className="stat-value">
              {latestHarvest?.crop || "-"}
            </span>

          </div>

        </div>


        {/* Latest Harvest */}

        <div className="stat-card">

          <div className="stat-icon">
            📅
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Latest Harvest
            </span>

            <span className="stat-value">
              {latestHarvest?.harvest_date || "-"}
            </span>

          </div>

        </div>

      </section>


      {/* ===================================================
          HARVEST RECORDS
      =================================================== */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
              Harvest Records
            </h2>

            <p>
              Select a harvest to continue planning.
            </p>

          </div>

        </div>


        {harvests.length === 0 ? (

          /* ===============================================
             EMPTY
          =============================================== */

          <div className="dashboard-state">

            <h2>
              No crops recorded
            </h2>

            <p>
              Add a harvest from the Dashboard
              to start planning.
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

          /* ===============================================
             HARVEST LIST
          =============================================== */

          <div className="my-crops-list">

            {harvests.map(
              (harvest) => (

                <div
                  className="my-crop-row"
                  key={harvest.id}
                >

                  {/* =====================================
                      LEFT
                  ===================================== */}

                  <div className="my-crop-main">

                    <div className="my-crop-icon">
                      🍅
                    </div>

                    <div>

                      <h3>
                        {harvest.crop}
                      </h3>

                      <p>

                        {harvest.variety || "Deshi"}
                        {" "}•{" "}
                        {harvest.quality || "Grade A"}

                      </p>

                      <span>

                        Harvest #{harvest.id}
                        {" "}•{" "}
                        {harvest.harvest_date || "-"}

                      </span>

                    </div>

                  </div>


                  {/* =====================================
                      MIDDLE — QUANTITY
                  ===================================== */}

                  <div className="my-crop-quantity">

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


                  {/* =====================================
                      RIGHT — ACTION
                  ===================================== */}

                  <button
                    className="primary-button"
                    onClick={() =>
                      navigate(
                        `/harvest-planner?harvest_id=${harvest.id}`
                      )
                    }
                    style={{
                      marginTop: 0,
                      minWidth: "120px"
                    }}
                  >
                    Open Harvest
                  </button>

                </div>

              )
            )}

          </div>

        )}

      </section>

    </div>
  );
}


export default MyCrops;