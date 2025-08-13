
"use client";

import { CircleIcon } from "@/components/ui/icons";
import { cn } from "@/lib/utils";
import Link from 'next/link';

export type SystemStatus = 'operational' | 'degraded' | 'error';

interface HealthIndicatorProps {
  status: SystemStatus;
}

const statusConfig = {
    operational: { color: "text-green-500", label: "All systems operational. Click to see details." },
    degraded: { color: "text-amber-500", label: "System is experiencing degraded performance. Click to see details." },
    error: { color: "text-red-500", label: "System is experiencing issues. Click to see details." },
}

export function HealthIndicator({ status }: HealthIndicatorProps) {
    const config = statusConfig[status];

    return (
        <Link href="/status" className="flex items-center gap-2" title={config.label}>
            <CircleIcon className={cn("h-3 w-3 fill-current", config.color)} />
            <span className="text-xs text-muted-foreground group-hover:underline">
                System Status
            </span>
        </Link>
    );
}

  