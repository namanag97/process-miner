'use client';

import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export default function SettingsPage() {
    return (
        <div className="flex flex-col">
            <Header title="Settings" />

            <div className="flex-1 p-4 md:p-6">
                <Tabs defaultValue="profile" className="space-y-6">
                    <TabsList>
                        <TabsTrigger value="profile">Profile</TabsTrigger>
                        <TabsTrigger value="account">Account</TabsTrigger>
                        <TabsTrigger value="notifications" className="gap-2">
                            Notifications
                            <Badge variant="secondary" className="ml-1.5 text-xs">
                                Soon
                            </Badge>
                        </TabsTrigger>
                    </TabsList>

                    {/* Profile Tab */}
                    <TabsContent value="profile" className="space-y-6">
                        <div>
                            <h3 className="text-lg font-medium">Profile</h3>
                            <p className="text-sm text-muted-foreground">
                                Manage your public profile information.
                            </p>
                        </div>
                        <Separator />

                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base">Personal Information</CardTitle>
                                <CardDescription>
                                    Update your personal details here.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {/* Avatar */}
                                <div className="flex items-center gap-4">
                                    <Avatar className="h-20 w-20">
                                        <AvatarImage src="/avatar.jpg" alt="User avatar" />
                                        <AvatarFallback className="text-lg">JD</AvatarFallback>
                                    </Avatar>
                                    <div className="space-y-2">
                                        <Button variant="outline" size="sm">
                                            Change Avatar
                                        </Button>
                                        <p className="text-xs text-muted-foreground">
                                            JPG, GIF or PNG. Max size of 2MB.
                                        </p>
                                    </div>
                                </div>

                                {/* Name */}
                                <div className="grid gap-2">
                                    <Label htmlFor="name">Name</Label>
                                    <Input
                                        id="name"
                                        placeholder="Your name"
                                        defaultValue="John Doe"
                                    />
                                </div>

                                {/* Email */}
                                <div className="grid gap-2">
                                    <Label htmlFor="email">Email</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="your@email.com"
                                        defaultValue="john@example.com"
                                        disabled
                                    />
                                    <p className="text-xs text-muted-foreground">
                                        Email cannot be changed.
                                    </p>
                                </div>

                                <Button>Save Changes</Button>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Account Tab */}
                    <TabsContent value="account" className="space-y-6">
                        <div>
                            <h3 className="text-lg font-medium">Account</h3>
                            <p className="text-sm text-muted-foreground">
                                Manage your account settings and preferences.
                            </p>
                        </div>
                        <Separator />

                        <Card className="border-destructive/50">
                            <CardHeader>
                                <CardTitle className="text-base text-destructive">
                                    Danger Zone
                                </CardTitle>
                                <CardDescription>
                                    Irreversible and destructive actions.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                                    <div>
                                        <p className="font-medium">Delete Account</p>
                                        <p className="text-sm text-muted-foreground">
                                            Permanently delete your account and all associated data.
                                        </p>
                                    </div>
                                    <Button variant="destructive">Delete Account</Button>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Notifications Tab */}
                    <TabsContent value="notifications" className="space-y-6">
                        <div>
                            <h3 className="text-lg font-medium">Notifications</h3>
                            <p className="text-sm text-muted-foreground">
                                Configure how you receive notifications.
                            </p>
                        </div>
                        <Separator />

                        <Card>
                            <CardContent className="py-8">
                                <div className="text-center text-muted-foreground">
                                    <p>Notification settings coming soon.</p>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}
