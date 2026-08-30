import { NavLink } from "react-router-dom";


function Sidebar() {

  return (
    <aside className="sidebar">

      {/* =================================================
          LOGO
      ================================================= */}

      <div className="logo-section">

        <h1>
          Vilai<span>Nilai</span>
        </h1>

        <p>
          Smart Decisions. Better Returns.
        </p>

      </div>


      {/* =================================================
          NAVIGATION
      ================================================= */}

      <nav className="sidebar-nav">

        <NavLink
          to="/dashboard"
          className="sidebar-item"
        >
          <span className="nav-icon">
            ▦
          </span>
          <span>
            Dashboard
          </span>
        </NavLink>


        <NavLink
          to="/markets"
          className="sidebar-item"
        >
          <span className="nav-icon">
            📊
          </span>
          <span>
            Markets
          </span>
        </NavLink>


        <NavLink
          to="/price-forecast"
          className="sidebar-item"
        >
          <span className="nav-icon">
            📈
          </span>
          <span>
            Price Forecast
          </span>
        </NavLink>


        <NavLink
          to="/harvest-planner"
          className="sidebar-item"
        >
          <span className="nav-icon">
            📋
          </span>
          <span>
            Harvest Planner
          </span>
        </NavLink>


        <NavLink
          to="/my-crops"
          className="sidebar-item"
        >
          <span className="nav-icon">
            🌱
          </span>
          <span>
            My Crops
          </span>
        </NavLink>


        <NavLink
          to="/storage-planner"
          className="sidebar-item"
        >
          <span className="nav-icon">
            🏠
          </span>
          <span>
            Storage Planner
          </span>
        </NavLink>


        <NavLink
          to="/fairdeal"
          className="sidebar-item"
        >
          <span className="nav-icon">
            🤝
          </span>
          <span>
            FairDeal
          </span>
        </NavLink>


        <NavLink
          to="/alerts"
          className="sidebar-item"
        >
          <span className="nav-icon">
            🔔
          </span>
          <span>
            Alerts
          </span>
        </NavLink>


        <NavLink
          to="/history"
          className="sidebar-item"
        >
          <span className="nav-icon">
            ◷
          </span>
          <span>
            History
          </span>
        </NavLink>


        <NavLink
          to="/help"
          className="sidebar-item"
        >
          <span className="nav-icon">
            ?
          </span>
          <span>
            Help &amp; Support
          </span>
        </NavLink>

      </nav>


      {/* =================================================
          ASSISTANCE CARD
      ================================================= */}

      <div className="assistance-card">

        <h3>
          Need Assistance?
        </h3>

        <p>
          Contact our agriculture expert
        </p>

        <strong>
          ☎ 1800-309-5700
        </strong>

      </div>

    </aside>
  );
}


export default Sidebar;