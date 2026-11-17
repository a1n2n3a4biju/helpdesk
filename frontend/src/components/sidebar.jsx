
import React from "react";
import { NavLink } from "react-router-dom";
import "./sidebar.css";

import {
  LayoutDashboard,
  PlusCircle,
  Ticket,
  ClipboardList,
  Settings,
  Headphones,
  ChevronRight,
  Bot
} from "lucide-react";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <Headphones size={25} />
        </div>
        <div>
          <h2>HelpDesk</h2>
          <span>IT SUPPORT PORTAL</span>
        </div>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-heading">EMPLOYEE</p>

        <NavLink to="/employee/dashboard" className="nav-item">
          <LayoutDashboard size={19} />
          <span>Dashboard</span>
        </NavLink>

        <NavLink to="/raise-ticket" className="nav-item">
          <PlusCircle size={19} />
          <span>Raise Ticket</span>
        </NavLink>

        <NavLink to="/my-tickets" className="nav-item">
          <Ticket size={19} />
          <span>My Tickets</span>
        </NavLink>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-heading">SUPPORT STAFF</p>

        <NavLink to="/support/dashboard" className="nav-item">
          <LayoutDashboard size={19} />
          <span>Dashboard</span>
        </NavLink>

        <NavLink to="/support/work-queue" className="nav-item">
          <ClipboardList size={19} />
          <span>Work Queue</span>
        </NavLink>

        <NavLink to="/support/ai-recommendations" className="nav-item">
          <Bot size={19} />
          <span>AI Recommendations</span>
        </NavLink>

        <NavLink to="/settings" className="nav-item">
          <Settings size={19} />
          <span>Settings</span>
        </NavLink>
      </div>

      <div className="sidebar-bottom">
        <NavLink to="/support/ai-recommendations" className="sidebar-help">
          <Bot size={22} />
          <div>
            <h4>AI Assistance</h4>
            <p>Smart ticket analysis</p>
          </div>
          <ChevronRight size={17} />
        </NavLink>
      </div>
    </aside>
  );
}

export default Sidebar;
