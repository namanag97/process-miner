import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Modal, Input, Button, message } from 'antd';
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
import { useAuditLogger } from '../../hooks';

const { TextArea } = Input;

/**
 * ProcessQuestionsPage - Question cards for process analysis
 * Users select a question to navigate to relevant analysis view
 */
export function ProcessQuestionsPage() {
  const { projectId, logId } = useParams<{ projectId: string; logId: string }>();
  const navigate = useNavigate();
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const auditLog = useAuditLogger();

  const { data: process, isLoading, error, refetch } = useProcess(logId || '');

  // Log page view for audit
  useEffect(() => {
    if (process && logId && projectId) {
      auditLog('explorer.viewed', { processId: logId, projectId, page: 'questions' });
    }
  }, [process, logId, projectId, auditLog]);

  const handleQuestionClick = (question: typeof PROCESS_QUESTIONS[0]) => {
    if (question.action === 'feedback') {
      setFeedbackModalOpen(true);
    } else if (question.route && projectId && logId) {
      navigate(question.route(projectId, logId));
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

  if (isLoading) {
    return <LoadingState type="fullPage" tip="Loading process..." />;
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
        onAction={() => navigate(`/projects/${projectId}`)}
      />
    );
  }

  return (
    <div>
      <PageHeader
        title="Explore Your Process"
        description={`Analyzing: ${process.name}`}
        breadcrumb={[
          { label: 'Home', href: '/home' },
          { label: 'Project', href: `/projects/${projectId}` },
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
