
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BotIcon } from "@/components/ui/icons";
import { ClaudeChatInterface } from "./claude-chat-interface";

export default function FrenlyCommandCenter() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
            <BotIcon />
            Frenly Command Center
        </CardTitle>
        <CardDescription>
          This is the central hub for managing and interacting with the Frenly AI Maintenance Agent.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex justify-center">
        <ClaudeChatInterface />
      </CardContent>
    </Card>
  );
}
