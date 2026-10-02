import { Menu, Bell, Search, ChevronDown, User } from 'lucide-react';

export default function Topbar({ title, subtitle }) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <h2>{title || 'Dashboard'}</h2>
        {subtitle && (
          <div className="topbar-breadcrumb">
            <span style={{ color: 'var(--text-dim)' }}>Home</span>
            <ChevronDown size={12} style={{ transform: 'rotate(-90deg)' }} />
            <span>{subtitle}</span>
          </div>
        )}
      </div>
      <div className="topbar-right">
        <div className="topbar-search">
          <Search size={14} color="var(--text-dim)" />
          <input placeholder="Search..." />
        </div>
        <button className="topbar-icon-btn">
          <Bell size={16} />
          <div className="notif-dot" />
        </button>
        <div className="topbar-user">
          <div className="topbar-avatar">
            <User size={14} />
          </div>
          <span className="topbar-user-name">User</span>
          <ChevronDown size={14} color="var(--text-muted)" />
        </div>
      </div>
    </div>
  );
}
