import React, { useState } from "react";

import "./settings.css";

function Settings() {

  const [user, setUser] = useState({

    name: "Amit Roy",

    email: "amit.roy@company.com",

    phone: "9876543210",

    department: "IT Department",

    role: "Employee",

  });

  const [notifications, setNotifications] = useState({

    email: true,

    ticketUpdates: true,

    announcements: false,

  });

  const handleChange = (e) => {

    setUser({

      ...user,

      [e.target.name]: e.target.value,

    });

  };

  const handleNotification = (e) => {

    setNotifications({

      ...notifications,

      [e.target.name]: e.target.checked,

    });

  };

  const handleSave = (e) => {

    e.preventDefault();

    alert("Settings saved successfully!");

  };

  return (
<div className="settings-page">
<div className="settings-header">
<h1>Settings</h1>
<p>Manage your account and application preferences.</p>
</div>
<div className="settings-container">

        {/* Profile Section */}
<div className="settings-card">
<h2>Personal Information</h2>
<p className="settings-description">

            Update your personal account information.
</p>
<form onSubmit={handleSave}>
<div className="settings-form-grid">
<div className="settings-field">
<label>Full Name</label>
<input

                  type="text"

                  name="name"

                  value={user.name}

                  onChange={handleChange}

                  required

                />
</div>
<div className="settings-field">
<label>Email Address</label>
<input

                  type="email"

                  name="email"

                  value={user.email}

                  onChange={handleChange}

                  required

                />
</div>
<div className="settings-field">
<label>Phone Number</label>
<input

                  type="tel"

                  name="phone"

                  value={user.phone}

                  onChange={handleChange}

                />
</div>
<div className="settings-field">
<label>Department</label>
<input

                  type="text"

                  name="department"

                  value={user.department}

                  readOnly

                />
</div>
<div className="settings-field">
<label>Role</label>
<input

                  type="text"

                  name="role"

                  value={user.role}

                  readOnly

                />
</div>
</div>
<button type="submit" className="settings-save-btn">

              Save Changes
</button>
</form>
</div>

        {/* Notification Section */}
<div className="settings-card">
<h2>Notification Preferences</h2>
<p className="settings-description">

            Manage how you receive notifications.
</p>
<div className="notification-option">
<div>
<h4>Email Notifications</h4>
<p>Receive updates through email.</p>
</div>
<input

              type="checkbox"

              name="email"

              checked={notifications.email}

              onChange={handleNotification}

            />
</div>
<div className="notification-option">
<div>
<h4>Ticket Updates</h4>
<p>Get notified when your ticket status changes.</p>
</div>
<input

              type="checkbox"

              name="ticketUpdates"

              checked={notifications.ticketUpdates}

              onChange={handleNotification}

            />
</div>
<div className="notification-option">
<div>
<h4>Announcements</h4>
<p>Receive important company announcements.</p>
</div>
<input

              type="checkbox"

              name="announcements"

              checked={notifications.announcements}

              onChange={handleNotification}

            />
</div>
</div>

        {/* Security Section */}
<div className="settings-card">
<h2>Security</h2>
<p className="settings-description">

            Manage your account security.
</p>
<div className="security-option">
<div>
<h4>Password</h4>
<p>Keep your account secure with a strong password.</p>
</div>
<button

              className="password-btn"

              onClick={() => alert("Password change feature coming soon!")}
>

              Change Password
</button>
</div>
</div>
</div>
</div>

  );

}

export default Settings;
 