import React, { useEffect } from 'react';
import { Card, Input, Row, Col, Collapse, Button, Typography, Space } from 'antd';
import {
  SearchOutlined,
  UploadOutlined,
  CompassOutlined,
  BarChartOutlined,
  QuestionCircleOutlined,
  MailOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, tokens } from '@lumina/design-system';
import { createLogger } from '../utils/logger';

const log = createLogger('Help');
const { Title, Paragraph, Text, Link } = Typography;

interface GettingStartedCard {
  icon: React.ReactNode;
  title: string;
  description: string;
  path: string;
}

const gettingStartedCards: GettingStartedCard[] = [
  {
    icon: <UploadOutlined style={{ fontSize: 32, color: tokens.colors.primary[500] }} />,
    title: 'Upload your first file',
    description: 'Get started by uploading a CSV or XES event log file',
    path: '/processes/upload',
  },
  {
    icon: <CompassOutlined style={{ fontSize: 32, color: tokens.colors.success[500] }} />,
    title: 'Explore processes',
    description: 'Visualize and understand your process flows',
    path: '/explorer',
  },
  {
    icon: <BarChartOutlined style={{ fontSize: 32, color: tokens.colors.warning[500] }} />,
    title: 'Analytics overview',
    description: 'Discover insights and optimize your processes',
    path: '/analytics',
  },
];

const faqItems = [
  {
    key: '1',
    label: 'How do I upload a file?',
    children: (
      <Paragraph>
        Navigate to Event Logs in the sidebar and click "Upload File". You can drag and drop
        your CSV or XES file, or click to browse. The system will automatically detect columns
        and guide you through mapping them to the required fields (Case ID, Activity, Timestamp).
      </Paragraph>
    ),
  },
  {
    key: '2',
    label: 'What file formats are supported?',
    children: (
      <Paragraph>
        We currently support <Text strong>CSV</Text> and <Text strong>XES</Text> file formats.
        CSV files should have columns for case identifier, activity name, and timestamp at minimum.
        XES files follow the IEEE XES standard for event logs.
      </Paragraph>
    ),
  },
  {
    key: '3',
    label: 'How do I interpret the process map?',
    children: (
      <Paragraph>
        The process map shows activities as nodes and transitions as edges. The thickness of edges
        represents frequency - thicker edges mean more cases followed that path. Colors indicate
        performance metrics like duration. Click on any node or edge to see detailed statistics.
      </Paragraph>
    ),
  },
  {
    key: '4',
    label: 'What are process variants?',
    children: (
      <Paragraph>
        A variant is a unique sequence of activities that cases follow from start to end.
        For example, if some orders go through approval while others don't, those represent
        different variants. The variant explorer helps you understand the most common paths
        and identify deviations.
      </Paragraph>
    ),
  },
  {
    key: '5',
    label: 'How can I filter my process data?',
    children: (
      <Paragraph>
        Use the filter panel in the Process Explorer to narrow down your analysis. You can filter
        by time period, include or exclude specific activities, focus on top variants, or apply
        custom attribute filters. All visualizations update in real-time as you apply filters.
      </Paragraph>
    ),
  },
];

export function HelpCenterPage() {
  const navigate = useNavigate();

  useEffect(() => {
    log.info('Help center viewed');
  }, []);

  const handleCardClick = (path: string) => {
    log.info('Getting started card clicked', { path });
    navigate(path);
  };

  const handleContactSupport = () => {
    log.info('Contact support clicked');
    window.open('mailto:support@lumina.io', '_blank');
  };

  const handleViewDocs = () => {
    log.info('Documentation link clicked');
    // In a real app, this would open documentation
    window.open('https://docs.lumina.io', '_blank');
  };

  return (
    <div>
      <PageHeader
        title="Help Center"
        description="Find answers and get help with the platform"
      />

      {/* Search */}
      <Input
        size="large"
        placeholder="Search help articles..."
        prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
        style={{ marginBottom: tokens.spacing[8] }}
        disabled
      />

      {/* Getting Started */}
      <Title level={4} style={{ marginBottom: tokens.spacing[4] }}>
        Getting Started
      </Title>
      <Row gutter={[16, 16]} style={{ marginBottom: tokens.spacing[8] }}>
        {gettingStartedCards.map((card, index) => (
          <Col xs={24} sm={8} key={index}>
            <Card
              hoverable
              onClick={() => handleCardClick(card.path)}
              style={{
                textAlign: 'center',
                height: '100%',
                cursor: 'pointer',
              }}
              bodyStyle={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: tokens.spacing[6],
              }}
            >
              <div style={{ marginBottom: tokens.spacing[3] }}>{card.icon}</div>
              <Text strong style={{ marginBottom: tokens.spacing[1] }}>
                {card.title}
              </Text>
              <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                {card.description}
              </Text>
            </Card>
          </Col>
        ))}
      </Row>

      {/* FAQ */}
      <Title level={4} style={{ marginBottom: tokens.spacing[4] }}>
        Common Questions
      </Title>
      <Collapse
        items={faqItems}
        defaultActiveKey={[]}
        style={{ marginBottom: tokens.spacing[8] }}
        expandIcon={({ isActive }) => (
          <QuestionCircleOutlined
            style={{
              color: isActive ? tokens.colors.primary[500] : tokens.colors.neutral[400],
            }}
          />
        )}
      />

      {/* Need More Help */}
      <Card style={{ backgroundColor: tokens.colors.neutral[50] }}>
        <Title level={5} style={{ marginBottom: tokens.spacing[2] }}>
          Need more help?
        </Title>
        <Paragraph type="secondary" style={{ marginBottom: tokens.spacing[4] }}>
          Can't find what you're looking for? Our support team is here to help.
        </Paragraph>
        <Space>
          <Button icon={<MailOutlined />} onClick={handleContactSupport}>
            Contact Support
          </Button>
          <Button type="link" icon={<BookOutlined />} onClick={handleViewDocs}>
            View Documentation →
          </Button>
        </Space>
      </Card>
    </div>
  );
}

export default HelpCenterPage;
