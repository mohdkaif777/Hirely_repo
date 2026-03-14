"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { listJobs, startConversation } from "@/lib/api";
import { JobCard, type Job } from "@/components/ui/JobCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { SearchIcon } from "lucide-react";
import { useRouter } from "next/navigation";

export default function BrowseJobsPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadJobs() {
      try {
        const data = await listJobs();
        setJobs(data.jobs || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load jobs");
      } finally {
        setLoading(false);
      }
    }
    loadJobs();
  }, []);

  async function handleMessageRecruiter(jobId: string) {
    if (!token) return;
    try {
      await startConversation(token, jobId);
      router.push("/dashboard/inbox");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start conversation");
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
        <p className="text-sm text-muted-foreground font-medium animate-pulse">Loading amazing jobs...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Browse Jobs</h1>
        <p className="text-muted-foreground mt-1 text-sm sm:text-base">Find the perfect roles matching your skills and experience.</p>
      </div>

      {error ? (
        <div className="bg-destructive/10 text-destructive p-4 rounded-2xl border border-destructive/20 backdrop-blur-sm text-sm font-medium">
          {error}
        </div>
      ) : jobs.length === 0 ? (
        <EmptyState 
          icon={SearchIcon}
          title="No jobs found"
          description="There are currently no job postings available on the platform. Please check back later."
        />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => (
            <JobCard 
              key={job.id} 
              job={job} 
              onAction={handleMessageRecruiter}
              actionLabel="Message Recruiter"
            />
          ))}
        </div>
      )}
    </div>
  );
}
