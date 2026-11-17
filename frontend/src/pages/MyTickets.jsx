import React, { useState, useEffect } from "react";

import { apiRequest } from "../services/api";

import "./my-tickets.css";

function MyTickets() {

  const [tickets, setTickets] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  useEffect(() => {

    const fetchTickets = async () => {

      try {

        const data = await apiRequest("/tickets");

        setTickets(data);

      } catch (err) {

        setError(err.detail || "Unable to load tickets.");

      } finally {

        setLoading(false);

      }

    };

    fetchTickets();

  }, []);

  if (loading) {

    return <div className="my-tickets-page">Loading tickets...</div>;

  }

  if (error) {

    return <div className="my-tickets-page" style={{ color: "red" }}>

      {error}
    </div>;

  }

  return (
    <div className="my-tickets-page">
      <h1>My Tickets</h1>
      <p>Track and manage your IT support requests.</p>

      {tickets.length === 0 ? (
        <p>No tickets found.</p>

      ) : (
        <div className="tickets-table">
          <table>
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Issue Title</th>
                <th>Category</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Date Created</th>
              </tr>
            </thead>
            <tbody>

              {tickets.map((ticket) => (
                <tr key={ticket.id}>
                  <td>TKT{String(ticket.id).padStart(3, "0")}</td>
                  <td>{ticket.title}</td>
                  <td>{ticket.category}</td>
                  <td>{ticket.priority}</td>
                  <td>{ticket.status}</td>
                  <td>

                    {new Date(ticket.created_at).toLocaleDateString()}
                  </td>
                </tr>

              ))}
            </tbody>
          </table>
        </div>

      )}
    </div>

  );

}

export default MyTickets;
