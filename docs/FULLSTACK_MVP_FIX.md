# FULL STACK MVP FIX - Complete Guide

**GOAL:** Fix everything so you can use the UI end-to-end and see visualizations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE COMPLETE USER JOURNEY                           │
│                                                                             │
│   Browser UI                                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  Login → Upload CSV → Map Columns → Wait → See Process Map →        │  │
│   │  → View Bottlenecks → View Variants → Export                        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                              ↕ HTTP/REST                                    │
│   Backend API                                                               │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  Auth → Datasets → Ingestion → Discovery → Visualization → Analytics│  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                              ↕ PM4Py                                        │
│   Process Mining Engine                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  Event Logs → Algorithms → Models → SVG/JSON                        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 0: START BOTH SERVERS

### Terminal 1: Backend
```bash
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
```

### Terminal 2: Frontend
```bash
cd /Users/namanagarwal/system/frontend-new
npm run start
```

### Terminal 3: Testing
```bash
# Verify both running
curl -s http://localhost:8001/health/live | jq .
curl -s -o /dev/null -w "%{http_code}" http://localhost:4200
```

**Expected:**
- Backend: `{"status": "healthy"}`
- Frontend: `200`

---

## PHASE 1: FIX BACKEND API

### 1.1 Test All Critical Endpoints

```bash
BASE="http://localhost:8001/api/v1"

# Get token
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')
echo "TOKEN=$TOKEN"

# Test each endpoint category
echo "=== Auth ===" && curl -s "$BASE/auth/me" -H "Authorization: Bearer $TOKEN" | jq '.email'
echo "=== Workspaces ===" && curl -s "$BASE/workspaces" -H "Authorization: Bearer $TOKEN" | jq '.items | length'
echo "=== Projects ===" && curl -s "$BASE/projects" -H "Authorization: Bearer $TOKEN" | jq '.items | length'
echo "=== Datasets ===" && curl -s "$BASE/datasets/" -H "Authorization: Bearer $TOKEN" | jq '.items | length'
echo "=== Miners ===" && curl -s "$BASE/discovery/miners" -H "Authorization: Bearer $TOKEN" | jq 'length'
```

### 1.2 Key Backend Files

| Component | Files |
|-----------|-------|
| **Main App** | `src/api/main.py` |
| **Routes** | `src/api/routes/*.py` |
| **Services** | `src/services/*/` |
| **Domain Logic** | `src/domain/*/` |
| **Database** | `src/infrastructure/repositories/` |
| **Config** | `src/core/config.py` |

### 1.3 CORS Configuration (Critical for FE-BE)

Check `src/api/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:3000",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

**If CORS errors in browser console, fix this first!**

---

## PHASE 2: FIX FRONTEND

### 2.1 Frontend Structure

```
frontend-new/
├── src/
│   ├── app/                    # Main app module
│   ├── components/             # Reusable components
│   ├── pages/                  # Page components
│   │   ├── Login/
│   │   ├── Workspace/
│   │   ├── Upload/
│   │   ├── Explorer/           # Process map visualization
│   │   ├── Discovery/
│   │   ├── Analytics/
│   │   └── KPI/
│   ├── services/               # API calls
│   │   ├── api.ts              # Base API client
│   │   ├── authService.ts
│   │   ├── datasetService.ts
│   │   ├── discoveryService.ts
│   │   └── analyticsService.ts
│   ├── stores/                 # State management
│   └── types/                  # TypeScript types
├── package.json
└── .env                        # Environment variables
```

### 2.2 Check Environment Config

Create/verify `frontend-new/.env`:
```env
VITE_API_URL=http://localhost:8001/api/v1
VITE_API_BASE_URL=http://localhost:8001
```

Or for Create React App:
```env
REACT_APP_API_URL=http://localhost:8001/api/v1
REACT_APP_API_BASE_URL=http://localhost:8001
```

### 2.3 Check API Base URL in Code

Find and verify the API client configuration:
```bash
cd /Users/namanagarwal/system/frontend-new
grep -r "localhost:8001\|API_URL\|baseURL\|apiUrl" src/ --include="*.ts" --include="*.tsx"
```

Common locations:
- `src/services/api.ts`
- `src/config/index.ts`
- `src/utils/axios.ts`

**Expected pattern:**
```typescript
// src/services/api.ts
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 2.4 Key Frontend Pages to Verify

| Page | URL | What It Does |
|------|-----|--------------|
| Login | `/login` | Auth, store token |
| Workspace | `/workspace` | List projects |
| Upload | `/workspace/:id/upload` | Upload CSV, map columns |
| Explorer | `/workspace/:id/data/:datasetId/explorer` | **Show process map** |
| Discovery | `/workspace/:id/data/:datasetId/discovery` | Run algorithms |
| Analytics | `/workspace/:id/data/:datasetId/analytics` | Show metrics |

---

## PHASE 3: FIX FE-BE CONNECTION

### 3.1 Debug Connection Issues

Open browser DevTools (F12) → Network tab → Check for:
- ❌ Red requests (failed)
- ❌ CORS errors in Console
- ❌ 401/403 errors (auth issues)

### 3.2 Common Connection Fixes

**Fix: CORS Error**
```
Access to XMLHttpRequest at 'http://localhost:8001/...' from origin 
'http://localhost:4200' has been blocked by CORS policy
```
→ Fix backend CORS middleware (see 1.3)

**Fix: 401 Unauthorized**
```typescript
// Ensure token is stored after login
const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login', { email, password });
  localStorage.setItem('token', response.data.access_token);
  return response.data;
};
```

**Fix: Network Error / Connection Refused**
→ Backend not running. Start it.

**Fix: 404 Not Found**
→ Wrong API path. Check endpoint URL matches backend routes.

### 3.3 Test FE-BE Connection

In browser console (F12):
```javascript
// Test API connection
fetch('http://localhost:8001/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'analyst@example.com', password: 'TestPass123' })
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

---

## PHASE 4: FIX VISUALIZATION IN UI

### 4.1 Process Map Visualization

The Explorer page should show an interactive process map. Common libraries:
- **Cytoscape.js** - Graph visualization
- **D3.js** - Custom visualizations
- **React Flow** - Node-based graphs
- **Raw SVG** - PM4Py generated SVGs

### 4.2 Find Visualization Components

```bash
cd /Users/namanagarwal/system/frontend-new
grep -r "cytoscape\|Cytoscape\|d3\|ReactFlow\|svg\|graph" src/ --include="*.ts" --include="*.tsx" | head -20
```

### 4.3 Cytoscape.js Integration (Common Pattern)

```typescript
// src/components/ProcessMap/ProcessMap.tsx
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';

interface Node {
  id: string;
  label: string;
  frequency?: number;
}

interface Edge {
  source: string;
  target: string;
  value?: number;
}

interface ProcessMapProps {
  nodes: Node[];
  edges: Edge[];
}

export const ProcessMap: React.FC<ProcessMapProps> = ({ nodes, edges }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || !nodes.length) return;

    // Transform data for Cytoscape
    const elements = [
      ...nodes.map(node => ({
        data: { id: node.id, label: node.label, frequency: node.frequency }
      })),
      ...edges.map(edge => ({
        data: { 
          id: `${edge.source}-${edge.target}`,
          source: edge.source, 
          target: edge.target,
          value: edge.value
        }
      }))
    ];

    // Create Cytoscape instance
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#4a90d9',
            'label': 'data(label)',
            'text-valign': 'center',
            'color': '#fff',
            'text-outline-width': 2,
            'text-outline-color': '#4a90d9',
            'width': 'mapData(frequency, 0, 100, 30, 80)',
            'height': 'mapData(frequency, 0, 100, 30, 80)',
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 'mapData(value, 0, 100, 1, 8)',
            'line-color': '#9dbaea',
            'target-arrow-color': '#9dbaea',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(value)',
            'font-size': '10px',
          }
        }
      ],
      layout: {
        name: 'dagre',  // Requires cytoscape-dagre
        rankDir: 'LR',
        padding: 50
      }
    });

    // Cleanup
    return () => {
      cyRef.current?.destroy();
    };
  }, [nodes, edges]);

  return (
    <div 
      ref={containerRef} 
      style={{ width: '100%', height: '600px', border: '1px solid #ddd' }} 
    />
  );
};
```

### 4.4 Install Visualization Dependencies

```bash
cd /Users/namanagarwal/system/frontend-new

# Cytoscape + layout
npm install cytoscape cytoscape-dagre @types/cytoscape

# Or D3
npm install d3 @types/d3

# Or React Flow
npm install reactflow
```

### 4.5 Fetching Visualization Data

```typescript
// src/services/visualizationService.ts
import { api } from './api';

export interface DFGData {
  nodes: Array<{ id: string; label: string; frequency: number }>;
  edges: Array<{ source: string; target: string; value: number }>;
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
}

export const getdfG = async (datasetId: string): Promise<DFGData> => {
  const response = await api.get(`/visualization/${datasetId}/dfg`);
  return response.data;
};

export const getDFGSvg = async (datasetId: string): Promise<string> => {
  const response = await api.get(`/visualization/${datasetId}/dfg/svg`);
  return response.data;
};

export const getPetriNet = async (modelId: string) => {
  const response = await api.get(`/visualization/models/${modelId}/petri`);
  return response.data;
};

export const getPetriNetSvg = async (modelId: string): Promise<string> => {
  const response = await api.get(`/visualization/models/${modelId}/svg`);
  return response.data;
};
```

### 4.6 SVG Rendering (Alternative to Cytoscape)

If backend returns SVG directly:

```typescript
// src/components/SVGViewer/SVGViewer.tsx
import React from 'react';

interface SVGViewerProps {
  svg: string;
}

export const SVGViewer: React.FC<SVGViewerProps> = ({ svg }) => {
  return (
    <div 
      className="svg-container"
      style={{ 
        width: '100%', 
        height: '600px', 
        overflow: 'auto',
        border: '1px solid #ddd'
      }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
};

// With zoom/pan
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';

export const ZoomableSVGViewer: React.FC<SVGViewerProps> = ({ svg }) => {
  return (
    <TransformWrapper>
      <TransformComponent>
        <div dangerouslySetInnerHTML={{ __html: svg }} />
      </TransformComponent>
    </TransformWrapper>
  );
};
```

Install: `npm install react-zoom-pan-pinch`

### 4.7 Explorer Page Example

```typescript
// src/pages/Explorer/Explorer.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ProcessMap } from '../../components/ProcessMap/ProcessMap';
import { getDFG, DFGData } from '../../services/visualizationService';

export const Explorer: React.FC = () => {
  const { datasetId } = useParams<{ datasetId: string }>();
  const [dfgData, setDfgData] = useState<DFGData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!datasetId) return;
      
      try {
        setLoading(true);
        const data = await getDFG(datasetId);
        setDfgData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load process map');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [datasetId]);

  if (loading) return <div>Loading process map...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!dfgData) return <div>No data available</div>;

  return (
    <div className="explorer-page">
      <h1>Process Explorer</h1>
      <div className="stats">
        <span>{dfgData.nodes.length} activities</span>
        <span>{dfgData.edges.length} transitions</span>
      </div>
      <ProcessMap nodes={dfgData.nodes} edges={dfgData.edges} />
    </div>
  );
};
```

---

## PHASE 5: FIX UPLOAD WIZARD

### 5.1 Upload Flow Components

```typescript
// src/pages/Upload/Upload.tsx
import React, { useState } from 'react';
import { FileUpload } from './steps/FileUpload';
import { ColumnMapping } from './steps/ColumnMapping';
import { Processing } from './steps/Processing';
import { Complete } from './steps/Complete';

type Step = 'upload' | 'mapping' | 'processing' | 'complete';

export const Upload: React.FC = () => {
  const [step, setStep] = useState<Step>('upload');
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [columns, setColumns] = useState<string[]>([]);

  return (
    <div className="upload-wizard">
      {step === 'upload' && (
        <FileUpload 
          onComplete={(id, cols) => {
            setDatasetId(id);
            setColumns(cols);
            setStep('mapping');
          }} 
        />
      )}
      {step === 'mapping' && datasetId && (
        <ColumnMapping 
          datasetId={datasetId}
          columns={columns}
          onComplete={() => setStep('processing')} 
        />
      )}
      {step === 'processing' && datasetId && (
        <Processing 
          datasetId={datasetId}
          onComplete={() => setStep('complete')} 
        />
      )}
      {step === 'complete' && datasetId && (
        <Complete datasetId={datasetId} />
      )}
    </div>
  );
};
```

### 5.2 File Upload Component

```typescript
// src/pages/Upload/steps/FileUpload.tsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadDataset } from '../../../services/datasetService';

interface Props {
  onComplete: (datasetId: string, columns: string[]) => void;
}

export const FileUpload: React.FC<Props> = ({ onComplete }) => {
  const [uploading, setUploading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const projectId = 'mvp-proj-001'; // Or get from context/params
      const result = await uploadDataset(file, projectId);
      
      // Get detected columns
      const columnsResponse = await getDatasetColumns(result.id);
      onComplete(result.id, columnsResponse.columns);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [onComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/xml': ['.xes'],
    },
    maxFiles: 1,
  });

  return (
    <div className="file-upload">
      <h2>Upload Event Log</h2>
      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <p>Uploading...</p>
        ) : isDragActive ? (
          <p>Drop the file here...</p>
        ) : (
          <p>Drag & drop a CSV or XES file here, or click to select</p>
        )}
      </div>
      {error && <div className="error">{error}</div>}
    </div>
  );
};
```

Install: `npm install react-dropzone`

### 5.3 Column Mapping Component

```typescript
// src/pages/Upload/steps/ColumnMapping.tsx
import React, { useState } from 'react';
import { submitColumnMapping } from '../../../services/datasetService';

interface Props {
  datasetId: string;
  columns: string[];
  onComplete: () => void;
}

export const ColumnMapping: React.FC<Props> = ({ datasetId, columns, onComplete }) => {
  const [mapping, setMapping] = useState({
    case_id_column: '',
    activity_column: '',
    timestamp_column: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await submitColumnMapping(datasetId, mapping);
      await triggerIngestion(datasetId);
      onComplete();
    } catch (err) {
      console.error('Mapping failed:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="column-mapping">
      <h2>Map Your Columns</h2>
      
      <div className="field">
        <label>Case ID *</label>
        <select 
          value={mapping.case_id_column}
          onChange={e => setMapping({...mapping, case_id_column: e.target.value})}
        >
          <option value="">Select column...</option>
          {columns.map(col => <option key={col} value={col}>{col}</option>)}
        </select>
      </div>

      <div className="field">
        <label>Activity *</label>
        <select 
          value={mapping.activity_column}
          onChange={e => setMapping({...mapping, activity_column: e.target.value})}
        >
          <option value="">Select column...</option>
          {columns.map(col => <option key={col} value={col}>{col}</option>)}
        </select>
      </div>

      <div className="field">
        <label>Timestamp *</label>
        <select 
          value={mapping.timestamp_column}
          onChange={e => setMapping({...mapping, timestamp_column: e.target.value})}
        >
          <option value="">Select column...</option>
          {columns.map(col => <option key={col} value={col}>{col}</option>)}
        </select>
      </div>

      <button 
        onClick={handleSubmit} 
        disabled={submitting || !mapping.case_id_column || !mapping.activity_column || !mapping.timestamp_column}
      >
        {submitting ? 'Processing...' : 'Start Import'}
      </button>
    </div>
  );
};
```

### 5.4 Dataset Service

```typescript
// src/services/datasetService.ts
import { api } from './api';

export const uploadDataset = async (file: File, projectId: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('name', file.name);
  formData.append('project_id', projectId);

  const response = await api.post('/datasets/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getDatasetColumns = async (datasetId: string) => {
  const response = await api.get(`/datasets/${datasetId}/columns`);
  return response.data;
};

export const submitColumnMapping = async (datasetId: string, mapping: {
  case_id_column: string;
  activity_column: string;
  timestamp_column: string;
}) => {
  const response = await api.post(`/datasets/${datasetId}/mapping`, mapping);
  return response.data;
};

export const triggerIngestion = async (datasetId: string) => {
  const response = await api.post(`/datasets/${datasetId}/ingest`);
  return response.data;
};

export const getDataset = async (datasetId: string) => {
  const response = await api.get(`/datasets/${datasetId}`);
  return response.data;
};

export const pollDatasetStatus = async (
  datasetId: string, 
  onProgress: (status: string) => void,
  maxAttempts = 60
): Promise<string> => {
  for (let i = 0; i < maxAttempts; i++) {
    const dataset = await getDataset(datasetId);
    onProgress(dataset.status);
    
    if (dataset.status === 'ready') return 'ready';
    if (dataset.status === 'failed') throw new Error('Ingestion failed');
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  throw new Error('Ingestion timeout');
};
```

---

## PHASE 6: COMPLETE VERIFICATION

### 6.1 Manual UI Test Checklist

Open http://localhost:4200 and test:

- [ ] **Login Page**
  - [ ] Page loads without errors
  - [ ] Can enter email/password
  - [ ] Login with `analyst@example.com` / `TestPass123`
  - [ ] Redirects to workspace after login

- [ ] **Workspace Page**
  - [ ] Shows list of projects
  - [ ] Can click on a project

- [ ] **Upload Page**
  - [ ] Drag & drop zone visible
  - [ ] Can upload CSV file
  - [ ] Column detection works
  - [ ] Column mapping dropdowns populated
  - [ ] Can submit mapping
  - [ ] Progress indicator during ingestion
  - [ ] Success message when complete

- [ ] **Explorer Page**
  - [ ] Process map renders
  - [ ] Nodes are visible (activities)
  - [ ] Edges are visible (transitions)
  - [ ] Can zoom/pan
  - [ ] Shows activity counts

- [ ] **Analytics Page**
  - [ ] Variants list shows
  - [ ] Bottlenecks displayed
  - [ ] Charts render

### 6.2 Browser Console Check

With DevTools open (F12):
- [ ] No red errors in Console
- [ ] No failed network requests
- [ ] No CORS errors

### 6.3 Automated E2E Test

```bash
# Run from frontend directory
cd /Users/namanagarwal/system/frontend-new
npm run test:e2e  # If configured

# Or use the backend test runner
cd /Users/namanagarwal/system/backend
bash scripts/ai_test_runner.sh full
```

---

## QUICK REFERENCE: FILE LOCATIONS

### Backend
```
src/api/main.py                     # App entry, CORS config
src/api/routes/auth.py              # Login endpoint
src/api/routes/datasets.py          # Upload, mapping, ingest
src/api/routes/discovery.py         # Run algorithms
src/api/routes/visualization.py     # Get DFG/Petri net data
src/api/routes/analytics.py         # Bottlenecks, variants
src/core/config.py                  # Settings
```

### Frontend
```
src/services/api.ts                 # API client, base URL
src/services/authService.ts         # Login
src/services/datasetService.ts      # Upload, mapping
src/services/visualizationService.ts # Get viz data
src/pages/Login/                    # Login page
src/pages/Upload/                   # Upload wizard
src/pages/Explorer/                 # Process map
src/components/ProcessMap/          # Visualization component
```

---

## TROUBLESHOOTING

### "Network Error" in frontend
1. Check backend is running on port 8001
2. Check CORS config in backend
3. Check API URL in frontend config

### "401 Unauthorized" 
1. Check token is stored: `localStorage.getItem('token')`
2. Check token is sent in headers
3. Try logging in again

### Process map doesn't render
1. Check browser console for errors
2. Check network tab - is `/visualization/{id}/dfg` returning data?
3. Check Cytoscape container has height set
4. Check nodes/edges arrays are not empty

### "Module not found" in frontend
```bash
cd /Users/namanagarwal/system/frontend-new
rm -rf node_modules
npm install
npm start
```

### Backend returns 500
1. Check backend terminal for Python traceback
2. Fix the error in the indicated file
3. Backend auto-reloads

---

## SUCCESS = 

You can:
1. ✅ Open http://localhost:4200
2. ✅ Login with test credentials
3. ✅ Upload a CSV file
4. ✅ Map columns and start ingestion
5. ✅ See processing complete
6. ✅ View interactive process map
7. ✅ See bottlenecks and variants
8. ✅ All without console errors

**When this works: The MVP is complete! 🎉**
