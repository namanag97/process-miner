/**
 * MapDataStep - Step 4: PM4Py column mapping
 * 
 * Maps columns to process mining fields:
 * - Case ID (required)
 * - Activity (required) 
 * - Timestamp (required)
 * - Resource (optional)
 * 
 * Includes AI-powered suggestions based on column names
 */

import React, { useState, useEffect } from 'react';
import { Card, Typography, Select, Space, Alert, Button, Tag, Row, Col } from 'antd';
import {
    UserOutlined,
    FieldTimeOutlined,
    AppstoreOutlined,
    IdcardOutlined,
    BulbOutlined,
    CheckCircleOutlined,
} from '@ant-design/icons';
import { tokens, logAction } from '@/src/shared/design-system';
import { devLog } from '../../../../../shared/ui/DevConsole';
import type { DataPreview, ColumnMapping } from '../../types';

const { Title, Text } = Typography;
const { Option } = Select;

interface MapDataStepProps {
    preview: DataPreview | null;
    mapping: ColumnMapping | null;
    onMappingChange: (mapping: ColumnMapping) => void;
    onNext: () => void;
    onBack: () => void;
}

// Column patterns for AI suggestions
const COLUMN_PATTERNS = {
    case_id: ['case', 'case_id', 'caseid', 'trace', 'trace_id', 'traceid', 'id', 'order', 'order_id', 'ticket', 'request'],
    activity: ['activity', 'action', 'event', 'step', 'task', 'status', 'state', 'operation', 'name', 'type'],
    timestamp: ['timestamp', 'time', 'datetime', 'date', 'created', 'start', 'end', 'ts', 'when'],
    resource: ['resource', 'user', 'agent', 'operator', 'employee', 'assignee', 'handler', 'person', 'actor'],
};

function suggestColumn(columns: string[], patterns: string[]): string | null {
    const lower = columns.map(c => c.toLowerCase());
    for (const pattern of patterns) {
        const match = lower.findIndex(col => col.includes(pattern));
        if (match >= 0) return columns[match];
    }
    return null;
}

export function MapDataStep({ preview, mapping, onMappingChange, onNext, onBack }: MapDataStepProps) {
    const [localMapping, setLocalMapping] = useState<Partial<ColumnMapping>>(mapping || {});
    const [suggestions, setSuggestions] = useState<Record<string, string | null>>({});

    const columnNames = preview?.columns.map(c => c.name) || [];

    // Generate AI suggestions on mount
    useEffect(() => {
        if (columnNames.length > 0) {
            const sugg = {
                case_id: suggestColumn(columnNames, COLUMN_PATTERNS.case_id),
                activity: suggestColumn(columnNames, COLUMN_PATTERNS.activity),
                timestamp: suggestColumn(columnNames, COLUMN_PATTERNS.timestamp),
                resource: suggestColumn(columnNames, COLUMN_PATTERNS.resource),
            };
            setSuggestions(sugg);

            // Auto-apply suggestions if no existing mapping
            if (!mapping) {
                setLocalMapping({
                    case_id_column: sugg.case_id || undefined,
                    activity_column: sugg.activity || undefined,
                    timestamp_column: sugg.timestamp || undefined,
                    resource_column: sugg.resource || undefined,
                });
            }

            // Log to DevConsole
            devLog.info('MapDataStep', 'AI column suggestions generated', sugg);
            logAction('UploadWizard', 'column_suggestions', sugg);
        }
    }, [columnNames.length]);

    const updateField = (field: keyof ColumnMapping, value: string | undefined) => {
        const updated = { ...localMapping, [field]: value };
        setLocalMapping(updated);
        devLog.action('MapDataStep', `Column mapped: ${field} = ${value}`);
    };

    const isComplete = localMapping.case_id_column && localMapping.activity_column && localMapping.timestamp_column;

    const handleNext = () => {
        if (isComplete) {
            onMappingChange(localMapping as ColumnMapping);
            devLog.info('MapDataStep', 'Mapping confirmed', localMapping);
            logAction('UploadWizard', 'mapping_confirmed', localMapping);
            onNext();
        }
    };

    const renderSelect = (
        field: keyof ColumnMapping,
        label: string,
        icon: React.ReactNode,
        required = true
    ) => {
        const value = localMapping[field];
        const suggestion = suggestions[field.replace('_column', '')];
        const isSuggested = value === suggestion;

        return (
            <Card size="small" style={{ marginBottom: tokens.spacing[3] }}>
                <Row align="middle" gutter={16}>
                    <Col span={8}>
                        <Space>
                            {icon}
                            <Text strong>{label}</Text>
                            {required && <Text type="danger">*</Text>}
                        </Space>
                    </Col>
                    <Col span={12}>
                        <Select
                            value={value}
                            onChange={(val) => updateField(field, val)}
                            placeholder={`Select ${label.toLowerCase()}`}
                            style={{ width: '100%' }}
                            allowClear={!required}
                        >
                            {columnNames.map(col => (
                                <Option key={col} value={col}>
                                    {col}
                                    {col === suggestion && (
                                        <Tag color="blue" style={{ marginLeft: 8 }}>
                                            Suggested
                                        </Tag>
                                    )}
                                </Option>
                            ))}
                        </Select>
                    </Col>
                    <Col span={4}>
                        {isSuggested && (
                            <Tag icon={<BulbOutlined />} color="processing">
                                AI Match
                            </Tag>
                        )}
                        {value && !isSuggested && (
                            <Tag icon={<CheckCircleOutlined />} color="success">
                                Set
                            </Tag>
                        )}
                    </Col>
                </Row>
            </Card>
        );
    };

    return (
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: tokens.spacing[6] }}>
                <Title level={3}>Map your data</Title>
                <Text type="secondary">
                    Tell us which columns contain your process mining data.
                    We've auto-detected some suggestions for you.
                </Text>
            </div>

            <Alert
                type="info"
                icon={<BulbOutlined />}
                message="AI Column Suggestions"
                description="We analyzed your column names and suggested likely matches. Review and adjust if needed."
                style={{ marginBottom: tokens.spacing[4] }}
            />

            {renderSelect('case_id_column', 'Case ID', <IdcardOutlined />, true)}
            {renderSelect('activity_column', 'Activity', <AppstoreOutlined />, true)}
            {renderSelect('timestamp_column', 'Timestamp', <FieldTimeOutlined />, true)}
            {renderSelect('resource_column', 'Resource', <UserOutlined />, false)}

            {!isComplete && (
                <Alert
                    type="warning"
                    message="Required fields missing"
                    description="Please map Case ID, Activity, and Timestamp columns to continue."
                    style={{ marginTop: tokens.spacing[4] }}
                />
            )}

            {/* Navigation */}
            <div style={{ marginTop: tokens.spacing[6], display: 'flex', justifyContent: 'flex-end', gap: tokens.spacing[2] }}>
                <Button onClick={onBack}>Back</Button>
                <Button type="primary" onClick={handleNext} disabled={!isComplete}>
                    Start Analysis →
                </Button>
            </div>
        </div>
    );
}
