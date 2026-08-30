import React, {
  useEffect,
  useState
} from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline
} from "react-leaflet";

import L from "leaflet";

import {
  useSearchParams,
  useNavigate
} from "react-router-dom";

import {
  getMarketMap,
  CURRENT_FARMER_ID
} from "../services/api";

import "leaflet/dist/leaflet.css";
import "./Dashboard.css";


/* =======================================================
   LEAFLET ICON FIX
======================================================= */

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({

  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png"

});


function MapPage() {

  const [
    searchParams
  ] = useSearchParams();

  const navigate =
    useNavigate();


  /* =====================================================
     SELECTED HARVEST
  ===================================================== */

  const harvestId =
    searchParams.get(
      "harvest_id"
    );


  /* =====================================================
     STATE
  ===================================================== */

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =====================================================
     LOAD MAP DATA
  ===================================================== */

  useEffect(() => {

    async function loadMap() {

      try {

        setLoading(true);
        setError("");

        const result =
          await getMarketMap(

            CURRENT_FARMER_ID,

            harvestId
              ? Number(harvestId)
              : null

          );

        setData(
          result
        );

      } catch (err) {

        console.error(
          "Map loading error:",
          err
        );

        setError(
          err.message ||
          "Unable to load map information."
        );

      } finally {

        setLoading(false);

      }

    }

    loadMap();

  }, [harvestId]);


  /* =====================================================
     LOADING
  ===================================================== */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state">

          <h2>
            Loading market map...
          </h2>

          <p>
            Calculating distances and transport information.
          </p>

        </div>

      </div>
    );

  }


  /* =====================================================
     ERROR
  ===================================================== */

  if (error) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state error-state">

          <h2>
            Unable to load map
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


  /* =====================================================
     EMPTY
  ===================================================== */

  if (!data) {
    return null;
  }


  /* =====================================================
     DATA
  ===================================================== */

  const farmerLocation =
    data.farmer_location || {};

  const markets =
    Array.isArray(
      data.markets
    )
      ? data.markets
      : [];


  /* =====================================================
     FARMER POSITION
  ===================================================== */

  const farmerPosition = [

    Number(
      farmerLocation.latitude
    ),

    Number(
      farmerLocation.longitude
    )

  ];


  return (
    <div className="dashboard-page">


      {/* =================================================
          PAGE HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          Market Map
        </h1>

        <p>
          View market locations, distances,
          travel estimates and transport costs.
        </p>

        <p className="fairdeal-harvest-info">

          Harvest #{data.harvest_id} •{" "}
          {data.crop} •{" "}
          {data.variety || "Deshi"} •{" "}
          {Number(
            data.quantity_kg || 0
          ).toLocaleString()} kg

        </p>

      </section>


      {/* =================================================
          MAP
      ================================================= */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
                Farmer → Market Locations
            </h2>

            <p>
                Compare nearby markets using distance,
                travel time and transport cost.
            </p>

            <p
                className="fairdeal-harvest-info"
                style={{
                    marginTop: "6px"
                }}
            >
                Farmer location:{" "}
                {farmerLocation.name || "Unknown"}
                {" "}•{" "}
                {farmerLocation.is_approximate
                    ? "Approximate reference point"
                    : "Exact location"
                }
            </p>

          </div>

        </div>


        <div
          style={{
            height: "450px",
            width: "100%",
            borderRadius: "10px",
            overflow: "hidden"
          }}
        >

          <MapContainer
            center={farmerPosition}
            zoom={9}
            scrollWheelZoom={true}
            style={{
              height: "100%",
              width: "100%"
            }}
          >

            {/* =========================================
                MAP TILE
            ========================================= */}

            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />


            {/* =========================================
                FARMER MARKER
            ========================================= */}

            <Marker
              position={farmerPosition}
            >

              <Popup>

                <strong>
                  Farmer
                </strong>

                <br />

                {farmerLocation.name}

                <br />

                <small>
                  Approximate reference location
                </small>

              </Popup>

            </Marker>


            {/* =========================================
                MARKET MARKERS + ROUTES
            ========================================= */}

            {markets.map(
              (market) => {

                const marketPosition = [

                  Number(
                    market.latitude
                  ),

                  Number(
                    market.longitude
                  )

                ];


                return (

                  <React.Fragment
                    key={
                      market.market_id
                    }
                  >

                    {/* ===============================
                        MARKET MARKER
                    =============================== */}

                    <Marker
                      position={
                        marketPosition
                      }
                    >

                      <Popup>

                        <strong>
                          {market.market_name}
                        </strong>

                        <br />

                        {market.district}

                        <br />
                        <br />

                        Distance:
                        {" "}
                        {market.distance_km}
                        {" "}km

                        <br />

                        Travel:
                        {" "}
                        {
                          market
                            .estimated_travel_time_minutes
                        }
                        {" "}min

                        <br />

                        Transport:
                        {" "}
                        ₹
                        {Number(
                          market.transport_cost_per_kg
                        ).toFixed(2)}
                        /kg

                        <br />

                        Total Transport:
                        {" "}
                        ₹
                        {Number(
                          market
                            .estimated_total_transport_cost
                        ).toLocaleString()}

                      </Popup>

                    </Marker>


                    {/* ===============================
                        FARMER → MARKET LINE
                    =============================== */}

                    <Polyline
                      positions={[
                        farmerPosition,
                        marketPosition
                      ]}
                    />

                  </React.Fragment>

                );

              }
            )}

          </MapContainer>

        </div>


        {/* =================================================
            TRAVEL TIME NOTE
        ================================================= */}

        <p
          className="recommendation-reason"
          style={{
            marginTop: "12px"
          }}
        >

          {data.travel_time_note}

        </p>

      </section>


      {/* =================================================
          MARKET DETAILS
      ================================================= */}

      <section
        className="dashboard-card"
        style={{
          marginTop: "20px"
        }}
      >

        <div className="card-header">

          <div>

            <h2>
              Market Locations
            </h2>

            <p>
              Geographic and transport information.
            </p>

          </div>

        </div>


        {markets.length === 0 ? (

          <div className="dashboard-state">

            <h2>
              No market locations
            </h2>

            <p>
              No markets with geographic
              coordinates are available.
            </p>

          </div>

        ) : (

          <div className="buyer-offer-list">

            {markets.map(
              (market) => (

                <div
                  className="buyer-offer"
                  key={
                    `market-${market.market_id}`
                  }
                >

                  {/* =================================
                      MARKET
                  ================================= */}

                  <div>

                    <strong>
                      {market.market_name}
                    </strong>

                    <span>
                      {market.district}
                    </span>

                  </div>


                  {/* =================================
                      DISTANCE
                  ================================= */}

                  <div>

                    <strong>

                      {market.distance_km}
                      {" "}km

                    </strong>

                    <span>
                      Distance
                    </span>

                  </div>


                  {/* =================================
                      TRAVEL
                  ================================= */}

                  <div>

                    <strong>

                      {
                        market
                          .estimated_travel_time_minutes
                      }
                      {" "}min

                    </strong>

                    <span>
                      Estimated travel
                    </span>

                  </div>


                  {/* =================================
                      TRANSPORT
                  ================================= */}

                  <div>

                    <strong>

                      ₹
                      {Number(
                        market.transport_cost_per_kg
                      ).toFixed(2)}
                      /kg

                    </strong>

                    <span>

                      ₹
                      {Number(
                        market
                          .estimated_total_transport_cost
                      ).toLocaleString()}
                      {" "}total

                    </span>

                  </div>

                </div>

              )
            )}

          </div>

        )}

      </section>

    </div>
  );
}


export default MapPage;