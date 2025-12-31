/**
 * ProjectCard - Card component for displaying a project summary
 */

import React from 'react';
import { Card, Typography, Space, Tag } from 'antd';
import { FolderOutlined, DatabaseOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { tokens } from '@lumina/design-system';
import type { Project } from '../types';

const { Text, Paragraph } = Typography;

interface ProjectCardProps {
  project: Project;
  onClick?: () => void;
}

export function ProjectCard({ project, onClick }: ProjectCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/projects/${project.id}`);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <Card
      hoverable
      onClick={handleClick}
      style={{ marginBottom: tokens.spacing[4] }}
    >
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <FolderOutlined style={{ color: tokens.colors.primary[500] }} />
            <Text strong style={{ fontSize: tokens.fontSize.lg }}>
              {project.name}
            </Text>
          </Space>
          <Tag icon={<DatabaseOutlined />}>
            {project.totalFiles} source{project.totalFiles !== 1 ? 's' : ''}
          </Tag>
        </div>

        {project.description && (
          <Paragraph
            type="secondary"
            ellipsis={{ rows: 2 }}
            style={{ marginBottom: 0 }}
          >
            {project.description}
          </Paragraph>
        )}

        <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
          <ClockCircleOutlined style={{ marginRight: 4 }} />
          Updated {formatDate(project.updatedAt)}
        </Text>
      </Space>
    </Card>
  );
}

export default ProjectCard;
