"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { createJob } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function PostJobPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    skills_required: "",
    salary_range: "",
    experience_required: "",
    location: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    setError("");

    const payload = {
      ...formData,
      skills_required: formData.skills_required.split(",").map((s) => s.trim()).filter(Boolean),
    };

    try {
      await createJob(token, payload);
      router.push("/dashboard/my-jobs");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create job, verify you have created a Company Profile first.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="outline" onClick={() => router.back()}>
          Back
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">Post a New Job</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Job Details</CardTitle>
          <CardDescription>
            Fill out the form below to create a new job posting.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="title">Job Title *</Label>
              <Input id="title" name="title" placeholder="e.g. Senior Frontend Developer" value={formData.title} onChange={handleChange} required />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Job Description *</Label>
              <Textarea id="description" name="description" placeholder="Describe the responsibilities and requirements..." value={formData.description} onChange={handleChange} required className="min-h-[150px]" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="skills_required">Skills Required (comma separated)</Label>
              <Input id="skills_required" name="skills_required" placeholder="React, TypeScript, Next.js" value={formData.skills_required} onChange={handleChange} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="experience_required">Experience Required</Label>
                <Input id="experience_required" name="experience_required" placeholder="e.g. 3-5 years" value={formData.experience_required} onChange={handleChange} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input id="location" name="location" placeholder="e.g. Remote, New York" value={formData.location} onChange={handleChange} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="salary_range">Salary Range</Label>
              <Input id="salary_range" name="salary_range" placeholder="e.g. $120k - $150k" value={formData.salary_range} onChange={handleChange} />
            </div>

          </CardContent>
          <CardFooter>
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Publishing Job..." : "Publish Job"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
