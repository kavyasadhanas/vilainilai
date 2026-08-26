const API_BASE_URL = "http://127.0.0.1:8000";

export async function getFarmerDashboard(farmerId) {
  const response = await fetch(
    `${API_BASE_URL}/dashboard/${farmerId}`
  );

  if (!response.ok) {
    throw new Error(
      `Dashboard request failed: ${response.status}`
    );
  }

  const data = await response.json();

  return data;
}