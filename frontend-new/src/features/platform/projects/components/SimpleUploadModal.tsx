/**
 * SimpleUploadModal - Simple file upload modal
 *
 * Pick file → Validate → Upload → Done.
 * Uses async_store=true for deferred ingestion.
 */

import { useState, useCallback } from 'react';
import { Modal, Upload, Button, Alert, Progress, Typography, Tag, type UploadFile, type UploadProps } from 'antd';
import { InboxOutlined, FileTextOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { useUploadDataset } from '../hooks';

const { Dragger } = Upload;
const { Text } = Typography;

interface SimpleUploadModalProps {
    open: boolean;
    onClose: () => void;
    projectId: string;
    onSuccess?: () => void;
}

const MAX_FILE_SIZE_MB = 100;
const SUPPORTED_FORMATS = ['csv', 'xes'];

// Format file size for display
function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

export function SimpleUploadModal({
    open,
    onClose,
    projectId,
    onSuccess,
}: SimpleUploadModalProps) {
    // Store the actual File object separately for reliable access to name/size
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [fileList, setFileList] = useState<UploadFile[]>([]);
    const [error, setError] = useState<string | null>(null);
    const uploadMutation = useUploadDataset();

    const validateFile = useCallback((file: File): string | null => {
        // Check file size
        if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
            return `File size exceeds ${MAX_FILE_SIZE_MB}MB limit`;
        }

        // Check file extension - support CSV and XES
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (!ext || !SUPPORTED_FORMATS.includes(ext)) {
            return `Unsupported format. Accepted: ${SUPPORTED_FORMATS.join(', ').toUpperCase()}`;
        }

        return null;
    }, []);

    const handleUpload = useCallback(async () => {
        if (!selectedFile) return;

        setError(null);
        console.log('[Upload] Starting upload:', selectedFile.name, selectedFile.size);

        try {
            await uploadMutation.mutateAsync({
                projectId,
                file: selectedFile,
                name: selectedFile.name,
            });
            setFileList([]);
            setSelectedFile(null);
            onSuccess?.();
            onClose();
        } catch (err) {
            // Error is already handled by the mutation
            console.error('[Upload] Failed:', err);
        }
    }, [selectedFile, projectId, uploadMutation, onSuccess, onClose]);

    const uploadProps: UploadProps = {
        accept: SUPPORTED_FORMATS.map(f => `.${f}`).join(','),
        maxCount: 1,
        fileList,
        showUploadList: false, // We'll show our own file display
        beforeUpload: (file) => {
            console.log('[Upload] File selected:', file.name, file.size, file.type);

            const validationError = validateFile(file);
            if (validationError) {
                setError(validationError);
                setSelectedFile(null);
                setFileList([]);
                return Upload.LIST_IGNORE;
            }

            setError(null);
            setSelectedFile(file);
            setFileList([{
                uid: file.name,
                name: file.name,
                size: file.size,
                type: file.type,
                status: 'done',
                originFileObj: file,
            } as UploadFile]);

            return false; // Prevent auto upload
        },
        onRemove: () => {
            setFileList([]);
            setSelectedFile(null);
            setError(null);
        },
    };

    const handleClose = () => {
        setFileList([]);
        setSelectedFile(null);
        setError(null);
        onClose();
    };

    const handleRemoveFile = () => {
        setFileList([]);
        setSelectedFile(null);
        setError(null);
    };

    const fileExtension = selectedFile?.name.split('.').pop()?.toUpperCase();

    return (
        <Modal
            title="Add Dataset"
            open={open}
            onCancel={handleClose}
            footer={[
                <Button key="cancel" onClick={handleClose}>
                    Cancel
                </Button>,
                <Button
                    key="upload"
                    type="primary"
                    onClick={handleUpload}
                    loading={uploadMutation.isPending}
                    disabled={!selectedFile || !!error}
                >
                    Upload
                </Button>,
            ]}
            width={520}
        >
            <div style={{ padding: `${tokens.spacing[4]} 0` }}>
                {error && (
                    <Alert
                        message={error}
                        type="error"
                        showIcon
                        style={{ marginBottom: tokens.spacing[4] }}
                    />
                )}

                {!selectedFile && (
                    <Dragger {...uploadProps}>
                        <p className="ant-upload-drag-icon">
                            <InboxOutlined style={{ fontSize: 48, color: tokens.colors.primary[500] }} />
                        </p>
                        <p className="ant-upload-text">
                            Click or drag file to this area
                        </p>
                        <p className="ant-upload-hint" style={{ color: tokens.colors.neutral[500] }}>
                            Supports: CSV, XES • Max size: {MAX_FILE_SIZE_MB}MB
                        </p>
                    </Dragger>
                )}

                {uploadMutation.isPending && (
                    <div style={{ marginTop: tokens.spacing[4] }}>
                        <Progress percent={99} status="active" showInfo={false} />
                        <Text type="secondary">Uploading {selectedFile?.name}...</Text>
                    </div>
                )}

                {selectedFile && !uploadMutation.isPending && (
                    <div
                        style={{
                            marginTop: tokens.spacing[2],
                            padding: tokens.spacing[4],
                            background: tokens.colors.primary[50],
                            borderRadius: tokens.radius.md,
                            border: `1px solid ${tokens.colors.primary[200]}`,
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: tokens.spacing[3] }}>
                            <FileTextOutlined
                                style={{
                                    fontSize: 32,
                                    color: tokens.colors.primary[500],
                                    marginTop: 4,
                                }}
                            />
                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: tokens.spacing[2] }}>
                                    <Text strong style={{
                                        fontSize: tokens.fontSize.md,
                                        wordBreak: 'break-all',
                                    }}>
                                        {selectedFile.name}
                                    </Text>
                                    <Tag color={fileExtension === 'CSV' ? 'blue' : 'purple'}>
                                        {fileExtension}
                                    </Tag>
                                </div>
                                <div style={{ marginTop: tokens.spacing[1] }}>
                                    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                                        Size: {formatFileSize(selectedFile.size)}
                                    </Text>
                                </div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: tokens.spacing[2] }}>
                                <CheckCircleOutlined
                                    style={{ fontSize: 20, color: tokens.colors.success[500] }}
                                />
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<CloseCircleOutlined />}
                                    onClick={handleRemoveFile}
                                    style={{ color: tokens.colors.neutral[400] }}
                                />
                            </div>
                        </div>
                    </div>
                )}

                <div style={{ marginTop: tokens.spacing[4] }}>
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                        After upload, click "Analyze" to configure column mapping and generate process map.
                    </Text>
                </div>
            </div>
        </Modal>
    );
}

export default SimpleUploadModal;
