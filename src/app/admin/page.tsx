'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
    Database,
    Upload,
    GitBranch,
    CheckCircle,
    XCircle,
    Clock,
    HardDrive,
    Activity
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DatabaseStats {
    database_stats: {
        users: number;
        uploads: number;
        mappings: number;
        jobs: number;
        datasets: number;
    };
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

async function fetchStats<T>(endpoint: string): Promise<T> {
    const res = await fetch(`${API_URL}/api/admin/${endpoint}`);
    if (!res.ok) throw new Error(`Failed to fetch ${endpoint}`);
    return res.json();
}

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

export default function AdminPage() {
    const { data: dbStats, isLoading: dbLoading } = useQuery<DatabaseStats>({
        queryKey: ['admin', 'stats'],
        queryFn: () => fetchStats<DatabaseStats>('stats'),
        refetchInterval: 10000, // Refresh every 10s
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

    const isLoading = dbLoading || jobLoading || storageLoading || activityLoading;

    return (
        <div className="container mx-auto py-8 px-4">
            <div className="mb-8">
                <h1 className="text-3xl font-bold">Admin Dashboard</h1>
                <p className="text-muted-foreground">
                    System health and database visibility
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
                <StatCard
                    title="Total Users"
                    value={dbStats?.database_stats.users ?? '-'}
                    description="Registered sessions"
                    icon={Database}
                />
                <StatCard
                    title="Uploads"
                    value={dbStats?.database_stats.uploads ?? '-'}
                    description="Files uploaded"
                    icon={Upload}
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

            {/* Job Statistics */}
            <div className="grid gap-4 md:grid-cols-2 mb-8">
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
                        <div className="space-y-2">
                            {dbStats && Object.entries(dbStats.database_stats).map(([key, value]) => (
                                <div key={key} className="flex justify-between items-center">
                                    <span className="capitalize text-sm">{key}</span>
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
