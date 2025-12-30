import React from 'react';
import { Card, Typography } from 'antd';

const { Text } = Typography;

export type VendorType = 'oracle' | 'sap' | 'google' | 'file' | 'custom';

export interface QuickstartCardProps {
  /** Main title displayed on the card */
  title: string;
  /** Optional subtitle or process type */
  subtitle?: string;
  /** Vendor type determines the logo displayed */
  vendor: VendorType;
  /** Click handler for navigation */
  onClick?: () => void;
  /** Custom logo element (used when vendor is 'custom') */
  customLogo?: React.ReactNode;
}

// Inline SVG logos for vendors
const OracleLogo: React.FC = () => (
  <svg viewBox="0 0 120 24" fill="white" width="100" height="20">
    <text x="0" y="18" fontFamily="Arial, sans-serif" fontSize="18" fontWeight="bold">
      ORACLE
    </text>
  </svg>
);

const SAPLogo: React.FC = () => (
  <svg viewBox="0 0 60 30" fill="none" width="60" height="30">
    <rect width="60" height="30" rx="2" fill="white" />
    <text x="8" y="22" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" fill="#1B2838">
      SAP
    </text>
  </svg>
);

const GoogleSheetsLogo: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="white" width="32" height="32">
    <path d="M14 2H6C4.9 2 4 2.9 4 4v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
  </svg>
);

const FileLogo: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="white" width="32" height="32">
    <path d="M14 2H6C4.9 2 4 2.9 4 4v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6z"/>
  </svg>
);

const vendorLogos: Record<VendorType, React.FC> = {
  oracle: OracleLogo,
  sap: SAPLogo,
  google: GoogleSheetsLogo,
  file: FileLogo,
  custom: () => null,
};

/**
 * QuickstartCard - A tile component for connector/quickstart cards
 * 
 * Displays a dark card with vendor logo and optional process type badge.
 * Used in the Quickstarts hub for ERP connections and file imports.
 */
export const QuickstartCard: React.FC<QuickstartCardProps> = ({
  title,
  subtitle,
  vendor,
  onClick,
  customLogo,
}) => {
  const LogoComponent = vendorLogos[vendor];

  return (
    <Card
      hoverable
      onClick={onClick}
      styles={{
        body: {
          background: '#1B2838',
          borderRadius: 12,
          padding: 24,
          minHeight: 160,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          cursor: 'pointer',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        },
      }}
      style={{
        border: 'none',
        borderRadius: 12,
        overflow: 'hidden',
      }}
      className="quickstart-card"
    >
      {/* Title / Subtitle area */}
      <div>
        {subtitle && (
          <Text
            style={{
              color: 'rgba(255, 255, 255, 0.9)',
              fontSize: 14,
              fontWeight: 500,
              display: 'block',
              marginBottom: 4,
            }}
          >
            {subtitle}
          </Text>
        )}
        {title && !subtitle && (
          <Text
            style={{
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: 12,
              display: 'block',
            }}
          >
            {title}
          </Text>
        )}
      </div>

      {/* Logo area */}
      <div style={{ marginTop: 'auto', paddingTop: 16 }}>
        {vendor === 'custom' ? customLogo : <LogoComponent />}
      </div>

      <style>{`
        .quickstart-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        }
        .quickstart-card .ant-card-body {
          background: #1B2838 !important;
        }
      `}</style>
    </Card>
  );
};

export default QuickstartCard;
