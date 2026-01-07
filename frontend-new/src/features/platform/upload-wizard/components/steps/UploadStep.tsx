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
        <div>
            {/* Step Header */}
            <div style={{ marginBottom: tokens.spacing[6] }}>
                <Title level={4} style={{ margin: 0 }}>Choose your Data Source</Title>
                <Text type="secondary">
                    Select an existing dataset or upload a new file to begin analysis.
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

            {/* Search box */}
            <div
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: tokens.spacing[2],
                    marginBottom: tokens.spacing[4],
                    padding: `${tokens.spacing[2]}px ${tokens.spacing[3]}px`,
                    border: `1px solid ${tokens.colors.neutral[200]}`,
                    borderRadius: tokens.radius.sm,
                    maxWidth: 280,
                    background: tokens.colors.neutral[0],
                }}
            >
                <InboxOutlined style={{ color: tokens.colors.neutral[400], fontSize: 14 }} />
                <input
                    type="text"
                    placeholder="Search datasets..."
                    style={{
                        flex: 1,
                        border: 'none',
                        outline: 'none',
                        fontSize: 13,
                        color: tokens.colors.neutral[900],
                        background: 'transparent',
                    }}
                />
            </div>

            {/* Existing datasets placeholder */}
            <Card
                size="small"
                style={{
                    marginBottom: tokens.spacing[4],
                    background: tokens.colors.neutral[50],
                    border: `1px solid ${tokens.colors.neutral[200]}`,
                }}
            >
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        Recent Datasets
                    </Text>
                    <Text type="secondary">No existing datasets in this project yet.</Text>
                </Space>
            </Card>

            {/* Divider */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: tokens.spacing[3],
                margin: `${tokens.spacing[6]}px 0 ${tokens.spacing[4]}px`,
            }}>
                <div style={{ flex: 1, height: 1, background: tokens.colors.neutral[200] }} />
                <Text type="secondary" style={{ fontSize: 12, fontWeight: 500, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                    Or upload new file
                </Text>
                <div style={{ flex: 1, height: 1, background: tokens.colors.neutral[200] }} />
            </div>

            {/* Upload Options - Inline Cards */}
            <div style={{ display: 'flex', gap: tokens.spacing[4] }}>
                {/* CSV/Excel Upload */}
                <Dragger
                    {...uploadProps}
                    disabled={isLoading}
                    style={{
                        flex: 1,
                        border: `2px dashed ${tokens.colors.neutral[300]}`,
                        borderRadius: tokens.radius.lg,
                        background: tokens.colors.neutral[0],
                        padding: tokens.spacing[4],
                    }}
                >
                    <div style={{ textAlign: 'center' }}>
                        <FileTextOutlined style={{ fontSize: 32, color: tokens.colors.neutral[500], marginBottom: tokens.spacing[3] }} />
                        <p style={{ fontWeight: 500, color: tokens.colors.neutral[700], marginBottom: tokens.spacing[1] }}>
                            CSV / Excel file
                        </p>
                        <p style={{ fontSize: 12, color: tokens.colors.neutral[500], margin: 0 }}>
                            Drop file or <span style={{ color: tokens.colors.primary[500] }}>browse</span>
                        </p>
                        <div style={{ marginTop: tokens.spacing[3], display: 'flex', justifyContent: 'center', gap: tokens.spacing[1] }}>
                            <span style={{ padding: '2px 6px', background: tokens.colors.neutral[100], borderRadius: tokens.radius.sm, fontSize: 11, color: tokens.colors.neutral[600] }}>CSV</span>
                            <span style={{ padding: '2px 6px', background: tokens.colors.neutral[100], borderRadius: tokens.radius.sm, fontSize: 11, color: tokens.colors.neutral[600] }}>XLSX</span>
                            <span style={{ padding: '2px 6px', background: tokens.colors.neutral[100], borderRadius: tokens.radius.sm, fontSize: 11, color: tokens.colors.neutral[600] }}>XES</span>
                        </div>
                    </div>
                </Dragger>

                {/* Google Sheet */}
                <Card
                    hoverable
                    style={{
                        flex: 1,
                        border: `2px dashed ${tokens.colors.neutral[300]}`,
                        borderRadius: tokens.radius.lg,
                        textAlign: 'center',
                        cursor: 'not-allowed',
                        opacity: 0.6,
                    }}
                    styles={{ body: { padding: tokens.spacing[6] } }}
                >
                    <div style={{ marginBottom: tokens.spacing[3] }}>
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={tokens.colors.neutral[500]} strokeWidth="1.5">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                            <line x1="3" y1="9" x2="21" y2="9" />
                            <line x1="9" y1="21" x2="9" y2="9" />
                        </svg>
                    </div>
                    <p style={{ fontWeight: 500, color: tokens.colors.neutral[700], margin: 0 }}>Google Sheet</p>
                    <p style={{ fontSize: 12, color: tokens.colors.neutral[500], margin: `${tokens.spacing[1]}px 0 0` }}>Coming soon</p>
                </Card>

                {/* Database */}
                <Card
                    hoverable
                    style={{
                        flex: 1,
                        border: `2px dashed ${tokens.colors.neutral[300]}`,
                        borderRadius: tokens.radius.lg,
                        textAlign: 'center',
                        cursor: 'not-allowed',
                        opacity: 0.6,
                    }}
                    styles={{ body: { padding: tokens.spacing[6] } }}
                >
                    <div style={{ marginBottom: tokens.spacing[3] }}>
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={tokens.colors.neutral[500]} strokeWidth="1.5">
                            <ellipse cx="12" cy="5" rx="9" ry="3" />
                            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
                        </svg>
                    </div>
                    <p style={{ fontWeight: 500, color: tokens.colors.neutral[700], margin: 0 }}>Database</p>
                    <p style={{ fontSize: 12, color: tokens.colors.neutral[500], margin: `${tokens.spacing[1]}px 0 0` }}>Coming soon</p>
                </Card>
            </div>

            {/* Upload Progress */}
            {uploadProgress > 0 && uploadProgress < 100 && (
                <Progress
                    percent={uploadProgress}
                    status="active"
                    style={{ marginTop: tokens.spacing[4] }}
                />
            )}
        </div>
    );
}
