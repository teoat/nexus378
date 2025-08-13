
"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { functions } from '@/lib/firebase';
import { httpsCallable } from 'firebase/functions';
import { Loader2Icon } from '@/components/ui/icons';

// This is a simple UI component to interact with the Claude API.
export function ClaudeChatInterface() {
    const [prompt, setPrompt] = useState('');
    const [response, setResponse] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSendPrompt = async () => {
        if (!prompt) return;
        setIsLoading(true);
        setError('');
        setResponse('');

        try {
            // This function call is what invokes your secure Cloud Function.
            const askClaude = httpsCallable(functions, 'askClaude');
            const result: any = await askClaude({ prompt });
            setResponse(result.data.response);
        } catch (err: any) {
            console.error(err);
            setError(`Error: ${err.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="w-full max-w-2xl">
            <CardHeader>
                <CardTitle>Chat with Claude</CardTitle>
                <CardDescription>
                    This interface uses a secure Firebase Cloud Function to interact with the Anthropic API.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2">
                    <Textarea
                        placeholder="Enter your prompt for Claude..."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        rows={4}
                    />
                </div>
                {response && (
                    <div className="p-4 border bg-muted rounded-md">
                        <p className="text-sm whitespace-pre-wrap">{response}</p>
                    </div>
                )}
                {error && (
                    <div className="p-4 border bg-destructive/10 text-destructive rounded-md">
                        <p className="text-sm font-bold">An Error Occurred</p>
                        <p className="text-xs">{error}</p>
                    </div>
                )}
            </CardContent>
            <CardFooter>
                <Button onClick={handleSendPrompt} disabled={isLoading}>
                    {isLoading && <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />}
                    Send Prompt
                </Button>
            </CardFooter>
        </Card>
    );
}
