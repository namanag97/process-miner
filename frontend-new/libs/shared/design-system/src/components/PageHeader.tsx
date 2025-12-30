import React from 'react';
import { Typography, Button } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { tokens } from '../theme';

const { Title, Text } = Typography;

export interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumb?: Array<{ label: string; href?: string; onClick?: () => void }>;
  showBack?: boolean;
  onBack?: () => void;
  actions?: React.ReactNode;
}

/**
 * PageHeader - Standard page header with breadcrumb and actions
 * Per DESIGN_SYSTEM.md Page Header pattern
 */
export function PageHeader({
  title,
  description,
  breadcrumb,
  showBack,
  onBack,
  actions,
}: PageHeaderProps) {
  return (
    <div style={{ marginBottom: tokens.spacing[6] }}>
      {/* Breadcrumb */}
      {breadcrumb && breadcrumb.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            marginBottom: tokens.spacing[2],
          }}
        >
          {breadcrumb.map((item, index) => (
            <React.Fragment key={index}>
              {index > 0 && (
                <span style={{ color: tokens.colors.neutral[400] }}>›</span>
              )}
              {item.href || item.onClick ? (
                <a
                  href={item.href}
                  onClick={(e) => {
                    if (item.onClick) {
                      e.preventDefault();
                      item.onClick();
                    }
                  }}
                  style={{
                    color: tokens.colors.primary[500],
                    fontSize: tokens.fontSize.sm,
                    textDecoration: 'none',
                  }}
                >
                  {item.label}
                </a>
              ) : (
                <span
                  style={{
                    color: tokens.colors.neutral[500],
                    fontSize: tokens.fontSize.sm,
                    fontWeight: tokens.fontWeight.medium,
                  }}
                >
                  {item.label}
                </span>
              )}
            </React.Fragment>
          ))}
        </div>
      )}

      {/* Header Row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: tokens.spacing[4],
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: tokens.spacing[2] }}>
          {showBack && onBack && (
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={onBack}
              style={{ marginTop: 4 }}
            />
          )}
          <div>
            <Title
              level={3}
              style={{
                margin: 0,
                color: tokens.colors.neutral[800],
                fontWeight: tokens.fontWeight.semibold,
              }}
            >
              {title}
            </Title>
            {description && (
              <Text
                style={{
                  color: tokens.colors.neutral[500],
                  marginTop: tokens.spacing[1],
                  display: 'block',
                }}
              >
                {description}
              </Text>
            )}
          </div>
        </div>

        {actions && (
          <div style={{ display: 'flex', gap: tokens.spacing[2] }}>
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

export default PageHeader;
