import Link from "next/link";
import {
  LayoutDashboard,
  BatteryCharging,
  Activity,
  FileText,
} from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <BatteryCharging size={24} />
        </div>

        <div>
          <h1>BatteryTwin</h1>
          <span>Industrial Intelligence</span>
        </div>
      </div>

      <nav>
        <Link href="/" className="nav-item active">
          <LayoutDashboard size={18} />
          Fleet Overview
        </Link>

        <div className="nav-section">MONITORING</div>

        <Link href="/" className="nav-item">
          <Activity size={18} />
          Risk Monitor
        </Link>

        <Link href="/" className="nav-item">
          <BatteryCharging size={18} />
          Digital Twins
        </Link>

        <div className="nav-section">REPORTING</div>

        <Link href="/" className="nav-item">
          <FileText size={18} />
          Reports
        </Link>
      </nav>

      <div className="sidebar-footer">
        <div className="status-dot" />
        <span>AI Systems Operational</span>
      </div>
    </aside>
  );
}