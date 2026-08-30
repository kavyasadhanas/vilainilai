import { useEffect, useState } from "react";

import {
  getBuyers,
  getAvailableBuyerHarvests,
  createBuyerOffer
} from "../services/api";

import "./Dashboard.css";


function BuyerPortal() {

  const [buyers, setBuyers] =
    useState([]);

  const [harvests, setHarvests] =
    useState([]);

  const [selectedBuyer, setSelectedBuyer] =
    useState("");

  const [selectedHarvest, setSelectedHarvest] =
    useState(null);

  const [quantity, setQuantity] =
    useState("");

  const [price, setPrice] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD BUYERS + HARVESTS
  ======================================================= */

  useEffect(() => {

    async function loadData() {

      try {

        setLoading(true);
        setError("");

        const [
          buyerResult,
          harvestResult
        ] = await Promise.all([

          getBuyers(),

          getAvailableBuyerHarvests()

        ]);


        setBuyers(
          Array.isArray(
            buyerResult
          )
            ? buyerResult
            : []
        );


        setHarvests(
          Array.isArray(
            harvestResult
          )
            ? harvestResult
            : []
        );


        if (
          Array.isArray(
            buyerResult
          ) &&
          buyerResult.length > 0
        ) {

          setSelectedBuyer(
            String(
              buyerResult[0].id
            )
          );

        }

      } catch (err) {

        console.error(
          "Buyer portal loading error:",
          err
        );

        setError(
          err.message ||
          "Unable to load buyer portal."
        );

      } finally {

        setLoading(false);

      }

    }


    loadData();

  }, []);


  /* =======================================================
     SELECT HARVEST
  ======================================================= */

  function handleSelectHarvest(
    harvest
  ) {

    setSelectedHarvest(
      harvest
    );

    setQuantity("");

    setPrice("");

    setMessage("");

    setError("");

    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });

  }


  /* =======================================================
     SUBMIT OFFER
  ======================================================= */

  async function handleSubmit(
    event
  ) {

    event.preventDefault();

    setMessage("");
    setError("");


    if (!selectedBuyer) {

      setError(
        "Please select a buyer."
      );

      return;

    }


    if (!selectedHarvest) {

      setError(
        "Please select a harvest."
      );

      return;

    }


    const quantityNumber =
      Number(
        quantity
      );

    const priceNumber =
      Number(
        price
      );


    if (
      !Number.isFinite(
        quantityNumber
      ) ||
      quantityNumber <= 0
    ) {

      setError(
        "Please enter a valid quantity."
      );

      return;

    }


    if (
      quantityNumber >
      Number(
        selectedHarvest.quantity_kg
      )
    ) {

      setError(
        "Offer quantity cannot exceed the harvest quantity."
      );

      return;

    }


    if (
      !Number.isFinite(
        priceNumber
      ) ||
      priceNumber <= 0
    ) {

      setError(
        "Please enter a valid offered price."
      );

      return;

    }


    try {

      setSubmitting(true);


      await createBuyerOffer({

        buyer_id:
          Number(
            selectedBuyer
          ),

        harvest_id:
          Number(
            selectedHarvest.id
          ),

        offered_price_per_kg:
          priceNumber,

        quantity_kg:
          quantityNumber

      });


      setMessage(
        "Offer submitted successfully. The farmer can now review it in FairDeal."
      );


      setQuantity("");
      setPrice("");

    } catch (err) {

      console.error(
        "Offer submission error:",
        err
      );

      setError(
        err.message ||
        "Unable to submit offer."
      );

    } finally {

      setSubmitting(false);

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
            Loading buyer portal...
          </h2>

          <p>
            Finding available harvests.
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     PAGE
  ======================================================= */

  return (
    <div className="dashboard-page">

      <section
        className="welcome-section dashboard-welcome"
      >

        <div>

          <h1>
            Buyer Portal 🛒
          </h1>

          <p>
            Browse available harvests and make a purchase offer.
          </p>

        </div>

      </section>


      {/* =================================================
          BUYER PROFILE
      ================================================= */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
              Buyer Profile
            </h2>

            <p>
              Select the buyer making the offer.
            </p>

          </div>

        </div>


        <div className="form-field">

          <label>
            Buyer
          </label>

          <select
            value={selectedBuyer}
            onChange={(event) =>
              setSelectedBuyer(
                event.target.value
              )
            }
          >

            <option value="">
              Select buyer
            </option>

            {buyers.map(
              (buyer) => (

                <option
                  key={buyer.id}
                  value={buyer.id}
                >
                  {buyer.name}
                  {buyer.location
                    ? ` — ${buyer.location}`
                    : ""
                  }
                </option>

              )
            )}

          </select>

        </div>

      </section>


      {/* =================================================
          OFFER FORM
      ================================================= */}

      {selectedHarvest && (

        <section className="dashboard-card">

          <div className="card-header">

            <div>

              <h2>
                Make an Offer
              </h2>

              <p>
                Submit your proposed price and quantity.
              </p>

            </div>

          </div>


          <div
            className="form-info-box"
            style={{
              marginBottom: "18px"
            }}
          >

            <div className="form-info-icon">
              🌾
            </div>

            <div>

              <strong>
                {selectedHarvest.crop}
                {" • "}
                {selectedHarvest.variety || "Local"}
              </strong>

              <p>
                Available:
                {" "}
                {Number(
                  selectedHarvest.quantity_kg
                ).toLocaleString()}
                {" kg"}
                {" • "}
                {selectedHarvest.quality || "Quality not specified"}
              </p>

            </div>

          </div>


          <form
            onSubmit={
              handleSubmit
            }
          >

            <div className="input-form-grid">

              {/* Quantity */}

              <div className="form-field">

                <label>
                  Offer Quantity (kg)
                </label>

                <div className="input-with-suffix">

                  <input
                    type="number"
                    min="1"
                    max={
                      selectedHarvest.quantity_kg
                    }
                    step="1"
                    value={quantity}
                    onChange={(event) =>
                      setQuantity(
                        event.target.value
                      )
                    }
                    placeholder="Enter quantity"
                  />

                  <span>
                    kg
                  </span>

                </div>

              </div>


              {/* Price */}

              <div className="form-field">

                <label>
                  Offered Price (₹/kg)
                </label>

                <div className="input-with-suffix">

                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={price}
                    onChange={(event) =>
                      setPrice(
                        event.target.value
                      )
                    }
                    placeholder="Enter price"
                  />

                  <span>
                    ₹/kg
                  </span>

                </div>

              </div>

            </div>


            {message && (

              <div
                className="form-info-box"
                style={{
                  marginTop: "16px"
                }}
              >
                ✅ {message}
              </div>

            )}


            {error && (

              <div
                className="form-error-box"
                style={{
                  marginTop: "16px"
                }}
              >
                {error}
              </div>

            )}


            <div
              className="form-action"
              style={{
                marginTop: "18px"
              }}
            >

              <button
                type="submit"
                className="primary-button"
                disabled={submitting}
              >

                {submitting
                  ? "Submitting..."
                  : "Submit Offer"
                }

                {!submitting && (
                  <span>
                    →
                  </span>
                )}

              </button>

              <button
                type="button"
                className="view-all"
                onClick={() =>
                  setSelectedHarvest(
                    null
                  )
                }
              >
                Cancel
              </button>

            </div>

          </form>

        </section>

      )}


      {/* =================================================
          AVAILABLE HARVESTS
      ================================================= */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
              Available Harvests
            </h2>

            <p>
              Select a harvest to make a buyer offer.
            </p>

          </div>

        </div>


        {harvests.length === 0 ? (

          <div
            className="dashboard-state"
            style={{
              minHeight: "180px"
            }}
          >

            <h2>
              No harvests available
            </h2>

            <p>
              No farmer harvests are currently available for offers.
            </p>

          </div>

        ) : (

          <div
            style={{
              display: "grid",
              gap: "12px"
            }}
          >

            {harvests.map(
              (harvest) => (

                <div
                  key={harvest.id}
                  className="summary-item"
                  style={{
                    border:
                      selectedHarvest?.id ===
                      harvest.id
                        ? "2px solid #079447"
                        : undefined,
                    borderRadius: "12px",
                    padding: "14px",
                    cursor: "pointer"
                  }}
                  onClick={() =>
                    handleSelectHarvest(
                      harvest
                    )
                  }
                >

                  <span className="summary-item-icon">
                    🌱
                  </span>

                  <div
                    style={{
                      flex: 1
                    }}
                  >

                    <span>
                      Harvest #{harvest.id}
                    </span>

                    <strong>
                      {harvest.crop}
                      {" • "}
                      {harvest.variety || "Local"}
                    </strong>

                    <span>
                      {Number(
                        harvest.quantity_kg
                      ).toLocaleString()}
                      {" kg"}
                      {" • "}
                      {harvest.quality || "Quality not specified"}
                    </span>

                  </div>


                  <button
                    type="button"
                    className="primary-button"
                    onClick={(event) => {

                      event.stopPropagation();

                      handleSelectHarvest(
                        harvest
                      );

                    }}
                  >
                    Make Offer →
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


export default BuyerPortal;