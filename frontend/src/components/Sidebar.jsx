function Sidebar() {
  return (
    <aside className="sidebar">

      {/* Logo */}
      <div className="logo-section">
        <h1>
          Vilai<span>Nilai</span>
        </h1>

        <p>
          Smart Decisions. Better Returns.
        </p>
      </div>


      {/* Navigation */}
      <nav className="sidebar-nav">

        <a className="sidebar-item active">
          <span className="nav-icon">▦</span>
          <span>Dashboard</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">📊</span>
          <span>Markets</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">📈</span>
          <span>Price Forecast</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">📊</span>
          <span>Harvest Planner</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">🌱</span>
          <span>My Crops</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">🏠</span>
          <span>Storage Planner</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">🔔</span>
          <span>Alerts</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">◷</span>
          <span>History</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">⚙</span>
          <span>Settings</span>
        </a>

        <a className="sidebar-item">
          <span className="nav-icon">?</span>
          <span>Help &amp; Support</span>
        </a>

      </nav>


      {/* Assistance Card */}
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


      {/* Bottom Illustration */}
      <div className="farm-image">
        <div className="farm-icons">
          🌾 🚜 🌱
        </div>
      </div>

    </aside>
  );
}

export default Sidebar;