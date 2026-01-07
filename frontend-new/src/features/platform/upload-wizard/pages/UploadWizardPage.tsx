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
import { Card, Typography, Button, Spin, message } from 'antd';
import { ArrowLeftOutlined, LoadingOutlined } from '@ant-design/icons';
import { tokens, logAction } from '@lumina/design-system';
import { devLog } from '../../../../shared/ui/DevConsole';
import { useUploadWizard } from '../hooks/useUploadWizard';
import {
    UploadStep,
    ConfigureStep,
    MapDataStep,
    FinalizeStep
} from '../components/steps';
import type { WizardStep } from '../types';

const { Text } = Typography;

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
        uploadFilePresigned: _uploadFilePresigned, // Presigned upload for production (requires MinIO/S3)
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

    // Step configuration for vertical stepper
    const STEP_CONFIG = [
        { key: 'upload', number: 1, title: 'Select Data Source', description: 'Choose or upload data' },
        { key: 'sheets', number: 2, title: 'Select Sheet', description: 'Choose worksheet' },
        { key: 'configure', number: 3, title: 'Configure', description: 'Review structure' },
        { key: 'mapping', number: 4, title: 'Map Columns', description: 'Map to PM fields' },
        { key: 'finalize', number: 5, title: 'Processing', description: 'Analyze data' },
    ];

    const STEP_ORDER: WizardStep[] = ['upload', 'sheets', 'configure', 'mapping', 'finalize'];
    const currentIndex = STEP_ORDER.indexOf(currentStep);

    const getStepStatus = (stepKey: string) => {
        const stepIndex = STEP_ORDER.indexOf(stepKey as WizardStep);
        if (stepIndex < currentIndex) return 'completed';
        if (stepIndex === currentIndex) return 'active';
        return 'pending';
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: tokens.colors.neutral[50],
            padding: tokens.spacing[6],
        }}>
            <div style={{ maxWidth: 1100, margin: '0 auto' }}>
                {/* Header with breadcrumb */}
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: tokens.spacing[3],
                    marginBottom: tokens.spacing[6],
                }}>
                    <Button
                        icon={<ArrowLeftOutlined />}
                        onClick={handleBackToProject}
                        type="text"
                        style={{ color: tokens.colors.primary[500] }}
                    >
                        Process Miner
                    </Button>
                    <Text type="secondary">›</Text>
                    <Text strong>Setting up your Process Workspace</Text>
                </div>

                {/* Main card with 2-column layout */}
                <Card
                    style={{
                        borderRadius: tokens.radius.lg,
                        boxShadow: tokens.shadow.md,
                    }}
                    styles={{ body: { padding: 0 } }}
                >
                    <div style={{ display: 'flex', minHeight: 560 }}>
                        {/* Left: Vertical Step Indicator */}
                        <div style={{
                            width: 280,
                            padding: tokens.spacing[6],
                            borderRight: `1px solid ${tokens.colors.neutral[200]}`,
                            background: tokens.colors.neutral[50],
                        }}>
                            {STEP_CONFIG.map((step, index) => {
                                const status = getStepStatus(step.key);
                                const isLast = index === STEP_CONFIG.length - 1;

                                return (
                                    <div key={step.key} style={{ display: 'flex', alignItems: 'flex-start', gap: tokens.spacing[4] }}>
                                        {/* Circle + Line */}
                                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                            <div
                                                style={{
                                                    width: 32,
                                                    height: 32,
                                                    borderRadius: '50%',
                                                    backgroundColor: status === 'completed'
                                                        ? tokens.colors.success[500]
                                                        : status === 'active'
                                                            ? tokens.colors.primary[500]
                                                            : tokens.colors.neutral[100],
                                                    border: status === 'pending'
                                                        ? `2px solid ${tokens.colors.neutral[300]}`
                                                        : 'none',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    color: status === 'pending' ? tokens.colors.neutral[500] : '#fff',
                                                    fontSize: 14,
                                                    fontWeight: 600,
                                                    transition: 'all 0.2s ease',
                                                }}
                                            >
                                                {status === 'completed' ? '✓' : step.number}
                                            </div>
                                            {!isLast && (
                                                <div
                                                    style={{
                                                        width: 2,
                                                        height: 48,
                                                        backgroundColor: status === 'completed'
                                                            ? tokens.colors.success[500]
                                                            : tokens.colors.neutral[200],
                                                        marginTop: tokens.spacing[2],
                                                        transition: 'background-color 0.3s ease',
                                                    }}
                                                />
                                            )}
                                        </div>

                                        {/* Text */}
                                        <div style={{ flex: 1, paddingBottom: tokens.spacing[6] }}>
                                            <Text
                                                strong
                                                style={{
                                                    fontSize: 14,
                                                    color: status === 'pending'
                                                        ? tokens.colors.neutral[500]
                                                        : tokens.colors.neutral[900],
                                                    display: 'block',
                                                    marginBottom: 2,
                                                }}
                                            >
                                                {step.title}
                                            </Text>
                                            <Text
                                                style={{
                                                    fontSize: 12,
                                                    color: tokens.colors.neutral[500],
                                                }}
                                            >
                                                {step.description}
                                            </Text>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Right: Step Content */}
                        <div style={{ flex: 1, padding: tokens.spacing[6] }}>
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
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}

export default UploadWizardPage;
