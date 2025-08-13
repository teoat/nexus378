
"use client";

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/hooks/use-auth';
import { ScaleIcon, Loader2Icon } from '../ui/icons';
import { Separator } from '../ui/separator';
import { isTwoFactorEnabled, verifyTwoFactorToken } from '@/app/actions/2fa.actions';
import { useToast } from '@/hooks/use-toast';
import { createSession } from '@/app/actions/auth.actions';
import { getAuth } from 'firebase/auth';
import ClientOnly from '../client-only';

export function AuthPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const { signUp, signIn, signInWithGoogle, signInWithSSO } = useAuth();
    const [twoFactorStep, setTwoFactorStep] = useState(false);
    const [twoFactorToken, setTwoFactorToken] = useState('');
    const [tempUserId, setTempUserId] = useState<string | null>(null);
    const { toast } = useToast();

    const handleSignIn = async () => {
        setError(null);
        setIsLoading(true);
        try {
            const userCredential = await signIn(email, password);
            const user = userCredential.user;
            const twoFactorIsEnabled = await isTwoFactorEnabled(user.uid);

            if (twoFactorIsEnabled) {
                setTempUserId(user.uid);
                setTwoFactorStep(true);
            } else {
                // If 2FA is not enabled, create session immediately
                const idToken = await user.getIdToken();
                await createSession(idToken);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleVerifyTwoFactor = async () => {
        if (!tempUserId) {
            setError("Session error. Please try logging in again.");
            return;
        }
        setError(null);
        setIsLoading(true);
        try {
            const isValid = await verifyTwoFactorToken(tempUserId, twoFactorToken);
            if (isValid) {
                const auth = getAuth();
                const user = auth.currentUser;
                if(user) {
                    const idToken = await user.getIdToken();
                    await createSession(idToken);
                    // The onAuthStateChanged listener in useAuth will handle the rest
                } else {
                     setError("Could not find authenticated user. Please restart login.");
                }
            } else {
                setError("Invalid 2FA token. Please try again.");
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }

    const handleSignUp = async () => {
        setError(null);
        setIsLoading(true);
        try {
            await signUp(email, password);
            // Session is created automatically by onAuthStateChanged
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };
    
    if (twoFactorStep) {
        return (
             <div className="flex min-h-screen items-center justify-center bg-muted/40">
                 <Card className="w-[400px]">
                     <CardHeader>
                         <CardTitle>Two-Factor Authentication</CardTitle>
                         <CardDescription>Enter the code from your authenticator app.</CardDescription>
                     </CardHeader>
                     <CardContent className="space-y-4">
                         <div className="space-y-2">
                            <Label htmlFor="2fa-token">Verification Code</Label>
                            <Input 
                                id="2fa-token" 
                                type="text" 
                                placeholder="123456" 
                                value={twoFactorToken} 
                                onChange={(e) => setTwoFactorToken(e.target.value)} 
                                maxLength={6}
                            />
                         </div>
                     </CardContent>
                     <CardFooter className="flex-col gap-4">
                        {error && <p className="text-sm text-destructive">{error}</p>}
                        <Button className="w-full" onClick={handleVerifyTwoFactor} disabled={isLoading}>
                             {isLoading && <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />}
                             Verify
                        </Button>
                     </CardFooter>
                 </Card>
            </div>
        )
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-muted/40">
            <Tabs defaultValue="login" className="w-[400px]">
                <div className="flex justify-center mb-6 items-center gap-2">
                    <ScaleIcon className="h-8 w-8 text-primary"/>
                    <h1 className="text-2xl font-bold font-headline">IntelliAudit AI</h1>
                </div>
                <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="login">Login</TabsTrigger>
                    <TabsTrigger value="signup">Sign Up</TabsTrigger>
                </TabsList>
                <TabsContent value="login">
                    <Card>
                        <CardHeader>
                            <CardTitle>Login</CardTitle>
                            <CardDescription>Enter your credentials to access your account.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="login-email">Email</Label>
                                <Input id="login-email" type="email" placeholder="m@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="login-password">Password</Label>
                                <Input id="login-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                            </div>
                        </CardContent>
                        <CardFooter className="flex-col gap-4">
                             {error && <p className="text-sm text-destructive">{error}</p>}
                            <Button className="w-full" onClick={handleSignIn} disabled={isLoading}>
                                {isLoading && <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />}
                                Sign In
                            </Button>
                            <div className="relative w-full">
                                <Separator />
                                <span className="absolute left-1/2 -translate-x-1/2 -top-2.5 bg-background px-2 text-xs text-muted-foreground">OR</span>
                            </div>
                            <ClientOnly>
                                <Button variant="outline" className="w-full" onClick={signInWithGoogle} disabled={isLoading}>Sign In with Google</Button>
                            </ClientOnly>
                             <ClientOnly>
                                <Button variant="outline" className="w-full" onClick={signInWithSSO} disabled={isLoading}>Sign In with SSO</Button>
                             </ClientOnly>
                        </CardFooter>
                    </Card>
                </TabsContent>
                <TabsContent value="signup">
                     <Card>
                        <CardHeader>
                            <CardTitle>Sign Up</CardTitle>
                            <CardDescription>Create a new account to get started.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="signup-email">Email</Label>
                                <Input id="signup-email" type="email" placeholder="m@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="signup-password">Password</Label>
                                <Input id="signup-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                            </div>
                        </CardContent>
                        <CardFooter className="flex-col gap-4">
                            {error && <p className="text-sm text-destructive">{error}</p>}
                            <Button className="w-full" onClick={handleSignUp} disabled={isLoading}>
                               {isLoading && <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />}
                               Create Account
                            </Button>
                             <ClientOnly>
                                <Button variant="outline" className="w-full" onClick={signInWithGoogle} disabled={isLoading}>Sign Up with Google</Button>
                             </ClientOnly>
                        </CardFooter>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
