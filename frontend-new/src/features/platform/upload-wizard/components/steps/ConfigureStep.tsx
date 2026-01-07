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

import { useState, useMemo } from 'react';
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
import { devLog } from '../../../../../shared/ui/DevConsole';
import type { DataPreview, ColumnTypeInfo } from '../../types';

const { Text } = Typography;
const { Option } = Select;

interface ConfigureStepProps {
    preview: DataPreview | null;
    isLoading?: boolean;
    onNext: () => void;
    onBack: () => void;
}

const COLUMN_TYPES = ['STRING', 'INTEGER', 'DECIMAL', 'DATETIME', 'BOOLEAN'];

// Consistent color scheme for data types
const TYPE_COLORS: Record<string, string> = {
    STRING: 'default',
    INTEGER: 'blue',
    DECIMAL: 'cyan',
    DATETIME: 'purple',
    BOOLEAN: 'orange',
};

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

export function ConfigureStep({ preview, onNext, onBack }: ConfigureStepProps) {
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
                <div style={{ minWidth: 140 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                        <Tooltip title={col.name}>
                            <span style={{
                                fontWeight: 600,
                                fontSize: 13,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                maxWidth: 110,
                                display: 'inline-block',
                            }}>
                                {col.name}
                            </span>
                        </Tooltip>
                        <Tooltip title={validation?.issues.join(', ') || 'Valid'}>
                            {statusIcon}
                        </Tooltip>
                    </div>
                    <Select
                        size="small"
                        value={currentType}
                        onChange={(val) => updateColumnType(col.name, val)}
                        style={{ width: '100%' }}
                        status={validation?.status === 'error' ? 'error' : undefined}
                    >
                        {COLUMN_TYPES.map(type => (
                            <Option key={type} value={type}>
                                <Tag color={TYPE_COLORS[type] || 'default'} style={{ margin: 0 }}>
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
                            style={{ width: '100%', marginTop: 4 }}
                            placeholder="Date format"
                        >
                            {DATE_FORMATS.map(fmt => (
                                <Option key={fmt} value={fmt}>{fmt}</Option>
                            ))}
                        </Select>
                    )}
                </div>
            ),
            dataIndex: col.name,
            key: col.name,
            width: 160,
            render: (value: unknown) => {
                const isEmpty = value === '' || value === null || value === undefined;
                const displayValue = isEmpty ? '(empty)' : String(value);
                return (
                    <Tooltip title={displayValue} mouseEnterDelay={0.5}>
                        <span
                            style={{
                                maxWidth: 140,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                display: 'inline-block',
                                color: isEmpty ? tokens.colors.neutral[400] : undefined,
                            }}
                        >
                            {displayValue}
                        </span>
                    </Tooltip>
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
        <div style={{ width: '100%', maxWidth: '100%', overflow: 'hidden' }}>
            {/* Validation summary - show at top if there are issues */}
            {(hasErrors || hasWarnings) && (
                <Alert
                    type={hasErrors ? 'error' : 'warning'}
                    showIcon
                    message={hasErrors ? 'Data validation issues detected' : 'Data quality warnings'}
                    description={
                        <span>
                            {validationSummary.errors > 0 && `${validationSummary.errors} column(s) with errors. `}
                            {validationSummary.warnings > 0 && `${validationSummary.warnings} column(s) with warnings. `}
                            Review the highlighted columns below.
                        </span>
                    }
                    style={{ marginBottom: tokens.spacing[4] }}
                />
            )}

            <div style={{ display: 'flex', gap: tokens.spacing[4], maxWidth: '100%', overflow: 'hidden' }}>
                {/* Main preview area */}
                <div style={{ flex: 1, minWidth: 0, maxWidth: 'calc(100% - 240px)' }}>
                    <Card
                        title={
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span>Data Preview</span>
                                <Text type="secondary" style={{ fontWeight: 'normal', fontSize: 12 }}>
                                    {preview.rows.length} of {preview.total_rows.toLocaleString()} rows
                                </Text>
                            </div>
                        }
                        size="small"
                        styles={{ body: { padding: 0, overflow: 'hidden' } }}
                    >
                        <div style={{
                            overflowX: 'auto',
                            overflowY: 'hidden',
                            maxWidth: '100%',
                        }}>
                            <Table
                                columns={tableColumns}
                                dataSource={tableData}
                                pagination={false}
                                scroll={{ x: tableColumns.length * 160 }}
                                size="small"
                                bordered
                            />
                        </div>
                        <div style={{
                            padding: `${tokens.spacing[2]} ${tokens.spacing[4]}`,
                            borderTop: `1px solid ${tokens.colors.neutral[200]}`,
                            display: 'flex',
                            justifyContent: 'flex-end',
                            gap: tokens.spacing[4],
                        }}>
                            <Badge status="success" text={`${validationSummary.valid} valid`} />
                            {validationSummary.warnings > 0 && (
                                <Badge status="warning" text={`${validationSummary.warnings} warnings`} />
                            )}
                            {validationSummary.errors > 0 && (
                                <Badge status="error" text={`${validationSummary.errors} errors`} />
                            )}
                        </div>
                    </Card>
                </div>

                {/* Configuration panel */}
                <Card
                    title={
                        <Space>
                            <SettingOutlined />
                            Settings
                        </Space>
                    }
                    size="small"
                    style={{ width: 220, flexShrink: 0 }}
                >
                    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                        <Checkbox
                            checked={hasHeader}
                            onChange={(e) => setHasHeader(e.target.checked)}
                        >
                            Has header row
                        </Checkbox>

                        <div>
                            <Text type="secondary" style={{ display: 'block', marginBottom: 4, fontSize: 12 }}>
                                Separator
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
                            <Text type="secondary" style={{ display: 'block', marginBottom: 4, fontSize: 12 }}>
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
