
import React, { useState, useEffect } from "react";
import { apiRequest } from "../services/api";
import "./raise-ticket.css";

function RaiseTicket() {
  const [requesters, setRequesters] = useState([]);
  const [loadingRequesters, setLoadingRequesters] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    requester_id: "",
    title: "",
    category: "",
    description: ""
  });

  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState("");
  const [generalError, setGeneralError] = useState("");

  // Fetch requesters when the page opens
  useEffect(() => {
    const fetchRequesters = async () => {
      try {
        const data = await apiRequest("/requesters");
        setRequesters(data);
      } catch (error) {
        setGeneralError(error.detail || "Unable to load requesters.");
      } finally {
        setLoadingRequesters(false);
      }
    };

    fetchRequesters();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value
    }));

    setErrors((previous) => ({
      ...previous,
      [name]: ""
    }));

    setSuccess("");
    setGeneralError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setErrors({});
    setSuccess("");
    setGeneralError("");

    const payload = {
      requester_id: Number(formData.requester_id),
      title: formData.title,
      description: formData.description
    };

    // Category is optional
    if (formData.category) {
      payload.category = formData.category;
    }

    setSubmitting(true);

    try {
      const result = await apiRequest("/tickets", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      setSuccess(`Ticket #${result.id} created successfully!`);

      setFormData({
        requester_id: "",
        title: "",
        category: "",
        description: ""
      });

    } catch (error) {
      if (error.status === 422 && Array.isArray(error.detail)) {
        const fieldErrors = {};

        error.detail.forEach((item) => {
          const field = item.loc[item.loc.length - 1];
          fieldErrors[field] = item.msg;
        });

        setErrors(fieldErrors);
      } else {
        setGeneralError(
          error.detail || "Unable to submit ticket. Please try again."
        );
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="raise-ticket-page">
      <h1>Raise a Ticket</h1>
      <p>Submit your IT support request below.</p>

      {success && (
        <p style={{ color: "green" }}>{success}</p>
      )}

      {generalError && (
        <p style={{ color: "red" }}>{generalError}</p>
      )}

      <form onSubmit={handleSubmit} className="ticket-form">

        <label>Requester</label>
        <select
          name="requester_id"
          value={formData.requester_id}
          onChange={handleChange}
          required
          disabled={loadingRequesters}
        >
          <option value="">
            {loadingRequesters
              ? "Loading requesters..."
              : "Select Requester"}
          </option>

          {requesters.map((requester) => (
            <option key={requester.id} value={requester.id}>
              {requester.display_name} - {requester.email}
            </option>
          ))}
        </select>
        {errors.requester_id && (
          <p style={{ color: "red" }}>{errors.requester_id}</p>
        )}

        <label>Issue Title</label>
        <input
          type="text"
          name="title"
          placeholder="Enter issue title"
          value={formData.title}
          onChange={handleChange}
          minLength={5}
          maxLength={200}
          required
        />
        {errors.title && (
          <p style={{ color: "red" }}>{errors.title}</p>
        )}

        <label>Category (Optional)</label>
        <select
          name="category"
          value={formData.category}
          onChange={handleChange}
        >
          <option value="">Let support team decide</option>
          <option value="Hardware">Hardware</option>
          <option value="Software">Software</option>
          <option value="Network">Network</option>
          <option value="Access">Access</option>
          <option value="Other">Other</option>
        </select>
        {errors.category && (
          <p style={{ color: "red" }}>{errors.category}</p>
        )}

        <label>Description</label>
        <textarea
          name="description"
          placeholder="Describe your issue..."
          value={formData.description}
          onChange={handleChange}
          minLength={10}
          required
        />
        {errors.description && (
          <p style={{ color: "red" }}>{errors.description}</p>
        )}

        <button
          type="submit"
          disabled={submitting || loadingRequesters}
        >
          {submitting ? "Submitting..." : "Submit Ticket"}
        </button>

      </form>
    </div>
  );
}

export default RaiseTicket;
