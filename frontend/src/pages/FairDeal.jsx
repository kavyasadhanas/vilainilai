import { useEffect, useState } from "react";

import {
  getFairDeal,
  getAllHarvestOffers,
  updateBuyerOfferStatus,
  CURRENT_FARMER_ID
} from "../services/api";

import "./Dashboard.css";


function FairDeal() {

  const [data, setData] =
    useState(null);

  const [allOffers, setAllOffers] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [actionLoading, setActionLoading] =
    useState(null);

  const [actionMessage, setActionMessage] =
    useState("");

  const [counteroffers, setCounteroffers] =
    useState({});


  /* =======================================================
     LOAD FAIRDEAL DATA
  ======================================================= */

  async function loadData() {

    try {

      setLoading(true);
      setError("");

      const fairdealResult =
        await getFairDeal(
          CURRENT_FARMER_ID
        );

      const latestHarvestId =
        fairdealResult.harvest_id;

      if (!latestHarvestId) {

        throw new Error(
          "Latest harvest ID was not returned by the server."
        );

      }

      const offersResult =
        await getAllHarvestOffers(
          latestHarvestId
        );

      setData(
        fairdealResult
      );

      setAllOffers(
        Array.isArray(offersResult)
          ? offersResult
          : []
      );

    } catch (err) {

      console.error(
        "FairDeal loading error:",
        err
      );

      setError(
        err.message ||
        "Unable to load FairDeal."
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadData();

  }, []);


  /* =======================================================
     FIND FAIRDEAL EVALUATION
  ======================================================= */

  function getEvaluation(
    offerId
  ) {

    const evaluatedOffers =
      data?.fairdeal?.buyer_offers || [];

    return evaluatedOffers.find(
      (offer) =>
        offer.buyer_offer_id === offerId
    );

  }


  /* =======================================================
     HANDLE OFFER ACTION
  ======================================================= */

  async function handleOfferAction(
    offer,
    status
  ) {

    try {

      setActionLoading(
        offer.id
      );

      setActionMessage("");
      setError("");

      let counteroffer = null;


      /* ---------------------------------------------------
         COUNTEROFFER VALIDATION
      --------------------------------------------------- */

      if (
        status === "NEGOTIATING"
      ) {

        counteroffer =
          Number(
            counteroffers[
              offer.id
            ]
          );

        if (
          !counteroffer ||
          counteroffer <= 0
        ) {

          setError(
            "Please enter a valid counteroffer."
          );

          return;

        }

      }


      /* ---------------------------------------------------
         UPDATE OFFER
      --------------------------------------------------- */

      await updateBuyerOfferStatus(

        offer.id,

        status,

        counteroffer

      );


      /* ---------------------------------------------------
         SUCCESS MESSAGE
      --------------------------------------------------- */

      if (
        status === "ACCEPTED"
      ) {

        setActionMessage(
          "Offer accepted successfully."
        );

      } else if (
        status === "REJECTED"
      ) {

        setActionMessage(
          "Offer rejected successfully."
        );

      } else {

        setActionMessage(
          "Counteroffer saved successfully."
        );

      }


      /* ---------------------------------------------------
         RELOAD
      --------------------------------------------------- */

      await loadData();


    } catch (err) {

      console.error(
        "Offer action error:",
        err
      );

      setError(
        err.message ||
        "Unable to update buyer offer."
      );

    } finally {

      setActionLoading(
        null
      );

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
            Loading FairDeal...
          </h2>

          <p>
            Loading buyer offers and negotiation analysis.
          </p>

        </div>

      </div>
    );

  }


  /* =======================================================
     ERROR
  ======================================================= */

  if (error && !data) {

    return (
      <div className="dashboard-page">

        <div className="dashboard-state error-state">

          <h2>
            Unable to load FairDeal
          </h2>

          <p>
            {error}
          </p>

        </div>

      </div>
    );

  }


  if (!data) {
    return null;
  }


  /* =======================================================
     DATA
  ======================================================= */

  const fairdeal =
    data.fairdeal || {};


  const pendingOffers =
    allOffers.filter(
      (offer) =>
        offer.status === "PENDING"
    );


  const acceptedOffers =
    allOffers.filter(
      (offer) =>
        offer.status === "ACCEPTED"
    );


  const negotiatingOffers =
    allOffers.filter(
      (offer) =>
        offer.status === "NEGOTIATING"
    );


  const rejectedOffers =
    allOffers.filter(
      (offer) =>
        offer.status === "REJECTED"
    );


  return (
    <div className="dashboard-page">


      {/* =================================================
          PAGE HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          FairDeal
        </h1>

        <p>
          Evaluate buyer offers against your
          minimum acceptable price.
        </p>

        <p className="fairdeal-harvest-info">

          Harvest #{data.harvest_id} •{" "}
          {data.crop || "-"} •{" "}
          {data.variety || "-"} •{" "}
          {data.quantity_kg != null
            ? Number(
                data.quantity_kg
              ).toLocaleString()
            : "-"
          } kg

        </p>

      </section>


      {/* =================================================
          SUCCESS MESSAGE
      ================================================= */}

      {actionMessage && (

        <div className="market-insight">

          <div className="insight-icon">
            ✓
          </div>

          <div>

            <strong>
              FairDeal Updated
            </strong>

            <p>
              {actionMessage}
            </p>

          </div>

        </div>

      )}


      {/* =================================================
          ERROR MESSAGE
      ================================================= */}

      {error && (

        <div
          className="form-error-box"
          style={{
            marginBottom: "15px"
          }}
        >
          {error}
        </div>

      )}


      {/* =================================================
          FAIRDEAL SUMMARY
      ================================================= */}

      <section className="stats-grid">


        <div className="stat-card">

          <div className="stat-icon">
            🎯
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Best Alternative
            </span>

            <span className="stat-value">
              {fairdeal.best_alternative || "-"}
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            💰
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Alternative Value
            </span>

            <span className="stat-value">

              ₹
              {fairdeal.alternative_value_per_kg != null
                ? Number(
                    fairdeal.alternative_value_per_kg
                  ).toFixed(2)
                : "-"
              }
              /kg

            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            🛡️
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Reservation Price
            </span>

            <span className="stat-value">

              ₹
              {fairdeal.reservation_price != null
                ? Number(
                    fairdeal.reservation_price
                  ).toFixed(2)
                : "-"
              }
              /kg

            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            🤝
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Total Offers
            </span>

            <span className="stat-value">
              {allOffers.length}
            </span>

          </div>

        </div>

      </section>


      {/* =================================================
          RESERVATION PRICE
      ================================================= */}

      <section className="dashboard-card recommendation-card">

        <div className="recommendation-header">

          <div>

            <span className="best-choice">
              MINIMUM ACCEPTABLE PRICE
            </span>

            <h3>

              ₹
              {fairdeal.reservation_price != null
                ? Number(
                    fairdeal.reservation_price
                  ).toFixed(2)
                : "-"
              }
              /kg

            </h3>

          </div>

          <span className="recommendation-icon">
            🎯
          </span>

        </div>


        <div className="recommendation-stats">

          <div>

            <span>
              Best Alternative
            </span>

            <strong>
              {fairdeal.best_alternative || "-"}
            </strong>

          </div>


          <div>

            <span>
              Alternative Value
            </span>

            <strong>

              ₹
              {fairdeal.alternative_value_per_kg != null
                ? Number(
                    fairdeal.alternative_value_per_kg
                  ).toFixed(2)
                : "-"
              }
              /kg

            </strong>

          </div>


          <div>

            <span>
              Risk Preference
            </span>

            <strong>
              {fairdeal.risk_preference || "-"}
            </strong>

          </div>


          <div>

            <span>
              Risk Adjustment
            </span>

            <strong>

              ₹
              {fairdeal.risk_adjustment != null
                ? Number(
                    fairdeal.risk_adjustment
                  ).toFixed(2)
                : "-"
              }
              /kg

            </strong>

          </div>

        </div>


        <p className="recommendation-reason">

          FairDeal uses the best active non-buyer
          alternative as the economic benchmark and
          applies the farmer's risk preference to
          calculate the reservation price.

        </p>

      </section>


      {/* =================================================
          OFFER STATUS
      ================================================= */}

      <section
        className="stats-grid"
        style={{
          marginTop: "18px"
        }}
      >

        <div className="stat-card">

          <div className="stat-icon">
            ⏳
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Pending
            </span>

            <span className="stat-value">
              {pendingOffers.length}
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            ✅
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Accepted
            </span>

            <span className="stat-value">
              {acceptedOffers.length}
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            💬
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Negotiating
            </span>

            <span className="stat-value">
              {negotiatingOffers.length}
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            ❌
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Rejected
            </span>

            <span className="stat-value">
              {rejectedOffers.length}
            </span>

          </div>

        </div>

      </section>


      {/* =================================================
          BUYER OFFERS
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
              Buyer Offers
            </h2>

            <p>
              Current and historical offers for
              Harvest #{data.harvest_id}.
            </p>

          </div>

        </div>


        {allOffers.length === 0 ? (

          <div className="dashboard-state">

            <h2>
              No buyer offers
            </h2>

            <p>
              Buyer offers will appear here
              when they are received.
            </p>

          </div>

        ) : (

          <div className="fairdeal-offer-list">

            {allOffers.map(
              (offer) => {

                const evaluation =
                  getEvaluation(
                    offer.id
                  );


                const decision =
                  evaluation?.decision ||
                  null;


                const buyerName =
                  offer.buyer_name ||
                  evaluation?.buyer_name ||
                  `Buyer #${offer.buyer_id}`;


                const isPending =
                  offer.status === "PENDING";


                return (

                  <article
                    className="fairdeal-offer"
                    key={offer.id}
                  >


                    {/* =================================
                        OFFER HEADER
                    ================================= */}

                    <div className="fairdeal-offer-header">

                      <div>

                        <span className="best-choice">
                          OFFER #{offer.id}
                        </span>

                        <h3>
                          {buyerName}
                        </h3>

                        <p>
                          {Number(
                            offer.quantity_kg || 0
                          ).toLocaleString()}
                          {" "}kg
                        </p>

                      </div>


                      <span
                        className={
                          `offer-status ${(
                            offer.status || ""
                          ).toLowerCase()}`
                        }
                      >

                        {offer.status === "ACCEPTED" &&
                          "✓ Accepted"
                        }

                        {offer.status === "NEGOTIATING" &&
                          "↔ Negotiating"
                        }

                        {offer.status === "REJECTED" &&
                          "✕ Rejected"
                        }

                        {offer.status === "PENDING" &&
                          "● Pending"
                        }

                      </span>

                    </div>


                    {/* =================================
                        OFFER INFORMATION
                    ================================= */}

                    <div className="recommendation-stats">

                      <div>

                        <span>
                          Offered Price
                        </span>

                        <strong>

                          ₹
                          {Number(
                            offer.offered_price_per_kg || 0
                          ).toFixed(2)}
                          /kg

                        </strong>

                      </div>


                      <div>

                        <span>
                          Quantity
                        </span>

                        <strong>

                          {Number(
                            offer.quantity_kg || 0
                          ).toLocaleString()}
                          {" "}kg

                        </strong>

                      </div>


                      <div>

                        <span>
                          Status
                        </span>

                        <strong>
                          {offer.status}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Counteroffer
                        </span>

                        <strong>

                          {offer.counteroffer_per_kg != null
                            ? (
                              <>
                                ₹
                                {Number(
                                  offer.counteroffer_per_kg
                                ).toFixed(2)}
                                /kg
                              </>
                            )
                            : "-"
                          }

                        </strong>

                      </div>

                    </div>


                    {/* =================================
                        FAIRDEAL EVALUATION
                    ================================= */}

                    {evaluation && (

                      <div className="market-insight">

                        <div className="insight-icon">
                          💡
                        </div>

                        <div>

                          <strong>
                            FairDeal Evaluation
                          </strong>

                          <p>

                            {decision}
                            {" • "}
                            Reservation ₹
                            {Number(
                              evaluation.reservation_price || 0
                            ).toFixed(2)}
                            /kg
                            {" • "}
                            Difference{" "}
                            {evaluation.price_difference >= 0
                              ? "+"
                              : ""
                            }
                            ₹
                            {Number(
                              evaluation.price_difference || 0
                            ).toFixed(2)}
                            /kg

                          </p>

                        </div>

                      </div>

                    )}


                    {/* =================================
                        ACTIONS
                    ================================= */}

                    {isPending &&
                      evaluation && (

                      <div className="fairdeal-actions">


                        {/* ---------------------------------
                            ACCEPT / REJECT
                        --------------------------------- */}

                        {decision === "ACCEPT" && (

                          <>
                            <button
                              className="primary-button"
                              disabled={
                                actionLoading ===
                                offer.id
                              }
                              onClick={() =>
                                handleOfferAction(
                                  offer,
                                  "ACCEPTED"
                                )
                              }
                            >

                              {actionLoading ===
                              offer.id
                                ? "Processing..."
                                : "Accept Offer"
                              }

                            </button>


                            <button
                              className="secondary-danger-button"
                              disabled={
                                actionLoading ===
                                offer.id
                              }
                              onClick={() =>
                                handleOfferAction(
                                  offer,
                                  "REJECTED"
                                )
                              }
                            >
                              Reject
                            </button>
                          </>

                        )}


                        {/* ---------------------------------
                            NEGOTIATE
                        --------------------------------- */}

                        {decision === "NEGOTIATE" && (

                          <div className="fairdeal-negotiate">

                            <div>

                              <label>
                                Counteroffer per kg
                              </label>

                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                value={
                                  counteroffers[
                                    offer.id
                                  ] || ""
                                }
                                onChange={(event) =>
                                  setCounteroffers(
                                    previous => ({
                                      ...previous,

                                      [offer.id]:
                                        event.target.value
                                    })
                                  )
                                }
                                placeholder="Enter amount"
                              />

                            </div>


                            <button
                              className="primary-button"
                              disabled={
                                actionLoading ===
                                offer.id
                              }
                              onClick={() =>
                                handleOfferAction(
                                  offer,
                                  "NEGOTIATING"
                                )
                              }
                            >

                              {actionLoading ===
                              offer.id
                                ? "Saving..."
                                : "Send Counteroffer"
                              }

                            </button>

                          </div>

                        )}


                        {/* ---------------------------------
                            REJECT
                        --------------------------------- */}

                        {decision === "REJECT" && (

                          <button
                            className="secondary-danger-button"
                            disabled={
                              actionLoading ===
                              offer.id
                            }
                            onClick={() =>
                              handleOfferAction(
                                offer,
                                "REJECTED"
                              )
                            }
                          >

                            {actionLoading ===
                            offer.id
                              ? "Processing..."
                              : "Reject Offer"
                            }

                          </button>

                        )}

                      </div>

                    )}


                    {/* =================================
                        NEGOTIATION RESULT
                    ================================= */}

                    {offer.status === "NEGOTIATING" && (

                      <div className="store-content">

                        <div className="store-option">

                          <span>
                            Counteroffer
                          </span>

                          <strong>

                            ₹
                            {offer.counteroffer_per_kg != null
                              ? Number(
                                  offer.counteroffer_per_kg
                                ).toFixed(2)
                              : "-"
                            }
                            /kg

                          </strong>

                        </div>

                      </div>

                    )}


                    {/* =================================
                        EXPLANATION
                    ================================= */}

                    {evaluation?.explanation && (

                      <p className="recommendation-reason">

                        {evaluation.explanation}

                      </p>

                    )}

                  </article>

                );

              }
            )}

          </div>

        )}

      </section>


    </div>
  );
}


export default FairDeal;