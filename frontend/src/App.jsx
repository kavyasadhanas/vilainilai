import {
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Dashboard from "./pages/Dashboard";
import Markets from "./pages/Markets";
import PriceForecast from "./pages/PriceForecast";
import HarvestPlanner from "./pages/HarvestPlanner";
import MyCrops from "./pages/MyCrops";
import StoragePlanner from "./pages/StoragePlanner";
import Alerts from "./pages/Alerts";
import History from "./pages/History";
import Settings from "./pages/Settings";
import HelpSupport from "./pages/HelpSupport";
import FairDeal from "./pages/FairDeal";
import WhatIfSimulation from "./pages/WhatIfSimulation";
import MapPage from "./pages/Map";
import BuyerPortal from "./pages/BuyerPortal";

import "./App.css";
import "./pages/Dashboard.css";


function App() {

  return (
    <div className="app-layout">

      {/* =================================================
          FIXED SIDEBAR
      ================================================= */}

      <Sidebar />


      {/* =================================================
          MAIN APPLICATION AREA
      ================================================= */}

      <div className="main-content">

        {/* ===============================================
            HEADER
        =============================================== */}

        <Header />


        {/* ===============================================
            SCROLLABLE PAGE CONTENT
        =============================================== */}

        <main className="page-content">

          <Routes>

            {/* =========================================
                DASHBOARD
            ========================================= */}

            <Route
              path="/dashboard"
              element={<Dashboard />}
            />


            {/* =========================================
                MARKETS
            ========================================= */}

            <Route
              path="/markets"
              element={<Markets />}
            />


            {/* =========================================
                PRICE FORECAST
            ========================================= */}

            <Route
              path="/price-forecast"
              element={<PriceForecast />}
            />


            {/* =========================================
                HARVEST PLANNER
            ========================================= */}

            <Route
              path="/harvest-planner"
              element={<HarvestPlanner />}
            />

            <Route
              path="/harvest-planner/:harvestId"
              element={<HarvestPlanner />}
            />


            {/* =========================================
                MY CROPS
            ========================================= */}

            <Route
              path="/my-crops"
              element={<MyCrops />}
            />


            {/* =========================================
                STORAGE PLANNER
            ========================================= */}

            <Route
              path="/storage-planner"
              element={<StoragePlanner />}
            />


            {/* =========================================
                FAIRDEAL
            ========================================= */}

            <Route
              path="/fairdeal"
              element={<FairDeal />}
            />


            {/* =========================================
                ALERTS
            ========================================= */}

            <Route
              path="/alerts"
              element={<Alerts />}
            />


            {/* =========================================
                HISTORY
            ========================================= */}

            <Route
              path="/history"
              element={<History />}
            />


            {/* =========================================
                SETTINGS
            ========================================= */}

            <Route
              path="/settings"
              element={<Settings />}
            />


            {/* =========================================
                HELP & SUPPORT
            ========================================= */}

            <Route
              path="/help"
              element={<HelpSupport />}
            />


            {/* =========================================
                DEFAULT
            ========================================= */}

            <Route
              path="/"
              element={
                <Navigate
                  to="/dashboard"
                  replace
                />
              }
            />

            <Route
              path="/what-if"
                element={
                  <WhatIfSimulation />
                }
            />  

            <Route
              path="/map"
                element={
                  <MapPage />
                }
            />

            <Route
              path="/buyer-portal"
                element={<BuyerPortal />}
            />

          </Routes>

        </main>

      </div>

    </div>
  );
}


export default App;