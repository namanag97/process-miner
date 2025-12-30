import React from 'react';
import { Row, Col, Card, Typography, Empty, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  PlusOutlined,
  FileTextOutlined,
  TableOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

// ============================================================================
// Vendor Logo Components (inline SVGs for reliability)
// ============================================================================

const OracleLogo: React.FC = () => (
  <svg viewBox="0 0 120 24" fill="white" width="90" height="18">
    <text x="0" y="18" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" letterSpacing="2">
      ORACLE
    </text>
  </svg>
);

const SAPLogo: React.FC = () => (
  <svg viewBox="0 0 50 24" fill="none" width="50" height="24">
    <rect width="50" height="24" rx="2" fill="white" />
    <text x="7" y="18" fontFamily="Arial, sans-serif" fontSize="14" fontWeight="bold" fill="#1B2838">
      SAP
    </text>
  </svg>
);

const GoogleSheetsIcon: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="white" width="28" height="28">
    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
    <path d="M7 7h4v4H7zm6 0h4v2h-4zm0 4h4v2h-4zm0 4h4v2h-4zm-6 0h4v2H7zm0-4h4v2H7z"/>
  </svg>
);

const XESFileIcon: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="white" width="28" height="28">
    <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
    <text x="7" y="16" fontSize="6" fill="white" fontWeight="bold">XES</text>
  </svg>
);

const CSVFileIcon: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="white" width="28" height="28">
    <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
    <text x="6" y="16" fontSize="6" fill="white" fontWeight="bold">CSV</text>
  </svg>
);

// ============================================================================
// QuickstartCard Component (inline for simplicity)
// ============================================================================

interface QuickstartCardProps {
  title?: string;
  subtitle?: string;
  logo: React.ReactNode;
  onClick?: () => void;
}

const QuickstartCard: React.FC<QuickstartCardProps> = ({
  title,
  subtitle,
  logo,
  onClick,
}) => (
  <Card
    hoverable
    onClick={onClick}
    style={{
      background: '#1B2838',
      border: 'none',
      borderRadius: 12,
      overflow: 'hidden',
      cursor: 'pointer',
      transition: 'transform 0.2s ease, box-shadow 0.2s ease',
    }}
    styles={{
      body: {
        padding: 20,
        minHeight: 140,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      },
    }}
    className="quickstart-card"
  >
    <div>
      {subtitle && (
        <Text
          style={{
            color: '#FFFFFF',
            fontSize: 13,
            fontWeight: 500,
            display: 'block',
          }}
        >
          {subtitle}
        </Text>
      )}
      {title && (
        <Text
          style={{
            color: 'rgba(255, 255, 255, 0.7)',
            fontSize: 11,
            display: 'block',
            marginTop: 2,
          }}
        >
          {title}
        </Text>
      )}
    </div>
    <div style={{ marginTop: 'auto', paddingTop: 12 }}>
      {logo}
    </div>
  </Card>
);

// ============================================================================
// SectionHeader Component
// ============================================================================

interface SectionHeaderProps {
  title: string;
  description?: string;
}

const SectionHeader: React.FC<SectionHeaderProps> = ({ title, description }) => (
  <div style={{ marginBottom: 16 }}>
    <Title level={4} style={{ marginBottom: 4, fontSize: 16, fontWeight: 600 }}>
      {title}
    </Title>
    {description && (
      <Text type="secondary" style={{ fontSize: 14 }}>
        {description}
      </Text>
    )}
  </div>
);

// ============================================================================
// Dashboard Page Component
// ============================================================================

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const handleConnectorClick = (connector: string) => {
    // Navigate to upload page with connector context
    navigate(`/data/upload?source=${connector}`);
  };

  return (
    <div>
      {/* Global Styles for hover effect */}
      <style>{`
        .quickstart-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25) !important;
        }
      `}</style>

      {/* Page Header */}
      <div style={{ marginBottom: 32 }}>
        <Title level={2} style={{ marginBottom: 4, fontWeight: 600 }}>
          Quickstarts
        </Title>
        <Text type="secondary" style={{ fontSize: 15 }}>
          Connect to your business data or upload event logs to start process mining
        </Text>
      </div>

      {/* ERP Process Connectors Section */}
      <section style={{ marginBottom: 40 }}>
        <SectionHeader
          title="ERP Process Connectors"
          description="Connect to business processes for common source systems."
        />
        <Row gutter={[16, 16]}>
          {/* Oracle Connectors */}
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              subtitle="Order Management"
              logo={<OracleLogo />}
              onClick={() => handleConnectorClick('oracle-om')}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              subtitle="Procurement"
              logo={<OracleLogo />}
              onClick={() => handleConnectorClick('oracle-procurement')}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              logo={<OracleLogo />}
              onClick={() => handleConnectorClick('oracle-generic')}
            />
          </Col>

          {/* SAP Connectors */}
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              subtitle="Accounts Payable"
              logo={<SAPLogo />}
              onClick={() => handleConnectorClick('sap-ap')}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              subtitle="Accounts Receivable"
              logo={<SAPLogo />}
              onClick={() => handleConnectorClick('sap-ar')}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              subtitle="Order Management"
              logo={<SAPLogo />}
              onClick={() => handleConnectorClick('sap-om')}
            />
          </Col>
        </Row>
      </section>

      {/* Event Log Import Section */}
      <section style={{ marginBottom: 40 }}>
        <SectionHeader
          title="Event Log Import"
          description="Upload process data from files or connect to spreadsheets."
        />
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              subtitle="Google Sheets"
              title="Connect spreadsheet"
              logo={<GoogleSheetsIcon />}
              onClick={() => handleConnectorClick('google-sheets')}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              subtitle="XES File"
              title="Process mining format"
              logo={<XESFileIcon />}
              onClick={() => handleConnectorClick('xes')}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <QuickstartCard
              subtitle="CSV / Excel"
              title="Tabular data"
              logo={<CSVFileIcon />}
              onClick={() => handleConnectorClick('csv')}
            />
          </Col>
        </Row>
      </section>

      {/* Recent Workspaces Section */}
      <section>
        <SectionHeader
          title="Recent Workspaces"
          description="Your process mining projects and analyses."
        />
        <Card
          style={{ borderRadius: 12 }}
          styles={{ body: { padding: 32 } }}
        >
          <Empty
            image={<FileTextOutlined style={{ fontSize: 48, color: '#C1C7D0' }} />}
            description={
              <div>
                <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
                  No workspaces yet. Get started by connecting a data source above.
                </Text>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => navigate('/data/upload')}
                >
                  Create Workspace
                </Button>
              </div>
            }
          />
        </Card>
      </section>
    </div>
  );
};

export default DashboardPage;
