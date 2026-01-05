/**
 * GraphVisualization Component
 * 
 * Wrapper for CytoscapeCanvas with showcase-appropriate sizing and controls.
 */

import { CytoscapeCanvas, type ProcessGraphData } from '../../../explorer/components/CytoscapeCanvas';
import { Card, Empty } from 'antd';

interface GraphVisualizationProps {
    data: ProcessGraphData;
    height?: number;
}

export function GraphVisualization({ data, height = 400 }: GraphVisualizationProps) {
    if (!data || !data.nodes || data.nodes.length === 0) {
        return (
            <Card>
                <Empty description="No graph data available" />
            </Card>
        );
    }

    return (
        <div style={{ height, border: '1px solid #f0f0f0', borderRadius: 8, overflow: 'hidden' }}>
            <CytoscapeCanvas
                data={data}
                layout="dagre"
                showLabels
                colorByFrequency
            />
        </div>
    );
}

export default GraphVisualization;
