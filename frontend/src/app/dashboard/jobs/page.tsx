"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { listJobs } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { startConversation } from "@/lib/api";
import { useRouter } from "next/navigation";

type Job = {
  id: string;
  title: string;
  description: string;
  skills_required: string[];
  salary_range: string;
  experience_required: string;
  location: string;
  created_at: string;
};

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
    return <div className="text-center py-10">Loading jobs...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Browse Jobs</h1>
        <p className="text-muted-foreground">Find the best matching roles for you.</p>
      </div>

      {error ? (
        <div className="bg-destructive/10 text-destructive p-4 rounded-md">
          {error}
        </div>
      ) : jobs.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center">
            <p className="text-muted-foreground">No jobs available right now.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => (
            <Card key={job.id} className="flex flex-col">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="line-clamp-2">{job.title}</CardTitle>
                </div>
                <CardDescription>{job.location || "Remote"} • {job.experience_required || "Entry Level"}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1">
                <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
                  {job.description}
                </p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {job.skills_required.map((skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
                {job.salary_range && (
                  <p className="text-sm font-medium">
                    Salary: {job.salary_range}
                  </p>
                )}
              </CardContent>
              <CardFooter>
                <Button 
                  className="w-full" 
                  onClick={() => handleMessageRecruiter(job.id)}
                >
                  Message Recruiter
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
