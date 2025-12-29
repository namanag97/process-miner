import React from 'react';
import { Typography, Card, Table, Tag } from 'antd';

const { Title, Text } = Typography;

const mockModels = [
  {
    key: '1',
    name: 'Order Process Model',
    type: 'Petri Net',
    source: 'Order-to-Cash Q4',
    createdAt: '2024-12-16',
  },
  {
    key: '2',
    name: 'Procurement DFG',
    type: 'DFG',
    source: 'Procure-to-Pay',
    createdAt: '2024-12-12',
  },
];

const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: 'Type',
    dataIndex: 'type',
    key: 'type',
    render: (type: string) => <Tag>{type}</Tag>,
  },
  {
    title: 'Source Log',
    dataIndex: 'source',
    key: 'source',
  },
  {
    title: 'Created',
    dataIndex: 'createdAt',
    key: 'createdAt',
  },
];

const ModelsPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Process Models</Title>
        <Text type="secondary">Discovered process models</Text>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={mockModels}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default ModelsPage;
