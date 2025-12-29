import React from 'react';
import { Header, KPITile, Card, CardHeader, CardContent, Button } from '@frontend/ui';
import './Dashboard.css';

// Icons
const CasesIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <path d="M14 2v6h6" />
    <path d="M16 13H8" />
    <path d="M16 17H8" />
    <path d="M10 9H8" />
  </svg>
);

const DurationIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <path d="M12 6v6l4 2" />
  </svg>
);

const FitnessIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <path d="M22 4L12 14.01l-3-3" />
  </svg>
);

const BottleneckIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <path d="M12 9v4" />
    <path d="M12 17h.01" />
  </svg>
);

const Dashboard: React.FC = () => {
  // Mock data - in real app, this comes from API
  const kpis = [
    {
      title: 'Total Cases',
      value: '15,234',
      change: { value: 12.5, direction: 'up' as const },
      icon: <CasesIcon />,
      status: 'success' as const,
    },
    {
      title: 'Avg Duration',
      value: '4.2 days',
      change: { value: -8.2, direction: 'down' as const },
      icon: <DurationIcon />,
      status: 'success' as const,
    },
    {
      title: 'Fitness Score',
      value: '87.3%',
      change: { value: 2.1, direction: 'up' as const },
      icon: <FitnessIcon />,
      status: 'info' as const,
    },
    {
      title: 'Bottlenecks',
      value: '3',
      change: { value: -1, direction: 'down' as const },
      icon: <BottleneckIcon />,
      status: 'warning' as const,
    },
  ];

  const recentProcesses = [
    { id: '1', name: 'Order-to-Cash', cases: 5432, updated: '2 hours ago' },
    { id: '2', name: 'Purchase-to-Pay', cases: 3218, updated: '5 hours ago' },
    { id: '3', name: 'Incident Management', cases: 1876, updated: '1 day ago' },
  ];

  const bottlenecks = [
    { activity: 'Approval Step', duration: '3.2 days', severity: 'high' },
    { activity: 'Manual Review', duration: '2.1 days', severity: 'medium' },
    { activity: 'Document Check', duration: '1.5 days', severity: 'low' },
  ];

  return (
    <div className="page animate-fade-in">
      <Header
        title="Dashboard"
        breadcrumbs={[{ label: 'Home' }]}
        actions={
          <Button variant="primary" size="sm">
            Upload Process
          </Button>
        }
      />

      <div className="dashboard-content">
        {/* KPI Grid */}
        <section className="dashboard-kpis">
          <div className="grid grid-cols-4">
            {kpis.map((kpi, index) => (
              <KPITile key={index} {...kpi} />
            ))}
          </div>
        </section>

        {/* Main Content Grid */}
        <section className="dashboard-main">
          <div className="dashboard-grid">
            {/* Process Flow Placeholder */}
            <Card className="dashboard-flow-card" padding="lg">
              <CardHeader title="Process Flow Visualization" subtitle="Order-to-Cash Process" />
              <CardContent>
                <div className="flow-placeholder">
                  <div className="flow-nodes">
                    <div className="flow-node flow-node-start">Create Order</div>
                    <div className="flow-arrow">→</div>
                    <div className="flow-node">Review Order</div>
                    <div className="flow-arrow">→</div>
                    <div className="flow-node">Approve Order</div>
                    <div className="flow-arrow">→</div>
                    <div className="flow-node flow-node-end">Ship Order</div>
                  </div>
                  <p className="flow-cta">
                    <Button variant="ghost" size="sm">
                      Open Process Explorer →
                    </Button>
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Recent Processes */}
            <Card padding="lg">
              <CardHeader title="Recent Processes" />
              <CardContent>
                <ul className="recent-list">
                  {recentProcesses.map((process) => (
                    <li key={process.id} className="recent-item">
                      <div className="recent-icon">📁</div>
                      <div className="recent-info">
                        <span className="recent-name">{process.name}</span>
                        <span className="recent-meta">{process.cases.toLocaleString()} cases</span>
                      </div>
                      <span className="recent-time">{process.updated}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Top Bottlenecks */}
            <Card padding="lg">
              <CardHeader title="Top Bottlenecks" />
              <CardContent>
                <ul className="bottleneck-list">
                  {bottlenecks.map((item, index) => (
                    <li key={index} className={`bottleneck-item bottleneck-${item.severity}`}>
                      <span className="bottleneck-icon">⚠️</span>
                      <span className="bottleneck-name">{item.activity}</span>
                      <span className="bottleneck-duration tabular-nums">{item.duration}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
