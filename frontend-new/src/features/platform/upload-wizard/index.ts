/**
 * Upload Wizard Feature
 * 
 * Celonis-style 5-step data upload wizard:
 * 1. Upload - Drag-drop file upload
 * 2. Select Sheet - Sheet picker (for Excel)
 * 3. Configure - Auto column mapping + data preview
 * 4. Map Data - PM4Py column mapping
 * 5. Finalize - Processing progress
 */

import { FeatureRegistry } from '../../../core/plugins/FeatureRegistry';
import { uploadWizardRouteConfig } from './routes';

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = 'upload-wizard';

export const FEATURE_CONFIG = {
    id: 'upload-wizard',
    name: 'Upload Wizard',
    version: '1.0.0',
    icon: 'UploadOutlined',
    // No navPath - upload wizard is accessed from project detail
    navOrder: 50,
};

// Register feature (auto-registration on import)
FeatureRegistry.register({
    ...FEATURE_CONFIG,
    routes: uploadWizardRouteConfig,
});

// ============================================
// Exports
// ============================================

export { UploadWizardPage } from './pages/UploadWizardPage';
export { WizardStepper } from './components/WizardStepper';
export { useUploadWizard } from './hooks/useUploadWizard';
export { useJobStream } from './hooks/useJobStream';
export type { WizardStep, WizardState, ColumnMapping, DataPreview } from './types';
