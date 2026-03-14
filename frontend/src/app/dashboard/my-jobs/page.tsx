"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getMyJobs } from "@/lib/api";
import { JobCard, type Job } from "@/components/ui/JobCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/button";
import { Plus, FolderOpen } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function MyJobsPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchJobs() {
      if (!token) return;
      try {
        const data = await getMyJobs(token);
        setJobs(data.jobs || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load your jobs");
      } finally {
        setLoading(false);
      }
    }
    fetchJobs();
  }, [token]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
        <p className="text-sm text-muted-foreground font-medium animate-pulse">Loading your postings...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Posted Jobs</h1>
          <p className="text-muted-foreground mt-1 text-sm sm:text-base">Manage the jobs you have created and review candidates.</p>
        </div>
        <Link href="/dashboard/post-job" passHref legacyBehavior>
          <Button className="rounded-xl shadow-md">
            <Plus className="mr-2 h-4 w-4" /> Post a Job
          </Button>
        </Link>
      </div>

      {error ? (
        <div className="bg-destructive/10 text-destructive p-4 rounded-2xl border border-destructive/20 backdrop-blur-sm text-sm font-medium">
          {error}
        </div>
      ) : jobs.length === 0 ? (
        <EmptyState 
          icon={FolderOpen}
          title="No jobs posted yet"
          description="Create your first job posting to start finding top candidates powered by AI matching."
          action={
            <Link href="/dashboard/post-job" passHref legacyBehavior>
              <Button variant="outline" className="rounded-xl mt-4">Create Job Posting</Button>
            </Link>
          }
        />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => (
            <JobCard 
              key={job.id} 
              job={job} 
              onAction={() => router.push(`/dashboard/inbox`)}
              actionLabel="View Messages"
            />
          ))}
        </div>
      )}
    </div>
  );
}
