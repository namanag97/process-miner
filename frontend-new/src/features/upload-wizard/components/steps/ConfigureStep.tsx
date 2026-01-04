/**
 * ConfigureStep - Step 3: Auto column mapping + data preview
 * 
 * Celonis-style features:
 * - Column headers with type dropdowns
 * - Date format picker for datetime columns
 * - Data preview table with validation
 * - Pre-import validation with error indicators
 * - Table configuration panel
 */

import React, { useState, useMemo } from 'react';
import {
    Card,
    Typography,
    Table,
    Select,
    Space,
    Checkbox,
    Button,
    Tooltip,
    Tag,
    Badge,
    Alert,
} from 'antd';
import {
    SettingOutlined,
    WarningOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
} from '@ant-design/icons';
import { tokens, logAction } from '@lumina/design-system';
import { devLog } from '../../../../components/DevConsole';
import type { DataPreview, ColumnTypeInfo } from '../../types';

const { Title, Text } = Typography;
const { Option } = Select;

interface ConfigureStepProps {
    preview: DataPreview | null;
    isLoading?: boolean;
    onNext: () => void;
    onBack: () => void;
}

const COLUMN_TYPES = ['STRING', 'INTEGER', 'DECIMAL', 'DATETIME', 'BOOLEAN'];

const DATE_FORMATS = [
    'yyyy-MM-dd HH:mm:ss',
    'yyyy-MM-dd',
    'MM/dd/yyyy HH:mm',
    'MM/dd/yyyy',
    'dd/MM/yyyy',
    'dd.MM.yyyy',
];

interface ColumnValidation {
    status: 'valid' | 'warning' | 'error';
    issues: string[];
    emptyCount: number;
    invalidCount: number;
}

// Validate column data based on type
function validateColumn(col: ColumnTypeInfo, rows: Record<string, unknown>[]): ColumnValidation {
    const values = rows.map(r => r[col.name]);
    const emptyCount = values.filter(v => v === '' || v === null || v === undefined).length;
    const issues: string[] = [];
    let invalidCount = 0;

    // Check empty values
    const emptyPercent = (emptyCount / values.length) * 100;
    if (emptyPercent > 50) {
        issues.push(`${emptyPercent.toFixed(0)}% empty values`);
    } else if (emptyPercent > 0) {
        issues.push(`${emptyCount} empty value${emptyCount > 1 ? 's' : ''}`);
    }

    // Type-specific validation
    if (col.detected_type === 'DATETIME') {
        // Check for datetime parsing issues
        const nonEmpty = values.filter(v => v && v !== '');
        const dateRegex = /^\d{1,4}[-\/\.]\d{1,2}[-\/\.]\d{1,4}/;
        invalidCount = nonEmpty.filter(v => !dateRegex.test(String(v))).length;
        if (invalidCount > 0) {
            issues.push(`${invalidCount} invalid date format${invalidCount > 1 ? 's' : ''}`);
        }
    }

    if (col.detected_type === 'INTEGER' || col.detected_type === 'DECIMAL') {
        const nonEmpty = values.filter(v => v && v !== '');
        invalidCount = nonEmpty.filter(v => isNaN(Number(String(v).replace(',', '')))).length;
        if (invalidCount > 0) {
            issues.push(`${invalidCount} non-numeric value${invalidCount > 1 ? 's' : ''}`);
        }
    }

    // Determine status
    let status: 'valid' | 'warning' | 'error' = 'valid';
    if (invalidCount > 0) status = 'error';
    else if (emptyPercent > 20) status = 'warning';

    return { status, issues, emptyCount, invalidCount };
}

export function ConfigureStep({ preview, isLoading, onNext, onBack }: ConfigureStepProps) {
    const [hasHeader, setHasHeader] = useState(true);
    const [fieldSeparator, setFieldSeparator] = useState(',');
    const [columnTypes, setColumnTypes] = useState<Record<string, string>>({});
    const [dateFormats, setDateFormats] = useState<Record<string, string>>({});

    // Pre-import validation
    const validations = useMemo(() => {
        if (!preview) return {};
        const result: Record<string, ColumnValidation> = {};
        for (const col of preview.columns) {
            result[col.name] = validateColumn(col, preview.rows);
        }
        return result;
    }, [preview]);

    // Summary stats
    const validationSummary = useMemo(() => {
        const vals = Object.values(validations);
        return {
            total: vals.length,
            valid: vals.filter(v => v.status === 'valid').length,
            warnings: vals.filter(v => v.status === 'warning').length,
            errors: vals.filter(v => v.status === 'error').length,
        };
    }, [validations]);

    if (!preview) {
        return (
            <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
                <Text type="secondary">Loading preview...</Text>
            </div>
        );
    }

    const updateColumnType = (columnName: string, type: string) => {
        setColumnTypes(prev => ({ ...prev, [columnName]: type }));
        devLog.action('ConfigureStep', `Column type changed: ${columnName} → ${type}`);
    };

    const updateDateFormat = (columnName: string, format: string) => {
        setDateFormats(prev => ({ ...prev, [columnName]: format }));
    };

    const handleNext = () => {
        // Log validation results
        devLog.info('ConfigureStep', 'Pre-import validation results', validationSummary);
        logAction('UploadWizard', 'configure_validated', validationSummary);
        onNext();
    };

    // Table columns with type dropdowns and validation indicators
    const tableColumns = preview.columns.map((col) => {
        const currentType = columnTypes[col.name] || col.detected_type;
        const currentFormat = dateFormats[col.name] || col.date_format;
        const validation = validations[col.name];

        const statusIcon = validation?.status === 'error'
            ? <ExclamationCircleOutlined style={{ color: tokens.colors.error[500] }} />
            : validation?.status === 'warning'
                ? <WarningOutlined style={{ color: tokens.colors.warning[500] }} />
                : <CheckCircleOutlined style={{ color: tokens.colors.success[500] }} />;

        return {
            title: (
                <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <Space>
                        <Text strong>{col.name}</Text>
                        <Tooltip title={validation?.issues.join(', ') || 'Valid'}>
                            {statusIcon}
                        </Tooltip>
                    </Space>
                    <Select
                        size="small"
                        value={currentType}
                        onChange={(val) => updateColumnType(col.name, val)}
                        style={{ width: '100%' }}
                        status={validation?.status === 'error' ? 'error' : undefined}
                    >
                        {COLUMN_TYPES.map(type => (
                            <Option key={type} value={type}>
                                <Tag color={type === 'DATETIME' ? 'blue' : type === 'INTEGER' ? 'green' : 'default'}>
                                    {type}
                                </Tag>
                            </Option>
                        ))}
                    </Select>
                    {currentType === 'DATETIME' && (
                        <Select
                            size="small"
                            value={currentFormat}
                            onChange={(val) => updateDateFormat(col.name, val)}
                            style={{ width: '100%' }}
                            placeholder="Date format"
                        >
                            {DATE_FORMATS.map(fmt => (
                                <Option key={fmt} value={fmt}>{fmt}</Option>
                            ))}
                        </Select>
                    )}
                </Space>
            ),
            dataIndex: col.name,
            key: col.name,
            width: 150,
            render: (value: unknown) => {
                const isEmpty = value === '' || value === null || value === undefined;
                return (
                    <Text
                        ellipsis
                        style={{ maxWidth: 130 }}
                        type={isEmpty ? 'secondary' : undefined}
                    >
                        {isEmpty ? '(empty)' : String(value)}
                    </Text>
                );
            },
        };
    });

    // Table data
    const tableData = preview.rows.map((row, idx) => ({
        key: idx,
        ...row,
    }));

    const hasErrors = validationSummary.errors > 0;
    const hasWarnings = validationSummary.warnings > 0;

    return (
        <div>
            <div style={{ textAlign: 'center', marginBottom: tokens.spacing[6] }}>
                <Title level={3}>Configure</Title>
                <Text type="secondary">
                    Almost there. How should we interpret your data?
                </Text>
            </div>

            {/* Validation summary */}
            {(hasErrors || hasWarnings) && (
                <Alert
                    type={hasErrors ? 'error' : 'warning'}
                    showIcon
                    message={hasErrors ? 'Data validation issues detected' : 'Data quality warnings'}
                    description={
                        <span>
                            {validationSummary.errors > 0 && `${validationSummary.errors} column(s) with errors. `}
                            {validationSummary.warnings > 0 && `${validationSummary.warnings} column(s) with warnings. `}
                            Review the highlighted columns above.
                        </span>
                    }
                    style={{ marginBottom: tokens.spacing[4] }}
                />
            )}

            <div style={{ display: 'flex', gap: tokens.spacing[4] }}>
                {/* Main preview area */}
                <Card style={{ flex: 1, overflow: 'auto' }}>
                    <Table
                        columns={tableColumns}
                        dataSource={tableData}
                        pagination={false}
                        scroll={{ x: true }}
                        size="small"
                        bordered
                    />
                    <div style={{ marginTop: tokens.spacing[2], display: 'flex', justifyContent: 'space-between' }}>
                        <Text type="secondary">
                            Showing {preview.rows.length} of {preview.total_rows} rows
                        </Text>
                        <Space>
                            <Badge status="success" text={`${validationSummary.valid} valid`} />
                            {validationSummary.warnings > 0 && (
                                <Badge status="warning" text={`${validationSummary.warnings} warnings`} />
                            )}
                            {validationSummary.errors > 0 && (
                                <Badge status="error" text={`${validationSummary.errors} errors`} />
                            )}
                        </Space>
                    </div>
                </Card>

                {/* Configuration panel */}
                <Card
                    title={
                        <Space>
                            <SettingOutlined />
                            Table configuration
                        </Space>
                    }
                    size="small"
                    style={{ width: 280 }}
                >
                    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                        <Checkbox
                            checked={hasHeader}
                            onChange={(e) => setHasHeader(e.target.checked)}
                        >
                            Sheet has header row
                        </Checkbox>

                        <div>
                            <Text type="secondary" style={{ display: 'block', marginBottom: 4 }}>
                                Field Separator
                            </Text>
                            <Select
                                value={fieldSeparator}
                                onChange={setFieldSeparator}
                                style={{ width: '100%' }}
                                size="small"
                            >
                                <Option value=",">Comma (,)</Option>
                                <Option value=";">Semicolon (;)</Option>
                                <Option value="\t">Tab</Option>
                                <Option value="|">Pipe (|)</Option>
                            </Select>
                        </div>

                        <div>
                            <Text type="secondary" style={{ display: 'block', marginBottom: 4 }}>
                                Encoding
                            </Text>
                            <Select
                                value={preview.encoding}
                                style={{ width: '100%' }}
                                size="small"
                                disabled
                            >
                                <Option value="utf-8">UTF-8</Option>
                            </Select>
                        </div>
                    </Space>
                </Card>
            </div>

            {/* Navigation buttons */}
            <div style={{ marginTop: tokens.spacing[6], display: 'flex', justifyContent: 'flex-end', gap: tokens.spacing[2] }}>
                <Button onClick={onBack}>Back</Button>
                <Button
                    type="primary"
                    onClick={handleNext}
                    danger={hasErrors}
                >
                    {hasErrors ? 'Continue with Errors →' : 'Next →'}
                </Button>
            </div>
        </div>
    );
}
