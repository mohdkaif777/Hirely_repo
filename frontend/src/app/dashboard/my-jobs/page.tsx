"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getMyJobs } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

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

export default function MyJobsPage() {
  const { token } = useAuth();
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
    return <div className="text-center py-10">Loading your jobs...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Posted Jobs</h1>
          <p className="text-muted-foreground">Manage the jobs you have created.</p>
        </div>
        <Link href="/dashboard/post-job" passHref legacyBehavior>
          <Button>
            <Plus className="mr-2 h-4 w-4" /> Post a Job
          </Button>
        </Link>
      </div>

      {error ? (
        <div className="bg-destructive/10 text-destructive p-4 rounded-md">
          {error}
        </div>
      ) : jobs.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <h3 className="text-lg font-semibold mb-2">No jobs posted yet</h3>
            <p className="text-muted-foreground mb-6">Create your first job posting to start finding candidates.</p>
            <Link href="/dashboard/post-job" passHref legacyBehavior>
              <Button variant="outline">Create Job</Button>
            </Link>
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
                <div className="mt-4 pt-4 border-t text-xs text-muted-foreground">
                  Posted on {new Date(job.created_at).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
