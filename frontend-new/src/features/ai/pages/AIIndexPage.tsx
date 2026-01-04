import { useNavigate } from 'react-router-dom';
import { Row, Col, Card, Space, Typography, Statistic } from 'antd';
import {
  BulbOutlined,
  ExperimentOutlined,
  RocketOutlined,
  ThunderboltOutlined,
  RobotOutlined,
  LineChartOutlined,
} from '@ant-design/icons';
import { PageHeader, tokens, logAction } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';

const { Text, Title } = Typography;
const log = createLogger('AIIndexPage');

// Feature card data
const features = [
  {
    key: 'insights',
    title: 'AI Insights',
    description: 'Auto-generated insights from your process data. Discover bottlenecks, patterns, and optimization opportunities.',
    icon: <BulbOutlined style={{ fontSize: 32, color: tokens.colors.primary[500] }} />,
    route: '/ai/insights',
    stats: { label: 'Active Insights', value: 12 },
  },
  {
    key: 'predictions',
    title: 'Predictions',
    description: 'Train ML models to predict next activities, remaining time, and process outcomes.',
    icon: <ExperimentOutlined style={{ fontSize: 32, color: tokens.colors.success[500] }} />,
    route: '/ai/predictions',
    stats: { label: 'Trained Models', value: 3 },
  },
];

// Quick action cards
const quickActions = [
  {
    key: 'generate',
    title: 'Generate Insights',
    description: 'Analyze your latest event log',
    icon: <ThunderboltOutlined />,
    action: '/ai/insights',
  },
  {
    key: 'train',
    title: 'Train Predictor',
    description: 'Create a new prediction model',
    icon: <RobotOutlined />,
    action: '/ai/predictions?action=train',
  },
  {
    key: 'analyze',
    title: 'Pattern Analysis',
    description: 'Discover frequent patterns',
    icon: <LineChartOutlined />,
    action: '/ai/insights?tab=patterns',
  },
];

export function AIIndexPage() {
  const navigate = useNavigate();

  const handleFeatureClick = (route: string) => {
    logAction('AIIndexPage', 'feature_clicked', { route });
    log.debug('Feature card clicked', { route });
    navigate(route);
  };

  const handleQuickAction = (action: string) => {
    logAction('AIIndexPage', 'quick_action_clicked', { action });
    log.debug('Quick action clicked', { action });
    navigate(action);
  };

  return (
    <div>
      <PageHeader
        title="AI & Advanced"
        description="Leverage machine learning to discover insights and predict process outcomes"
      />

      {/* Summary Stats */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Insights Generated"
              value={47}
              prefix={<BulbOutlined style={{ color: tokens.colors.primary[500] }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Active Predictors"
              value={3}
              prefix={<ExperimentOutlined style={{ color: tokens.colors.success[500] }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Predictions Made"
              value={1284}
              prefix={<RocketOutlined style={{ color: tokens.colors.warning[500] }} />}
            />
          </Card>
        </Col>
      </Row>

      {/* Feature Cards */}
      <Title level={5} style={{ marginBottom: tokens.spacing[4] }}>
        AI Features
      </Title>
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        {features.map((feature) => (
          <Col xs={24} md={12} key={feature.key}>
            <Card
              hoverable
              onClick={() => handleFeatureClick(feature.route)}
              style={{ marginBottom: tokens.spacing[4], cursor: 'pointer' }}
            >
              <Space align="start" size={16}>
                <div
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: 8,
                    backgroundColor: tokens.colors.neutral[50],
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {feature.icon}
                </div>
                <div style={{ flex: 1 }}>
                  <Title level={5} style={{ marginBottom: tokens.spacing[1] }}>
                    {feature.title}
                  </Title>
                  <Text type="secondary" style={{ display: 'block', marginBottom: tokens.spacing[2] }}>
                    {feature.description}
                  </Text>
                  <Text strong style={{ color: tokens.colors.primary[500] }}>
                    {feature.stats.value} {feature.stats.label}
                  </Text>
                </div>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Quick Actions */}
      <Title level={5} style={{ marginBottom: tokens.spacing[4] }}>
        Quick Actions
      </Title>
      <Row gutter={16}>
        {quickActions.map((action) => (
          <Col xs={24} sm={8} key={action.key}>
            <Card
              hoverable
              size="small"
              onClick={() => handleQuickAction(action.action)}
              style={{ cursor: 'pointer', textAlign: 'center' }}
            >
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  backgroundColor: tokens.colors.primary[50],
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto',
                  marginBottom: tokens.spacing[3],
                  fontSize: 24,
                  color: tokens.colors.primary[500],
                }}
              >
                {action.icon}
              </div>
              <Title level={5} style={{ marginBottom: tokens.spacing[1] }}>
                {action.title}
              </Title>
              <Text type="secondary">{action.description}</Text>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

export default AIIndexPage;
