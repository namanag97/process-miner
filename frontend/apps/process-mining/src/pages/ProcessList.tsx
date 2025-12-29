import React from 'react';
import { Header, Card, CardContent, Button } from '@frontend/ui';
import { useNavigate } from 'react-router-dom';
import './ProcessList.css';

interface Process {
  id: string;
  name: string;
  description: string;
  caseCount: number;
  eventCount: number;
  createdAt: string;
  status: 'active' | 'processing' | 'error';
}

const ProcessList: React.FC = () => {
  const navigate = useNavigate();

  // Mock data - in real app, this comes from API via TanStack Query
  const processes: Process[] = [
    {
      id: '1',
      name: 'Order-to-Cash',
      description: 'End-to-end order management process',
      caseCount: 5432,
      eventCount: 87654,
      createdAt: '2024-12-28',
      status: 'active',
    },
    {
      id: '2',
      name: 'Purchase-to-Pay',
      description: 'Procurement and payment workflow',
      caseCount: 3218,
      eventCount: 45231,
      createdAt: '2024-12-27',
      status: 'active',
    },
    {
      id: '3',
      name: 'Incident Management',
      description: 'IT incident resolution process',
      caseCount: 1876,
      eventCount: 23456,
      createdAt: '2024-12-26',
      status: 'processing',
    },
    {
      id: '4',
      name: 'Claims Processing',
      description: 'Insurance claims handling workflow',
      caseCount: 2341,
      eventCount: 34567,
      createdAt: '2024-12-25',
      status: 'active',
    },
  ];

  const handleUpload = () => {
    // In real app, open upload modal
    console.log('Upload clicked');
  };

  const handleViewProcess = (id: string) => {
    navigate(`/processes/${id}`);
  };

  return (
    <div className="page animate-fade-in">
      <Header
        title="Processes"
        breadcrumbs={[{ label: 'Home', href: '/' }, { label: 'Processes' }]}
        actions={
          <Button variant="primary" onClick={handleUpload}>
            Upload Process
          </Button>
        }
      />

      <div className="process-list-content">
        {/* Search and Filters */}
        <div className="process-toolbar">
          <div className="search-box">
            <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
            <input
              type="text"
              placeholder="Search processes..."
              className="search-input"
            />
          </div>
          <div className="filter-group">
            <Button variant="ghost" size="sm">
              All Processes
            </Button>
            <Button variant="ghost" size="sm">
              Recent
            </Button>
            <Button variant="ghost" size="sm">
              Favorites
            </Button>
          </div>
        </div>

        {/* Process Grid */}
        <div className="process-grid">
          {processes.map((process) => (
            <Card
              key={process.id}
              className="process-card"
              interactive
              onClick={() => handleViewProcess(process.id)}
            >
              <CardContent>
                <div className="process-card-header">
                  <h3 className="process-name">{process.name}</h3>
                  <span className={`process-status status-${process.status}`}>
                    {process.status}
                  </span>
                </div>
                <p className="process-description">{process.description}</p>
                <div className="process-stats">
                  <div className="stat">
                    <span className="stat-value tabular-nums">{process.caseCount.toLocaleString()}</span>
                    <span className="stat-label">Cases</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value tabular-nums">{process.eventCount.toLocaleString()}</span>
                    <span className="stat-label">Events</span>
                  </div>
                </div>
                <div className="process-footer">
                  <span className="process-date">Created {process.createdAt}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProcessList;
