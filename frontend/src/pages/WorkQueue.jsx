
import React, { useEffect, useState } from "react";
import "./workqueue.css";

const API_URL = "http://127.0.0.1:8000";

function WorkQueue() {
  const [tickets, setTickets] = useState([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        setLoading(true);
        setError("");

        const [ticketResponse, requesterResponse] = await Promise.all([
          fetch(`${API_URL}/tickets`),
          fetch(`${API_URL}/requesters`)
        ]);

        if (!ticketResponse.ok || !requesterResponse.ok) {
          throw new Error("Unable to fetch tickets or requesters.");
        }

        const ticketData = await ticketResponse.json();
        const requesterData = await requesterResponse.json();

        const requesterMap = {};
        requesterData.forEach((requester) => {
          requesterMap[requester.id] = requester.display_name;
        });

        const formattedTickets = ticketData.map((ticket) => ({
          ...ticket,
          ticketCode: `TKT${String(ticket.id).padStart(3, "0")}`,
          employee: requesterMap[ticket.requester_id] || "Unknown",
          title: ticket.title,
          category: ticket.category || "Unassigned",
          priority: ticket.priority || "Medium",
          status: ticket.status || "New"
        }));

        setTickets(formattedTickets);
      } catch (err) {
        console.error("Work Queue error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, []);

  const updateStatus = async (id, newStatus) => {
 const previousTickets = [...tickets];
 try {
   const response = await fetch(
     `http://127.0.0.1:8000/tickets/${id}/status`,
     {
       method: "PATCH",
       headers: {
         "Content-Type": "application/json",
       },
       body: JSON.stringify({
         status: newStatus,
         actor: "Support Staff",
         note: `Status changed to ${newStatus}`,
       }),
     }
   );
   if (!response.ok) {
     const errorData = await response.json();
     throw new Error(
       errorData.detail?.toString() || "Status update failed"
     );
   }
   const updatedTicket = await response.json();
   setTickets((prev) =>
     prev.map((ticket) =>
ticket.id === id
         ? { ...ticket, status: updatedTicket.status }
         : ticket
     )
   );
   alert("Ticket status updated successfully!");
 } catch (error) {
   console.error("Status update error:", error);
   alert(error.message);
 }
};

  const filteredTickets = tickets.filter((ticket) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      ticket.ticketCode.toLowerCase().includes(searchText) ||
      ticket.employee.toLowerCase().includes(searchText) ||
      ticket.title.toLowerCase().includes(searchText);

    const matchesFilter =
      filter === "All" || ticket.status === filter;

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="work-queue-page">
      <div className="queue-header">
        <div>
          <h1>Work Queue</h1>
          <p>Manage and resolve employee support tickets.</p>
        </div>
      </div>

      {loading && <p>Loading tickets...</p>}
      {error && <p className="error-message">{error}</p>}

      {!loading && !error && (
        <>
          <div className="queue-stats">
            <div className="queue-stat-card">
              <h3>Total Tickets</h3>
              <h2>{tickets.length}</h2>
            </div>

            <div className="queue-stat-card">
              <h3>New Tickets</h3>
              <h2>{tickets.filter(t => t.status === "New").length}</h2>
            </div>

            <div className="queue-stat-card">
              <h3>In Progress</h3>
              <h2>{tickets.filter(t => t.status === "In Progress").length}</h2>
            </div>

            <div className="queue-stat-card">
              <h3>Resolved</h3>
              <h2>{tickets.filter(t => t.status === "Resolved").length}</h2>
            </div>
          </div>

          <div className="queue-table-container">
            <div className="queue-toolbar">
              <h2>All Support Tickets</h2>

              <input
                type="text"
                placeholder="Search tickets..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />

              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="All">All Status</option>
                <option value="New">New</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Ticket ID</th>
                  <th>Employee</th>
                  <th>Issue</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {filteredTickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>{ticket.ticketCode}</td>
                    <td>{ticket.employee}</td>
                    <td>{ticket.title}</td>
                    <td>{ticket.category}</td>

                    <td>
                      <span className={`priority ${String(ticket.priority).toLowerCase()}`}>
                        {ticket.priority}
                      </span>
                    </td>

                    <td>
                      <span className={`status ${String(ticket.status).toLowerCase().replace(" ", "-")}`}>
                        {ticket.status}
                      </span>
                    </td>

                    <td>
                      <select
                        value={ticket.status}
                        onChange={(e) =>
                          updateStatus(ticket.id, e.target.value)
                        }
                      >
                        <option value="New">New</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Resolved">Resolved</option>
                      </select>
                    </td>
                  </tr>
                ))}

                {filteredTickets.length === 0 && (
                  <tr>
                    <td colSpan="7">No tickets found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default WorkQueue;
