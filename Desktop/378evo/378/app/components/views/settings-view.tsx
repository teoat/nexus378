
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ThemeToggle } from "@/components/theme-toggle";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState, useCallback, useEffect } from "react";
import { useAuditStore, TableDensity, ColumnSizing } from "@/hooks/use-audit-store";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { Loader2Icon, ShieldCheckIcon, CheckCircle2Icon } from "@/components/ui/icons";
import { saveWebhookUrl, getWebhookUrl } from "@/app/actions/webhook.actions";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { AchievementsView } from "./achievements-view";
import { usePlaidLink } from "react-plaid-link";
import { getQuickBooksAuthUrl, createPlaidLinkToken, exchangePublicToken } from "@/lib/financial-integrations";
import { generateTwoFactorSecret, verifyAndEnableTwoFactor, disableTwoFactor } from "@/app/actions/2fa.actions";
import { app } from '@/lib/firebase';
import { getFirestore, doc, onSnapshot } from "firebase/firestore";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import Image from "next/image";
import ClientOnly from "../client-only";

const db = getFirestore(app);


function PlaidIntegration() {
    const { user } = useAuth();
    const { toast } = useToast();
    const [linkToken, setLinkToken] = useState<string | null>(null);

    const onSuccess = useCallback(async (public_token: string) => {
        try {
            await exchangePublicToken(public_token);
            toast({ title: "Plaid connection successful!" });
        } catch (error) {
            toast({ variant: "destructive", title: "Plaid Error", description: "Could not exchange public token." });
        }
    }, [toast]);

    const { open, ready } = usePlaidLink({
        token: linkToken,
        onSuccess,
    });

    useEffect(() => {
        async function getLinkToken() {
            if (user) {
                try {
                    const token = await createPlaidLinkToken(user.uid);
                    setLinkToken(token);
                } catch (error) {
                    toast({ variant: "destructive", title: "Plaid Error", description: "Could not fetch Plaid link token." });
                }
            }
        }
        getLinkToken();
    }, [user, toast]);
    
    return (
         <Button onClick={() => open()} disabled={!ready}>
            Connect Bank via Plaid
        </Button>
    )
}

function TwoFactorAuthManager() {
    const { toast } = useToast();
    const [twoFactorStatus, setTwoFactorStatus] = useState<'enabled' | 'disabled' | 'pending' | 'loading'>('loading');
    const [qrCode, setQrCode] = useState<string | null>(null);
    const [manualSecret, setManualSecret] = useState<string | null>(null);
    const [verificationToken, setVerificationToken] = useState('');
    const { user } = useAuth();

    const checkStatus = useCallback(async () => {
        if (!user) return;
        setTwoFactorStatus('loading');
        const userDocRef = doc(db, "users", user.uid);
        const unsubscribe = onSnapshot(userDocRef, (doc) => {
            const userData = doc.data();
            setTwoFactorStatus(userData?.twoFactorEnabled ? 'enabled' : 'disabled');
        });
        return () => unsubscribe();
    }, [user]);
    
    useEffect(() => {
        checkStatus();
    }, [checkStatus]);

    const handleGenerateSecret = async () => {
        setTwoFactorStatus('loading');
        const result = await generateTwoFactorSecret();
        if (result.success && result.qrCodeDataUrl && result.secret) {
            setQrCode(result.qrCodeDataUrl);
            setManualSecret(result.secret);
            setTwoFactorStatus('pending');
        } else {
            toast({ variant: 'destructive', title: 'Error', description: result.error || 'Failed to generate 2FA secret.' });
            setTwoFactorStatus('disabled');
        }
    };

    const handleVerifyToken = async () => {
        setTwoFactorStatus('loading');
        const result = await verifyAndEnableTwoFactor(verificationToken);
        if (result.success) {
            toast({ title: '2FA Enabled!', description: 'Two-factor authentication has been successfully enabled.' });
            setQrCode(null);
            setManualSecret(null);
            setVerificationToken('');
            setTwoFactorStatus('enabled');
        } else {
            toast({ variant: 'destructive', title: 'Verification Failed', description: result.error || 'That code was not valid. Please try again.' });
            setTwoFactorStatus('pending');
        }
    };
    
    const handleDisable = async () => {
        setTwoFactorStatus('loading');
        const result = await disableTwoFactor();
        if (result.success) {
            toast({ title: '2FA Disabled', description: 'Two-factor authentication has been disabled.' });
            setTwoFactorStatus('disabled');
        } else {
             toast({ variant: 'destructive', title: 'Error', description: result.error || 'Failed to disable 2FA.' });
             setTwoFactorStatus('enabled');
        }
    }

    if (twoFactorStatus === 'loading') {
        return <div className="flex items-center justify-center h-24"><Loader2Icon className="animate-spin" /></div>;
    }

    if (twoFactorStatus === 'enabled') {
        return (
            <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-center gap-3">
                    <ShieldCheckIcon className="h-6 w-6 text-green-600 dark:text-green-500"/>
                    <div>
                        <p className="font-semibold text-green-800 dark:text-green-300">2FA is Enabled</p>
                        <p className="text-xs text-green-700 dark:text-green-400">Your account is protected with two-factor authentication.</p>
                    </div>
                </div>
                <AlertDialog>
                    <AlertDialogTrigger asChild>
                        <Button variant="destructive">Disable</Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                        <AlertDialogHeader>
                            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                            <AlertDialogDescription>
                                Disabling two-factor authentication will make your account less secure.
                            </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction onClick={handleDisable}>Confirm Disable</AlertDialogAction>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialog>
            </div>
        )
    }

    if (twoFactorStatus === 'pending') {
        return (
            <div className="space-y-4">
                <p className="text-sm text-muted-foreground">Scan the QR code with your authenticator app (like Google Authenticator or Authy), then enter the 6-digit code below to complete setup.</p>
                <div className="flex flex-col md:flex-row items-center gap-6">
                    {qrCode && <Image src={qrCode} alt="2FA QR Code" width={200} height={200} className="rounded-lg bg-white p-2" />}
                    <div className="space-y-4 flex-1">
                        <p className="text-xs text-muted-foreground">Can't scan the code? You can manually enter this secret into your app:</p>
                        <p className="font-mono bg-muted p-2 rounded-md text-center">{manualSecret}</p>
                         <div className="space-y-2">
                            <Label htmlFor="2fa-token">Verification Code</Label>
                            <Input 
                                id="2fa-token" 
                                placeholder="123456"
                                defaultValue={verificationToken}
                                value={verificationToken}
                                onChange={(e) => setVerificationToken(e.target.value)}
                            />
                        </div>
                        <div className="flex gap-2">
                             <Button onClick={handleVerifyToken}>Verify & Enable</Button>
                             <Button variant="ghost" onClick={() => setTwoFactorStatus('disabled')}>Cancel</Button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Add an extra layer of security to your account by requiring a second verification step when you sign in.</p>
            <Button onClick={handleGenerateSecret}>Enable 2-Factor Authentication</Button>
        </div>
    )
}


export function SettingsView() {
    const { user } = useAuth();
    const { toast } = useToast();
    
    const {
        tableDensity,
        columnSizing,
        setTableDensity,
        setColumnSizing,
    } = useAuditStore();

    const [webhookUrl, setWebhookUrl] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [quickbooksConnected, setQuickbooksConnected] = useState(false);


    const fetchSettings = useCallback(async () => {
        if (!user) return;
        setIsLoading(true);
        try {
            const url = await getWebhookUrl(user.uid);
            setWebhookUrl(url || '');
            
            const savedDensity = localStorage.getItem('intelliaudit-tableDensity') as TableDensity | null;
            if (savedDensity) setTableDensity(savedDensity);

            const savedSizing = localStorage.getItem('intelliaudit-columnSizing') as ColumnSizing | null;
            if (savedSizing) setColumnSizing(savedSizing);

            const userDocRef = doc(db, "users", user.uid);
            const unsubscribe = onSnapshot(userDocRef, (doc) => {
                 setQuickbooksConnected(doc.data()?.quickbooksConnected === true);
            });
            return () => unsubscribe();

        } catch (error) {
            console.error("Failed to fetch settings:", error);
            toast({ variant: "destructive", title: "Could not load settings."});
        } finally {
            setIsLoading(false);
        }
    }, [user, toast, setTableDensity, setColumnSizing]);

    useEffect(() => {
        fetchSettings();
    }, [fetchSettings]);

    useEffect(() => {
        const query = new URLSearchParams(window.location.search);
        if (query.get('quickbooks') === 'success') {
            toast({
                title: "QuickBooks Connected!",
                description: "Your QuickBooks account has been successfully linked.",
            });
        }
    }, [toast]);
    
    const handleSaveSettings = useCallback(async () => {
        if (!user) return;
        setIsLoading(true);
        try {
            await saveWebhookUrl(user.uid, webhookUrl);
            localStorage.setItem('intelliaudit-tableDensity', tableDensity);
            localStorage.setItem('intelliaudit-columnSizing', columnSizing);
            toast({ title: "Settings saved successfully." });
        } catch (error) {
            console.error("Failed to save settings:", error);
            toast({ variant: "destructive", title: "Failed to save settings." });
        } finally {
            setIsLoading(false);
        }
    }, [user, webhookUrl, toast, tableDensity, columnSizing]);

    const handleConnectQuickBooks = async () => {
        if (!user) return;
        try {
            const authUrl = await getQuickBooksAuthUrl(user.uid);
            window.location.href = authUrl;
        } catch (error) {
            toast({ variant: "destructive", title: "QuickBooks Connection Failed", description: "Could not initiate the connection." });
        }
    };

    if (isLoading) {
        return (
            <div className="container mx-auto max-w-4xl space-y-6 py-8 flex justify-center">
                <Loader2Icon className="h-8 w-8 animate-spin" />
            </div>
        )
    }

    return (
        <div className="container mx-auto max-w-4xl space-y-6 py-8">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">Settings</h1>
                 <Button onClick={handleSaveSettings} disabled={isLoading}>
                    {isLoading && <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />}
                    Save All Settings
                 </Button>
            </div>
            
            <Tabs defaultValue="preferences">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="preferences">Preferences</TabsTrigger>
                    <TabsTrigger value="security">Security</TabsTrigger>
                    <TabsTrigger value="integrations">Integrations</TabsTrigger>
                    <TabsTrigger value="achievements">Achievements</TabsTrigger>
                </TabsList>
                <TabsContent value="preferences" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Display Preferences</CardTitle>
                            <CardDescription>Customize the look and feel of the application.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <Label>Theme</Label>
                                <ThemeToggle />
                            </div>
                             <div className="flex items-center justify-between">
                                <Label>Table Density</Label>
                                <Select value={tableDensity} onValueChange={(v) => setTableDensity(v as TableDensity)}>
                                    <SelectTrigger className="w-[180px]">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="comfortable">Comfortable</SelectItem>
                                        <SelectItem value="default">Default</SelectItem>
                                        <SelectItem value="compact">Compact</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="flex items-center justify-between">
                                <Label>Table Column Sizing</Label>
                                <Select value={columnSizing} onValueChange={(v) => setColumnSizing(v as ColumnSizing)}>
                                    <SelectTrigger className="w-[180px]">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="auto">Fit to Container</SelectItem>
                                        <SelectItem value="fitContent">Fit to Content</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                 <TabsContent value="security" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Security Settings</CardTitle>
                            <CardDescription>Manage your account's security settings.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <TwoFactorAuthManager />
                        </CardContent>
                    </Card>
                 </TabsContent>

                 <TabsContent value="integrations" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Integrations</CardTitle>
                            <CardDescription>Connect IntelliAudit to other services.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                             <div className="space-y-2">
                                <Label htmlFor="webhook-url">Webhook URL</Label>
                                <p className="text-sm text-muted-foreground">
                                    Get notified of important events (e.g., high-risk anomalies) by providing a webhook URL for services like Zapier.
                                </p>
                                <div className="flex items-center gap-2">
                                     <Input 
                                        id="webhook-url"
                                        placeholder="https://your-service.com/webhook"
                                        value={webhookUrl}
                                        onChange={(e) => setWebhookUrl(e.target.value)}
                                        disabled={isLoading}
                                     />
                                </div>
                            </div>
                             <div className="border-t pt-4">
                                <h4 className="font-semibold text-sm mb-2">Financial Software</h4>
                                <div className="flex gap-2">
                                    <ClientOnly>
                                        <PlaidIntegration />
                                    </ClientOnly>
                                    {quickbooksConnected ? (
                                        <Button variant="outline" disabled>
                                            <CheckCircle2Icon className="mr-2 h-4 w-4 text-green-500" />
                                            QuickBooks Connected
                                        </Button>
                                    ) : (
                                        <Button onClick={handleConnectQuickBooks}>
                                            Connect to QuickBooks
                                        </Button>
                                    )}
                                </div>
                             </div>
                        </CardContent>
                    </Card>
                 </TabsContent>

                 <TabsContent value="achievements" className="mt-6">
                     <Card>
                        <CardHeader>
                            <CardTitle>Achievements</CardTitle>
                            <CardDescription>Track your progress and milestones within the app.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <AchievementsView />
                        </CardContent>
                     </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}

    