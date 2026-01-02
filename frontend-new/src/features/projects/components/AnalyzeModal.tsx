/**
 * AnalyzeModal - Column mapping modal for CSV analysis
 *
 * Shows detected columns and lets user map them to required fields.
 * Starts background analysis job on submit.
 */

import React, { useState, useEffect } from 'react';
import { Modal, Select, Button, Alert, Spin, Space, Typography, Form, Divider, Tag } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { useDetectColumns, useStartAnalysis, useJobStatus, type ColumnMapping } from '../hooks';
import { useNavigate } from 'react-router-dom';

const { Text, Title } = Typography;
const { Option } = Select;

interface AnalyzeModalProps {
    open: boolean;
    onClose: () => void;
    datasetId: string;
    datasetName: string;
    projectId: string;
    onSuccess?: () => void;
}

export function AnalyzeModal({
    open,
    onClose,
    datasetId,
    datasetName,
    projectId,
    onSuccess,
}: AnalyzeModalProps) {
    const navigate = useNavigate();
    const [form] = Form.useForm();
    const [jobId, setJobId] = useState<string | null>(null);

    // Fetch columns
    const { data: columnData, isLoading: isLoadingColumns, error: columnsError } = useDetectColumns(
        open ? datasetId : null
    );

    // Start analysis mutation
    const startAnalysis = useStartAnalysis();

    // Poll job status
    const { data: jobStatus } = useJobStatus(jobId);

    // Pre-fill form with suggestions
    useEffect(() => {
        if (columnData?.suggestions) {
            form.setFieldsValue({
                case_id_column: columnData.suggestions.case_id,
                activity_column: columnData.suggestions.activity,
                timestamp_column: columnData.suggestions.timestamp,
                resource_column: columnData.suggestions.resource,
            });
        }
    }, [columnData, form]);

    // Handle job completion
    useEffect(() => {
        if (jobStatus?.status === 'completed') {
            onSuccess?.();
            onClose();
        }
    }, [jobStatus, onSuccess, onClose]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            const mapping: ColumnMapping = {
                case_id_column: values.case_id_column,
                activity_column: values.activity_column,
                timestamp_column: values.timestamp_column,
                resource_column: values.resource_column,
            };

            const result = await startAnalysis.mutateAsync({ datasetId, mapping });
            setJobId(result.job_id);
        } catch (err) {
            // Validation or API error - handled by mutation
        }
    };

    const handleClose = () => {
        setJobId(null);
        form.resetFields();
        onClose();
    };

    const handleViewInExplore = () => {
        navigate(`/workspace/${projectId}/data/${datasetId}/explorer`);
        handleClose();
    };

    const isAnalyzing = !!jobId && jobStatus?.status !== 'completed' && jobStatus?.status !== 'failed';
    const isComplete = jobStatus?.status === 'completed';
    const isFailed = jobStatus?.status === 'failed';

    return (
        <Modal
            title={`Analyze: ${datasetName}`}
            open={open}
            onCancel={handleClose}
            footer={
                isComplete ? (
                    <Space>
                        <Button onClick={handleClose}>Close</Button>
                        <Button type="primary" onClick={handleViewInExplore}>
                            View in Explorer
                        </Button>
                    </Space>
                ) : (
                    <Space>
                        <Button onClick={handleClose} disabled={isAnalyzing}>
                            Cancel
                        </Button>
                        <Button
                            type="primary"
                            onClick={handleSubmit}
                            loading={startAnalysis.isPending || isAnalyzing}
                            disabled={isLoadingColumns || !!columnsError}
                        >
                            {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
                        </Button>
                    </Space>
                )
            }
            width={560}
            maskClosable={!isAnalyzing}
            closable={!isAnalyzing}
        >
            {isLoadingColumns && (
                <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
                    <Spin size="large" />
                    <div style={{ marginTop: tokens.spacing[4] }}>
                        <Text type="secondary">Detecting columns...</Text>
                    </div>
                </div>
            )}

            {columnsError && (
                <Alert
                    message="Failed to detect columns"
                    description="Unable to read the CSV file. Please check the file format."
                    type="error"
                    showIcon
                />
            )}

            {isComplete && (
                <div style={{ textAlign: 'center', padding: tokens.spacing[6] }}>
                    <CheckCircleOutlined
                        style={{ fontSize: 64, color: tokens.colors.success[500], marginBottom: 16 }}
                    />
                    <Title level={4}>Analysis Complete!</Title>
                    <Text type="secondary">
                        Your dataset has been processed and is ready to explore.
                    </Text>
                </div>
            )}

            {isFailed && (
                <Alert
                    message="Analysis Failed"
                    description={jobStatus?.error || 'An error occurred during analysis.'}
                    type="error"
                    showIcon
                    style={{ marginBottom: tokens.spacing[4] }}
                />
            )}

            {isAnalyzing && (
                <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
                    <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
                    <div style={{ marginTop: tokens.spacing[4] }}>
                        <Title level={5}>Analyzing your data...</Title>
                        <Text type="secondary">This may take a moment for large files.</Text>
                    </div>
                    {jobStatus?.progress && (
                        <Tag color="blue" style={{ marginTop: tokens.spacing[3] }}>
                            {Math.round(jobStatus.progress * 100)}% complete
                        </Tag>
                    )}
                </div>
            )}

            {columnData && !isAnalyzing && !isComplete && (
                <>
                    <Text type="secondary">
                        Map your CSV columns to the required process mining fields.
                    </Text>

                    <Divider style={{ margin: `${tokens.spacing[4]} 0` }} />

                    <Form form={form} layout="vertical">
                        <Form.Item
                            name="case_id_column"
                            label="Case ID Column"
                            rules={[{ required: true, message: 'Case ID is required' }]}
                            extra="Unique identifier for each process instance"
                        >
                            <Select placeholder="Select column" showSearch>
                                {columnData.columns.map((col) => (
                                    <Option key={col} value={col}>
                                        {col}
                                    </Option>
                                ))}
                            </Select>
                        </Form.Item>

                        <Form.Item
                            name="activity_column"
                            label="Activity Column"
                            rules={[{ required: true, message: 'Activity is required' }]}
                            extra="The name of each step in the process"
                        >
                            <Select placeholder="Select column" showSearch>
                                {columnData.columns.map((col) => (
                                    <Option key={col} value={col}>
                                        {col}
                                    </Option>
                                ))}
                            </Select>
                        </Form.Item>

                        <Form.Item
                            name="timestamp_column"
                            label="Timestamp Column"
                            rules={[{ required: true, message: 'Timestamp is required' }]}
                            extra="When each activity occurred"
                        >
                            <Select placeholder="Select column" showSearch>
                                {columnData.columns.map((col) => (
                                    <Option key={col} value={col}>
                                        {col}
                                    </Option>
                                ))}
                            </Select>
                        </Form.Item>

                        <Form.Item
                            name="resource_column"
                            label="Resource Column (Optional)"
                            extra="Who performed each activity"
                        >
                            <Select placeholder="Select column (optional)" showSearch allowClear>
                                {columnData.columns.map((col) => (
                                    <Option key={col} value={col}>
                                        {col}
                                    </Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </Form>

                    {columnData.sample_rows && columnData.sample_rows.length > 0 && (
                        <div
                            style={{
                                marginTop: tokens.spacing[4],
                                padding: tokens.spacing[3],
                                background: tokens.colors.neutral[50],
                                borderRadius: tokens.radius.md,
                                fontSize: tokens.fontSize.sm,
                            }}
                        >
                            <Text type="secondary">
                                <strong>Detected {columnData.columns.length} columns:</strong>{' '}
                                {columnData.columns.join(', ')}
                            </Text>
                        </div>
                    )}
                </>
            )}
        </Modal>
    );
}

export default AnalyzeModal;
