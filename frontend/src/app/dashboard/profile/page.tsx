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
                  skillsArray.map((skill) => (
                    <Badge key={skill} variant="secondary" className="px-3 py-1 bg-muted">
                      {skill}
                    </Badge>
                  ))
                ) : (
                  <span className="text-muted-foreground text-sm">No skills listed.</span>
                )}
              </div>
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
