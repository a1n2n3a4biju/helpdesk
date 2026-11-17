
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Sidebar from "./components/sidebar";
import Dashboard from "./pages/dashboard";
import RaiseTicket from "./pages/RaiseTicket";
import MyTickets from "./pages/MyTickets";
import SupportDashboard from "./pages/SupportDashboard";
import WorkQueue from "./pages/WorkQueue";
import AIRecommendations from "./pages/AIRecommendations";
import Settings from "./pages/Settings";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />

        <main className="main-area">
          <Routes>
            <Route path="/" element={<Navigate to="/employee/dashboard" replace />} />

            {/* Employee */}
            <Route path="/employee/dashboard" element={<Dashboard />} />
            <Route path="/raise-ticket" element={<RaiseTicket />} />
            <Route path="/my-tickets" element={<MyTickets />} />

            {/* Support Staff */}
            <Route path="/support/dashboard" element={<SupportDashboard />} />
            <Route path="/support/work-queue" element={<WorkQueue />} />
            <Route path="/support/ai-recommendations" element={<AIRecommendations />} />

            {/* Settings */}
            <Route path="/settings" element={<Settings />} />

            {/* Invalid URL */}
            <Route path="*" element={<Navigate to="/employee/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
