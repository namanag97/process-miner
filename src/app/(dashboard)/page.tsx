'use client';

import { format } from 'date-fns';
import {
    Database,
    FileBox,
    Calendar,
    Activity,
    Upload,
    BookOpen,
} from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { EmptyState } from '@/components/shared/EmptyState';
import Link from 'next/link';

// Placeholder data
const stats = [
    {
        name: 'Data Models',
        value: '0',
        icon: Database,
        description: 'Total models',
    },
    {
        name: 'Total Cases',
        value: '0',
        icon: FileBox,
        description: 'Across all models',
    },
    {
        name: 'Total Events',
        value: '0',
        icon: Activity,
        description: 'Tracked events',
    },
    {
        name: 'Last Upload',
        value: 'Never',
        icon: Calendar,
        description: 'Last activity',
    },
];

const quickActions = [
    {
        title: 'Upload Data',
        description: 'Import your event log files to start analyzing processes',
        icon: Upload,
        href: '/data',
    },
    {
        title: 'View Documentation',
        description: 'Learn how to use ProcessMiner effectively',
        icon: BookOpen,
        href: '/docs',
    },
];

export default function DashboardPage() {
    const today = format(new Date(), 'EEEE, MMMM d, yyyy');

    return (
        <div className="flex flex-col">
            <Header title="Dashboard" />

            <div className="flex-1 space-y-6 p-4 md:p-6">
                {/* Welcome section */}
                <div className="space-y-1">
                    <h2 className="text-2xl font-bold tracking-tight">
                        Welcome back, John
                    </h2>
                    <p className="text-muted-foreground">{today}</p>
                </div>

                {/* Quick stats */}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {stats.map((stat) => (
                        <Card key={stat.name}>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">
                                    {stat.name}
                                </CardTitle>
                                <stat.icon className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stat.value}</div>
                                <p className="text-xs text-muted-foreground">
                                    {stat.description}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                {/* Recent Data Models */}
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Data Models</CardTitle>
                        <CardDescription>
                            Your most recently created and updated data models
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <EmptyState
                            icon={Database}
                            title="No data models yet"
                            description="Upload your first file to get started with process mining."
                            action={{
                                label: 'Upload Data',
                                href: '/data',
                            }}
                        />
                    </CardContent>
                </Card>

                {/* Quick Actions */}
                <div className="space-y-4">
                    <h3 className="text-lg font-medium">Quick Actions</h3>
                    <div className="grid gap-4 sm:grid-cols-2">
                        {quickActions.map((action) => (
                            <Card
                                key={action.title}
                                className="transition-colors hover:bg-accent/50"
                            >
                                <Link href={action.href}>
                                    <CardHeader className="flex flex-row items-start gap-4">
                                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                                            <action.icon className="h-5 w-5 text-primary" />
                                        </div>
                                        <div className="flex-1 space-y-1">
                                            <CardTitle className="text-base">{action.title}</CardTitle>
                                            <CardDescription>{action.description}</CardDescription>
                                        </div>
                                    </CardHeader>
                                </Link>
                            </Card>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
