import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  Input,
  Row,
  Col,
  Collapse,
  Button,
  Typography,
  Space,
  Tabs,
  Tag,
  Modal,
  Badge,
  Divider,
  Timeline,
} from 'antd';
import {
  SearchOutlined,
  UploadOutlined,
  CompassOutlined,
  BarChartOutlined,
  QuestionCircleOutlined,
  MailOutlined,
  BookOutlined,
  KeyOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  RocketOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
  RobotOutlined,
  HistoryOutlined,
  LikeOutlined,
  DislikeOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, tokens } from '@/src/shared/design-system';
import { createLogger } from '../../../shared/lib/logger';

const log = createLogger('Help');
const { Title, Paragraph, Text } = Typography;

// ============ DATA ============

interface GettingStartedStep {
  icon: React.ReactNode;
  title: string;
  description: string;
  path: string;
  completed?: boolean;
}

const gettingStartedSteps: GettingStartedStep[] = [
  {
    icon: <UploadOutlined />,
    title: 'Upload your first file',
    description: 'Get started by uploading a CSV or XES event log file',
    path: '/workspace',
    completed: false,
  },
  {
    icon: <CompassOutlined />,
    title: 'Explore a process',
    description: 'Visualize and understand your process flows',
    path: '/explorer',
    completed: false,
  },
  {
    icon: <BarChartOutlined />,
    title: 'Analyze performance',
    description: 'Discover bottlenecks and optimize your processes',
    path: '/analytics',
    completed: false,
  },
  {
    icon: <RobotOutlined />,
    title: 'Get AI insights',
    description: 'Let AI help you understand your processes',
    path: '/ai/insights',
    completed: false,
  },
];

interface GuideCategory {
  key: string;
  label: string;
  icon: React.ReactNode;
  color: string;
}

const guideCategories: GuideCategory[] = [
  { key: 'data', label: 'Data Import', icon: <UploadOutlined />, color: tokens.colors.primary[500] },
  { key: 'discovery', label: 'Process Discovery', icon: <CompassOutlined />, color: tokens.colors.success[500] },
  { key: 'analytics', label: 'Analytics', icon: <BarChartOutlined />, color: tokens.colors.warning[500] },
  { key: 'ai', label: 'AI Features', icon: <RobotOutlined />, color: tokens.colors.info[500] },
];

interface GuideItem {
  title: string;
  description: string;
  category: string;
  path: string;
}

const guides: GuideItem[] = [
  { title: 'Uploading CSV Files', description: 'Learn how to upload and map CSV columns', category: 'data', path: '/workspace' },
  { title: 'Importing XES Files', description: 'Work with IEEE XES standard event logs', category: 'data', path: '/workspace' },
  { title: 'Column Mapping', description: 'Map your data to Case ID, Activity, and Timestamp', category: 'data', path: '/help' },
  { title: 'Process Map Visualization', description: 'Understand nodes, edges, and frequency', category: 'discovery', path: '/explorer' },
  { title: 'Variant Analysis', description: 'Explore different execution paths', category: 'discovery', path: '/explorer' },
  { title: 'Filtering Processes', description: 'Use filters to focus your analysis', category: 'discovery', path: '/explorer' },
  { title: 'Performance Metrics', description: 'Analyze cycle times and throughput', category: 'analytics', path: '/analytics' },
  { title: 'Bottleneck Detection', description: 'Find and fix process delays', category: 'analytics', path: '/analytics' },
  { title: 'Resource Analytics', description: 'Analyze resource utilization', category: 'analytics', path: '/analytics' },
  { title: 'AI-Powered Insights', description: 'Get intelligent recommendations', category: 'ai', path: '/ai/insights' },
  { title: 'Outcome Predictions', description: 'Predict process outcomes', category: 'ai', path: '/ai/predictions' },
];

const faqItems = [
  {
    key: '1',
    label: 'How do I upload a file?',
    category: 'data',
    children: (
      <Paragraph>
        Navigate to <Text strong>Processes</Text> in the sidebar and click "Upload File". You can drag and drop
        your CSV or XES file, or click to browse. The system will automatically detect columns
        and guide you through mapping them to the required fields (Case ID, Activity, Timestamp).
      </Paragraph>
    ),
  },
  {
    key: '2',
    label: 'What file formats are supported?',
    category: 'data',
    children: (
      <Paragraph>
        We support <Text strong>CSV</Text> and <Text strong>XES</Text> file formats.
        CSV files should have columns for case identifier, activity name, and timestamp at minimum.
        XES files follow the IEEE XES standard for event logs.
      </Paragraph>
    ),
  },
  {
    key: '3',
    label: 'How do I interpret the process map?',
    category: 'discovery',
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
    category: 'discovery',
    children: (
      <Paragraph>
        A variant is a unique sequence of activities from start to end.
        For example, if some orders go through approval while others don't, those represent
        different variants. The variant explorer helps you understand the most common paths.
      </Paragraph>
    ),
  },
  {
    key: '5',
    label: 'How can I filter my process data?',
    category: 'analytics',
    children: (
      <Paragraph>
        Use the filter panel in the Process Explorer to narrow down your analysis. You can filter
        by time period, include or exclude specific activities, focus on top variants, or apply
        custom attribute filters. All visualizations update in real-time.
      </Paragraph>
    ),
  },
  {
    key: '6',
    label: 'How does AI insights work?',
    category: 'ai',
    children: (
      <Paragraph>
        Our AI analyzes your process data to identify patterns, anomalies, and improvement opportunities.
        It provides actionable recommendations based on industry best practices and your specific data.
      </Paragraph>
    ),
  },
];

interface ChangelogEntry {
  version: string;
  date: string;
  type: 'major' | 'minor' | 'patch';
  changes: { type: 'new' | 'improved' | 'fixed'; text: string }[];
}

const changelog: ChangelogEntry[] = [
  {
    version: '2.1.0',
    date: 'December 2024',
    type: 'minor',
    changes: [
      { type: 'new', text: 'User Audit Logs with comprehensive tracking' },
      { type: 'new', text: 'Enhanced Help Center with guides and keyboard shortcuts' },
      { type: 'improved', text: 'Process Explorer performance and animations' },
      { type: 'fixed', text: 'File upload progress indicator accuracy' },
    ],
  },
  {
    version: '2.0.0',
    date: 'November 2024',
    type: 'major',
    changes: [
      { type: 'new', text: 'AI Insights and Predictions module' },
      { type: 'new', text: 'Resource Analytics dashboard' },
      { type: 'improved', text: 'Complete UI redesign with premium styling' },
      { type: 'improved', text: 'Storybook component documentation' },
    ],
  },
  {
    version: '1.5.0',
    date: 'October 2024',
    type: 'minor',
    changes: [
      { type: 'new', text: 'Process variant analysis' },
      { type: 'new', text: 'Export process maps as images' },
      { type: 'fixed', text: 'Timezone handling in analytics' },
    ],
  },
  {
    version: '1.0.0',
    date: 'September 2024',
    type: 'major',
    changes: [
      { type: 'new', text: 'Initial release with core process mining features' },
      { type: 'new', text: 'CSV and XES file support' },
      { type: 'new', text: 'Interactive process map visualization' },
    ],
  },
];

const keyboardShortcuts = [
  {
    category: 'Navigation', shortcuts: [
      { keys: ['G', 'H'], description: 'Go to Home' },
      { keys: ['G', 'P'], description: 'Go to Processes' },
      { keys: ['G', 'E'], description: 'Go to Explorer' },
      { keys: ['G', 'A'], description: 'Go to Analytics' },
    ]
  },
  {
    category: 'Process Explorer', shortcuts: [
      { keys: ['F'], description: 'Toggle filter panel' },
      { keys: ['R'], description: 'Reset view' },
      { keys: ['+'], description: 'Zoom in' },
      { keys: ['-'], description: 'Zoom out' },
      { keys: ['Esc'], description: 'Deselect node' },
    ]
  },
  {
    category: 'General', shortcuts: [
      { keys: ['?'], description: 'Show keyboard shortcuts' },
      { keys: ['Cmd', 'K'], description: 'Quick search' },
      { keys: ['Cmd', 'S'], description: 'Save changes' },
    ]
  },
];

// ============ COMPONENTS ============

const GradientHero: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      background: `linear-gradient(135deg, ${tokens.colors.primary[50]} 0%, ${tokens.colors.neutral[0]} 100%)`,
      borderRadius: tokens.radius.xl,
      padding: tokens.spacing[8],
      marginBottom: tokens.spacing[6],
      border: `1px solid ${tokens.colors.primary[100]}`,
    }}
  >
    {children}
  </div>
);

const StepCard: React.FC<{
  step: GettingStartedStep;
  index: number;
  onClick: () => void;
}> = ({ step, index, onClick }) => (
  <Card
    hoverable
    onClick={onClick}
    style={{
      height: '100%',
      transition: 'all 0.2s ease',
      border: step.completed ? `2px solid ${tokens.colors.success[500]}` : undefined,
    }}
    bodyStyle={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      textAlign: 'center',
      padding: tokens.spacing[5],
    }}
  >
    <Badge
      count={step.completed ? <CheckCircleOutlined style={{ color: tokens.colors.success[500] }} /> : index + 1}
      style={{
        backgroundColor: step.completed ? 'transparent' : tokens.colors.primary[100],
        color: tokens.colors.primary[600],
        marginBottom: tokens.spacing[3],
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: tokens.radius.lg,
          background: `linear-gradient(135deg, ${tokens.colors.primary[100]} 0%, ${tokens.colors.primary[50]} 100%)`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 24,
          color: tokens.colors.primary[600],
        }}
      >
        {step.icon}
      </div>
    </Badge>
    <Text strong style={{ marginTop: tokens.spacing[2], marginBottom: tokens.spacing[1] }}>
      {step.title}
    </Text>
    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
      {step.description}
    </Text>
  </Card>
);

const GuideCard: React.FC<{
  guide: GuideItem;
  category: GuideCategory;
  onClick: () => void;
}> = ({ guide, category, onClick }) => (
  <Card
    hoverable
    size="small"
    onClick={onClick}
    style={{
      height: '100%',
      borderLeft: `3px solid ${category.color}`,
    }}
    bodyStyle={{ padding: tokens.spacing[4] }}
  >
    <Space direction="vertical" size={4} style={{ width: '100%' }}>
      <Tag
        icon={category.icon}
        style={{
          backgroundColor: `${category.color}15`,
          color: category.color,
          border: 'none',
        }}
      >
        {category.label}
      </Tag>
      <Text strong>{guide.title}</Text>
      <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
        {guide.description}
      </Text>
    </Space>
  </Card>
);

const ChangeTypeTag: React.FC<{ type: 'new' | 'improved' | 'fixed' }> = ({ type }) => {
  const config = {
    new: { color: 'green', label: 'New' },
    improved: { color: 'blue', label: 'Improved' },
    fixed: { color: 'orange', label: 'Fixed' },
  };
  return <Tag color={config[type].color}>{config[type].label}</Tag>;
};

const KeyboardKey: React.FC<{ children: string }> = ({ children }) => (
  <kbd
    style={{
      display: 'inline-block',
      padding: '2px 8px',
      fontSize: tokens.fontSize.sm,
      fontFamily: 'monospace',
      color: tokens.colors.neutral[700],
      backgroundColor: tokens.colors.neutral[100],
      border: `1px solid ${tokens.colors.neutral[300]}`,
      borderRadius: tokens.radius.sm,
      boxShadow: '0 1px 0 rgba(0,0,0,0.1)',
    }}
  >
    {children}
  </kbd>
);

// ============ MAIN COMPONENT ============

export function HelpCenterPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('getting-started');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [shortcutsModalOpen, setShortcutsModalOpen] = useState(false);

  useEffect(() => {
    log.info('Help center viewed');
  }, []);

  // Filter guides based on search and category
  const filteredGuides = useMemo(() => {
    return guides.filter((guide) => {
      const matchesSearch =
        !searchQuery ||
        guide.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        guide.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = !selectedCategory || guide.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [searchQuery, selectedCategory]);

  // Filter FAQs based on search
  const filteredFaqs = useMemo(() => {
    if (!searchQuery) return faqItems;
    return faqItems.filter(
      (faq) =>
        faq.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (selectedCategory && faq.category === selectedCategory)
    );
  }, [searchQuery, selectedCategory]);

  const handleNavigate = (path: string) => {
    log.info('Help navigation', { path });
    navigate(path);
  };

  const handleContactSupport = () => {
    log.info('Contact support clicked');
    window.open('mailto:support@lumina.io', '_blank');
  };

  const tabItems = [
    {
      key: 'getting-started',
      label: (
        <span>
          <RocketOutlined /> Getting Started
        </span>
      ),
      children: (
        <div>
          <GradientHero>
            <Row align="middle" gutter={24}>
              <Col flex="auto">
                <Title level={4} style={{ marginBottom: tokens.spacing[1] }}>
                  Welcome to Process Mining! 🎉
                </Title>
                <Paragraph type="secondary" style={{ margin: 0 }}>
                  Follow these steps to get the most out of the platform. Complete each step to unlock the full power of process analytics.
                </Paragraph>
              </Col>
              <Col>
                <Button
                  icon={<PlayCircleOutlined />}
                  style={{
                    backgroundColor: tokens.colors.primary[500],
                    color: 'white',
                    border: 'none',
                  }}
                  onClick={() => handleNavigate('/workspace')}
                >
                  Start Tutorial
                </Button>
              </Col>
            </Row>
          </GradientHero>

          <Title level={5} style={{ marginBottom: tokens.spacing[4] }}>
            <ThunderboltOutlined style={{ color: tokens.colors.warning[500], marginRight: 8 }} />
            Quick Start Checklist
          </Title>
          <Row gutter={[16, 16]}>
            {gettingStartedSteps.map((step, index) => (
              <Col xs={24} sm={12} lg={6} key={index}>
                <StepCard
                  step={step}
                  index={index}
                  onClick={() => handleNavigate(step.path)}
                />
              </Col>
            ))}
          </Row>

          <Divider />

          <Title level={5} style={{ marginBottom: tokens.spacing[4] }}>
            <PlayCircleOutlined style={{ color: tokens.colors.error[500], marginRight: 8 }} />
            Video Tutorials
          </Title>
          <Row gutter={[16, 16]}>
            {[
              { title: 'Getting Started Overview', duration: '5:30' },
              { title: 'Understanding Process Maps', duration: '8:15' },
              { title: 'Advanced Analytics', duration: '12:00' },
            ].map((video, index) => (
              <Col xs={24} sm={8} key={index}>
                <Card
                  hoverable
                  cover={
                    <div
                      style={{
                        height: 120,
                        background: `linear-gradient(135deg, ${tokens.colors.neutral[800]} 0%, ${tokens.colors.neutral[700]} 100%)`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        position: 'relative',
                      }}
                    >
                      <PlayCircleOutlined
                        style={{
                          fontSize: 48,
                          color: 'white',
                          opacity: 0.9,
                        }}
                      />
                      <Tag
                        style={{
                          position: 'absolute',
                          bottom: 8,
                          right: 8,
                          backgroundColor: 'rgba(0,0,0,0.7)',
                          color: 'white',
                          border: 'none',
                        }}
                      >
                        {video.duration}
                      </Tag>
                    </div>
                  }
                  bodyStyle={{ padding: tokens.spacing[3] }}
                >
                  <Text strong>{video.title}</Text>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      ),
    },
    {
      key: 'guides',
      label: (
        <span>
          <BookOutlined /> User Guides
        </span>
      ),
      children: (
        <div>
          <Row gutter={16} style={{ marginBottom: tokens.spacing[4] }}>
            <Col flex="auto">
              <Input
                placeholder="Search guides..."
                prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                allowClear
              />
            </Col>
          </Row>

          <Space wrap style={{ marginBottom: tokens.spacing[4] }}>
            <Button
              type={selectedCategory === null ? 'primary' : 'default'}
              onClick={() => setSelectedCategory(null)}
              size="small"
            >
              All
            </Button>
            {guideCategories.map((cat) => (
              <Button
                key={cat.key}
                type={selectedCategory === cat.key ? 'primary' : 'default'}
                icon={cat.icon}
                onClick={() => setSelectedCategory(cat.key)}
                size="small"
                style={
                  selectedCategory === cat.key
                    ? { backgroundColor: cat.color, borderColor: cat.color }
                    : undefined
                }
              >
                {cat.label}
              </Button>
            ))}
          </Space>

          <Row gutter={[16, 16]}>
            {filteredGuides.map((guide, index) => {
              const category = guideCategories.find((c) => c.key === guide.category)!;
              return (
                <Col xs={24} sm={12} lg={8} key={index}>
                  <GuideCard
                    guide={guide}
                    category={category}
                    onClick={() => handleNavigate(guide.path)}
                  />
                </Col>
              );
            })}
          </Row>

          {filteredGuides.length === 0 && (
            <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
              <Text type="secondary">No guides found matching your search.</Text>
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'faq',
      label: (
        <span>
          <QuestionCircleOutlined /> FAQ
        </span>
      ),
      children: (
        <div>
          <Input
            placeholder="Search frequently asked questions..."
            prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            allowClear
            style={{ marginBottom: tokens.spacing[4] }}
          />

          <Collapse
            items={filteredFaqs.map((faq) => ({
              ...faq,
              label: (
                <Space>
                  <Tag color={guideCategories.find((c) => c.key === faq.category)?.color} style={{ fontSize: 10 }}>
                    {guideCategories.find((c) => c.key === faq.category)?.label}
                  </Tag>
                  {faq.label}
                </Space>
              ),
              extra: (
                <Space size={4} onClick={(e) => e.stopPropagation()}>
                  <Button type="text" size="small" icon={<LikeOutlined />} />
                  <Button type="text" size="small" icon={<DislikeOutlined />} />
                </Space>
              ),
            }))}
            defaultActiveKey={[]}
            expandIcon={({ isActive }) => (
              <QuestionCircleOutlined
                style={{
                  color: isActive ? tokens.colors.primary[500] : tokens.colors.neutral[400],
                  transition: 'color 0.2s',
                }}
              />
            )}
          />

          {filteredFaqs.length === 0 && (
            <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
              <Text type="secondary">No FAQs found matching your search.</Text>
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'changelog',
      label: (
        <span>
          <HistoryOutlined /> Changelog
        </span>
      ),
      children: (
        <div>
          <Timeline
            items={changelog.map((release) => ({
              color:
                release.type === 'major'
                  ? tokens.colors.primary[500]
                  : release.type === 'minor'
                    ? tokens.colors.success[500]
                    : tokens.colors.neutral[400],
              children: (
                <Card
                  size="small"
                  style={{ marginBottom: tokens.spacing[2] }}
                  bodyStyle={{ padding: tokens.spacing[4] }}
                >
                  <Space style={{ marginBottom: tokens.spacing[2] }}>
                    <Text strong style={{ fontSize: tokens.fontSize.lg }}>
                      v{release.version}
                    </Text>
                    <Tag
                      color={
                        release.type === 'major'
                          ? 'blue'
                          : release.type === 'minor'
                            ? 'green'
                            : 'default'
                      }
                    >
                      {release.type.toUpperCase()}
                    </Tag>
                    <Text type="secondary">{release.date}</Text>
                  </Space>
                  <ul style={{ margin: 0, paddingLeft: tokens.spacing[4] }}>
                    {release.changes.map((change, idx) => (
                      <li key={idx} style={{ marginBottom: 4 }}>
                        <ChangeTypeTag type={change.type} />
                        <Text style={{ marginLeft: 8 }}>{change.text}</Text>
                      </li>
                    ))}
                  </ul>
                </Card>
              ),
            }))}
          />
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Help Center"
        description="Find answers, learn features, and get the most out of the platform"
        actions={
          <Space>
            <Button
              icon={<KeyOutlined />}
              onClick={() => setShortcutsModalOpen(true)}
            >
              Keyboard Shortcuts
            </Button>
            <Button icon={<FileTextOutlined />} onClick={() => navigate('/audit-logs')}>
              Audit Logs
            </Button>
          </Space>
        }
      />

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        size="large"
        style={{ marginBottom: tokens.spacing[6] }}
      />

      {/* Support Card */}
      <Card
        style={{
          background: `linear-gradient(135deg, ${tokens.colors.neutral[50]} 0%, ${tokens.colors.primary[50]} 100%)`,
          border: `1px solid ${tokens.colors.primary[100]}`,
        }}
      >
        <Row align="middle" gutter={16}>
          <Col>
            <BulbOutlined
              style={{
                fontSize: 32,
                color: tokens.colors.warning[500],
              }}
            />
          </Col>
          <Col flex="auto">
            <Title level={5} style={{ marginBottom: 0 }}>
              Need more help?
            </Title>
            <Text type="secondary">
              Can't find what you're looking for? Our support team is here to help.
            </Text>
          </Col>
          <Col>
            <Space>
              <Button icon={<MailOutlined />} onClick={handleContactSupport}>
                Contact Support
              </Button>
              <Button
                type="link"
                icon={<BookOutlined />}
                onClick={() => window.open('https://docs.lumina.io', '_blank')}
              >
                View Docs →
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Keyboard Shortcuts Modal */}
      <Modal
        title={
          <Space>
            <KeyOutlined />
            Keyboard Shortcuts
          </Space>
        }
        open={shortcutsModalOpen}
        onCancel={() => setShortcutsModalOpen(false)}
        footer={null}
        width={500}
      >
        {keyboardShortcuts.map((group) => (
          <div key={group.category} style={{ marginBottom: tokens.spacing[4] }}>
            <Text
              strong
              style={{
                display: 'block',
                marginBottom: tokens.spacing[2],
                color: tokens.colors.neutral[600],
              }}
            >
              {group.category}
            </Text>
            {group.shortcuts.map((shortcut, idx) => (
              <Row
                key={idx}
                justify="space-between"
                align="middle"
                style={{
                  padding: `${tokens.spacing[2]}px 0`,
                  borderBottom:
                    idx < group.shortcuts.length - 1
                      ? `1px solid ${tokens.colors.neutral[100]}`
                      : undefined,
                }}
              >
                <Col>
                  <Text>{shortcut.description}</Text>
                </Col>
                <Col>
                  <Space size={4}>
                    {shortcut.keys.map((key, keyIdx) => (
                      <React.Fragment key={keyIdx}>
                        <KeyboardKey>{key}</KeyboardKey>
                        {keyIdx < shortcut.keys.length - 1 && (
                          <Text type="secondary" style={{ fontSize: 10 }}>
                            +
                          </Text>
                        )}
                      </React.Fragment>
                    ))}
                  </Space>
                </Col>
              </Row>
            ))}
          </div>
        ))}
        <div
          style={{
            marginTop: tokens.spacing[4],
            padding: tokens.spacing[3],
            backgroundColor: tokens.colors.info[50],
            borderRadius: tokens.radius.md,
          }}
        >
          <Space>
            <InfoCircleOutlined style={{ color: tokens.colors.info[500] }} />
            <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
              Press <KeyboardKey>?</KeyboardKey> anywhere to open this dialog
            </Text>
          </Space>
        </div>
      </Modal>
    </div>
  );
}

export default HelpCenterPage;
