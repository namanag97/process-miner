/**
 * UploadWizardPage - Full-page 5-step Celonis-style upload wizard
 * 
 * Supports:
 * - Resuming wizard from any step based on dataset status
 * - Background processing after column mapping
 * - Navigation away and back without data loss
 * - Comprehensive DevConsole telemetry throughout
 * 
 * Dataset Status → Wizard Step Mapping:
 * - UNSTRUCTURED → Upload complete, goto sheets/configure
 * - AWAITING_MAPPING → Goto mapping step
 * - INGESTING → Goto finalize step (show progress)
 * - READY → Redirect to explorer/questions
 * - ERROR → Show error with retry option
 */

import { useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Typography, Button, Space, Spin, message } from 'antd';
import { ArrowLeftOutlined, LoadingOutlined } from '@ant-design/icons';
import { tokens, logAction } from '@lumina/design-system';
import { devLog } from '../../../../components/DevConsole';
import { useUploadWizard } from '../hooks/useUploadWizard';
import { WizardStepper } from '../components/WizardStepper';
import {
    UploadStep,
    ConfigureStep,
    MapDataStep,
    FinalizeStep
} from '../components/steps';

const { Title, Text } = Typography;

export function UploadWizardPage() {
    const { projectId } = useParams<{ projectId: string }>();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    // Resume wizard from existing dataset if provided
    const resumeDatasetId = searchParams.get('datasetId');

    const {
        currentStep,
        datasetId,
        filename,
        preview,
        mapping,
        jobId,
        jobStatus,
        isLoading,
        error,

        // Actions
        goToStep,
        setUploadResult,
        setMapping,
        startAnalysis,
        uploadFileDirect, // Direct upload for local dev (no MinIO needed)
        uploadFilePresigned, // Presigned upload for production (requires MinIO/S3)
    } = useUploadWizard(projectId!, resumeDatasetId || undefined);

    // Log wizard initialization
    useEffect(() => {
        console.log('[UploadWizard:Page] Wizard initialized', {
            projectId,
            resumeDatasetId,
            initialStep: currentStep,
            timestamp: new Date().toISOString()
        });
        devLog.action('UploadWizardPage', 'Wizard initialized', {
            projectId,
            resumeDatasetId,
            initialStep: currentStep,
        });
        logAction('UploadWizard', 'wizard_opened', { projectId, resumeDatasetId });
    // This should only run once on mount to log initial wizard state
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Log step changes
    useEffect(() => {
        console.log('[UploadWizard:Page] Step changed', {
            currentStep,
            datasetId,
            filename,
            hasMapping: !!mapping,
            hasPreview: !!preview,
            jobId,
            jobStatus: jobStatus?.status,
            isLoading,
            error
        });
        devLog.info('UploadWizardPage', `Step changed: ${currentStep}`, {
            datasetId,
            filename,
            hasMapping: !!mapping,
            jobId,
        });
    // Only trigger when step changes; other values are for logging context only
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentStep]);

    // Log errors when they occur
    useEffect(() => {
        if (error) {
            console.error('[UploadWizard:Page] Error occurred', {
                error,
                currentStep,
                datasetId,
                filename
            });
        }
    }, [error, currentStep, datasetId, filename]);

    const handleBackToProject = () => {
        devLog.action('UploadWizardPage', 'Navigating back to project', { projectId, currentStep });

        // Warn if upload in progress
        if (currentStep === 'upload') {
            navigate(`/workspace/${projectId}`);
        } else if (currentStep === 'finalize' && jobStatus?.status === 'running') {
            // Processing continues in background
            message.info('Processing will continue in the background. You can return anytime to check progress.');
            navigate(`/workspace/${projectId}`);
        } else {
            // Data is preserved, user can return
            message.info('Your progress has been saved. Return anytime to continue.');
            navigate(`/workspace/${projectId}`);
        }
    };

    const handleComplete = () => {
        devLog.info('UploadWizardPage', 'Wizard complete, navigating to questions', { datasetId, projectId });
        logAction('UploadWizard', 'wizard_complete', { datasetId, projectId });
        navigate(`/workspace/${projectId}/data/${datasetId}/questions`);
    };

    const handleRetry = () => {
        devLog.action('UploadWizardPage', 'Retrying after error');
        goToStep('mapping');
    };

    if (!projectId) {
        return <Text type="danger">Project ID required</Text>;
    }

    // Render current step
    const renderStep = () => {
        switch (currentStep) {
            case 'upload':
                return (
                    <UploadStep
                        projectId={projectId}
                        onUploadComplete={(id, name, size) => {
                            console.log('[UploadWizard:Page] Upload complete callback', {
                                datasetId: id,
                                filename: name,
                                fileSize: size
                            });
                            devLog.info('UploadWizardPage', `Upload complete: ${name}`, { id, size });
                            setUploadResult(id, name, size);
                        }}
                        isLoading={isLoading}
                        uploadFilePresigned={uploadFileDirect} // Using direct upload for local dev
                    />
                );

            case 'sheets':
                // Auto-skip for CSV (handled in hook), show loading
                return (
                    <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
                        <Spin indicator={<LoadingOutlined style={{ fontSize: 32 }} spin />} />
                        <Text style={{ display: 'block', marginTop: tokens.spacing[4] }}>
                            Analyzing file structure...
                        </Text>
                    </div>
                );

            case 'configure':
                return (
                    <ConfigureStep
                        preview={preview}
                        isLoading={isLoading}
                        onNext={() => {
                            devLog.action('UploadWizardPage', 'Configure complete, moving to mapping');
                            goToStep('mapping');
                        }}
                        onBack={() => goToStep('upload')}
                    />
                );

            case 'mapping':
                return (
                    <MapDataStep
                        preview={preview}
                        mapping={mapping}
                        onMappingChange={setMapping}
                        onNext={() => {
                            devLog.action('UploadWizardPage', 'Mapping complete, starting analysis');
                            startAnalysis();
                        }}
                        onBack={() => goToStep('configure')}
                    />
                );

            case 'finalize':
                return (
                    <FinalizeStep
                        jobId={jobId}
                        jobStatus={jobStatus}
                        datasetId={datasetId!}
                        projectId={projectId}
                        onComplete={handleComplete}
                        onRetry={handleRetry}
                    />
                );

            default:
                return null;
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: tokens.colors.neutral[50],
            padding: tokens.spacing[6],
        }}>
            {/* Header */}
            <div style={{
                maxWidth: 1200,
                margin: '0 auto',
                marginBottom: tokens.spacing[6],
            }}>
                <Space>
                    <Button
                        icon={<ArrowLeftOutlined />}
                        onClick={handleBackToProject}
                        type="text"
                    >
                        Back to Project
                    </Button>
                </Space>

                <Title level={2} style={{ marginTop: tokens.spacing[4], marginBottom: 0 }}>
                    CSV/XLSX Upload
                </Title>
                <Text type="secondary">
                    {filename ? `Configuring: ${filename}` : 'Upload and configure your event log'}
                </Text>
            </div>

            {/* Wizard content */}
            <Card
                style={{
                    maxWidth: 1200,
                    margin: '0 auto',
                    minHeight: 500,
                }}
            >
                {/* Stepper */}
                <WizardStepper currentStep={currentStep} />

                {/* Error display */}
                {error && (
                    <div style={{
                        background: tokens.colors.error[50],
                        padding: tokens.spacing[4],
                        borderRadius: tokens.radius.md,
                        marginBottom: tokens.spacing[4],
                    }}>
                        <Text type="danger">{error}</Text>
                    </div>
                )}

                {/* Step content */}
                {renderStep()}
            </Card>

            {/* Debug info for dev console */}
            <div style={{
                display: 'none',
                position: 'fixed',
                bottom: 0,
                left: 0,
                padding: 8,
                background: '#000',
                color: '#0f0',
                fontSize: 10,
            }}>
                Step: {currentStep} | Dataset: {datasetId?.slice(0, 8)} | Job: {jobId?.slice(0, 8)}
            </div>
        </div>
    );
}

export default UploadWizardPage;
