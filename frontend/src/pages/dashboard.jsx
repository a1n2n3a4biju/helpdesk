import React, { useEffect, useState } from "react";
import {
  Ticket,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  ArrowUpRight
} from "lucide-react";

import { apiRequest } from "../services/api";
import "./dashboard.css";

function Dashboard() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await apiRequest("/tickets");
      setTickets(Array.isArray(data) ? data : []);
      setError("");
    } catch (err) {
      setError(err.detail || "Unable to load tickets.");
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      title: "Total Tickets",
      value: tickets.length,
      icon: <Ticket />,
      color: "blue"
    },
    {
      title: "New Tickets",
      value: tickets.filter(t => t.status === "New").length,
      icon: <AlertCircle />,
      color: "orange"
    },
    {
      title: "In Progress",
      value: tickets.filter(t => t.status === "In Progress").length,
      icon: <Clock />,
      color: "purple"
    },
    {
      title: "Resolved",
      value: tickets.filter(t => t.status === "Resolved").length,
      icon: <CheckCircle />,
      color: "green"
    }
  ];

  const recentTickets = [...tickets]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5);

  const formatDate = (date) => {
    return date
      ? new Date(date).toLocaleDateString("en-IN")
      : "-";
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Employee Dashboard</h1>
          <p>Welcome back! Here's an overview of your IT support requests.</p>
        </div>

        <button
          className="primary-btn"
          onClick={() => window.location.href = "/raise-ticket"}
        >
          <Plus size={18} />
          Raise New Ticket
        </button>
      </div>

      {loading ? (
        <p>Loading dashboard...</p>
      ) : error ? (
        <div>
          <p>{error}</p>
          <button onClick={loadDashboard}>Retry</button>
        </div>
      ) : (
        <>
          <div className="stats-grid">
            {stats.map((stat, index) => (
              <div className="stat-card" key={index}>
                <div className={`stat-icon ${stat.color}`}>
                  {stat.icon}
                </div>

                <div>
                  <p>{stat.title}</p>
                  <h2>{stat.value}</h2>
                </div>

                <ArrowUpRight className="stat-arrow" size={18} />
              </div>
            ))}
          </div>

          <div className="tickets-section">
            <div className="section-header">
              <div>
                <h2>Recent Tickets</h2>
                <p>Track your recently submitted IT requests.</p>
              </div>

              <button
                className="view-btn"
                onClick={() => window.location.href = "/my-tickets"}
              >
                View All
              </button>
            </div>

            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Ticket ID</th>
                    <th>Issue Title</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>

                <tbody>
                  {recentTickets.length === 0 ? (
                    <tr>
                      <td colSpan="6">No tickets available.</td>
                    </tr>
                  ) : (
                    recentTickets.map(ticket => (
                      <tr key={ticket.id}>
                        <td className="ticket-id">TKT{ticket.id}</td>
                        <td>{ticket.title}</td>
                        <td>{ticket.category}</td>

                        <td>
                          <span className={`priority ${ticket.priority.toLowerCase()}`}>
                            {ticket.priority}
                          </span>
                        </td>

                        <td>
                          <span className={`status ${ticket.status.toLowerCase().replace(" ", "-")}`}>
                            {ticket.status}
                          </span>
                        </td>

                        <td>{formatDate(ticket.created_at)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;