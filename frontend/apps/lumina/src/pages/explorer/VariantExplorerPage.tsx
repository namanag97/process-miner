import React, { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Typography, Row, Col, Breadcrumb, Space, Button, Modal, Alert } from 'antd';
import { HomeOutlined, BranchesOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import type { ProcessVariant } from 'process-mining-sdk';
import {
  VariantList,
  VariantStatistics,
  VariantComparison,
  VariantTrace,
} from '@lumina/variants';

const { Title, Text } = Typography;

const VariantExplorerPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();
  const [searchParams] = useSearchParams();
  const logName = searchParams.get('name') || logId;

  const [selectedVariant, setSelectedVariant] = useState<ProcessVariant | null>(null);
  const [compareVariants, setCompareVariants] = useState<ProcessVariant[]>([]);
  const [showComparison, setShowComparison] = useState(false);

  if (!logId) {
    return (
      <Alert
        type="error"
        message="No log selected"
        description="Please select an event log to analyze variants."
      />
    );
  }

  const handleVariantSelect = (variant: ProcessVariant) => {
    setSelectedVariant(variant);
  };

  const handleCompare = (variants: ProcessVariant[]) => {
    setCompareVariants(variants);
    setShowComparison(true);
  };

  return (
    <div>
      {/* Breadcrumb Navigation */}
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          {
            title: (
              <Link to="/data-hub">
                <HomeOutlined /> Data Hub
              </Link>
            ),
          },
          {
            title: (
              <Link to={`/explorer/${logId}`}>
                Process Explorer
              </Link>
            ),
          },
          {
            title: (
              <Space>
                <BranchesOutlined />
                Variants
              </Space>
            ),
          },
        ]}
      />

      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        <Space align="center" style={{ marginBottom: 8 }}>
          <Link to={`/explorer/${logId}?name=${encodeURIComponent(logName || '')}`}>
            <Button icon={<ArrowLeftOutlined />} type="text">
              Back to Explorer
            </Button>
          </Link>
        </Space>
        <Title level={3} style={{ marginBottom: 4 }}>
          <BranchesOutlined style={{ marginRight: 8 }} />
          Variant Explorer
        </Title>
        <Text type="secondary">
          Analyze and compare process variants for: <strong>{logName}</strong>
        </Text>
      </div>

      <Row gutter={[16, 16]}>
        {/* Statistics Panel */}
        <Col xs={24} lg={8}>
          <VariantStatistics logId={logId} />
        </Col>

        {/* Variant List */}
        <Col xs={24} lg={16}>
          <VariantList
            logId={logId}
            onVariantSelect={handleVariantSelect}
            onCompare={handleCompare}
            selectedVariantKey={selectedVariant?.key}
            showCompareButton
          />
        </Col>

        {/* Selected Variant Details */}
        {selectedVariant && (
          <Col span={24}>
            <div
              style={{
                background: '#fafafa',
                border: '1px solid #d9d9d9',
                borderRadius: 8,
                padding: 16,
              }}
            >
              <div style={{ marginBottom: 12 }}>
                <Space>
                  <Title level={5} style={{ margin: 0 }}>
                    Selected: {selectedVariant.key}
                  </Title>
                  <Text type="secondary">
                    ({selectedVariant.caseCount} cases, {selectedVariant.length} steps)
                  </Text>
                </Space>
              </div>
              <VariantTrace
                activities={selectedVariant.activities}
                showStartEnd
                maxVisible={20}
              />
            </div>
          </Col>
        )}
      </Row>

      {/* Comparison Modal */}
      <Modal
        title="Variant Comparison"
        open={showComparison}
        onCancel={() => setShowComparison(false)}
        footer={null}
        width={900}
        styles={{ body: { padding: 0 } }}
      >
        <VariantComparison
          logId={logId}
          variantKeys={compareVariants.map((v) => v.key)}
          onClose={() => setShowComparison(false)}
        />
      </Modal>
    </div>
  );
};

export default VariantExplorerPage;
