'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    Database,
    Upload,
    GitBranch,
    CheckCircle,
    XCircle,
    Clock,
    HardDrive,
    Activity,
    Table,
    FileText,
    AlertTriangle,
    Building,
    FolderOpen,
    Users,
    ChevronLeft,
    ChevronRight,
    RefreshCw,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// =============================================================================
// Types
// =============================================================================

interface DatabaseStats {
    database_stats: Record<string, number>;
    timestamp: string;
}

interface JobStats {
    job_statistics: {
        queued: number;
        processing: number;
        completed: number;
        failed: number;
    };
    total: number;
    success_rate: number;
    timestamp: string;
}

interface StorageStats {
    storage: {
        total_bytes: number;
        total_mb: number;
        total_rows_processed: number;
    };
    timestamp: string;
}

interface RecentActivity {
    period_hours: number;
    recent_uploads: Array<{
        id: string;
        filename: string;
        status: string;
        row_count: number;
        created_at: string;
    }>;
    recent_jobs: Array<{
        id: string;
        status: string;
        progress: number;
        dataset_id: string | null;
        error: string | null;
        created_at: string;
    }>;
    timestamp: string;
}

interface TableData {
    table: string;
    data: Record<string, unknown>[];
    pagination: {
        total: number;
        limit: number;
        offset: number;
        has_more: boolean;
    };
    timestamp: string;
}

interface AuditLog {
    id: string;
    user_id: string | null;
    entity_type: string;
    entity_id: string | null;
    action: string;
    details: Record<string, unknown> | null;
    ip_address: string | null;
    request_path: string | null;
    created_at: string;
}

interface InsightSummary {
    summary: {
        total_insights: number;
        by_type: Record<string, number>;
        by_severity: Record<string, number>;
        critical_count: number;
        unacknowledged_count: number;
    };
    timestamp: string;
}

interface Insight {
    id: string;
    dataset_id: string;
    insight_type: string;
    severity: string;
    severity_score: number;
    title: string;
    description: string;
    affected_activity: string | null;
    affected_case_count: number;
    is_acknowledged: boolean;
    created_at: string;
}

// =============================================================================
// API Functions
// =============================================================================

async function fetchStats<T>(endpoint: string): Promise<T> {
    const res = await fetch(`${API_URL}/api/admin/${endpoint}`);
    if (!res.ok) throw new Error(`Failed to fetch ${endpoint}`);
    return res.json();
}

async function fetchTableData(table: string, limit = 20, offset = 0): Promise<TableData> {
    const res = await fetch(`${API_URL}/api/admin/tables/${table}?limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error(`Failed to fetch table ${table}`);
    return res.json();
}

async function fetchAuditLogs(limit = 50): Promise<AuditLog[]> {
    const res = await fetch(`${API_URL}/api/admin/logs?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
}

async function fetchInsights(limit = 50): Promise<Insight[]> {
    const res = await fetch(`${API_URL}/api/admin/insights?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch insights');
    return res.json();
}

async function acknowledgeInsight(insightId: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/admin/insights/${insightId}/acknowledge`, {
        method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to acknowledge insight');
}

// =============================================================================
// Components
// =============================================================================

function StatCard({
    title,
    value,
    description,
    icon: Icon
}: {
    title: string;
    value: string | number;
    description?: string;
    icon: React.ComponentType<{ className?: string }>;
}) {
    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{value}</div>
                {description && (
                    <p className="text-xs text-muted-foreground">{description}</p>
                )}
            </CardContent>
        </Card>
    );
}

function JobStatusBadge({ status }: { status: string }) {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
        completed: 'default',
        processing: 'secondary',
        queued: 'outline',
        failed: 'destructive',
    };
    return <Badge variant={variants[status] || 'outline'}>{status}</Badge>;
}

function SeverityBadge({ severity }: { severity: string }) {
    const colors: Record<string, string> = {
        critical: 'bg-red-500 text-white',
        high: 'bg-orange-500 text-white',
        medium: 'bg-yellow-500 text-black',
        low: 'bg-green-500 text-white',
    };
    return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${colors[severity] || 'bg-gray-500 text-white'}`}>
            {severity}
        </span>
    );
}

function ActionBadge({ action }: { action: string }) {
    const colors: Record<string, string> = {
        create: 'bg-green-100 text-green-800',
        update: 'bg-blue-100 text-blue-800',
        delete: 'bg-red-100 text-red-800',
        view: 'bg-gray-100 text-gray-800',
        process: 'bg-purple-100 text-purple-800',
    };
    return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${colors[action] || 'bg-gray-100 text-gray-800'}`}>
            {action}
        </span>
    );
}

function DataTable({ tableName }: { tableName: string }) {
    const [offset, setOffset] = useState(0);
    const limit = 10;

    const { data, isLoading, refetch } = useQuery({
        queryKey: ['table', tableName, offset],
        queryFn: () => fetchTableData(tableName, limit, offset),
    });

    if (isLoading) return <div className="p-4">Loading...</div>;
    if (!data) return <div className="p-4">No data</div>;

    const columns = data.data.length > 0 ? Object.keys(data.data[0]) : [];

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <p className="text-sm text-muted-foreground">
                    Showing {offset + 1}-{Math.min(offset + limit, data.pagination.total)} of {data.pagination.total}
                </p>
                <Button variant="outline" size="sm" onClick={() => refetch()}>
                    <RefreshCw className="h-4 w-4 mr-1" />
                    Refresh
                </Button>
            </div>

            <div className="border rounded-lg overflow-auto max-h-[400px]">
                <table className="w-full text-sm">
                    <thead className="bg-muted sticky top-0">
                        <tr>
                            {columns.map(col => (
                                <th key={col} className="px-3 py-2 text-left font-medium">
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.data.map((row, i) => (
                            <tr key={i} className="border-t hover:bg-muted/50">
                                {columns.map(col => (
                                    <td key={col} className="px-3 py-2 truncate max-w-[200px]">
                                        {typeof row[col] === 'object'
                                            ? JSON.stringify(row[col])
                                            : String(row[col] ?? '')}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="flex justify-between items-center">
                <Button
                    variant="outline"
                    size="sm"
                    disabled={offset === 0}
                    onClick={() => setOffset(Math.max(0, offset - limit))}
                >
                    <ChevronLeft className="h-4 w-4" /> Previous
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    disabled={!data.pagination.has_more}
                    onClick={() => setOffset(offset + limit)}
                >
                    Next <ChevronRight className="h-4 w-4" />
                </Button>
            </div>
        </div>
    );
}

// =============================================================================
// Main Component
// =============================================================================

export default function AdminPage() {
    const [selectedTable, setSelectedTable] = useState<string>('organizations');
    const queryClient = useQueryClient();

    // Stats queries
    const { data: dbStats, isLoading: dbLoading } = useQuery<DatabaseStats>({
        queryKey: ['admin', 'stats'],
        queryFn: () => fetchStats<DatabaseStats>('stats'),
        refetchInterval: 10000,
    });

    const { data: jobStats, isLoading: jobLoading } = useQuery<JobStats>({
        queryKey: ['admin', 'job-stats'],
        queryFn: () => fetchStats<JobStats>('job-stats'),
        refetchInterval: 5000,
    });

    const { data: storageStats, isLoading: storageLoading } = useQuery<StorageStats>({
        queryKey: ['admin', 'storage'],
        queryFn: () => fetchStats<StorageStats>('storage'),
        refetchInterval: 30000,
    });

    const { data: activity, isLoading: activityLoading } = useQuery<RecentActivity>({
        queryKey: ['admin', 'recent-activity'],
        queryFn: () => fetchStats<RecentActivity>('recent-activity?hours=24'),
        refetchInterval: 15000,
    });

    // Audit logs query
    const { data: auditLogs } = useQuery({
        queryKey: ['admin', 'logs'],
        queryFn: () => fetchAuditLogs(50),
        refetchInterval: 10000,
    });

    // Insights queries
    const { data: insightSummary } = useQuery<InsightSummary>({
        queryKey: ['admin', 'insights-summary'],
        queryFn: () => fetchStats<InsightSummary>('insights/summary'),
        refetchInterval: 30000,
    });

    const { data: insights } = useQuery({
        queryKey: ['admin', 'insights'],
        queryFn: () => fetchInsights(50),
        refetchInterval: 30000,
    });

    // Acknowledge mutation
    const acknowledgeMutation = useMutation({
        mutationFn: acknowledgeInsight,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'insights'] });
            queryClient.invalidateQueries({ queryKey: ['admin', 'insights-summary'] });
        },
    });

    const isLoading = dbLoading || jobLoading || storageLoading || activityLoading;

    const tableOptions = [
        { name: 'organizations', icon: Building },
        { name: 'users', icon: Users },
        { name: 'processes', icon: FolderOpen },
        { name: 'uploads', icon: Upload },
        { name: 'mappings', icon: GitBranch },
        { name: 'jobs', icon: Activity },
        { name: 'datasets', icon: Database },
        { name: 'audit_logs', icon: FileText },
        { name: 'insights', icon: AlertTriangle },
    ];

    return (
        <div className="container mx-auto py-8 px-4">
            <div className="mb-8">
                <h1 className="text-3xl font-bold">Admin Dashboard</h1>
                <p className="text-muted-foreground">
                    System health, database visibility, and audit logs
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
                <StatCard
                    title="Organizations"
                    value={dbStats?.database_stats.organizations ?? '-'}
                    description="Total orgs"
                    icon={Building}
                />
                <StatCard
                    title="Processes"
                    value={dbStats?.database_stats.processes ?? '-'}
                    description="Business processes"
                    icon={FolderOpen}
                />
                <StatCard
                    title="Datasets"
                    value={dbStats?.database_stats.datasets ?? '-'}
                    description="Processed analyses"
                    icon={GitBranch}
                />
                <StatCard
                    title="Storage Used"
                    value={storageStats ? `${storageStats.storage.total_mb} MB` : '-'}
                    description={`${storageStats?.storage.total_rows_processed?.toLocaleString() ?? 0} rows processed`}
                    icon={HardDrive}
                />
            </div>

            {/* Main Tabs */}
            <Tabs defaultValue="overview" className="space-y-6">
                <TabsList className="grid w-full grid-cols-4 lg:w-[500px]">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="tables">Data Tables</TabsTrigger>
                    <TabsTrigger value="logs">Audit Logs</TabsTrigger>
                    <TabsTrigger value="insights">Insights</TabsTrigger>
                </TabsList>

                {/* Overview Tab */}
                <TabsContent value="overview" className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-2">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Activity className="h-5 w-5" />
                                    Job Statistics
                                </CardTitle>
                                <CardDescription>
                                    Success rate: {jobStats?.success_rate.toFixed(1) ?? 0}%
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="flex items-center gap-2">
                                        <Clock className="h-4 w-4 text-muted-foreground" />
                                        <span>Queued: {jobStats?.job_statistics.queued ?? 0}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Activity className="h-4 w-4 text-blue-500" />
                                        <span>Processing: {jobStats?.job_statistics.processing ?? 0}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <CheckCircle className="h-4 w-4 text-green-500" />
                                        <span>Completed: {jobStats?.job_statistics.completed ?? 0}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <XCircle className="h-4 w-4 text-red-500" />
                                        <span>Failed: {jobStats?.job_statistics.failed ?? 0}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Entity Counts</CardTitle>
                                <CardDescription>Database table statistics</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-2 max-h-[200px] overflow-y-auto">
                                    {dbStats && Object.entries(dbStats.database_stats).map(([key, value]) => (
                                        <div key={key} className="flex justify-between items-center">
                                            <span className="capitalize text-sm">{key.replace('_', ' ')}</span>
                                            <Badge variant="secondary">{value}</Badge>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Recent Activity */}
                    <div className="grid gap-4 md:grid-cols-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Recent Uploads (24h)</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {activity?.recent_uploads.length === 0 ? (
                                    <p className="text-sm text-muted-foreground">No recent uploads</p>
                                ) : (
                                    <div className="space-y-3">
                                        {activity?.recent_uploads.map((upload) => (
                                            <div key={upload.id} className="flex justify-between items-center text-sm">
                                                <div>
                                                    <p className="font-medium truncate max-w-[200px]">{upload.filename}</p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {upload.row_count.toLocaleString()} rows
                                                    </p>
                                                </div>
                                                <Badge variant={upload.status === 'uploaded' ? 'default' : 'secondary'}>
                                                    {upload.status}
                                                </Badge>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Recent Jobs (24h)</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {activity?.recent_jobs.length === 0 ? (
                                    <p className="text-sm text-muted-foreground">No recent jobs</p>
                                ) : (
                                    <div className="space-y-3">
                                        {activity?.recent_jobs.map((job) => (
                                            <div key={job.id} className="flex justify-between items-center text-sm">
                                                <div>
                                                    <p className="font-mono text-xs truncate max-w-[150px]">{job.id}</p>
                                                    {job.error && (
                                                        <p className="text-xs text-red-500 truncate max-w-[200px]">{job.error}</p>
                                                    )}
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    {job.status === 'processing' && (
                                                        <span className="text-xs">{job.progress}%</span>
                                                    )}
                                                    <JobStatusBadge status={job.status} />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Data Tables Tab */}
                <TabsContent value="tables" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Table className="h-5 w-5" />
                                Browse Database Tables
                            </CardTitle>
                            <CardDescription>
                                View and explore data in all tables
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-2 mb-6">
                                {tableOptions.map(({ name, icon: Icon }) => (
                                    <Button
                                        key={name}
                                        variant={selectedTable === name ? 'default' : 'outline'}
                                        size="sm"
                                        onClick={() => setSelectedTable(name)}
                                        className="capitalize"
                                    >
                                        <Icon className="h-4 w-4 mr-1" />
                                        {name.replace('_', ' ')}
                                        {dbStats?.database_stats[name] !== undefined && (
                                            <Badge variant="secondary" className="ml-2">
                                                {dbStats.database_stats[name]}
                                            </Badge>
                                        )}
                                    </Button>
                                ))}
                            </div>

                            <DataTable tableName={selectedTable} />
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Audit Logs Tab */}
                <TabsContent value="logs" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="h-5 w-5" />
                                Audit Logs
                            </CardTitle>
                            <CardDescription>
                                Complete activity trail of all user actions
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {!auditLogs || auditLogs.length === 0 ? (
                                <p className="text-sm text-muted-foreground">No audit logs yet</p>
                            ) : (
                                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                                    {auditLogs.map((log) => (
                                        <div key={log.id} className="border rounded-lg p-3 space-y-2">
                                            <div className="flex justify-between items-start">
                                                <div className="flex items-center gap-2">
                                                    <ActionBadge action={log.action} />
                                                    <span className="font-medium capitalize">
                                                        {log.entity_type}
                                                    </span>
                                                </div>
                                                <span className="text-xs text-muted-foreground">
                                                    {new Date(log.created_at).toLocaleString()}
                                                </span>
                                            </div>
                                            {log.entity_id && (
                                                <p className="text-xs font-mono text-muted-foreground">
                                                    ID: {log.entity_id}
                                                </p>
                                            )}
                                            {log.details && Object.keys(log.details).length > 0 && (
                                                <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                                                    {JSON.stringify(log.details, null, 2)}
                                                </pre>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Insights Tab */}
                <TabsContent value="insights" className="space-y-6">
                    {/* Insights Summary */}
                    <div className="grid gap-4 md:grid-cols-4">
                        <StatCard
                            title="Total Insights"
                            value={insightSummary?.summary.total_insights ?? 0}
                            icon={AlertTriangle}
                        />
                        <StatCard
                            title="Critical"
                            value={insightSummary?.summary.critical_count ?? 0}
                            description="Require immediate attention"
                            icon={XCircle}
                        />
                        <StatCard
                            title="Unacknowledged"
                            value={insightSummary?.summary.unacknowledged_count ?? 0}
                            description="Not yet reviewed"
                            icon={Clock}
                        />
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium">By Type</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-1">
                                    {insightSummary?.summary.by_type && Object.entries(insightSummary.summary.by_type).map(([type, count]) => (
                                        <div key={type} className="flex justify-between text-sm">
                                            <span className="capitalize">{type}</span>
                                            <Badge variant="outline">{count}</Badge>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Insights List */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <AlertTriangle className="h-5 w-5" />
                                All Insights
                            </CardTitle>
                            <CardDescription>
                                Extracted findings from process analysis
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {!insights || insights.length === 0 ? (
                                <p className="text-sm text-muted-foreground">
                                    No insights yet. Process some data to generate insights.
                                </p>
                            ) : (
                                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                                    {insights.map((insight) => (
                                        <div key={insight.id} className="border rounded-lg p-4 space-y-2">
                                            <div className="flex justify-between items-start">
                                                <div className="space-y-1">
                                                    <div className="flex items-center gap-2">
                                                        <SeverityBadge severity={insight.severity} />
                                                        <Badge variant="outline" className="capitalize">
                                                            {insight.insight_type}
                                                        </Badge>
                                                        {insight.is_acknowledged && (
                                                            <Badge variant="secondary">
                                                                <CheckCircle className="h-3 w-3 mr-1" />
                                                                Acknowledged
                                                            </Badge>
                                                        )}
                                                    </div>
                                                    <h4 className="font-medium">{insight.title}</h4>
                                                </div>
                                                {!insight.is_acknowledged && (
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => acknowledgeMutation.mutate(insight.id)}
                                                        disabled={acknowledgeMutation.isPending}
                                                    >
                                                        Acknowledge
                                                    </Button>
                                                )}
                                            </div>
                                            <p className="text-sm text-muted-foreground">
                                                {insight.description}
                                            </p>
                                            {insight.affected_activity && (
                                                <p className="text-xs">
                                                    Activity: <span className="font-mono">{insight.affected_activity}</span>
                                                </p>
                                            )}
                                            <p className="text-xs text-muted-foreground">
                                                Affected cases: {insight.affected_case_count} •
                                                Score: {(insight.severity_score * 100).toFixed(0)}%
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            {/* Footer */}
            <div className="mt-8 text-center text-sm text-muted-foreground">
                {isLoading ? (
                    <span>Loading...</span>
                ) : (
                    <span>
                        Last updated: {new Date().toLocaleTimeString()} • Auto-refreshing
                    </span>
                )}
            </div>
        </div>
    );
}
