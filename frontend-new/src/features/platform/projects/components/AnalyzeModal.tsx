/**
 * AnalyzeModal - Column mapping modal for CSV/XES analysis
 *
 * Flow: Load Data → Map Columns → Queue Analysis → Process Map
 */

import { useState, useEffect } from 'react';
import { Modal, Select, Button, Alert, Spin, Space, Typography, Form, Tag, Steps, Card } from 'antd';
import {
    LoadingOutlined,
    CheckCircleOutlined,
    TableOutlined,
    SettingOutlined,
    RocketOutlined,
    EyeOutlined,
} from '@ant-design/icons';
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

type StepKey = 'loading' | 'mapping' | 'processing' | 'complete' | 'error';

const STEP_ITEMS = [
    { key: 'loading', title: 'Load Data', icon: <TableOutlined /> },
    { key: 'mapping', title: 'Map Columns', icon: <SettingOutlined /> },
    { key: 'processing', title: 'Processing', icon: <RocketOutlined /> },
    { key: 'complete', title: 'View Map', icon: <EyeOutlined /> },
];

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
    const [currentStep, setCurrentStep] = useState<StepKey>('loading');
    const [jobId, setJobId] = useState<string | null>(null);

    // Fetch columns from stored file
    const {
        data: columnData,
        isLoading: isLoadingColumns,
        error: columnsError,
        refetch: refetchColumns,
    } = useDetectColumns(open ? datasetId : null);

    // Start analysis mutation
    const startAnalysis = useStartAnalysis();

    // Poll job status
    const { data: jobStatus } = useJobStatus(jobId);

    // Update step based on loading state
    useEffect(() => {
        if (open) {
            if (isLoadingColumns) {
                setCurrentStep('loading');
            } else if (columnsError) {
                setCurrentStep('error');
            } else if (columnData) {
                setCurrentStep('mapping');
            }
        }
    }, [open, isLoadingColumns, columnsError, columnData]);

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
            setCurrentStep('complete');
        } else if (jobStatus?.status === 'failed') {
            setCurrentStep('error');
        }
    }, [jobStatus]);

    const handleSubmit = async () => {
        // Prevent double-click race condition (BUG-012)
        if (startAnalysis.isPending) return;

        try {
            const values = await form.validateFields();
            const mapping: ColumnMapping = {
                case_id_column: values.case_id_column,
                activity_column: values.activity_column,
                timestamp_column: values.timestamp_column,
                resource_column: values.resource_column,
            };

            console.log('[AnalyzeModal] Starting analysis with mapping:', mapping);
            setCurrentStep('processing');

            const result = await startAnalysis.mutateAsync({ datasetId, mapping });
            console.log('[AnalyzeModal] Analysis queued:', result);
            setJobId(result.id);
        } catch (err) {
            console.error('[AnalyzeModal] Error:', err);
            setCurrentStep('error');
        }
    };

    const handleClose = () => {
        setJobId(null);
        setCurrentStep('loading');
        form.resetFields();
        onClose();
    };

    const handleViewProcessMap = () => {
        onSuccess?.();
        navigate(`/workspace/${projectId}/data/${datasetId}/explorer`);
        handleClose();
    };

    const handleRetry = () => {
        setCurrentStep('loading');
        refetchColumns();
    };

    const getCurrentStepIndex = () => {
        return STEP_ITEMS.findIndex(s => s.key === currentStep);
    };

    return (
        <Modal
            title={
                <Space>
                    <SettingOutlined />
                    <span>Analyze: {datasetName}</span>
                </Space>
            }
            open={open}
            onCancel={handleClose}
            footer={null}
            width={640}
            maskClosable={currentStep !== 'processing'}
            closable={currentStep !== 'processing'}
        >
            <div style={{ padding: `${tokens.spacing[4]} 0` }}>
                {/* Progress Steps */}
                <Steps
                    current={getCurrentStepIndex()}
                    size="small"
                    style={{ marginBottom: tokens.spacing[6] }}
                    items={STEP_ITEMS.map(item => ({
                        title: item.title,
                        icon: item.icon,
                    }))}
                />

                {/* Step: Loading */}
                {currentStep === 'loading' && (
                    <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
                        <Spin size="large" tip="Reading file and detecting columns..." />
                        <div style={{ marginTop: tokens.spacing[4] }}>
                            <Text type="secondary">Parsing {datasetName}...</Text>
                        </div>
                    </div>
                )}

                {/* Step: Error */}
                {currentStep === 'error' && (
                    <div style={{ textAlign: 'center', padding: tokens.spacing[6] }}>
                        <Alert
                            message="Failed to analyze file"
                            description={columnsError?.message || jobStatus?.error || 'An error occurred'}
                            type="error"
                            showIcon
                            style={{ marginBottom: tokens.spacing[4] }}
                        />
                        <Space>
                            <Button onClick={handleClose}>Close</Button>
                            <Button type="primary" onClick={handleRetry}>Retry</Button>
                        </Space>
                    </div>
                )}

                {/* Step: Mapping */}
                {currentStep === 'mapping' && columnData && (
                    <>
                        <Card size="small" style={{ marginBottom: tokens.spacing[4], background: tokens.colors.neutral[50] }}>
                            <Space>
                                <CheckCircleOutlined style={{ color: tokens.colors.success[500] }} />
                                <Text>
                                    Found <strong>{columnData.columns.length}</strong> columns and <strong>{columnData.row_count?.toLocaleString() || 'N/A'}</strong> rows
                                </Text>
                            </Space>
                        </Card>

                        <Text type="secondary" style={{ display: 'block', marginBottom: tokens.spacing[4] }}>
                            Map your columns to process mining fields. We've pre-selected the most likely matches.
                        </Text>

                        <Form form={form} layout="vertical">
                            <Form.Item
                                name="case_id_column"
                                label={<Text strong>Case ID Column</Text>}
                                rules={[{ required: true, message: 'Case ID is required' }]}
                                extra="Unique identifier for each process instance (e.g., OrderID, TicketNumber)"
                            >
                                <Select placeholder="Select column" showSearch size="large">
                                    {columnData.columns.map((col) => (
                                        <Option key={col} value={col}>{col}</Option>
                                    ))}
                                </Select>
                            </Form.Item>

                            <Form.Item
                                name="activity_column"
                                label={<Text strong>Activity Column</Text>}
                                rules={[{ required: true, message: 'Activity is required' }]}
                                extra="The name of each step in the process (e.g., Status, Action)"
                            >
                                <Select placeholder="Select column" showSearch size="large">
                                    {columnData.columns.map((col) => (
                                        <Option key={col} value={col}>{col}</Option>
                                    ))}
                                </Select>
                            </Form.Item>

                            <Form.Item
                                name="timestamp_column"
                                label={<Text strong>Timestamp Column</Text>}
                                rules={[{ required: true, message: 'Timestamp is required' }]}
                                extra="When each activity occurred (e.g., CreatedAt, EventTime)"
                            >
                                <Select placeholder="Select column" showSearch size="large">
                                    {columnData.columns.map((col) => (
                                        <Option key={col} value={col}>{col}</Option>
                                    ))}
                                </Select>
                            </Form.Item>

                            <Form.Item
                                name="resource_column"
                                label={<Text strong>Resource Column (Optional)</Text>}
                                extra="Who performed each activity (e.g., AssignedTo, User)"
                            >
                                <Select placeholder="Select column (optional)" showSearch allowClear size="large">
                                    {columnData.columns.map((col) => (
                                        <Option key={col} value={col}>{col}</Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </Form>

                        <div style={{ marginTop: tokens.spacing[4], textAlign: 'right' }}>
                            <Space>
                                <Button onClick={handleClose}>Cancel</Button>
                                <Button
                                    type="primary"
                                    size="large"
                                    icon={<RocketOutlined />}
                                    onClick={handleSubmit}
                                    loading={startAnalysis.isPending}
                                >
                                    Start Analysis
                                </Button>
                            </Space>
                        </div>
                    </>
                )}

                {/* Step: Processing */}
                {currentStep === 'processing' && (
                    <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
                        <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
                        <div style={{ marginTop: tokens.spacing[4] }}>
                            <Title level={5}>Generating Process Map...</Title>
                            <Text type="secondary">
                                Analyzing events and discovering process patterns. This may take a moment.
                            </Text>
                        </div>
                        {jobStatus?.progress && (
                            <Tag color="blue" style={{ marginTop: tokens.spacing[3] }}>
                                {Math.round(jobStatus.progress * 100)}% complete
                            </Tag>
                        )}
                    </div>
                )}

                {/* Step: Complete */}
                {currentStep === 'complete' && (
                    <div style={{ textAlign: 'center', padding: tokens.spacing[6] }}>
                        <CheckCircleOutlined
                            style={{ fontSize: 64, color: tokens.colors.success[500], marginBottom: 16 }}
                        />
                        <Title level={4}>Analysis Complete!</Title>
                        <Text type="secondary" style={{ display: 'block', marginBottom: tokens.spacing[4] }}>
                            Your process map is ready to explore.
                        </Text>
                        <Space>
                            <Button onClick={handleClose}>Close</Button>
                            <Button type="primary" size="large" icon={<EyeOutlined />} onClick={handleViewProcessMap}>
                                View Process Map
                            </Button>
                        </Space>
                    </div>
                )}
            </div>
        </Modal>
    );
}

export default AnalyzeModal;
