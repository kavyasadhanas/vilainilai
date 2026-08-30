const API_BASE_URL =
  "http://127.0.0.1:8000";


/* =========================================================
   CURRENT FARMER
========================================================= */

export const CURRENT_FARMER_ID = 1;


/* =========================================================
   DASHBOARD
========================================================= */

export async function getFarmerDashboard(
  farmerId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/dashboard/${farmerId}`
    );

  if (!response.ok) {

    throw new Error(
      `Dashboard request failed: ${response.status}`
    );

  }

  return await response.json();
}


/* =========================================================
   MARKET RECOMMENDATION
========================================================= */

export async function getMarketRecommendation(
  crop,
  variety,
  quantityKg
) {

  const response =
    await fetch(
      `${API_BASE_URL}/recommendations/market`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json"
        },

        body: JSON.stringify({

          crop: crop,

          variety: variety,

          quantity_kg: Number(
            quantityKg
          )

        })

      }
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Market recommendation request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   PRICE FORECAST
========================================================= */

export async function getPriceForecast(
  market,
  district,
  variety,
  quantityKg,
  predictionDate = null
) {

  const response =
    await fetch(
      `${API_BASE_URL}/forecast/price`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json"
        },

        body: JSON.stringify({

          market: market,

          district: district,

          variety: variety,

          arrival_quantity_kg:
            Number(quantityKg),

          prediction_date:
            predictionDate

        })

      }
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Price forecast request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   HARVEST
========================================================= */

export async function getHarvest(
  harvestId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/harvests/${harvestId}`
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Harvest request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   CREATE HARVEST
========================================================= */

export async function createHarvest(
  harvestData
) {

  const response =
    await fetch(
      `${API_BASE_URL}/harvests/`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json"
        },

        body: JSON.stringify({

          farmer_id:
            Number(
              harvestData.farmer_id
            ),

          crop:
            harvestData.crop,

          variety:
            harvestData.variety,

          quantity_kg:
            Number(
              harvestData.quantity_kg
            ),

          quality:
            harvestData.quality,

          harvest_date:
            harvestData.harvest_date,

          shelf_life_days:
            Number(
              harvestData.shelf_life_days
              ?? 5
            )

        })

      }
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Harvest creation failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   FARMER HARVESTS
========================================================= */

export async function getFarmerHarvests(
  farmerId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/farmers/${farmerId}/harvests`
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Farmer harvests request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   STORAGE ANALYSIS
========================================================= */

export async function getStorageAnalysis(
  farmerId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/optimization/storage/${farmerId}`
    );


  if (!response.ok) {

    throw new Error(
      `Storage analysis request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   HISTORY
========================================================= */

export async function getFarmerHistory(
  farmerId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/history/${farmerId}`
    );


  if (!response.ok) {

    throw new Error(
      `History request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   FARMER
========================================================= */

export async function getFarmer(
  farmerId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/farmers/${farmerId}`
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Farmer request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   BUYER OFFERS
========================================================= */

export async function getHarvestBuyerOffers(
  harvestId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/buyers/harvests/${harvestId}/offers`
    );


  if (!response.ok) {

    throw new Error(
      `Buyer offers request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   ALL BUYER OFFERS
========================================================= */

export async function getAllHarvestOffers(
  harvestId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/buyers/harvests/${harvestId}/all-offers`
    );


  if (!response.ok) {

    throw new Error(
      `All buyer offers request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   FAIRDEAL
========================================================= */

export async function getFairDeal(
  farmerId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/fairdeal/${farmerId}`
    );


  if (!response.ok) {

    throw new Error(
      `FairDeal request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   UPDATE BUYER OFFER STATUS
========================================================= */

export async function updateBuyerOfferStatus(
  offerId,
  status,
  counterofferPerKg = null
) {

  const params =
    new URLSearchParams();


  params.append(
    "status",
    status
  );


  if (
    counterofferPerKg !== null
  ) {

    params.append(
      "counteroffer_per_kg",
      counterofferPerKg
    );

  }


  const response =
    await fetch(
      `${API_BASE_URL}/buyers/offers/${offerId}/status?${params.toString()}`,
      {
        method: "PATCH"
      }
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Offer update failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   STORAGE FOR SELECTED HARVEST
========================================================= */

export async function getHarvestStorageAnalysis(
  harvestId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/optimization/storage/harvest/${harvestId}`
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Harvest storage analysis request failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   UPDATE FARMER
========================================================= */

export async function updateFarmer(
  farmerId,
  farmerData
) {

  const response =
    await fetch(
      `${API_BASE_URL}/farmers/${farmerId}`,
      {
        method: "PATCH",

        headers: {
          "Content-Type":
            "application/json"
        },

        body: JSON.stringify({

          name:
            farmerData.name,

          location:
            farmerData.location,

          risk_preference:
            farmerData.risk_preference,

          storage_capacity_kg:
            Number(
              farmerData.storage_capacity_kg
            )

        })

      }
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Farmer update failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   WHAT-IF SIMULATION
========================================================= */

export async function simulateWhatIf(
  farmerId,
  scenario
) {

  const response =
    await fetch(
      `${API_BASE_URL}/optimization/what-if/${farmerId}`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json"
        },

        body: JSON.stringify({

          harvest_id:
            scenario.harvest_id ?? null,

          price_change_pct:
            Number(
              scenario.price_change_pct || 0
            ),

          transport_change_per_kg:
            Number(
              scenario.transport_change_per_kg || 0
            ),

          storage_capacity_kg:
            scenario.storage_capacity_kg === null ||
            scenario.storage_capacity_kg === undefined ||
            scenario.storage_capacity_kg === ""
              ? null
              : Number(
                  scenario.storage_capacity_kg
                ),

          spoilage_risk_pct:
            Number(
              scenario.spoilage_risk_pct || 0
            )

        })

      }
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `What-if simulation failed: ${response.status}`
    );

  }


  return await response.json();
}


/* =========================================================
   MARKET MAP
========================================================= */

export async function getMarketMap(
  farmerId,
  harvestId = null
) {

  const query =
    harvestId !== null
      ? `?harvest_id=${harvestId}`
      : "";


  const response =
    await fetch(
      `${API_BASE_URL}/optimization/map/${farmerId}${query}`
    );


  if (!response.ok) {

    const errorData =
      await response
        .json()
        .catch(() => null);

    throw new Error(
      errorData?.detail ||
      `Market map request failed: ${response.status}`
    );

  }


  return await response.json();
}