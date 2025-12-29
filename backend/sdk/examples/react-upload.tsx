/**
 * React File Upload Component Example
 *
 * This example demonstrates a complete file upload component with:
 * - File selection and validation
 * - Upload progress tracking
 * - Column mapping preview (for CSV files)
 * - Error handling
 * - Type-safe SDK usage
 *
 * Install dependencies:
 *   npm install @process-mining-saas/sdk @tanstack/react-query
 */

import { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ProcessesService,
  ProcessResponse,
  ColumnDetectionResponse,
  ApiError,
} from '@process-mining-saas/sdk';

// =============================================================================
// Types
// =============================================================================

interface UploadState {
  file: File | null;
  status: 'idle' | 'detecting' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
  columnDetection?: ColumnDetectionResponse;
}

interface ColumnMapping {
  case_id: string;
  activity: string;
  timestamp: string;
  resource?: string;
}

interface ProcessUploadProps {
  onSuccess?: (process: ProcessResponse) => void;
  onError?: (error: ApiError) => void;
}

// =============================================================================
// Hook: useProcessUpload
// =============================================================================

export function useProcessUpload(options?: {
  onSuccess?: (process: ProcessResponse) => void;
  onError?: (error: ApiError) => void;
}) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<UploadState>({
    file: null,
    status: 'idle',
    progress: 0,
  });

  // Detect columns mutation (for CSV files)
  const detectColumnsMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return ProcessesService.detectColumns({ formData });
    },
    onSuccess: (data) => {
      setState((prev) => ({
        ...prev,
        status: 'idle',
        columnDetection: data,
      }));
    },
    onError: (error: ApiError) => {
      setState((prev) => ({
        ...prev,
        status: 'error',
        error: error.body?.detail || 'Failed to detect columns',
      }));
    },
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async ({
      file,
      name,
      mapping,
    }: {
      file: File;
      name?: string;
      mapping?: ColumnMapping;
    }) => {
      setState((prev) => ({ ...prev, status: 'uploading', progress: 0 }));

      const formData = new FormData();
      formData.append('file', file);

      if (name) {
        formData.append('name', name);
      }

      if (mapping) {
        formData.append('case_id_column', mapping.case_id);
        formData.append('activity_column', mapping.activity);
        formData.append('timestamp_column', mapping.timestamp);
        if (mapping.resource) {
          formData.append('resource_column', mapping.resource);
        }
      }

      return ProcessesService.uploadProcess({ formData });
    },
    onSuccess: (data) => {
      setState({
        file: null,
        status: 'success',
        progress: 100,
      });
      queryClient.invalidateQueries({ queryKey: ['processes'] });
      options?.onSuccess?.(data);
    },
    onError: (error: ApiError) => {
      setState((prev) => ({
        ...prev,
        status: 'error',
        error: error.body?.detail || 'Upload failed',
      }));
      options?.onError?.(error);
    },
  });

  // Handle file selection
  const selectFile = useCallback(
    (file: File) => {
      setState({
        file,
        status: 'idle',
        progress: 0,
        columnDetection: undefined,
      });

      // Auto-detect columns for CSV files
      if (file.name.endsWith('.csv')) {
        setState((prev) => ({ ...prev, status: 'detecting' }));
        detectColumnsMutation.mutate(file);
      }
    },
    [detectColumnsMutation]
  );

  // Handle upload
  const upload = useCallback(
    (name?: string, mapping?: ColumnMapping) => {
      if (!state.file) return;
      uploadMutation.mutate({ file: state.file, name, mapping });
    },
    [state.file, uploadMutation]
  );

  // Reset state
  const reset = useCallback(() => {
    setState({
      file: null,
      status: 'idle',
      progress: 0,
    });
  }, []);

  return {
    state,
    selectFile,
    upload,
    reset,
    isLoading: state.status === 'detecting' || state.status === 'uploading',
  };
}

// =============================================================================
// Component: ProcessUpload
// =============================================================================

export function ProcessUpload({ onSuccess, onError }: ProcessUploadProps) {
  const { state, selectFile, upload, reset, isLoading } = useProcessUpload({
    onSuccess,
    onError,
  });

  const [name, setName] = useState('');
  const [mapping, setMapping] = useState<ColumnMapping>({
    case_id: '',
    activity: '',
    timestamp: '',
    resource: '',
  });

  // Handle file input change
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      selectFile(file);
      setName(file.name.replace(/\.[^/.]+$/, '')); // Default name from filename
    }
  };

  // Handle drag and drop
  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.xes'))) {
      selectFile(file);
      setName(file.name.replace(/\.[^/.]+$/, ''));
    }
  };

  // Update mapping when column detection completes
  const suggestions = state.columnDetection?.suggestions;
  if (suggestions && !mapping.case_id) {
    setMapping({
      case_id: suggestions.case_id || '',
      activity: suggestions.activity || '',
      timestamp: suggestions.timestamp || '',
      resource: suggestions.resource || '',
    });
  }

  // Handle upload
  const handleUpload = () => {
    upload(name || undefined, mapping.case_id ? mapping : undefined);
  };

  return (
    <div className="process-upload">
      {/* File Selection */}
      {!state.file && (
        <div
          className="dropzone"
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          <input
            type="file"
            accept=".csv,.xes"
            onChange={handleFileChange}
            id="file-input"
            hidden
          />
          <label htmlFor="file-input" className="dropzone-label">
            <span className="dropzone-icon">+</span>
            <span>Drop a CSV or XES file here, or click to select</span>
          </label>
        </div>
      )}

      {/* File Info */}
      {state.file && (
        <div className="file-info">
          <span className="file-name">{state.file.name}</span>
          <span className="file-size">
            ({(state.file.size / 1024).toFixed(1)} KB)
          </span>
          <button type="button" onClick={reset} className="btn-clear">
            Clear
          </button>
        </div>
      )}

      {/* Detecting Columns */}
      {state.status === 'detecting' && (
        <div className="status detecting">Detecting columns...</div>
      )}

      {/* Column Mapping (for CSV) */}
      {state.columnDetection && (
        <div className="column-mapping">
          <h4>Column Mapping</h4>
          <p className="hint">
            {state.columnDetection.row_count} rows detected
          </p>

          <div className="mapping-grid">
            <label>
              Case ID *
              <select
                value={mapping.case_id}
                onChange={(e) =>
                  setMapping({ ...mapping, case_id: e.target.value })
                }
              >
                <option value="">Select column...</option>
                {state.columnDetection.columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Activity *
              <select
                value={mapping.activity}
                onChange={(e) =>
                  setMapping({ ...mapping, activity: e.target.value })
                }
              >
                <option value="">Select column...</option>
                {state.columnDetection.columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Timestamp *
              <select
                value={mapping.timestamp}
                onChange={(e) =>
                  setMapping({ ...mapping, timestamp: e.target.value })
                }
              >
                <option value="">Select column...</option>
                {state.columnDetection.columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Resource (optional)
              <select
                value={mapping.resource}
                onChange={(e) =>
                  setMapping({ ...mapping, resource: e.target.value })
                }
              >
                <option value="">None</option>
                {state.columnDetection.columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {/* Sample Data Preview */}
          <details className="sample-preview">
            <summary>Preview sample data</summary>
            <table>
              <thead>
                <tr>
                  {state.columnDetection.columns.map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {state.columnDetection.sample_rows.slice(0, 3).map((row, i) => (
                  <tr key={i}>
                    {state.columnDetection!.columns.map((col) => (
                      <td key={col}>{String(row[col] ?? '')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        </div>
      )}

      {/* Name Input */}
      {state.file && state.status !== 'detecting' && (
        <div className="name-input">
          <label>
            Process Name
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter a name for this event log"
            />
          </label>
        </div>
      )}

      {/* Upload Progress */}
      {state.status === 'uploading' && (
        <div className="progress">
          <div
            className="progress-bar"
            style={{ width: `${state.progress}%` }}
          />
          <span className="progress-text">Uploading...</span>
        </div>
      )}

      {/* Error */}
      {state.status === 'error' && (
        <div className="error">
          <span className="error-icon">!</span>
          {state.error}
        </div>
      )}

      {/* Success */}
      {state.status === 'success' && (
        <div className="success">Upload complete!</div>
      )}

      {/* Upload Button */}
      {state.file && state.status === 'idle' && (
        <button
          type="button"
          onClick={handleUpload}
          disabled={isLoading}
          className="btn-upload"
        >
          Upload Event Log
        </button>
      )}
    </div>
  );
}

// =============================================================================
// Styles (CSS-in-JS example)
// =============================================================================

export const styles = `
.process-upload {
  max-width: 600px;
  margin: 0 auto;
}

.dropzone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
}

.dropzone:hover {
  border-color: #007bff;
}

.dropzone-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.dropzone-icon {
  font-size: 48px;
  color: #ccc;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.file-name {
  font-weight: 500;
}

.file-size {
  color: #666;
}

.btn-clear {
  margin-left: auto;
  padding: 4px 8px;
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}

.column-mapping {
  margin-top: 16px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.mapping-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.mapping-grid label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}

.mapping-grid select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.name-input {
  margin-top: 16px;
}

.name-input label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-input input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.progress {
  margin-top: 16px;
  height: 24px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: #007bff;
  transition: width 0.3s;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
}

.error {
  margin-top: 16px;
  padding: 12px;
  background: #fee;
  border: 1px solid #f00;
  border-radius: 4px;
  color: #c00;
}

.success {
  margin-top: 16px;
  padding: 12px;
  background: #efe;
  border: 1px solid #0a0;
  border-radius: 4px;
  color: #060;
}

.btn-upload {
  margin-top: 16px;
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-upload:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.sample-preview {
  margin-top: 16px;
}

.sample-preview table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-top: 8px;
}

.sample-preview th,
.sample-preview td {
  padding: 4px 8px;
  border: 1px solid #ddd;
  text-align: left;
}

.sample-preview th {
  background: #f0f0f0;
}
`;

export default ProcessUpload;
