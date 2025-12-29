import React from 'react';
import './Sidebar.css';

export interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href?: string;
  onClick?: () => void;
  badge?: string | number;
  children?: NavItem[];
}

export interface SidebarProps {
  logo?: React.ReactNode;
  navItems: NavItem[];
  activeId?: string;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  footer?: React.ReactNode;
}

export const Sidebar: React.FC<SidebarProps> = ({
  logo,
  navItems,
  activeId,
  collapsed = false,
  onToggleCollapse,
  footer,
}) => {
  return (
    <aside className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">{logo}</div>
        <button className="sidebar-toggle" onClick={onToggleCollapse} aria-label="Toggle sidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {collapsed ? (
              <path d="M9 18l6-6-6-6" />
            ) : (
              <path d="M15 18l-6-6 6-6" />
            )}
          </svg>
        </button>
      </div>

      <nav className="sidebar-nav">
        <ul className="sidebar-nav-list">
          {navItems.map((item) => (
            <li key={item.id} className="sidebar-nav-item">
              <a
                href={item.href || '#'}
                className={`sidebar-nav-link ${activeId === item.id ? 'active' : ''}`}
                onClick={(e) => {
                  if (item.onClick) {
                    e.preventDefault();
                    item.onClick();
                  }
                }}
              >
                <span className="sidebar-nav-icon">{item.icon}</span>
                {!collapsed && (
                  <>
                    <span className="sidebar-nav-label">{item.label}</span>
                    {item.badge && <span className="sidebar-nav-badge">{item.badge}</span>}
                  </>
                )}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {footer && <div className="sidebar-footer">{footer}</div>}
    </aside>
  );
};

export default Sidebar;
