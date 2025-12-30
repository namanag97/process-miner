import React from 'react';
import { List, Typography, Tag, Progress, Space, Button, Tooltip } from 'antd';
import { FilterOutlined, CheckCircleFilled } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';
import { MockVariant, formatDuration } from '../mockExplorerData';

const log = createLogger('VariantPanel');
const { Text, Title } = Typography;

export interface VariantPanelProps {
  variants: MockVariant[];
  selectedVariantKey?: string | null;
  onSelectVariant?: (variantKey: string | null) => void;
  onFilterToVariant?: (variantKey: string) => void;
}

export function VariantPanel({
  variants,
  selectedVariantKey,
  onSelectVariant,
  onFilterToVariant,
}: VariantPanelProps) {
  log.debug('Rendering VariantPanel', { variantCount: variants.length, selected: selectedVariantKey });

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: tokens.spacing[4], borderBottom: `1px solid ${tokens.colors.neutral[200]}` }}>
        <Title level={5} style={{ margin: 0 }}>
          Variants
        </Title>
        <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
          {variants.length} unique paths
        </Text>
      </div>

      <div style={{ flex: 1, overflow: 'auto' }}>
        <List
          dataSource={variants}
          size="small"
          renderItem={(variant) => {
            const isSelected = variant.key === selectedVariantKey;
            return (
              <List.Item
                onClick={() => onSelectVariant?.(isSelected ? null : variant.key)}
                style={{
                  padding: tokens.spacing[3],
                  cursor: 'pointer',
                  backgroundColor: isSelected ? tokens.colors.primary[50] : undefined,
                  borderLeft: isSelected ? `3px solid ${tokens.colors.primary[500]}` : '3px solid transparent',
                  transition: 'all 150ms ease',
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = tokens.colors.neutral[50];
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
              >
                <Space direction="vertical" size={4} style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space size={4}>
                      {variant.isHappyPath && (
                        <Tooltip title="Happy Path">
                          <CheckCircleFilled style={{ color: tokens.colors.success[500] }} />
                        </Tooltip>
                      )}
                      <Text strong style={{ fontSize: tokens.fontSize.sm }}>
                        {variant.caseCount.toLocaleString()} cases
                      </Text>
                    </Space>
                    <Tag color={variant.frequencyPercent > 50 ? 'blue' : 'default'}>
                      {variant.frequencyPercent.toFixed(1)}%
                    </Tag>
                  </div>

                  <Progress
                    percent={variant.frequencyPercent}
                    showInfo={false}
                    size="small"
                    strokeColor={tokens.colors.primary[500]}
                    trailColor={tokens.colors.neutral[200]}
                  />

                  <Text
                    type="secondary"
                    ellipsis
                    style={{ fontSize: tokens.fontSize.xs }}
                  >
                    {variant.activities.join(' → ')}
                  </Text>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
                      Avg: {formatDuration(variant.avgDurationSeconds)}
                    </Text>
                    {isSelected && onFilterToVariant && (
                      <Button
                        type="link"
                        size="small"
                        icon={<FilterOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          onFilterToVariant(variant.key);
                          log.info('Filter to variant', { variantKey: variant.key });
                        }}
                        style={{ padding: 0, height: 'auto', fontSize: tokens.fontSize.xs }}
                      >
                        Filter
                      </Button>
                    )}
                  </div>
                </Space>
              </List.Item>
            );
          }}
        />
      </div>
    </div>
  );
}

export default VariantPanel;
