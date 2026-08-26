function StatCard({ icon, label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">
        {icon}
      </div>

      <div className="stat-content">
        <span className="stat-label">
          {label}
        </span>

        <strong className="stat-value">
          {value}
        </strong>
      </div>
    </div>
  );
}

export default StatCard;