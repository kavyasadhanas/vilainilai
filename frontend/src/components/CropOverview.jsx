function CropOverview({ harvest }) {
  if (!harvest) {
    return (
      <div className="dashboard-card crop-overview">
        <div className="card-header">
          <h2>Your Crop Overview</h2>
        </div>

        <p>No harvest data available.</p>
      </div>
    );
  }

  const quantity =
    harvest.quantity_kg != null
      ? Number(harvest.quantity_kg).toLocaleString()
      : "-";

  const harvestDate = harvest.harvest_date || "-";

  const shelfLife =
    harvest.shelf_life_days != null
      ? `${harvest.shelf_life_days} days`
      : "-";

  return (
    <div className="dashboard-card crop-overview">

      {/* Card Header */}
      <div className="card-header">
        <h2>Your Crop Overview</h2>
      </div>

      {/* Crop Image */}
      <div className="crop-image">
        <div className="crop-emoji">
          🍅
        </div>
      </div>

      {/* Crop Details */}
      <div className="crop-details">

        <div className="detail-row">
          <span>Crop</span>
          <strong>
            {harvest.crop || "-"}
          </strong>
        </div>

        <div className="detail-row">
          <span>Quality</span>
          <strong>
            {harvest.quality || "-"}
          </strong>
        </div>

        <div className="detail-row">
          <span>Expected Quantity</span>
          <strong>
            {quantity} kg
          </strong>
        </div>

        <div className="detail-row">
          <span>Harvest Date</span>
          <strong>
            {harvestDate}
          </strong>
        </div>

        <div className="detail-row">
          <span>Shelf Life</span>
          <strong>
            {shelfLife}
          </strong>
        </div>

      </div>

      {/* Action Button */}
      <button
        type="button"
        className="primary-button"
      >
        View Full Crop Details
      </button>

    </div>
  );
}

export default CropOverview;