/**
 * UploadStep - Step 1: File upload with drag-drop
 */

import React, { useState } from 'react';
import { Upload, Card, Typography, Space, Alert, Progress } from 'antd';
import { InboxOutlined, FileTextOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { tokens } from '@lumina/design-system';
import { env } from '../../../../config/env';

const { Dragger } = Upload;
const { Title, Text } = Typography;

interface UploadStepProps {
    projectId: string;
    onUploadComplete: (datasetId: string, filename: string, fileSize: number) => void;
    isLoading?: boolean;
}

const MAX_FILE_SIZE_MB = 100;
const ACCEPTED_FORMATS = '.csv,.xlsx,.xls,.xes';

export function UploadStep({ projectId, onUploadComplete, isLoading }: UploadStepProps) {
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const uploadProps: UploadProps = {
        name: 'file',
        multiple: false,
        accept: ACCEPTED_FORMATS,
        action: `${env.API_BASE_URL}/api/v1/datasets/upload`,
        data: {
            project_id: projectId,
            async_store: 'true', // Deferred ingestion - preserves file for return visits
        },
        showUploadList: false,
        beforeUpload: (file) => {
            setError(null);

            // Validate size
            const sizeMB = file.size / (1024 * 1024);
            if (sizeMB > MAX_FILE_SIZE_MB) {
                setError(`File too large (${sizeMB.toFixed(1)}MB). Maximum: ${MAX_FILE_SIZE_MB}MB`);
                return false;
            }

            // Validate format
            const ext = file.name.split('.').pop()?.toLowerCase();
            if (!['csv', 'xlsx', 'xls', 'xes'].includes(ext || '')) {
                setError('Invalid file format. Accepted: CSV, XLSX, XLS, XES');
                return false;
            }

            return true;
        },
        onChange: (info) => {
            const { status, percent, response } = info.file;

            if (status === 'uploading' && percent) {
                setUploadProgress(Math.round(percent));
            }

            if (status === 'done' && response) {
                setUploadProgress(100);
                onUploadComplete(response.id, response.source_file || info.file.name, info.file.size || 0);
            }

            if (status === 'error') {
                setError(response?.detail || 'Upload failed. Please try again.');
                setUploadProgress(0);
            }
        },
    };

    return (
        <div style={{ maxWidth: 640, margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: tokens.spacing[6] }}>
                <Title level={3}>Upload your data</Title>
                <Text type="secondary">
                    Drag and drop your event log file or click to browse.
                    Supported formats: CSV, Excel (XLSX, XLS), XES
                </Text>
            </div>

            {error && (
                <Alert
                    type="error"
                    message={error}
                    showIcon
                    closable
                    onClose={() => setError(null)}
                    style={{ marginBottom: tokens.spacing[4] }}
                />
            )}

            <Dragger {...uploadProps} disabled={isLoading}>
                <p className="ant-upload-drag-icon">
                    <InboxOutlined style={{ fontSize: 48, color: tokens.colors.primary[500] }} />
                </p>
                <p className="ant-upload-text">
                    Click or drag file to this area to upload
                </p>
                <p className="ant-upload-hint">
                    Maximum file size: {MAX_FILE_SIZE_MB}MB
                </p>
            </Dragger>

            {uploadProgress > 0 && uploadProgress < 100 && (
                <Progress
                    percent={uploadProgress}
                    status="active"
                    style={{ marginTop: tokens.spacing[4] }}
                />
            )}

            <Card
                size="small"
                style={{ marginTop: tokens.spacing[6], background: tokens.colors.neutral[50] }}
            >
                <Space direction="vertical" size="small">
                    <Text strong>Accepted file formats:</Text>
                    <Space>
                        <FileTextOutlined /> CSV (Comma-Separated Values)
                    </Space>
                    <Space>
                        <FileTextOutlined /> XLSX / XLS (Excel)
                    </Space>
                    <Space>
                        <FileTextOutlined /> XES (IEEE Standard for Event Logs)
                    </Space>
                </Space>
            </Card>
        </div>
    );
}
