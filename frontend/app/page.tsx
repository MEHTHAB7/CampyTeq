"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function Home() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
        const timer = setTimeout(() => {
          window.location.href = "/login";
        }, 800);
        return () => clearTimeout(timer);
      }
    }
  }, [user, isLoading, router]);

  return (
    <div className="flex h-screen w-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4 text-center px-4">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
        <div className="space-y-1">
          <p className="text-sm font-semibold text-white">CampyTeq Ecosystem</p>
          <p className="text-xs text-muted-foreground">Directing to institutional portal...</p>
        </div>
        {!isLoading && !user && (
          <a
            href="/login"
            className="mt-2 inline-flex items-center justify-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all"
          >
            Go to Sign In
          </a>
        )}
      </div>
    </div>
  );
}
