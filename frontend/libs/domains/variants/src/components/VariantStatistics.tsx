import React, { useMemo } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Typography,
  Space,
  Divider,
  Alert,
  Spin,
} from 'antd';
import {
  BranchesOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import type { ProcessVariant } from 'process-mining-sdk';
import { useVariants } from '../hooks';

const { Text, Title } = Typography;

interface VariantStatisticsProps {
  logId: string;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

export const VariantStatistics: React.FC<VariantStatisticsProps> = ({ logId }) => {
  const { data, isLoading, error } = useVariants(logId);

  const stats = useMemo(() => {
    if (!data?.variants || data.variants.length === 0) {
      return null;
    }

    const variants = data.variants as ProcessVariant[];
    const totalCases = variants.reduce((sum: number, v: ProcessVariant) => sum + v.caseCount, 0);
    const totalVariants = variants.length;
    const happyPathVariants = variants.filter((v: ProcessVariant) => v.isHappyPath);

    // Calculate coverage by top variants
    let cumulativeCases = 0;
    let top80Index = 0;
    for (let i = 0; i < variants.length; i++) {
      cumulativeCases += variants[i].caseCount;
      if (cumulativeCases / totalCases >= 0.8) {
        top80Index = i + 1;
        break;
      }
    }

    const avgLength =
      variants.reduce((sum: number, v: ProcessVariant) => sum + v.length, 0) / variants.length;
    const avgDuration =
      variants.reduce((sum: number, v: ProcessVariant) => sum + (v.avgDurationSeconds || 0), 0) /
      variants.length;

    const minLength = Math.min(...variants.map((v: ProcessVariant) => v.length));
    const maxLength = Math.max(...variants.map((v: ProcessVariant) => v.length));

    const topVariantCoverage = variants[0]
      ? (variants[0].caseCount / totalCases) * 100
      : 0;

    return {
      totalVariants,
      totalCases,
      happyPathCount: happyPathVariants.length,
      happyPathCoverage: happyPathVariants.reduce(
        (sum: number, v: ProcessVariant) => sum + (v.caseCount / totalCases) * 100,
        0
      ),
      top80VariantCount: top80Index,
      top80Coverage: (top80Index / totalVariants) * 100,
      avgLength,
      avgDuration,
      minLength,
      maxLength,
      topVariantCoverage,
      mostFrequentVariant: variants[0],
    };
  }, [data]);

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load statistics"
        description="Could not calculate variant statistics."
      />
    );
  }

  if (isLoading) {
    return (
      <Card>
        <Spin tip="Calculating statistics..." />
      </Card>
    );
  }

  if (!stats) {
    return (
      <Card>
        <Text type="secondary">No variant data available</Text>
      </Card>
    );
  }

  return (
    <Card title={<Space><BarChartOutlined /> Variant Statistics</Space>}>
      {/* Primary Metrics */}
      <Row gutter={[16, 24]}>
        <Col xs={12} sm={8} md={6}>
          <Statistic
            title="Total Variants"
            value={stats.totalVariants}
            prefix={<BranchesOutlined />}
          />
        </Col>
        <Col xs={12} sm={8} md={6}>
          <Statistic
            title="Total Cases"
            value={stats.totalCases}
            prefix={<BarChartOutlined />}
          />
        </Col>
        <Col xs={12} sm={8} md={6}>
          <Statistic
            title="Happy Paths"
            value={stats.happyPathCount}
            prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
          />
        </Col>
        <Col xs={12} sm={8} md={6}>
          <Statistic
            title="Avg Duration"
            value={formatDuration(stats.avgDuration)}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
      </Row>

      <Divider />

      {/* Coverage Analysis */}
      <Title level={5}>Coverage Analysis</Title>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12}>
          <div style={{ marginBottom: 8 }}>
            <Text>Top Variant Coverage</Text>
          </div>
          <Progress
            percent={stats.topVariantCoverage}
            strokeColor="#0052cc"
            format={(pct) => `${pct?.toFixed(1)}%`}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            Most frequent variant: {stats.mostFrequentVariant?.key}
          </Text>
        </Col>
        <Col xs={24} sm={12}>
          <div style={{ marginBottom: 8 }}>
            <Text>80% Case Coverage</Text>
          </div>
          <Progress
            percent={(stats.top80VariantCount / stats.totalVariants) * 100}
            strokeColor="#52c41a"
            format={() =>
              `${stats.top80VariantCount} of ${stats.totalVariants} variants`
            }
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {stats.top80VariantCount} variants cover 80% of all cases
          </Text>
        </Col>
      </Row>

      {/* Happy Path Coverage */}
      {stats.happyPathCount > 0 && (
        <>
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col span={24}>
              <div style={{ marginBottom: 8 }}>
                <Text>Happy Path Coverage</Text>
              </div>
              <Progress
                percent={stats.happyPathCoverage}
                strokeColor="#52c41a"
                format={(pct) => `${pct?.toFixed(1)}%`}
              />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {stats.happyPathCount} happy path variants covering{' '}
                {stats.happyPathCoverage.toFixed(1)}% of cases
              </Text>
            </Col>
          </Row>
        </>
      )}

      <Divider />

      {/* Length Distribution */}
      <Title level={5}>Variant Length</Title>
      <Row gutter={[16, 16]}>
        <Col xs={8}>
          <Statistic
            title="Minimum"
            value={stats.minLength}
            suffix="steps"
            valueStyle={{ fontSize: 18 }}
          />
        </Col>
        <Col xs={8}>
          <Statistic
            title="Average"
            value={stats.avgLength.toFixed(1)}
            suffix="steps"
            valueStyle={{ fontSize: 18 }}
            prefix={<ThunderboltOutlined />}
          />
        </Col>
        <Col xs={8}>
          <Statistic
            title="Maximum"
            value={stats.maxLength}
            suffix="steps"
            valueStyle={{ fontSize: 18 }}
          />
        </Col>
      </Row>
    </Card>
  );
};
