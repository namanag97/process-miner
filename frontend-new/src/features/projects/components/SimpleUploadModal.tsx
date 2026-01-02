/**
 * SimpleUploadModal - Simple file upload modal
 *
 * Pick file → Validate → Upload → Done.
 * Uses async_store=true for deferred ingestion.
 */

import React, { useState, useCallback } from 'react';
import { Modal, Upload, Button, Alert, Progress, Typography, Space } from 'antd';
import type { UploadFile, UploadProps } from 'antd';
import { InboxOutlined, FileTextOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { useUploadDataset } from '../hooks';

const { Dragger } = Upload;
const { Text, Title } = Typography;

interface SimpleUploadModalProps {
    open: boolean;
    onClose: () => void;
    projectId: string;
    onSuccess?: () => void;
}

const MAX_FILE_SIZE_MB = 100;

export function SimpleUploadModal({
    open,
    onClose,
    projectId,
    onSuccess,
}: SimpleUploadModalProps) {
    const [fileList, setFileList] = useState<UploadFile[]>([]);
    const [error, setError] = useState<string | null>(null);
    const uploadMutation = useUploadDataset();

    const validateFile = useCallback((file: File): string | null => {
        // Check file size
        if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
            return `File size exceeds ${MAX_FILE_SIZE_MB}MB limit`;
        }

        // Check file extension
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (ext !== 'csv') {
            return 'Only CSV files are supported';
        }

        return null;
    }, []);

    const handleUpload = useCallback(async () => {
        if (fileList.length === 0) return;

        const file = fileList[0].originFileObj;
        if (!file) return;

        setError(null);

        try {
            await uploadMutation.mutateAsync({
                projectId,
                file,
            });
            setFileList([]);
            onSuccess?.();
            onClose();
        } catch (err) {
            // Error is already handled by the mutation
        }
    }, [fileList, projectId, uploadMutation, onSuccess, onClose]);

    const uploadProps: UploadProps = {
        accept: '.csv',
        maxCount: 1,
        fileList,
        beforeUpload: (file) => {
            const validationError = validateFile(file);
            if (validationError) {
                setError(validationError);
                return Upload.LIST_IGNORE;
            }
            setError(null);
            setFileList([{ ...file, uid: file.name, originFileObj: file } as UploadFile]);
            return false; // Prevent auto upload
        },
        onRemove: () => {
            setFileList([]);
            setError(null);
        },
    };

    const handleClose = () => {
        setFileList([]);
        setError(null);
        onClose();
    };

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
                    disabled={fileList.length === 0 || !!error}
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

                <Dragger {...uploadProps}>
                    <p className="ant-upload-drag-icon">
                        <InboxOutlined style={{ fontSize: 48, color: tokens.colors.primary[500] }} />
                    </p>
                    <p className="ant-upload-text">
                        Click or drag CSV file to this area
                    </p>
                    <p className="ant-upload-hint" style={{ color: tokens.colors.neutral[500] }}>
                        Maximum file size: {MAX_FILE_SIZE_MB}MB
                    </p>
                </Dragger>

                {uploadMutation.isPending && (
                    <div style={{ marginTop: tokens.spacing[4] }}>
                        <Progress percent={99} status="active" showInfo={false} />
                        <Text type="secondary">Uploading...</Text>
                    </div>
                )}

                {fileList.length > 0 && !uploadMutation.isPending && (
                    <div
                        style={{
                            marginTop: tokens.spacing[4],
                            padding: tokens.spacing[3],
                            background: tokens.colors.primary[50],
                            borderRadius: tokens.radius.md,
                            display: 'flex',
                            alignItems: 'center',
                            gap: tokens.spacing[3],
                        }}
                    >
                        <FileTextOutlined style={{ fontSize: 24, color: tokens.colors.primary[500] }} />
                        <div style={{ flex: 1 }}>
                            <Text strong>{fileList[0].name}</Text>
                            <br />
                            <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                                {(fileList[0].size! / 1024 / 1024).toFixed(2)} MB
                            </Text>
                        </div>
                        <CheckCircleOutlined style={{ fontSize: 20, color: tokens.colors.success[500] }} />
                    </div>
                )}

                <div style={{ marginTop: tokens.spacing[4] }}>
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                        After upload, you'll need to configure column mapping before analysis.
                    </Text>
                </div>
            </div>
        </Modal>
    );
}

export default SimpleUploadModal;
