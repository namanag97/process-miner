import React from 'react';
import { Typography, Card, Row, Col, Button } from 'antd';
import { ApiOutlined, DatabaseOutlined, CloudOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const connectors = [
  {
    name: 'SAP ERP',
    icon: <DatabaseOutlined style={{ fontSize: 32, color: '#0052CC' }} />,
    description: 'Connect to SAP ERP systems',
    status: 'available',
  },
  {
    name: 'Salesforce',
    icon: <CloudOutlined style={{ fontSize: 32, color: '#00A1E0' }} />,
    description: 'Connect to Salesforce CRM',
    status: 'available',
  },
  {
    name: 'REST API',
    icon: <ApiOutlined style={{ fontSize: 32, color: '#36B37E' }} />,
    description: 'Connect via custom REST API',
    status: 'available',
  },
];

const ConnectorsPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Connectors</Title>
        <Text type="secondary">Connect external data sources</Text>
      </div>

      <Row gutter={[16, 16]}>
        {connectors.map((connector) => (
          <Col xs={24} sm={12} lg={8} key={connector.name}>
            <Card
              hoverable
              style={{ textAlign: 'center' }}
            >
              <div style={{ marginBottom: 16 }}>{connector.icon}</div>
              <Title level={5} style={{ marginBottom: 8 }}>{connector.name}</Title>
              <Text type="secondary">{connector.description}</Text>
              <div style={{ marginTop: 16 }}>
                <Button type="primary">Configure</Button>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default ConnectorsPage;
