"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";
import { Navbar } from "@/components/Navbar";
import { useEffect } from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    } else if (!loading && user && !user.role) {
      router.push("/role-selection");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
          <p className="text-sm text-muted-foreground font-medium animate-pulse">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (!user || !user.role) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Background Gradient Elements for Premium Feel */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-40">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] rounded-full bg-accent-soft/5 blur-[100px]" />
      </div>

      <Sidebar />
      <div className="flex-1 flex flex-col relative z-10 overflow-hidden shadow-2xl shadow-black/50 sm:rounded-l-2xl border-l border-border bg-background/50 backdrop-blur-3xl m-0 sm:my-2 sm:mr-2">
        <Navbar />
        <main className="flex-1 overflow-y-auto scrollbar-hide">
          <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
