"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function DashboardNav() {
  const { user, logout } = useAuth();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/");
  }

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="text-2xl font-bold tracking-tight">
              Hire<span className="text-primary">AI</span>
            </Link>
            {user?.role === "job_seeker" && (
              <div className="hidden sm:flex items-center gap-4">
                <Link href="/dashboard/jobs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Browse Jobs
                </Link>
                <Link href="/dashboard/inbox" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Messages
                </Link>
                <Link href="/dashboard/profile" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  My Profile
                </Link>
              </div>
            )}
            {user?.role === "recruiter" && (
              <div className="hidden sm:flex items-center gap-4">
                <Link href="/dashboard/my-jobs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  My Jobs
                </Link>
                <Link href="/dashboard/post-job" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Post Job
                </Link>
                <Link href="/dashboard/inbox" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Messages
                </Link>
                <Link href="/dashboard/company" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Company Profile
                </Link>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden sm:inline">
              {user?.email}
            </span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              Log out
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
