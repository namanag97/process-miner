/**
 * WizardStepper - Horizontal step indicator for upload wizard
 * 
 * Matches Celonis style with:
 * - Checkmarks for completed steps
 * - Blue circle for current step
 * - Gray for pending steps
 */

import React from 'react';
import { Steps } from 'antd';
import {
    CloudUploadOutlined,
    FileTextOutlined,
    SettingOutlined,
    LinkOutlined,
    CheckCircleOutlined,
} from '@ant-design/icons';
import type { WizardStep } from '../types';

interface WizardStepperProps {
    currentStep: WizardStep;
    className?: string;
}

const STEPS: { key: WizardStep; title: string; icon: React.ReactNode }[] = [
    { key: 'upload', title: 'Upload', icon: <CloudUploadOutlined /> },
    { key: 'sheets', title: 'Select sheet', icon: <FileTextOutlined /> },
    { key: 'configure', title: 'Configure', icon: <SettingOutlined /> },
    { key: 'mapping', title: 'Map your data', icon: <LinkOutlined /> },
    { key: 'finalize', title: 'Finalize', icon: <CheckCircleOutlined /> },
];

const STEP_ORDER: WizardStep[] = ['upload', 'sheets', 'configure', 'mapping', 'finalize'];

export function WizardStepper({ currentStep, className }: WizardStepperProps) {
    const currentIndex = STEP_ORDER.indexOf(currentStep);

    return (
        <Steps
            current={currentIndex}
            className={className}
            items={STEPS.map((step, index) => ({
                title: step.title,
                icon: step.icon,
                status: index < currentIndex ? 'finish' : index === currentIndex ? 'process' : 'wait',
            }))}
            style={{ marginBottom: 32 }}
        />
    );
}
