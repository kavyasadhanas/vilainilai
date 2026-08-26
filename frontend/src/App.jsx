import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";

import "./App.css";

function App() {
  return (
    <div className="app">
      <Sidebar />

      <div className="main-area">
        <Header />

        <main className="page-content">
          <Dashboard />
        </main>
      </div>
    </div>
  );
}

export default App;