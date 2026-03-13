"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.push("/login");
    } else if (!user.role) {
      router.push("/role-selection");
    } else if (user.role === "job_seeker") {
      router.push("/dashboard/jobs");
    } else if (user.role === "recruiter") {
      router.push("/dashboard/my-jobs");
    }
  }, [user, loading, router]);

  return (
    <div className="flex items-center justify-center py-20">
      <p className="text-muted-foreground">Redirecting...</p>
    </div>
  );
}
