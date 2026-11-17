
import React, { useEffect, useState } from "react";
import { apiRequest } from "../services/api";
import "./ai-recommendations.css";

function AIRecommendations() {
  const [tickets, setTickets] = useState([]);
  const [requesters, setRequesters] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState("");
  const [suggestion, setSuggestion] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [aiStatus, setAiStatus] = useState("Checking...");
  const [feedback, setFeedback] = useState({
    final_category: "",
    final_priority: "",
    useful: true,
    actor: "Support Staff",
    comment: ""
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        const [ticketData, requesterData, statusData] =
          await Promise.all([
            apiRequest("/tickets"),
            apiRequest("/requesters"),
            apiRequest("/ai/status")
          ]);

        setTickets(ticketData);
        setRequesters(requesterData);
        setAiStatus(
          statusData.available ? "Online" : "Offline"
        );

        if (ticketData.length > 0) {
          setSelectedTicket(String(ticketData[0].id));
        }
      } catch (err) {
        setError(err.detail || "Unable to load AI page.");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const employeeName = (requesterId) => {
    const requester = requesters.find(
      r => r.id === requesterId
    );
    return requester?.display_name || "Unknown";
  };

  const loadSuggestions = async (ticketId) => {
    try {
      setError("");
      setSuggestion(null);

      const data = await apiRequest(
        `/tickets/${ticketId}/suggestions`
      );

      setSuggestions(data);

      if (data.length > 0) {
        setSuggestion(data[0]);
        setFeedback({
          final_category: data[0].suggested_category,
          final_priority: data[0].suggested_priority,
          useful: true,
          actor: "Support Staff",
          comment: ""
        });
      }
    } catch (err) {
      setError(err.detail || "Unable to load suggestions.");
    }
  };

  useEffect(() => {
    if (selectedTicket) {
      loadSuggestions(selectedTicket);
    }
  }, [selectedTicket]);

  const analyzeTicket = async () => {
    try {
      setAnalyzing(true);
      setError("");
      setSuggestion(null);

      const result = await apiRequest(
        `/tickets/${selectedTicket}/analyze`,
        { method: "POST" }
      );

      setSuggestion(result);
      setSuggestions(prev => [result, ...prev]);

      setFeedback({
        final_category: result.suggested_category,
        final_priority: result.suggested_priority,
        useful: true,
        actor: "Support Staff",
        comment: ""
      });
    } catch (err) {
      setError(err.detail || "AI analysis failed.");
    } finally {
      setAnalyzing(false);
    }
  };

  const submitFeedback = async () => {
    if (!suggestion) return;

    try {
      setError("");

      await apiRequest(
        `/tickets/${selectedTicket}/feedback`,
        {
          method: "POST",
          body: JSON.stringify({
            suggestion_id: suggestion.id,
            ...feedback
          })
        }
      );

      alert("Staff feedback saved successfully!");

      await loadSuggestions(selectedTicket);
    } catch (err) {
      setError(err.detail || "Unable to save feedback.");
    }
  };

  const currentTicket = tickets.find(
    t => String(t.id) === selectedTicket
  );

  if (loading) return <h2>Loading AI recommendations...</h2>;

  return (
    <div className="ai-recommendations-page">
      <div className="ai-header">
        <div>
          <h1>AI Recommendations</h1>
          <p>Smart ticket analysis and suggested resolutions.</p>
        </div>
        <span className="ai-badge">AI {aiStatus}</span>
      </div>

      {error && (
        <p style={{ color: "red", marginBottom: "15px" }}>
          {error}
        </p>
      )}

      <div className="ai-layout">
        <div className="ai-ticket-panel">
          <h2>Select Ticket</h2>

          {tickets.map(ticket => (
            <div
              key={ticket.id}
              className={`ai-ticket ${
                selectedTicket === String(ticket.id) ? "active" : ""
              }`}
              onClick={() => setSelectedTicket(String(ticket.id))}
            >
              <h3>TKT{String(ticket.id).padStart(3, "0")}</h3>
              <p>{ticket.title}</p>
              <span>{employeeName(ticket.requester_id)}</span>
            </div>
          ))}
        </div>

        <div className="ai-result-panel">
          {currentTicket ? (
            <>
              <div className="ai-result-heading">
                <h2>AI Analysis Result</h2>
                <button
                  onClick={analyzeTicket}
                  disabled={analyzing || aiStatus === "Offline"}
                >
                  {analyzing ? "Analyzing..." : "Analyze with AI"}
                </button>
              </div>

              <div className="ai-issue-details">
                <div>
                  <label>Employee</label>
                  <h3>{employeeName(currentTicket.requester_id)}</h3>
                </div>
                <div>
                  <label>Issue</label>
                  <h3>{currentTicket.title}</h3>
                </div>
                <div>
                  <label>Current Category</label>
                  <h3>{currentTicket.category}</h3>
                </div>
                <div>
                  <label>Current Priority</label>
                  <h3>{currentTicket.priority}</h3>
                </div>
              </div>

              {suggestion ? (
                <>
                  <div className="ai-suggestion">
                    <h3>AI Suggested Category</h3>
                    <p>{suggestion.suggested_category}</p>

                    <h3>AI Suggested Priority</h3>
                    <p>{suggestion.suggested_priority}</p>

                    <h3>Priority Reason</h3>
                    <p>{suggestion.priority_reason}</p>
                  </div>

                  <div className="ai-steps">
                    <h3>Suggested Action Steps</h3>
                    {suggestion.troubleshooting_steps.map((step, index) => (
                      <div className="ai-step" key={index}>
                        <span>{index + 1}</span>
                        <p>{step}</p>
                      </div>
                    ))}
                  </div>

                  <div className="ai-suggestion">
                    <h3>Human Review</h3>

                    <label>Final Category</label>
                    <select
                      value={feedback.final_category}
                      onChange={e => setFeedback({
                        ...feedback,
                        final_category: e.target.value
                      })}
                    >
                      {["Hardware", "Software", "Network", "Access", "Other"].map(v =>
                        <option key={v} value={v}>{v}</option>
                      )}
                    </select>

                    <label>Final Priority</label>
                    <select
                      value={feedback.final_priority}
                      onChange={e => setFeedback({
                        ...feedback,
                        final_priority: e.target.value
                      })}
                    >
                      {["Low", "Medium", "High"].map(v =>
                        <option key={v} value={v}>{v}</option>
                      )}
                    </select>

                    <label>
                      <input
                        type="checkbox"
                        checked={feedback.useful}
                        onChange={e => setFeedback({
                          ...feedback,
                          useful: e.target.checked
                        })}
                      />
                      AI suggestion was useful
                    </label>

                    <textarea
                      placeholder="Staff comments (optional)"
                      value={feedback.comment}
                      onChange={e => setFeedback({
                        ...feedback,
                        comment: e.target.value
                      })}
                    />

                    <button onClick={submitFeedback}>
                      Submit Staff Feedback
                    </button>
                  </div>
                </>
              ) : (
                <p>No AI recommendation yet. Click Analyze with AI.</p>
              )}

              <div className="ai-disclaimer">
                AI recommendations are advisory only. Support staff make
                the final category and priority decisions.
              </div>
            </>
          ) : (
            <p>No tickets available for analysis.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default AIRecommendations;
