
"use client";

import { AuthProvider, useAuth } from "@/hooks/use-auth";
import { useState, useEffect } from "react";
import { AuthPage } from "./views/auth-page";
import IntelliAuditDashboard from "./features/3-analysis/components/intelliaudit-dashboard";
import { Loader2Icon } from "./ui/icons";

function AppContent() {
  const { user, loading } = useAuth();
  
  if (loading) {
     return <div className="flex h-screen w-full items-center justify-center"><Loader2Icon className="h-8 w-8 animate-spin" /></div>;
  }

  if (!user) {
    return <AuthPage />;
  }

  return <IntelliAuditDashboard />;
}


export function AppShell() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return <div className="flex h-screen w-full items-center justify-center"><Loader2Icon className="h-8 w-8 animate-spin" /></div>;
  }
  
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
