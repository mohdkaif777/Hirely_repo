"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getJobSeekerProfile, createJobSeekerProfile, updateJobSeekerProfile } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Edit2, MapPin, Briefcase, Mail } from "lucide-react";

export default function JobSeekerProfilePage() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [hasProfile, setHasProfile] = useState(false);
  const [isEditing, setIsEditing] = useState(true);

  const [formData, setFormData] = useState({
    name: "",
    age: "",
    location: "",
    skills: "",
    experience: "",
    preferred_roles: "",
    expected_salary: "",
    resume_url: "",
    education: "",
    projects: [] as Array<{ title: string; description: string; tech_stack: string; project_url: string }>,
    job_type_preference: "",
  });

  useEffect(() => {
    async function loadProfile() {
      if (!token) return;
      try {
        const data = await getJobSeekerProfile(token);
        if (data && data.name) {
          setHasProfile(true);
          setIsEditing(false); // Display the card instantly because data exists
          setFormData({
            name: data.name || "",
            age: data.age?.toString() || "",
            location: data.location || "",
            skills: (data.skills || []).join(", "),
            experience: data.experience || "",
            preferred_roles: (data.preferred_roles || []).join(", "),
            expected_salary: data.expected_salary || "",
            resume_url: data.resume_url || "",
            education: data.education || "",
            projects: data.projects || [],
            job_type_preference: data.job_type_preference || "",
          });
        }
      } catch (err: any) {
        if (!err.message?.includes("404")) {
          setError("Failed to load profile");
        }
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, [token]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setSaving(true);
    setError("");
    setSuccess("");

    const payload = {
      ...formData,
      age: formData.age ? parseInt(formData.age, 10) : undefined,
      skills: formData.skills.split(",").map((s) => s.trim()).filter(Boolean),
      preferred_roles: formData.preferred_roles.split(",").map((s) => s.trim()).filter(Boolean),
      projects: formData.projects.map(p => ({
        title: p.title.trim(),
        description: p.description.trim(),
        tech_stack: p.tech_stack.split(",").map(t => t.trim()).filter(Boolean),
        project_url: p.project_url.trim(),
      })).filter(p => p.title || p.description),
    };

    try {
      if (hasProfile) {
        await updateJobSeekerProfile(token, payload);
      } else {
        await createJobSeekerProfile(token, payload);
        setHasProfile(true);
      }
      setSuccess("Profile saved successfully!");
      setIsEditing(false); // Automatically switch back to view mode on success
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center py-10">Loading profile...</div>;
  }

  // Visual Mode (Decent UI)
  if (!isEditing && hasProfile) {
    const skillsArray = formData.skills.split(",").map((s) => s.trim()).filter(Boolean);
    const uniqueSkills = [...new Set(skillsArray)];
    const rolesArray = formData.preferred_roles.split(",").map((s) => s.trim()).filter(Boolean);

    return (
      <div className="max-w-3xl mx-auto">
        <Card className="shadow-sm border-border/50">
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b">
            <div className="space-y-1">
              <CardTitle className="text-2xl font-bold">{formData.name}</CardTitle>
              <CardDescription className="flex items-center gap-2 text-sm text-muted-foreground">
                <Briefcase className="w-4 h-4" /> Professional Candidate
              </CardDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setIsEditing(true)}>
              <Edit2 className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardContent className="pt-6 space-y-6">
            <div className="flex items-center gap-6 text-sm">
              {formData.location && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <MapPin className="w-4 h-4" /> {formData.location}
                </div>
              )}
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold text-sm">Experience Summary</h3>
              <p className="text-muted-foreground text-sm leading-relaxed whitespace-pre-wrap">
                {formData.experience || "No experience listed."}
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Top Skills</h3>
              <div className="flex flex-wrap gap-2">
                {skillsArray.length > 0 ? (
                  uniqueSkills.map((skill: string) => (
                    <Badge key={skill} variant="secondary" className="px-3 py-1 bg-muted">
                      {skill}
                    </Badge>
                  ))
                ) : (
                  <span className="text-muted-foreground text-sm">No skills listed.</span>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold text-sm">Education</h3>
              <p className="text-muted-foreground text-sm leading-relaxed whitespace-pre-wrap">
                {formData.education || "No education listed."}
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Projects</h3>
              {formData.projects.length > 0 ? (
                <div className="space-y-3">
                  {formData.projects.map((proj, idx) => (
                    <div key={idx} className="border rounded p-3 bg-muted/20">
                      <h4 className="font-medium text-sm">{proj.title}</h4>
                      <p className="text-xs text-muted-foreground mt-1">{proj.description}</p>
                      {proj.tech_stack && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {proj.tech_stack.split(",").map((tech, i) => (
                            <Badge key={i} variant="outline" className="text-xs px-1 py-0">
                              {tech.trim()}
                            </Badge>
                          ))}
                        </div>
                      )}
                      {proj.project_url && (
                        <a href={proj.project_url} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline mt-1 block">
                          View Project →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <span className="text-muted-foreground text-sm">No projects listed.</span>
              )}
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold text-sm">Job Type Preference</h3>
              <p className="text-muted-foreground text-sm">{formData.job_type_preference || "Not specified"}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t">
              <div>
                <h3 className="font-semibold text-sm mb-2">Preferred Roles</h3>
                <div className="flex flex-wrap gap-2">
                  {rolesArray.length > 0 ? (
                    rolesArray.map((role) => (
                      <Badge key={role} variant="outline" className="text-primary border-primary/20">
                        {role}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-muted-foreground text-sm">None listed.</span>
                  )}
                </div>
              </div>
              <div className="flex flex-col items-end text-right">
                <h3 className="font-semibold text-sm mb-1">Expected Salary</h3>
                <span className="text-muted-foreground text-sm">
                  {formData.expected_salary || "Not Disclosed"}
                </span>
              </div>
            </div>
          </CardContent>
          {formData.resume_url && (
            <CardFooter className="pt-4 border-t bg-muted/20">
              <a 
                href={formData.resume_url} 
                target="_blank" 
                rel="noreferrer" 
                className="text-sm font-medium text-primary hover:underline flex items-center gap-2"
              >
                View Linked Resume &rarr;
              </a>
            </CardFooter>
          )}
        </Card>
      </div>
    );
  }

  // Form Editing Mode
  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>My Profile</CardTitle>
          <CardDescription>
            Update your personal details and professional experience.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && <div className="text-destructive text-sm font-medium">{error}</div>}
            {success && <div className="text-green-600 text-sm font-medium">{success}</div>}
            
            <div className="space-y-2">
              <Label htmlFor="name">Full Name *</Label>
              <Input id="name" name="name" value={formData.name} onChange={handleChange} required />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input id="age" name="age" type="number" value={formData.age} onChange={handleChange} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input id="location" name="location" value={formData.location} onChange={handleChange} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="skills">Skills (comma separated)</Label>
              <Input id="skills" name="skills" placeholder="React, Python, Design" value={formData.skills} onChange={handleChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="experience">Experience Summary</Label>
              <Textarea id="experience" name="experience" placeholder="Briefly describe your work experience..." value={formData.experience} onChange={handleChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="education">Education</Label>
              <Textarea id="education" name="education" placeholder="Your education background..." value={formData.education} onChange={handleChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="job_type_preference">Job Type Preference</Label>
              <select id="job_type_preference" name="job_type_preference" value={formData.job_type_preference} onChange={handleSelectChange} className="w-full border rounded px-3 py-2 text-sm">
                <option value="">Select...</option>
                <option value="Full Time">Full Time</option>
                <option value="Part Time">Part Time</option>
                <option value="Internship">Internship</option>
                <option value="Remote">Remote</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="preferred_roles">Preferred Roles (comma separated)</Label>
                <Input id="preferred_roles" name="preferred_roles" value={formData.preferred_roles} onChange={handleChange} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="expected_salary">Expected Salary</Label>
                <Input id="expected_salary" name="expected_salary" placeholder="$100k, 50k EUR..." value={formData.expected_salary} onChange={handleChange} />
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label>Projects</Label>
                <Button type="button" variant="outline" size="sm" onClick={() => setFormData(prev => ({
                  ...prev,
                  projects: [...prev.projects, { title: "", description: "", tech_stack: "", project_url: "" }]
                }))}>
                  + Add Project
                </Button>
              </div>
              {formData.projects.map((proj, idx) => (
                <div key={idx} className="border rounded p-3 space-y-2">
                  <div className="flex justify-between items-center">
                    <h4 className="text-sm font-medium">Project {idx + 1}</h4>
                    {formData.projects.length > 1 && (
                      <Button type="button" variant="ghost" size="sm" onClick={() => setFormData(prev => ({
                        ...prev,
                        projects: prev.projects.filter((_, i) => i !== idx)
                      }))}>
                        Remove
                      </Button>
                    )}
                  </div>
                  <Input placeholder="Title" value={proj.title} onChange={e => {
                    const updated = [...formData.projects];
                    updated[idx].title = e.target.value;
                    setFormData(prev => ({ ...prev, projects: updated }));
                  }} />
                  <Textarea placeholder="Description" value={proj.description} onChange={e => {
                    const updated = [...formData.projects];
                    updated[idx].description = e.target.value;
                    setFormData(prev => ({ ...prev, projects: updated }));
                  }} />
                  <Input placeholder="Tech stack (comma separated)" value={proj.tech_stack} onChange={e => {
                    const updated = [...formData.projects];
                    updated[idx].tech_stack = e.target.value;
                    setFormData(prev => ({ ...prev, projects: updated }));
                  }} />
                  <Input placeholder="Project URL (optional)" value={proj.project_url} onChange={e => {
                    const updated = [...formData.projects];
                    updated[idx].project_url = e.target.value;
                    setFormData(prev => ({ ...prev, projects: updated }));
                  }} />
                </div>
              ))}
            </div>

            <div className="space-y-2">
              <Label htmlFor="resume_url">Resume URL</Label>
              <Input id="resume_url" name="resume_url" type="url" placeholder="https://..." value={formData.resume_url} onChange={handleChange} />
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            {hasProfile && (
              <Button type="button" variant="outline" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            )}
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save Profile"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
