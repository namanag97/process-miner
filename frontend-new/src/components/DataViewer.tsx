/**
 * DataViewer - Database inspection panel for DevConsole
 * 
 * Browse tables and records directly in the browser.
 * Only works in development mode.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Select, Table, Button, Space, Tag, Spin, Alert, Input, Typography } from 'antd';
import { ReloadOutlined, DatabaseOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface RecordsResponse {
    table: string;
    total: number;
    limit: number;
    offset: number;
    columns: string[];
    records: Record<string, unknown>[];
}

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';

export function DataViewer() {
    const [tables, setTables] = useState<string[]>([]);
    const [selectedTable, setSelectedTable] = useState<string>('');
    const [data, setData] = useState<RecordsResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [searchText, setSearchText] = useState('');

    // Fetch table list
    const fetchTables = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/v1/dev/data/tables`);
            if (!res.ok) throw new Error('Failed to fetch tables');
            const tableList = await res.json();
            setTables(tableList);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tables');
        }
    }, []);

    // Fetch records for selected table
    const fetchRecords = useCallback(async (table: string, offset = 0) => {
        if (!table) return;

        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE}/api/v1/dev/data/records/${table}?limit=50&offset=${offset}`);
            if (!res.ok) throw new Error('Failed to fetch records');
            const result: RecordsResponse = await res.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load records');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTables();
    }, [fetchTables]);

    useEffect(() => {
        if (selectedTable) {
            fetchRecords(selectedTable);
        }
    }, [selectedTable, fetchRecords]);

    // Generate table columns dynamically
    const columns = data?.columns.map(col => ({
        title: col,
        dataIndex: col,
        key: col,
        ellipsis: true,
        width: col === 'id' ? 100 : col.includes('_at') ? 180 : undefined,
        render: (value: unknown) => {
            if (value === null || value === undefined) {
                return <Text type="secondary" italic>null</Text>;
            }
            if (typeof value === 'object') {
                return <Text code style={{ fontSize: 10 }}>{JSON.stringify(value).slice(0, 50)}...</Text>;
            }
            if (typeof value === 'boolean') {
                return <Tag color={value ? 'green' : 'red'}>{value ? 'true' : 'false'}</Tag>;
            }
            return String(value);
        },
    })) || [];

    // Filter records by search text
    const filteredRecords = searchText && data?.records
        ? data.records.filter(record =>
            Object.values(record).some(v =>
                String(v).toLowerCase().includes(searchText.toLowerCase())
            )
        )
        : data?.records || [];

    return (
        <div style={{ padding: 12, height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Controls */}
            <div style={{ display: 'flex', gap: 12, marginBottom: 12, alignItems: 'center' }}>
                <DatabaseOutlined style={{ fontSize: 16, color: '#1890ff' }} />
                <Select
                    placeholder="Select table..."
                    style={{ width: 220 }}
                    value={selectedTable || undefined}
                    onChange={setSelectedTable}
                    showSearch
                    options={tables.map(t => ({
                        value: t,
                        label: t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
                    }))}
                />
                {selectedTable && (
                    <>
                        <Input.Search
                            placeholder="Filter records..."
                            style={{ width: 200 }}
                            allowClear
                            onSearch={setSearchText}
                            onChange={e => !e.target.value && setSearchText('')}
                        />
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={() => fetchRecords(selectedTable)}
                            loading={loading}
                        >
                            Refresh
                        </Button>
                        {data && (
                            <Tag color="blue">{data.total} total records</Tag>
                        )}
                    </>
                )}
            </div>

            {/* Error */}
            {error && (
                <Alert
                    message={error}
                    type="error"
                    closable
                    style={{ marginBottom: 12 }}
                    onClose={() => setError(null)}
                />
            )}

            {/* Table */}
            {!selectedTable ? (
                <div style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#888',
                }}>
                    <Space direction="vertical" align="center">
                        <DatabaseOutlined style={{ fontSize: 32 }} />
                        <Text type="secondary">Select a table to view records</Text>
                    </Space>
                </div>
            ) : loading ? (
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Spin size="large" />
                </div>
            ) : (
                <Table
                    dataSource={filteredRecords}
                    columns={columns}
                    size="small"
                    rowKey={(record) => record.id as string || JSON.stringify(record)}
                    pagination={{
                        pageSize: 20,
                        showSizeChanger: false,
                        showTotal: (total) => `${total} records`,
                    }}
                    scroll={{ x: 'max-content', y: 'calc(50vh - 220px)' }}
                    style={{ flex: 1 }}
                />
            )}
        </div>
    );
}

export default DataViewer;
