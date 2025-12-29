import React from 'react';
import { Header, Card, CardHeader, CardContent, Button } from '@frontend/ui';
import './Settings.css';

const Settings: React.FC = () => {
  return (
    <div className="page animate-fade-in">
      <Header
        title="Settings"
        breadcrumbs={[{ label: 'Home', href: '/' }, { label: 'Settings' }]}
      />

      <div className="settings-content">
        <Card padding="lg">
          <CardHeader title="Profile" subtitle="Manage your account settings" />
          <CardContent>
            <div className="settings-form">
              <div className="form-group">
                <label className="form-label">Display Name</label>
                <input type="text" className="form-input" defaultValue="John Doe" />
              </div>
              <div className="form-group">
                <label className="form-label">Email</label>
                <input type="email" className="form-input" defaultValue="john@example.com" />
              </div>
              <div className="form-actions">
                <Button variant="primary">Save Changes</Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card padding="lg">
          <CardHeader title="Appearance" subtitle="Customize the look and feel" />
          <CardContent>
            <div className="settings-option">
              <div className="option-info">
                <span className="option-title">Dark Mode</span>
                <span className="option-description">Use dark theme throughout the application</span>
              </div>
              <label className="toggle">
                <input type="checkbox" defaultChecked />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="settings-option">
              <div className="option-info">
                <span className="option-title">Compact View</span>
                <span className="option-description">Show more content with reduced spacing</span>
              </div>
              <label className="toggle">
                <input type="checkbox" />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </CardContent>
        </Card>

        <Card padding="lg">
          <CardHeader title="API Settings" subtitle="Configure backend connection" />
          <CardContent>
            <div className="form-group">
              <label className="form-label">API Base URL</label>
              <input type="text" className="form-input" defaultValue="http://localhost:8001/api/v1" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
