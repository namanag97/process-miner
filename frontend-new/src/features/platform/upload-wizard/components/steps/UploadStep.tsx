/**
 * UploadStep - Step 1: File upload with drag-drop
 */

import { useState } from 'react';
import { Upload, Card, Typography, Space, Alert, Progress, type UploadProps } from 'antd';
import { InboxOutlined, FileTextOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { devLog } from '../../../../../shared/ui/DevConsole';

const { Dragger } = Upload;
const { Title, Text } = Typography;

interface UploadStepProps {
    projectId: string;
    onUploadComplete: (datasetId: string, filename: string, fileSize: number) => void;
    isLoading?: boolean;
    uploadFilePresigned: (file: File) => Promise<string>;
}

const MAX_FILE_SIZE_MB = 100;
const ACCEPTED_FORMATS = '.csv,.xlsx,.xls,.xes';

export function UploadStep({ onUploadComplete, isLoading, uploadFilePresigned }: UploadStepProps) {
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const uploadProps: UploadProps = {
        name: 'file',
        multiple: false,
        accept: ACCEPTED_FORMATS,
        showUploadList: false,
        customRequest: async (options) => {
            const { file, onSuccess, onError } = options;
            const fileObj = file as File;

            const logData = {
                fileName: fileObj.name,
                fileSize: fileObj.size,
                fileType: fileObj.type,
                timestamp: new Date().toISOString()
            };
            console.log('[UploadWizard:UploadStep] customRequest started', logData);
            devLog.action('UploadStep', 'Upload request started', logData);

            try {
                setUploadProgress(10);
                console.log('[UploadWizard:UploadStep] Starting presigned upload...');
                devLog.info('UploadStep', 'Starting presigned upload flow');

                // Use the custom presigned upload flow
                const datasetId = await uploadFilePresigned(fileObj);

                const successData = { datasetId, fileName: fileObj.name };
                console.log('[UploadWizard:UploadStep] Upload completed successfully', successData);
                devLog.action('UploadStep', 'Upload completed successfully', successData);

                setUploadProgress(100);
                onSuccess?.({ id: datasetId, source_file: fileObj.name });
                onUploadComplete(datasetId, fileObj.name, fileObj.size);
            } catch (err: unknown) {
                const error = err instanceof Error ? err : new Error(String(err));
                const errorData = {
                    error: error.message,
                    message: error.message,
                    stack: error.stack,
                    fileName: fileObj.name
                };
                console.error('[UploadWizard:UploadStep] Upload failed', errorData);
                devLog.error('UploadStep', `Upload failed: ${error.message}`, errorData);

                onError?.(error);
                setError(error.message || 'Upload failed');
                setUploadProgress(0);
            }
        },
        beforeUpload: (file) => {
            const fileData = {
                fileName: file.name,
                fileSize: file.size,
                fileType: file.type
            };
            console.log('[UploadWizard:UploadStep] beforeUpload validation', fileData);
            devLog.info('UploadStep', 'Validating file before upload', fileData);

            setError(null);

            // Validate size
            const sizeMB = file.size / (1024 * 1024);
            if (sizeMB > MAX_FILE_SIZE_MB) {
                const errorMsg = `File too large (${sizeMB.toFixed(1)}MB). Maximum: ${MAX_FILE_SIZE_MB}MB`;
                const errorData = { sizeMB, maxSize: MAX_FILE_SIZE_MB };
                console.error('[UploadWizard:UploadStep] File too large', errorData);
                devLog.error('UploadStep', errorMsg, errorData);
                setError(errorMsg);
                return Upload.LIST_IGNORE;
            }

            // Validate format
            const ext = file.name.split('.').pop()?.toLowerCase();
            if (!['csv', 'xlsx', 'xls', 'xes'].includes(ext || '')) {
                const errorMsg = 'Invalid file format. Accepted: CSV, XLSX, XLS, XES';
                console.error('[UploadWizard:UploadStep] Invalid file format', { extension: ext });
                devLog.error('UploadStep', errorMsg, { extension: ext, fileName: file.name });
                setError(errorMsg);
                return Upload.LIST_IGNORE;
            }

            console.log('[UploadWizard:UploadStep] Validation passed', { fileName: file.name, extension: ext });
            devLog.action('UploadStep', 'File validation passed', { fileName: file.name, extension: ext });
            return true;
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
