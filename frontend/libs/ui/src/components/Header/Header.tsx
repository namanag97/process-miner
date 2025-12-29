import React from 'react';
import './Header.css';

export interface HeaderProps {
  title?: string;
  breadcrumbs?: Array<{ label: string; href?: string }>;
  actions?: React.ReactNode;
  userMenu?: React.ReactNode;
  notifications?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  breadcrumbs,
  actions,
  userMenu,
  notifications,
}) => {
  return (
    <header className="header">
      <div className="header-left">
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="header-breadcrumbs" aria-label="Breadcrumb">
            {breadcrumbs.map((crumb, index) => (
              <React.Fragment key={index}>
                {index > 0 && <span className="breadcrumb-separator">/</span>}
                {crumb.href ? (
                  <a href={crumb.href} className="breadcrumb-link">
                    {crumb.label}
                  </a>
                ) : (
                  <span className="breadcrumb-current">{crumb.label}</span>
                )}
              </React.Fragment>
            ))}
          </nav>
        )}
        {title && <h1 className="header-title">{title}</h1>}
      </div>

      <div className="header-right">
        {actions && <div className="header-actions">{actions}</div>}
        {notifications && <div className="header-notifications">{notifications}</div>}
        {userMenu && <div className="header-user">{userMenu}</div>}
      </div>
    </header>
  );
};

export default Header;
