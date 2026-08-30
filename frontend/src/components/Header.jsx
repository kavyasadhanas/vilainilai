import { useEffect, useState } from "react";

import {
  getFarmer,
  CURRENT_FARMER_ID
} from "../services/api";


function Header() {

  const [currentTime, setCurrentTime] =
    useState(new Date());

  const [farmer, setFarmer] =
    useState(null);


  /* =======================================================
     LIVE DATE AND TIME
  ======================================================= */

  useEffect(() => {

    const timer =
      setInterval(() => {

        setCurrentTime(
          new Date()
        );

      }, 1000);


    return () => {
      clearInterval(timer);
    };

  }, []);


  /* =======================================================
     LOAD FARMER PROFILE
  ======================================================= */

  useEffect(() => {

    async function loadFarmer() {

      try {

        const result =
          await getFarmer(
            CURRENT_FARMER_ID
          );

        setFarmer(result);

      } catch (err) {

        console.error(
          "Header farmer loading error:",
          err
        );

      }

    }

    loadFarmer();

  }, []);


  /* =======================================================
     DATE FORMAT
  ======================================================= */

  const dateText =
    currentTime.toLocaleDateString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric"
      }
    );


  /* =======================================================
     TIME FORMAT
  ======================================================= */

  const timeText =
    currentTime.toLocaleTimeString(
      "en-IN",
      {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true
      }
    );


  return (
    <header className="header">


      {/* ===================================================
          DATE AND TIME
      =================================================== */}

      <div className="header-date">

        <strong>
          {dateText}
        </strong>

        <span>
          •
        </span>

        <span>
          {timeText}
        </span>

      </div>


      {/* ===================================================
          RIGHT SIDE
      =================================================== */}

      <div className="header-right">


        {/* ===============================================
            WEATHER
        =============================================== */}

        <div className="header-weather">

          <span className="weather-icon">
            ☁️
          </span>

          <div>

            <strong>
              31°C
            </strong>

            <p>
              Partly Cloudy
            </p>

          </div>

        </div>


        {/* ===============================================
            NOTIFICATIONS
        =============================================== */}

        <button
          className="header-icon-button"
          type="button"
          aria-label="Notifications"
        >
          🔔
        </button>


        {/* ===============================================
            LANGUAGE
        =============================================== */}

        <button
          className="header-language"
          type="button"
          aria-label="Change language"
        >

          <span>
            English
          </span>

          <span>
            ⌄
          </span>

        </button>


        {/* ===============================================
            FARMER PROFILE
        =============================================== */}

        <button
          className="farmer-profile"
          type="button"
          aria-label="Open farmer profile"
        >

          <div className="profile-icon">
            ♙
          </div>

          <div className="profile-info">

            <strong>
              {farmer?.name ||
                `Farmer #${CURRENT_FARMER_ID}`}
            </strong>

            <span>
              Farmer
            </span>

          </div>

          <span className="profile-arrow">
            ⌄
          </span>

        </button>


      </div>

    </header>
  );
}


export default Header;