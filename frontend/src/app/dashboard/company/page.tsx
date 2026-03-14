"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getRecruiterProfile, createRecruiterProfile, updateRecruiterProfile } from "@/lib/api";
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
import { Building2, Edit2, Users, Briefcase } from "lucide-react";
import Link from "next/link";

export default function CompanyProfilePage() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [hasProfile, setHasProfile] = useState(false);
  const [isEditing, setIsEditing] = useState(true);

  const [formData, setFormData] = useState({
    company_name: "",
    industry: "",
    company_size: "",
    website: "",
    gst_number: "",
  });

  useEffect(() => {
    async function loadProfile() {
      if (!token) return;
      try {
        const data = await getRecruiterProfile(token);
        if (data && data.company_name) {
          setHasProfile(true);
          setIsEditing(false); // Display the card instantly because data exists
          setFormData({
            company_name: data.company_name || "",
            industry: data.industry || "",
            company_size: data.company_size || "",
            website: data.website || "",
            gst_number: data.gst_number || "",
          });
        }
      } catch (err: any) {
        if (!err.message?.includes("404")) {
          setError("Failed to load company profile");
        }
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, [token]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      if (hasProfile) {
        await updateRecruiterProfile(token, formData);
      } else {
        await createRecruiterProfile(token, formData);
        setHasProfile(true);
      }
      setSuccess("Company profile saved successfully!");
      setIsEditing(false); // Automatically switch back to view mode on success
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save company profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center py-10">Loading company profile...</div>;
  }

  // Visual Mode (Decent UI)
  if (!isEditing && hasProfile) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card className="shadow-sm border-border/50">
          <CardHeader className="flex flex-row items-center justify-between pb-4 border-b">
            <div className="space-y-1">
              <CardTitle className="text-2xl font-bold flex items-center gap-2">
                <Building2 className="w-6 h-6 text-primary" />
                {formData.company_name}
              </CardTitle>
              <CardDescription className="text-sm text-muted-foreground">
                Verified Recruiter Account
              </CardDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setIsEditing(true)}>
              <Edit2 className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardContent className="pt-6 space-y-6">
            <div className="grid grid-cols-2 gap-4">
              {formData.industry && (
                <div className="flex flex-col space-y-1 p-4 rounded-lg bg-muted/30 border border-muted">
                  <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider flex items-center gap-2">
                    <Briefcase className="w-3 h-3" /> Industry
                  </span>
                  <span className="font-semibold text-foreground">
                    {formData.industry}
                  </span>
                </div>
              )}
              {formData.company_size && (
                <div className="flex flex-col space-y-1 p-4 rounded-lg bg-muted/30 border border-muted">
                  <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider flex items-center gap-2">
                    <Users className="w-3 h-3" /> Company Size
                  </span>
                  <span className="font-semibold text-foreground">
                    {formData.company_size} Employees
                  </span>
                </div>
              )}
            </div>
            {formData.website && (
              <div className="flex flex-col space-y-1 p-4 rounded-lg bg-muted/30 border border-muted">
                <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Website</span>
                <a href={formData.website} target="_blank" rel="noreferrer" className="font-semibold text-primary hover:underline">
                  {formData.website}
                </a>
              </div>
            )}
            {formData.gst_number && (
              <div className="flex flex-col space-y-1 p-4 rounded-lg bg-muted/30 border border-muted">
                <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">GST Number</span>
                <span className="font-semibold text-foreground">{formData.gst_number}</span>
              </div>
            )}
          </CardContent>
          <CardFooter className="pt-4 border-t bg-muted/10 gap-3">
            <Link href="/dashboard/post-job" className="w-full">
              <Button className="w-full">
                Post a New Job
              </Button>
            </Link>
            <Link href="/dashboard/my-jobs" className="w-full">
              <Button variant="outline" className="w-full">
                Manage Jobs
              </Button>
            </Link>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // Form Editing Mode
  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Company Profile</CardTitle>
          <CardDescription>
            Update your company details. This profile is required before you can post jobs.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && <div className="text-destructive text-sm font-medium">{error}</div>}
            {success && <div className="text-green-600 text-sm font-medium">{success}</div>}
            
            <div className="space-y-2">
              <Label htmlFor="company_name">Company Name *</Label>
              <Input id="company_name" name="company_name" value={formData.company_name} onChange={handleChange} required />
            </div>

            <div className="space-y-2">
              <Label htmlFor="industry">Industry</Label>
              <Input id="industry" name="industry" placeholder="e.g. Technology, Healthcare" value={formData.industry} onChange={handleChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="company_size">Company Size</Label>
              <Input id="company_size" name="company_size" placeholder="e.g. 1-10, 11-50, 51-200" value={formData.company_size} onChange={handleChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="website">Website</Label>
              <Input id="website" name="website" type="url" placeholder="https://example.com" value={formData.website} onChange={handleChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="gst_number">GST Number (optional)</Label>
              <Input id="gst_number" name="gst_number" placeholder="e.g. 22AAAAA0000A1ZV" value={formData.gst_number} onChange={handleChange} />
            </div>

          </CardContent>
          <CardFooter className="flex justify-between">
            {hasProfile && (
              <Button type="button" variant="outline" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            )}
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save Company Profile"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
