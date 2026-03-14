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
import { Briefcase, ArrowLeft, Sparkles, Building2, AlignLeft, Tags } from "lucide-react";

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
    job_type: "",
    project_keywords: "",
    number_of_vacancies: "1",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
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
      project_keywords: formData.project_keywords.split(",").map((s) => s.trim()).filter(Boolean),
      number_of_vacancies: parseInt(formData.number_of_vacancies, 10) || 1,
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
    <div className="max-w-3xl mx-auto space-y-6 pt-4 pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" onClick={() => router.back()} className="rounded-full hover:bg-secondary">
          <ArrowLeft className="w-5 h-5 text-muted-foreground" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Post a New Job</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Create an AI-optimized job posting to attract top candidates automatically.
          </p>
        </div>
      </div>

      <Card className="rounded-2xl border-border/50 bg-card/60 backdrop-blur-xl shadow-xl overflow-hidden">
        <div className="h-1.5 w-full bg-gradient-to-r from-primary/80 to-accent-soft/80" />
        <CardHeader className="bg-secondary/10 pb-8 border-b border-border/50">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl">Job Details</CardTitle>
              <CardDescription>
                Provide detailed requirements to help our AI match the best candidates.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-8 p-6 sm:p-8">
            {error && (
              <div className="bg-destructive/10 text-destructive text-sm font-medium p-4 rounded-xl border border-destructive/20 flex items-start gap-3">
                <span className="shrink-0 leading-tight">⚠</span>
                <p>{error}</p>
              </div>
            )}
            
            <div className="space-y-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <Briefcase className="w-4 h-4" /> The Role
              </h3>
              
              <div className="space-y-3">
                <Label htmlFor="title" className="text-foreground font-medium">Job Title <span className="text-destructive">*</span></Label>
                <Input 
                  id="title" 
                  name="title" 
                  placeholder="e.g. Senior Frontend Developer" 
                  value={formData.title} 
                  onChange={handleChange} 
                  required 
                  className="bg-secondary/30 border-border/50 rounded-xl focus-visible:ring-primary/50 transition-all h-12 px-4"
                />
              </div>

              <div className="space-y-3">
                <Label htmlFor="description" className="text-foreground font-medium">Job Description <span className="text-destructive">*</span></Label>
                <Textarea 
                  id="description" 
                  name="description" 
                  placeholder="Describe the responsibilities, requirements, and day-to-day... The more detail, the better the AI can match candidates." 
                  value={formData.description} 
                  onChange={handleChange} 
                  required 
                  className="min-h-[180px] bg-secondary/30 border-border/50 rounded-xl focus-visible:ring-primary/50 transition-all p-4 resize-y" 
                />
              </div>
            </div>

            <div className="w-full h-px bg-border/50" />

            <div className="space-y-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <AlignLeft className="w-4 h-4" /> Requirements
              </h3>
              
              <div className="space-y-3">
                <Label htmlFor="skills_required" className="text-foreground font-medium flex items-baseline gap-2">
                  Skills Required
                  <span className="text-xs font-normal text-muted-foreground">Comma separated</span>
                </Label>
                <Input 
                  id="skills_required" 
                  name="skills_required" 
                  placeholder="React, TypeScript, Next.js, Node.js" 
                  value={formData.skills_required} 
                  onChange={handleChange} 
                  className="bg-secondary/30 border-border/50 rounded-xl focus-visible:ring-primary/50 transition-all h-11 px-4"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <Label htmlFor="experience_required" className="text-foreground font-medium">Experience Required</Label>
                  <Input 
                    id="experience_required" 
                    name="experience_required" 
                    placeholder="e.g. 3-5 years" 
                    value={formData.experience_required} 
                    onChange={handleChange} 
                    className="bg-secondary/30 border-border/50 rounded-xl focus-visible:ring-primary/50 transition-all h-11 px-4"
                  />
                </div>
                <div className="space-y-3">
                  <Label htmlFor="location" className="text-foreground font-medium">Location</Label>
                  <Input 
                    id="location" 
                    name="location" 
                    placeholder="e.g. Remote, San Francisco, CA" 
                    value={formData.location} 
                    onChange={handleChange} 
                    className="bg-secondary/30 border-border/50 rounded-xl focus-visible:ring-primary/50 transition-all h-11 px-4"
                  />
                </div>
              </div>
            </div>

            <div className="w-full h-px bg-border/50" />

            <div className="space-y-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <Tags className="w-4 h-4" /> Logistics
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <Label htmlFor="job_type" className="text-foreground font-medium">Job Type</Label>
                  <div className="relative">
                    <select 
                      id="job_type" 
                      name="job_type" 
                      value={formData.job_type} 
                      onChange={handleChange} 
                      className="w-full appearance-none bg-secondary/30 border border-border/50 rounded-xl text-sm focus:outline-none focus:ring-1 focus:ring-primary/50 transition-all h-11 px-4"
                    >
                      <option value="" className="bg-background">Select...</option>
                      <option value="Full Time" className="bg-background">Full Time</option>
                      <option value="Part Time" className="bg-background">Part Time</option>
                      <option value="Contract" className="bg-background">Contract</option>
                      <option value="Internship" className="bg-background">Internship</option>
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-muted-foreground">
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label htmlFor="salary_range" className="text-foreground font-medium">Salary Range</Label>
                  <Input 
                    id="salary_range" 
                    name="salary_range" 
                    placeholder="e.g. $120k - $150k" 
                    value={formData.salary_range} 
                    onChange={handleChange} 
                    className="bg-secondary/30 border-border/50 rounded-xl focus-visible:ring-primary/50 transition-all h-11 px-4"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-end">
                <div className="space-y-3">
                  <Label htmlFor="project_keywords" className="text-foreground font-medium flex items-baseline gap-2">
                    Project Keywords
                    <span className="text-xs font-normal text-muted-foreground">Comma separated</span>
                  </Label>
                  <Input 
                    id="project_keywords" 
                    name="project_keywords" 
                    placeholder="e-commerce, SaaS, mobile transition" 
                    value={formData.project_keywords} 
                    onChange={handleChange} 
                    className="bg-secondary/30 border-border/50 rounded-xl focus-visible:ring-primary/50 transition-all h-11 px-4"
                  />
                  <p className="text-[10px] text-muted-foreground px-1">Used to rank candidates whose past projects align with yours.</p>
                </div>

                <div className="space-y-3">
                  <Label htmlFor="number_of_vacancies" className="text-foreground font-medium">Number of Vacancies <span className="text-destructive">*</span></Label>
                  <Input 
                    id="number_of_vacancies" 
                    type="number" 
                    min="1" 
                    name="number_of_vacancies" 
                    value={formData.number_of_vacancies} 
                    onChange={handleChange} 
                    required 
                    className="bg-secondary/30 border-border/50 rounded-xl focus-visible:ring-primary/50 transition-all h-11 px-4"
                  />
                </div>
              </div>
            </div>

          </CardContent>
          <CardFooter className="bg-secondary/10 px-6 py-6 sm:px-8 border-t border-border/50 flex justify-end">
            <Button 
              type="submit" 
              disabled={loading} 
              className="w-full sm:w-auto rounded-xl px-10 shadow-md font-medium"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <span className="w-4 h-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin inline-block"></span>
                  Publishing Job...
                </div>
              ) : (
                "Publish Job"
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
