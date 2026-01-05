import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Modal, Input, Button, message, Spin, Card, Typography } from 'antd';
import {
  LoadingOutlined,
  SettingOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import {
  PageHeader,
  ProcessQuestion,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
  useProcess,
} from '@lumina/design-system';
import { PROCESS_QUESTIONS } from './questionsData';
import { useAuditLogger } from '../../../shared/hooks';

const { TextArea } = Input;
const { Title, Text } = Typography;

/**
 * ProcessQuestionsPage - Question cards for process analysis
 * Users select a question to navigate to relevant analysis view
 * 
 * STATUS VALIDATION:
 * - Only shows questions if dataset.status === 'ready'
 * - For 'unstructured' status: prompts user to analyze (map columns)
 * - For 'analyzing' status: shows progress indicator
 * - For 'error' status: shows error with retry option
 */
export function ProcessQuestionsPage() {
  const { projectId, datasetId } = useParams<{ projectId: string; datasetId: string }>();
  const navigate = useNavigate();
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const auditLog = useAuditLogger();

  const { data: process, isLoading, error, refetch } = useProcess(datasetId || '');

  // Log page view for audit
  useEffect(() => {
    if (process && datasetId && projectId) {
      auditLog('explorer.viewed', { processId: datasetId, projectId, page: 'questions' });
    }
  }, [process, datasetId, projectId, auditLog]);

  const handleQuestionClick = (question: typeof PROCESS_QUESTIONS[0]) => {
    if (question.action === 'feedback') {
      setFeedbackModalOpen(true);
    } else if (question.route && projectId && datasetId) {
      navigate(question.route(projectId, datasetId));
    }
  };

  const handleFeedbackSubmit = () => {
    if (feedbackText.trim()) {
      message.success('Thank you for your feedback!');
      setFeedbackModalOpen(false);
      setFeedbackText('');
    } else {
      message.warning('Please enter your question or feedback');
    }
  };

  const handleGoToProject = () => {
    navigate(`/workspace/${projectId}`);
  };

  if (isLoading) {
    return <LoadingState type="fullPage" text="Loading process..." />;
  }

  if (error) {
    return (
      <QueryError
        error={error}
        onRetry={() => refetch()}
        variant="fullPage"
      />
    );
  }

  if (!process) {
    return (
      <EmptyState
        title="Process not found"
        description="The process you're looking for doesn't exist"
        actionLabel="Go Back"
        onAction={() => navigate(`/workspace/${projectId}`)}
      />
    );
  }

  // Dataset status validation - check if ready for analysis
  const status = (process as any).status || 'ready'; // Fallback for older API responses
  const totalCases = (process as any).totalCases || 0;

  // UNSTRUCTURED or ZOMBIE (Ready but 0 cases): Dataset needs column mapping
  if (status === 'unstructured' || (status === 'ready' && totalCases === 0)) {
    return (
      <div style={{ padding: tokens.spacing[8], maxWidth: 640, margin: '0 auto' }}>
        <Card>
          <div style={{ textAlign: 'center', padding: tokens.spacing[6] }}>
            <SettingOutlined style={{ fontSize: 48, color: tokens.colors.primary[500], marginBottom: 16 }} />
            <Title level={4}>Column Mapping Required</Title>
            <Text type="secondary" style={{ display: 'block', marginBottom: tokens.spacing[4] }}>
              Before exploring your process, you need to map the columns in your dataset.
              This tells us which columns contain the Case ID, Activity, and Timestamp.
            </Text>
            <Button type="primary" size="large" onClick={handleGoToProject}>
              Go to Project to Analyze
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // ANALYZING: Dataset is being processed
  if (status === 'analyzing') {
    return (
      <div style={{ padding: tokens.spacing[8], maxWidth: 640, margin: '0 auto' }}>
        <Card>
          <div style={{ textAlign: 'center', padding: tokens.spacing[6] }}>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
            <Title level={4} style={{ marginTop: tokens.spacing[4] }}>
              Processing Your Data...
            </Title>
            <Text type="secondary" style={{ display: 'block', marginBottom: tokens.spacing[4] }}>
              Your dataset is being analyzed. This may take a few moments depending on the file size.
            </Text>
            <Button onClick={() => refetch()}>Check Status</Button>
          </div>
        </Card>
      </div>
    );
  }

  // ERROR: Analysis failed
  if (status === 'error') {
    return (
      <div style={{ padding: tokens.spacing[8], maxWidth: 640, margin: '0 auto' }}>
        <Card>
          <div style={{ textAlign: 'center', padding: tokens.spacing[6] }}>
            <WarningOutlined style={{ fontSize: 48, color: tokens.colors.error[500], marginBottom: 16 }} />
            <Title level={4}>Analysis Failed</Title>
            <Text type="secondary" style={{ display: 'block', marginBottom: tokens.spacing[4] }}>
              There was an error processing your dataset. Please try again or contact support.
            </Text>
            <Button type="primary" onClick={handleGoToProject}>
              Go to Project to Retry
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // READY: Dataset is ready for analysis - show questions
  return (
    <div>
      <PageHeader
        title="Explore Your Process"
        description={`Analyzing: ${process.name}`}
        breadcrumb={[
          { label: 'Workspace', href: '/workspace' },
          { label: 'Project', href: `/workspace/${projectId}` },
          { label: 'Questions' },
        ]}
      />

      <div style={{ marginTop: tokens.spacing[6] }}>
        <Row gutter={[24, 24]}>
          {PROCESS_QUESTIONS.map((question) => {
            const IconComponent = question.icon;
            return (
              <Col xs={24} sm={12} lg={8} key={question.id}>
                <ProcessQuestion
                  icon={<IconComponent />}
                  title={question.title}
                  description={question.description}
                  onClick={() => handleQuestionClick(question)}
                />
              </Col>
            );
          })}
        </Row>
      </div>

      <Modal
        title="What would you like to know?"
        open={feedbackModalOpen}
        onCancel={() => setFeedbackModalOpen(false)}
        footer={[
          <Button key="cancel" onClick={() => setFeedbackModalOpen(false)}>
            Cancel
          </Button>,
          <Button key="submit" type="primary" onClick={handleFeedbackSubmit}>
            Submit
          </Button>,
        ]}
      >
        <TextArea
          rows={4}
          placeholder="Tell us what questions you have about your process..."
          value={feedbackText}
          onChange={(e) => setFeedbackText(e.target.value)}
          style={{ marginTop: tokens.spacing[4] }}
        />
      </Modal>
    </div>
  );
}

export default ProcessQuestionsPage;

