
import React, { useState, useEffect } from "react";
import { apiRequest } from "../services/api";

function SupportDashboard() {
  const [tickets, setTickets] = useState([]);
  const [requesters, setRequesters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [ticketData, requesterData] = await Promise.all([
          apiRequest("/tickets"),
          apiRequest("/requesters")
        ]);

        setTickets(ticketData);
        setRequesters(requesterData);
      } catch (err) {
        setError(err.detail || "Unable to load dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const stats = [
    {
      title: "Total Tickets",
      count: tickets.length,
      color: "blue"
    },
    {
      title: "New Tickets",
      count: tickets.filter(t => t.status === "New").length,
      color: "orange"
    },
    {
      title: "In Progress",
      count: tickets.filter(t => t.status === "In Progress").length,
      color: "purple"
    },
    {
      title: "Resolved",
      count: tickets.filter(t => t.status === "Resolved").length,
      color: "green"
    }
  ];

  const getEmployeeName = (requesterId) => {
    const employee = requesters.find(
      r => r.id === requesterId
    );

    return employee ? employee.display_name : "Unknown";
  };

  if (loading) {
    return <h2>Loading dashboard...</h2>;
  }

  if (error) {
    return <p style={{ color: "red" }}>{error}</p>;
  }

  return (
    <div className="support-dashboard">
      <h1>Support Staff Dashboard</h1>
      <p>Monitor and manage employee IT support requests.</p>

      <div className="stats-container">
        {stats.map((stat) => (
          <div
            className={`stat-card ${stat.color}`}
            key={stat.title}
          >
            <h3>{stat.title}</h3>
            <h2>{stat.count}</h2>
          </div>
        ))}
      </div>

      <div className="support-tickets">
        <h2>Recent Tickets</h2>

        {tickets.length === 0 ? (
          <p>No tickets found.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Employee</th>
                <th>Issue</th>
                <th>Category</th>
                <th>Priority</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {tickets.map((ticket) => (
                <tr key={ticket.id}>
                  <td>
                    TKT{String(ticket.id).padStart(3, "0")}
                  </td>
                  <td>{getEmployeeName(ticket.requester_id)}</td>
                  <td>{ticket.title}</td>
                  <td>{ticket.category}</td>
                  <td>{ticket.priority}</td>
                  <td>{ticket.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default SupportDashboard;
