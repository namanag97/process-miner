import React from 'react';
import { Row, Col } from 'antd';
import { LineChartOutlined, ClockCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { MetricCard, EmptyState, tokens } from '@lumina/design-system';

interface OverviewTabProps {
  stats?: {
    totalProjects: number;
    totalProcesses: number;
    activeAnalyses: number;
  };
}

/**
 * OverviewTab - Dashboard overview with key metrics
 * Shows high-level stats and recent activity summary
 */
export function OverviewTab({ stats }: OverviewTabProps) {
  if (!stats || stats.totalProjects === 0) {
    return (
      <EmptyState
        icon={<LineChartOutlined />}
        title="No data yet"
        description="Create a project and upload data to see your process insights here"
      />
    );
  }

  return (
    <div style={{ padding: tokens.spacing[4] }}>
      <Row gutter={[24, 24]}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Total Projects"
            value={stats.totalProjects}
            prefix={<LineChartOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Total Processes"
            value={stats.totalProcesses}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Active Analyses"
            value={stats.activeAnalyses}
            prefix={<CheckCircleOutlined />}
            status="success"
          />
        </Col>
      </Row>
    </div>
  );
}

export default OverviewTab;
