import { useEffect, useState } from "react";

import {
  getFarmer,
  updateFarmer,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function Settings() {

  const [farmer, setFarmer] =
    useState(null);

  const [formData, setFormData] =
    useState({
      name: "",
      location: "",
      risk_preference: "MEDIUM",
      storage_capacity_kg: 0
    });

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  /* =======================================================
     LOAD FARMER
  ======================================================= */

  useEffect(() => {

    async function loadFarmer() {

      try {

        setLoading(true);
        setError("");

        const result =
          await getFarmer(
            CURRENT_FARMER_ID
          );

        setFarmer(
          result
        );

        setFormData({

          name:
            result.name || "",

          location:
            result.location || "",

          risk_preference:
            result.risk_preference ||
            "MEDIUM",

          storage_capacity_kg:
            result.storage_capacity_kg ||
            0

        });

      } catch (err) {

        console.error(
          "Settings loading error:",
          err
        );

        setError(
          err.message ||
          "Unable to load farmer settings."
        );

      } finally {

        setLoading(false);

      }

    }

    loadFarmer();

  }, []);


  /* =======================================================
     HANDLE INPUT
  ======================================================= */

  function handleChange(event) {

    const {
      name,
      value
    } = event.target;

    setFormData(
      previous => ({
        ...previous,
        [name]: value
      })
    );

  }


  /* =======================================================
     SAVE SETTINGS
  ======================================================= */

  async function handleSave(event) {

    event.preventDefault();

    try {

      setSaving(true);
      setError("");
      setSuccess("");


      /* -----------------------------------------------
         Basic validation
      ----------------------------------------------- */

      if (
        !formData.name.trim()
      ) {

        throw new Error(
          "Farmer name cannot be empty."
        );

      }


      if (
        !formData.location.trim()
      ) {

        throw new Error(
          "Location cannot be empty."
        );

      }


      const storageCapacity =
        Number(
          formData.storage_capacity_kg
        );


      if (
        Number.isNaN(storageCapacity) ||
        storageCapacity < 0
      ) {

        throw new Error(
          "Storage capacity must be zero or greater."
        );

      }


      /* -----------------------------------------------
         Update backend
      ----------------------------------------------- */

      const updatedFarmer =
        await updateFarmer(

          CURRENT_FARMER_ID,

          {
            ...formData,

            storage_capacity_kg:
              storageCapacity
          }

        );


      setFarmer(
        updatedFarmer
      );


      setFormData({

        name:
          updatedFarmer.name || "",

        location:
          updatedFarmer.location || "",

        risk_preference:
          updatedFarmer.risk_preference ||
          "MEDIUM",

        storage_capacity_kg:
          updatedFarmer.storage_capacity_kg ||
          0

      });


      setSuccess(
        "Settings saved successfully."
      );

    } catch (err) {

      console.error(
        "Settings update error:",
        err
      );

      setError(
        err.message ||
        "Unable to save settings."
      );

    } finally {

      setSaving(false);

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
            Loading settings...
          </h2>

          <p>
            Fetching your farmer profile.
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     ERROR
  ======================================================= */

  if (error && !farmer) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state error-state">

          <h2>
            Unable to load settings
          </h2>

          <p>
            {error}
          </p>

        </div>

      </div>
    );

  }


  if (!farmer) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Farmer profile not found
          </h2>

        </div>

      </div>
    );

  }


  return (
    <div className="dashboard-page">


      {/* ===================================================
          HEADER
      =================================================== */}

      <section className="welcome-section">

        <h1>
          Settings
        </h1>

        <p>
          Manage your farmer profile and
          decision preferences.
        </p>

        <p className="fairdeal-harvest-info">

          Farmer #{farmer.id} •{" "}
          {farmer.location}

        </p>

      </section>


      {/* ===================================================
          MESSAGES
      =================================================== */}

      {success && (

        <div
          className="market-insight"
          style={{
            marginBottom: "25px"
          }}
        >

          <div className="insight-icon">
            ✓
          </div>

          <div>

            <strong>
              Settings Updated
            </strong>

            <p>
              {success}
            </p>

          </div>

        </div>

      )}


      {error && (

        <div
          className="dashboard-state error-state"
          style={{
            marginBottom: "25px"
          }}
        >

          <p>
            {error}
          </p>

        </div>

      )}


      {/* ===================================================
          EDIT PROFILE
      =================================================== */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
              Farmer Information
            </h2>

            <p>
              Update your registered profile.
            </p>

          </div>

          <span className="recommendation-icon">
            👨‍🌾
          </span>

        </div>


        <form
          onSubmit={handleSave}
        >


          {/* ===============================================
              NAME
          =============================================== */}

          <div
            style={{
              marginBottom: "22px"
            }}
          >

            <label
              style={{
                display: "block",
                marginBottom: "8px",
                fontWeight: 600
              }}
            >
              Farmer Name
            </label>

            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "13px",
                border:
                  "1px solid #ccdcd6",
                borderRadius: "8px",
                fontSize: "16px",
                boxSizing: "border-box"
              }}
            />

          </div>


          {/* ===============================================
              LOCATION
          =============================================== */}

          <div
            style={{
              marginBottom: "22px"
            }}
          >

            <label
              style={{
                display: "block",
                marginBottom: "8px",
                fontWeight: 600
              }}
            >
              Location
            </label>

            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "13px",
                border:
                  "1px solid #ccdcd6",
                borderRadius: "8px",
                fontSize: "16px",
                boxSizing: "border-box"
              }}
            />

          </div>


          {/* ===============================================
              RISK PREFERENCE
          =============================================== */}

          <div
            style={{
              marginBottom: "22px"
            }}
          >

            <label
              style={{
                display: "block",
                marginBottom: "8px",
                fontWeight: 600
              }}
            >
              Risk Preference
            </label>

            <select
              name="risk_preference"
              value={formData.risk_preference}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "13px",
                border:
                  "1px solid #ccdcd6",
                borderRadius: "8px",
                fontSize: "16px",
                background: "white",
                boxSizing: "border-box"
              }}
            >

              <option value="LOW">
                LOW — More conservative
              </option>

              <option value="MEDIUM">
                MEDIUM — Balanced
              </option>

              <option value="HIGH">
                HIGH — More risk tolerant
              </option>

            </select>

          </div>


          {/* ===============================================
              STORAGE CAPACITY
          =============================================== */}

          <div
            style={{
              marginBottom: "25px"
            }}
          >

            <label
              style={{
                display: "block",
                marginBottom: "8px",
                fontWeight: 600
              }}
            >
              Storage Capacity (kg)
            </label>

            <input
              type="number"
              name="storage_capacity_kg"
              min="0"
              step="1"
              value={
                formData.storage_capacity_kg
              }
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "13px",
                border:
                  "1px solid #ccdcd6",
                borderRadius: "8px",
                fontSize: "16px",
                boxSizing: "border-box"
              }}
            />

          </div>


          {/* ===============================================
              SAVE
          =============================================== */}

          <button
            type="submit"
            className="primary-button"
            disabled={saving}
          >

            {saving
              ? "Saving..."
              : "Save Changes"
            }

          </button>

        </form>

      </section>


      {/* ===================================================
          CURRENT VALUES
      =================================================== */}

      <section
        className="dashboard-card"
        style={{
          marginTop: "28px"
        }}
      >

        <div className="card-header">

          <div>

            <h2>
              Current Decision Preferences
            </h2>

            <p>
              These values are used by VilaiNilai's
              optimization and negotiation systems.
            </p>

          </div>

        </div>


        <div className="recommendation-stats">


          <div>

            <span>
              Farmer ID
            </span>

            <strong>
              #{farmer.id}
            </strong>

          </div>


          <div>

            <span>
              Risk Preference
            </span>

            <strong>
              {farmer.risk_preference ||
                "MEDIUM"}
            </strong>

          </div>


          <div>

            <span>
              Storage Capacity
            </span>

            <strong>

              {Number(
                farmer.storage_capacity_kg || 0
              ).toLocaleString()} kg

            </strong>

          </div>


          <div>

            <span>
              Storage Cost
            </span>

            <strong>
              ₹0.30/kg/day
            </strong>

          </div>

        </div>

      </section>


      {/* ===================================================
          DECISION SYSTEM
      =================================================== */}

      <section
        className="dashboard-card"
        style={{
          marginTop: "28px"
        }}
      >

        <div className="card-header">

          <div>

            <h2>
              Decision System
            </h2>

            <p>
              Intelligence connected to your profile.
            </p>

          </div>

        </div>


        <div className="recommendation-stats">


          <div>

            <span>
              Price Forecasting
            </span>

            <strong>
              XGBoost
            </strong>

          </div>


          <div>

            <span>
              Allocation Optimization
            </span>

            <strong>
              OR-Tools
            </strong>

          </div>


          <div>

            <span>
              Negotiation
            </span>

            <strong>
              FairDeal
            </strong>

          </div>


          <div>

            <span>
              Decision Risk
            </span>

            <strong>
              {farmer.risk_preference ||
                "MEDIUM"}
            </strong>

          </div>


        </div>

      </section>


    </div>
  );
}


export default Settings;