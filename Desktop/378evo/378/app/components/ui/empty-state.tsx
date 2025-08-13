
import { Button } from "@/components/ui/button";
import { PlusCircle } from "lucide-react";
import React from "react";

interface EmptyStateProps {
    title: string;
    description: string;
    actionText?: string;
    onAction?: () => void;
    icon?: React.ElementType; // Optional icon component (e.g., from lucide-react)
    children?: React.ReactNode; // Optional content for more complex empty states
}

export function EmptyState({
    title,
    description,
    actionText,
    onAction,
    icon: Icon,
    children,
}: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-12 text-center">
            {Icon && <Icon className="mx-auto h-12 w-12 text-muted-foreground" />}
            <h3 className="mt-2 text-lg font-semibold text-foreground">{title}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
                {description}
            </p>
            {children && <div className="mt-4">{children}</div>}
            {actionText && onAction && (
                <Button onClick={onAction} className="mt-6">
                    <PlusCircle className="mr-2 h-4 w-4" />
                    {actionText}
                </Button>
            )}
        </div>
    );
}
