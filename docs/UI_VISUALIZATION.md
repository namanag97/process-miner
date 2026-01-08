# UI VISUALIZATION GUIDE

## Goal: See Process Maps in the Browser

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     WHAT YOU SHOULD SEE                                 │
│                                                                         │
│   ┌─────────┐         ┌─────────┐         ┌─────────┐                  │
│   │ Create  │────────▶│ Review  │────────▶│ Approve │                  │
│   │  (150)  │   120   │  (120)  │   100   │  (100)  │                  │
│   └─────────┘         └────┬────┘         └────┬────┘                  │
│                            │ 20                │ 100                    │
│                            ▼                   ▼                        │
│                       ┌─────────┐         ┌─────────┐                  │
│                       │ Reject  │         │Complete │                  │
│                       │  (20)   │         │  (100)  │                  │
│                       └─────────┘         └─────────┘                  │
│                                                                         │
│   Interactive: Zoom, Pan, Click nodes for details                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## OPTION 1: Cytoscape.js (Recommended)

### Install Dependencies
```bash
cd /Users/namanagarwal/system/frontend-new
npm install cytoscape cytoscape-dagre @types/cytoscape
```

### ProcessMap Component
```typescript
// src/components/ProcessMap/ProcessMap.tsx
import React, { useEffect, useRef, useCallback } from 'react';
import cytoscape, { Core, ElementDefinition } from 'cytoscape';
import dagre from 'cytoscape-dagre';

// Register dagre layout
cytoscape.use(dagre);

export interface ProcessNode {
  id: string;
  label: string;
  frequency?: number;
  type?: 'activity' | 'start' | 'end';
}

export interface ProcessEdge {
  source: string;
  target: string;
  value: number;
  label?: string;
}

interface ProcessMapProps {
  nodes: ProcessNode[];
  edges: ProcessEdge[];
  onNodeClick?: (nodeId: string) => void;
  onEdgeClick?: (source: string, target: string) => void;
  height?: string;
}

export const ProcessMap: React.FC<ProcessMapProps> = ({
  nodes,
  edges,
  onNodeClick,
  onEdgeClick,
  height = '600px'
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  // Calculate max values for scaling
  const maxFrequency = Math.max(...nodes.map(n => n.frequency || 1), 1);
  const maxEdgeValue = Math.max(...edges.map(e => e.value || 1), 1);

  // Build Cytoscape elements
  const elements: ElementDefinition[] = [
    // Nodes
    ...nodes.map(node => ({
      data: {
        id: node.id,
        label: `${node.label}\n(${node.frequency || 0})`,
        frequency: node.frequency || 0,
        nodeType: node.type || 'activity'
      }
    })),
    // Edges
    ...edges.map(edge => ({
      data: {
        id: `${edge.source}->${edge.target}`,
        source: edge.source,
        target: edge.target,
        value: edge.value,
        label: edge.label || edge.value.toString()
      }
    }))
  ];

  useEffect(() => {
    if (!containerRef.current) return;

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Create Cytoscape instance
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        // Node styles
        {
          selector: 'node',
          style: {
            'background-color': '#4A90D9',
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#ffffff',
            'text-outline-color': '#4A90D9',
            'text-outline-width': 2,
            'font-size': '12px',
            'text-wrap': 'wrap',
            'text-max-width': '80px',
            'width': `mapData(frequency, 0, ${maxFrequency}, 50, 100)`,
            'height': `mapData(frequency, 0, ${maxFrequency}, 50, 100)`,
            'shape': 'roundrectangle',
            'border-width': 2,
            'border-color': '#2E5A8C'
          }
        },
        // Start node style
        {
          selector: 'node[nodeType="start"]',
          style: {
            'background-color': '#27AE60',
            'text-outline-color': '#27AE60',
            'border-color': '#1E8449',
            'shape': 'ellipse'
          }
        },
        // End node style
        {
          selector: 'node[nodeType="end"]',
          style: {
            'background-color': '#E74C3C',
            'text-outline-color': '#E74C3C',
            'border-color': '#B03A2E',
            'shape': 'ellipse'
          }
        },
        // Selected node
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#F39C12'
          }
        },
        // Edge styles
        {
          selector: 'edge',
          style: {
            'width': `mapData(value, 0, ${maxEdgeValue}, 1, 8)`,
            'line-color': '#95A5A6',
            'target-arrow-color': '#95A5A6',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.8,
            'text-background-padding': '2px'
          }
        },
        // Selected edge
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#F39C12',
            'target-arrow-color': '#F39C12',
            'width': 4
          }
        }
      ],
      layout: {
        name: 'dagre',
        rankDir: 'LR',  // Left to right
        nodeSep: 80,
        rankSep: 120,
        padding: 50
      },
      // Interaction options
      minZoom: 0.2,
      maxZoom: 3,
      wheelSensitivity: 0.3
    });

    // Event handlers
    if (onNodeClick) {
      cyRef.current.on('tap', 'node', (event) => {
        onNodeClick(event.target.id());
      });
    }

    if (onEdgeClick) {
      cyRef.current.on('tap', 'edge', (event) => {
        const source = event.target.source().id();
        const target = event.target.target().id();
        onEdgeClick(source, target);
      });
    }

    // Fit to view
    cyRef.current.fit(undefined, 50);

    return () => {
      cyRef.current?.destroy();
    };
  }, [nodes, edges, maxFrequency, maxEdgeValue, onNodeClick, onEdgeClick]);

  // Control methods
  const zoomIn = useCallback(() => {
    cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
  }, []);

  const zoomOut = useCallback(() => {
    cyRef.current?.zoom(cyRef.current.zoom() / 1.2);
  }, []);

  const fitView = useCallback(() => {
    cyRef.current?.fit(undefined, 50);
  }, []);

  return (
    <div className="process-map-container">
      {/* Controls */}
      <div className="process-map-controls" style={{ marginBottom: '10px' }}>
        <button onClick={zoomIn}>Zoom In (+)</button>
        <button onClick={zoomOut}>Zoom Out (-)</button>
        <button onClick={fitView}>Fit View</button>
      </div>
      
      {/* Graph container */}
      <div 
        ref={containerRef} 
        style={{ 
          width: '100%', 
          height, 
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: '#fafafa'
        }} 
      />
    </div>
  );
};

export default ProcessMap;
```

### Usage in Explorer Page
```typescript
// src/pages/Explorer/Explorer.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ProcessMap, { ProcessNode, ProcessEdge } from '../../components/ProcessMap/ProcessMap';
import { visualizationService } from '../../services/visualizationService';

interface DFGResponse {
  nodes: Array<{ id: string; label: string; frequency: number }>;
  edges: Array<{ source: string; target: string; value: number }>;
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
}

export const Explorer: React.FC = () => {
  const { datasetId } = useParams<{ datasetId: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nodes, setNodes] = useState<ProcessNode[]>([]);
  const [edges, setEdges] = useState<ProcessEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) return;

    const loadVisualization = async () => {
      try {
        setLoading(true);
        const data: DFGResponse = await visualizationService.getDFG(datasetId);
        
        // Transform nodes
        const transformedNodes: ProcessNode[] = data.nodes.map(n => ({
          id: n.id,
          label: n.label || n.id,
          frequency: n.frequency,
          type: data.start_activities[n.id] ? 'start' 
              : data.end_activities[n.id] ? 'end' 
              : 'activity'
        }));

        // Transform edges
        const transformedEdges: ProcessEdge[] = data.edges.map(e => ({
          source: e.source,
          target: e.target,
          value: e.value
        }));

        setNodes(transformedNodes);
        setEdges(transformedEdges);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load visualization');
      } finally {
        setLoading(false);
      }
    };

    loadVisualization();
  }, [datasetId]);

  const handleNodeClick = (nodeId: string) => {
    setSelectedNode(nodeId);
    console.log('Clicked node:', nodeId);
  };

  if (loading) {
    return (
      <div className="explorer-loading">
        <p>Loading process map...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="explorer-error">
        <p>Error: {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="explorer-page">
      <header className="explorer-header">
        <h1>Process Explorer</h1>
        <div className="stats">
          <span>{nodes.length} Activities</span>
          <span>{edges.length} Transitions</span>
        </div>
      </header>

      <main className="explorer-main">
        <ProcessMap 
          nodes={nodes} 
          edges={edges}
          onNodeClick={handleNodeClick}
          height="calc(100vh - 200px)"
        />
      </main>

      {selectedNode && (
        <aside className="node-details">
          <h3>Activity Details</h3>
          <p>Selected: {selectedNode}</p>
          {/* Add more details here */}
        </aside>
      )}
    </div>
  );
};

export default Explorer;
```

---

## OPTION 2: Raw SVG from Backend

### SVG Viewer Component
```typescript
// src/components/SVGViewer/SVGViewer.tsx
import React, { useState, useRef, useCallback } from 'react';

interface SVGViewerProps {
  svg: string;
  height?: string;
}

export const SVGViewer: React.FC<SVGViewerProps> = ({ svg, height = '600px' }) => {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setScale(s => Math.min(Math.max(s * delta, 0.1), 5));
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  }, [position]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return;
    setPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const resetView = useCallback(() => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  }, []);

  return (
    <div className="svg-viewer">
      <div className="svg-controls">
        <button onClick={() => setScale(s => Math.min(s * 1.2, 5))}>+</button>
        <button onClick={() => setScale(s => Math.max(s / 1.2, 0.1))}>-</button>
        <button onClick={resetView}>Reset</button>
        <span>{Math.round(scale * 100)}%</span>
      </div>
      
      <div
        ref={containerRef}
        className="svg-container"
        style={{
          width: '100%',
          height,
          overflow: 'hidden',
          border: '1px solid #ddd',
          cursor: isDragging ? 'grabbing' : 'grab',
          background: '#fafafa'
        }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div
          style={{
            transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.1s'
          }}
          dangerouslySetInnerHTML={{ __html: svg }}
        />
      </div>
    </div>
  );
};

export default SVGViewer;
```

### Usage with SVG
```typescript
// src/pages/Explorer/ExplorerSVG.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import SVGViewer from '../../components/SVGViewer/SVGViewer';
import { visualizationService } from '../../services/visualizationService';

export const ExplorerSVG: React.FC = () => {
  const { datasetId } = useParams<{ datasetId: string }>();
  const [svg, setSvg] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!datasetId) return;
    
    visualizationService.getDFGSvg(datasetId)
      .then(setSvg)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (loading) return <p>Loading...</p>;
  if (!svg) return <p>No visualization available</p>;

  return (
    <div className="explorer-svg">
      <h1>Process Map</h1>
      <SVGViewer svg={svg} height="600px" />
    </div>
  );
};
```

---

## OPTION 3: React Flow (Alternative)

### Install
```bash
npm install reactflow
```

### ReactFlow Process Map
```typescript
// src/components/ReactFlowMap/ReactFlowMap.tsx
import React, { useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface ProcessMapData {
  nodes: Array<{ id: string; label: string; frequency: number }>;
  edges: Array<{ source: string; target: string; value: number }>;
}

export const ReactFlowMap: React.FC<{ data: ProcessMapData }> = ({ data }) => {
  // Transform to ReactFlow format
  const initialNodes: Node[] = data.nodes.map((n, i) => ({
    id: n.id,
    data: { label: `${n.label}\n(${n.frequency})` },
    position: { x: (i % 4) * 200, y: Math.floor(i / 4) * 100 },
    style: {
      background: '#4A90D9',
      color: 'white',
      border: '2px solid #2E5A8C',
      borderRadius: '8px',
      padding: '10px',
      width: 120,
    }
  }));

  const initialEdges: Edge[] = data.edges.map(e => ({
    id: `${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    label: e.value.toString(),
    animated: true,
    style: { strokeWidth: Math.max(1, Math.log(e.value)) }
  }));

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background />
      </ReactFlow>
    </div>
  );
};
```

---

## BACKEND: Ensure Visualization Endpoints Work

### Required Endpoints
```bash
# Test these return valid data:
curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN" | jq .

curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/dfg/svg" \
  -H "Authorization: Bearer $TOKEN" | head -c 500

curl -s "http://localhost:8001/api/v1/visualization/$DATASET_ID/explorer-data" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Expected DFG Response Format
```json
{
  "nodes": [
    { "id": "Create Order", "label": "Create Order", "frequency": 150 },
    { "id": "Review", "label": "Review", "frequency": 120 },
    { "id": "Approve", "label": "Approve", "frequency": 100 }
  ],
  "edges": [
    { "source": "Create Order", "target": "Review", "value": 120 },
    { "source": "Review", "target": "Approve", "value": 100 }
  ],
  "start_activities": { "Create Order": 150 },
  "end_activities": { "Approve": 100 }
}
```

### Backend Visualization Code
```python
# src/api/routes/visualization.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/visualization", tags=["visualization"])

@router.get("/{dataset_id}/dfg")
async def get_dfg(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get DFG as JSON for frontend rendering"""
    dataset = await get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    if dataset.status != "ready":
        raise HTTPException(400, f"Dataset not ready: {dataset.status}")
    
    # Load event log
    log = load_event_log(dataset)
    
    # Discover DFG
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    
    # Get activity frequencies
    from pm4py.statistics.attributes.log.get import get_attribute_values
    activity_freq = get_attribute_values(log, "concept:name")
    
    # Build response
    nodes = []
    for activity, freq in activity_freq.items():
        nodes.append({
            "id": activity,
            "label": activity,
            "frequency": freq
        })
    
    edges = []
    for (source, target), count in dfg.items():
        edges.append({
            "source": source,
            "target": target,
            "value": count
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "start_activities": dict(start_activities),
        "end_activities": dict(end_activities)
    }

@router.get("/{dataset_id}/dfg/svg")
async def get_dfg_svg(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get DFG as SVG image"""
    dataset = await get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    log = load_event_log(dataset)
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    
    from pm4py.visualization.dfg import visualizer as dfg_viz
    
    gviz = dfg_viz.apply(
        dfg,
        activities_count=dict(pm4py.get_attribute_values(log, "concept:name")),
        variant=dfg_viz.Variants.FREQUENCY
    )
    
    svg_bytes = dfg_viz.serialize(gviz)
    return svg_bytes.decode('utf-8')
```

---

## TROUBLESHOOTING

### Graph doesn't render
1. Check `nodes` and `edges` arrays are not empty
2. Check container has explicit height
3. Check browser console for errors
4. Verify Cytoscape is imported correctly

### Nodes overlap / bad layout
```typescript
// Try different layouts
layout: { name: 'dagre', rankDir: 'TB' }  // Top to bottom
layout: { name: 'dagre', rankDir: 'LR' }  // Left to right
layout: { name: 'breadthfirst' }
layout: { name: 'cose' }
```

### SVG doesn't show
1. Check SVG string is valid: `console.log(svg.substring(0, 100))`
2. Check it starts with `<svg` or `<?xml`
3. Try rendering in a simple div first

### Performance with large graphs
```typescript
// Filter low-frequency edges
const filteredEdges = edges.filter(e => e.value > threshold);

// Limit nodes
const topNodes = nodes.sort((a, b) => b.frequency - a.frequency).slice(0, 50);
```

---

## CHECKLIST

- [ ] Cytoscape (or alternative) installed
- [ ] ProcessMap component created
- [ ] Explorer page fetches DFG data
- [ ] Graph renders with nodes and edges
- [ ] Zoom/pan controls work
- [ ] Node click shows details
- [ ] Colors indicate frequency
- [ ] Start/end nodes styled differently
- [ ] Layout is readable (not overlapping)

**When all checked: Visualization is working! 🎉**
