function HelpSupport() {
  return (
    <div className="dashboard-page">

      {/* =================================================
          PAGE HEADER
      ================================================= */}

      <section className="welcome-section">

        <h1>
          Help &amp; Support
        </h1>

        <p>
          Get assistance with VilaiNilai and
          your farm decisions.
        </p>

      </section>


      {/* =================================================
          QUICK HELP
      ================================================= */}

      <section className="stats-grid">

        <div className="stat-card">

          <div className="stat-icon">
            📊
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Markets
            </span>

            <span className="stat-value">
              Market comparison
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            📈
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Forecasts
            </span>

            <span className="stat-value">
              ML price prediction
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            🤖
          </div>

          <div className="stat-content">

            <span className="stat-label">
              Optimization
            </span>

            <span className="stat-value">
              Best selling strategy
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            🤝
          </div>

          <div className="stat-content">

            <span className="stat-label">
              FairDeal
            </span>

            <span className="stat-value">
              Buyer negotiation
            </span>

          </div>

        </div>

      </section>


      {/* =================================================
          HOW VILAINILAI WORKS
      ================================================= */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>

            <h2>
              How VilaiNilai Helps
            </h2>

            <p>
              Your decision journey from harvest
              to market.
            </p>

          </div>

        </div>


        <div className="store-content">

          <div className="store-option">

            <span>
              1. Harvest
            </span>

            <strong>
              Record crop and harvest details
            </strong>

          </div>


          <div className="store-option">

            <span>
              2. Forecast
            </span>

            <strong>
              Predict future market prices
            </strong>

          </div>


          <div className="store-option">

            <span>
              3. Optimize
            </span>

            <strong>
              Compare selling and storage options
            </strong>

          </div>


          <div className="store-option">

            <span>
              4. Negotiate
            </span>

            <strong>
              Evaluate buyer offers with FairDeal
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          SUPPORT
      ================================================= */}

      <section
        className="dashboard-card"
        style={{
          marginTop: "28px"
        }}
      >

        <div className="card-header">

          <div>

            <h2>
              Contact Support
            </h2>

            <p>
              Need assistance with the application?
            </p>

          </div>

          <span className="recommendation-icon">
            ☎
          </span>

        </div>


        <div className="recommendation-stats">

          <div>

            <span>
              Agriculture Expert
            </span>

            <strong>
              1800-309-5700
            </strong>

          </div>


          <div>

            <span>
              Availability
            </span>

            <strong>
              Support Centre
            </strong>

          </div>


          <div>

            <span>
              Application
            </span>

            <strong>
              VilaiNilai
            </strong>

          </div>


          <div>

            <span>
              Assistance
            </span>

            <strong>
              Farm Decision Support
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          FAQ
      ================================================= */}

      <section
        className="dashboard-card"
        style={{
          marginTop: "28px"
        }}
      >

        <div className="card-header">

          <div>

            <h2>
              Frequently Asked Questions
            </h2>

          </div>

        </div>


        <div className="store-content">

          <div className="store-option">

            <span>
              How is the market selected?
            </span>

            <strong>
              Market price, costs and expected return
              are compared.
            </strong>

          </div>


          <div className="store-option">

            <span>
              What is the price forecast?
            </span>

            <strong>
              It is generated using the XGBoost
              price forecasting model.
            </strong>

          </div>


          <div className="store-option">

            <span>
              What does storage analysis do?
            </span>

            <strong>
              It compares immediate selling with
              risk-adjusted future storage returns.
            </strong>

          </div>


          <div className="store-option">

            <span>
              What is FairDeal?
            </span>

            <strong>
              It calculates a reservation price and
              evaluates buyer offers.
            </strong>

          </div>

        </div>

      </section>

    </div>
  );
}

export default HelpSupport;