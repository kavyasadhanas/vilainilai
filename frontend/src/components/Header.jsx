function Header() {
  return (
    <header className="header">

      {/* Date and Time */}
      <div className="header-date">
        <strong>Today, 26 Aug 2026</strong>
        <span>•</span>
        <span>10:42 AM</span>
      </div>


      {/* Right Side */}
      <div className="header-right">

        {/* Weather */}
        <div className="header-weather">
          <span className="weather-icon">
            ☁️
          </span>

          <div>
            <strong>31°C</strong>
            <p>Partly Cloudy</p>
          </div>
        </div>


        {/* Notification */}
        <button
          className="header-icon-button"
          type="button"
          aria-label="Notifications"
        >
          🔔
        </button>


        {/* Language */}
        <button
          className="header-language"
          type="button"
          aria-label="Change language"
        >
          <span>தமிழ்</span>
          <span>⌄</span>
        </button>


        {/* Farmer Profile */}
        <button
          className="farmer-profile"
          type="button"
          aria-label="Open farmer profile"
        >

          <div className="profile-icon">
            ♙
          </div>

          <div className="profile-info">
            <strong>Kavya Sadhana</strong>
            <span>Farmer</span>
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