import React from 'react';
import { useParams, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Header, Card, CardHeader, CardContent, KPITile, Button } from '@frontend/ui';
import './ProcessDetail.css';

const ProcessDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();

  // Mock process data
  const process = {
    id,
    name: 'Order-to-Cash',
    description: 'End-to-end order management process from order creation to cash collection',
    caseCount: 5432,
    eventCount: 87654,
    activities: 12,
    variants: 156,
    avgDuration: '4.2 days',
    fitness: 87.3,
    precision: 82.1,
  };

  const tabs = [
    { id: 'overview', label: 'Overview', path: '' },
    { id: 'dfg', label: 'Process Graph', path: '/dfg' },
    { id: 'performance', label: 'Performance', path: '/performance' },
    { id: 'conformance', label: 'Conformance', path: '/conformance' },
    { id: 'variants', label: 'Variants', path: '/variants' },
  ];

  const currentTab = tabs.find(tab => 
    location.pathname === `/processes/${id}${tab.path}` ||
    (tab.path === '' && location.pathname === `/processes/${id}`)
  )?.id || 'overview';

  return (
    <div className="page animate-fade-in">
      <Header
        title={process.name}
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: 'Processes', href: '/processes' },
          { label: process.name },
        ]}
        actions={
          <div className="header-actions-group">
            <Button variant="ghost" size="sm">Export</Button>
            <Button variant="primary" size="sm">Discover Model</Button>
          </div>
        }
      />

      <div className="process-detail-content">
        {/* Tab Navigation */}
        <nav className="process-tabs">
          {tabs.map((tab) => (
            <Link
              key={tab.id}
              to={`/processes/${id}${tab.path}`}
              className={`process-tab ${currentTab === tab.id ? 'active' : ''}`}
            >
              {tab.label}
            </Link>
          ))}
        </nav>

        {/* Tab Content */}
        <Routes>
          <Route path="/" element={<OverviewTab process={process} />} />
          <Route path="/dfg" element={<DFGTab />} />
          <Route path="/performance" element={<PerformanceTab />} />
          <Route path="/conformance" element={<ConformanceTab process={process} />} />
          <Route path="/variants" element={<VariantsTab />} />
        </Routes>
      </div>
    </div>
  );
};

// Tab Components
const OverviewTab: React.FC<{ process: any }> = ({ process }) => (
  <div className="tab-content">
    <div className="grid grid-cols-4">
      <KPITile title="Cases" value={process.caseCount.toLocaleString()} status="info" />
      <KPITile title="Events" value={process.eventCount.toLocaleString()} status="info" />
      <KPITile title="Activities" value={process.activities} status="neutral" />
      <KPITile title="Variants" value={process.variants} status="neutral" />
    </div>
    <div className="overview-grid">
      <Card padding="lg">
        <CardHeader title="Process Description" />
        <CardContent>
          <p>{process.description}</p>
        </CardContent>
      </Card>
      <Card padding="lg">
        <CardHeader title="Quick Stats" />
        <CardContent>
          <ul className="stats-list">
            <li><span>Average Duration:</span> <strong>{process.avgDuration}</strong></li>
            <li><span>Fitness Score:</span> <strong>{process.fitness}%</strong></li>
            <li><span>Precision Score:</span> <strong>{process.precision}%</strong></li>
          </ul>
        </CardContent>
      </Card>
    </div>
  </div>
);

const DFGTab: React.FC = () => (
  <div className="tab-content">
    <Card padding="lg" className="dfg-card">
      <CardHeader 
        title="Directly-Follows Graph" 
        subtitle="Interactive process flow visualization"
        action={<Button variant="ghost" size="sm">Full Screen</Button>}
      />
      <CardContent>
        <div className="dfg-placeholder">
          <p>🔄 Process Graph Visualization</p>
          <p className="dfg-hint">React Flow integration will render the DFG here</p>
        </div>
      </CardContent>
    </Card>
  </div>
);

const PerformanceTab: React.FC = () => (
  <div className="tab-content">
    <div className="grid grid-cols-3">
      <KPITile title="Avg Duration" value="4.2 days" change={{ value: -8.2, direction: 'down' }} status="success" />
      <KPITile title="Bottlenecks" value="3" status="warning" />
      <KPITile title="Throughput" value="128/day" change={{ value: 5.3, direction: 'up' }} status="success" />
    </div>
    <Card padding="lg">
      <CardHeader title="Duration Distribution" />
      <CardContent>
        <div className="chart-placeholder">📊 Duration Histogram Chart</div>
      </CardContent>
    </Card>
  </div>
);

const ConformanceTab: React.FC<{ process: any }> = ({ process }) => (
  <div className="tab-content">
    <div className="grid grid-cols-2">
      <KPITile title="Fitness" value={`${process.fitness}%`} status="success" />
      <KPITile title="Precision" value={`${process.precision}%`} status="info" />
    </div>
    <Card padding="lg">
      <CardHeader title="Deviation Analysis" />
      <CardContent>
        <div className="chart-placeholder">📈 Conformance Diagnostics</div>
      </CardContent>
    </Card>
  </div>
);

const VariantsTab: React.FC = () => (
  <div className="tab-content">
    <Card padding="lg">
      <CardHeader title="Process Variants" subtitle="156 unique variants discovered" />
      <CardContent>
        <div className="variants-list">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="variant-row">
              <span className="variant-rank">#{i}</span>
              <span className="variant-path">Start → Activity A → Activity B → End</span>
              <span className="variant-count tabular-nums">{Math.floor(1000 / i)} cases</span>
              <span className="variant-percent tabular-nums">{(20 / i).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

export default ProcessDetail;
