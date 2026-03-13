"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/lib/auth-context";
import { setRole } from "@/lib/api";

const roles = [
  {
    value: "job_seeker" as const,
    title: "Job Seeker",
    description:
      "I'm looking for job opportunities. I want to upload my resume and get matched with relevant positions.",
    icon: "M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
  },
  {
    value: "recruiter" as const,
    title: "Recruiter",
    description:
      "I'm hiring talent. I want to post jobs and find the best candidates using AI-powered matching.",
    icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z",
  },
];

export default function RoleSelectionPage() {
  const router = useRouter();
  const { user, token, logout, refreshUser } = useAuth();
  const [selected, setSelected] = useState<"job_seeker" | "recruiter" | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleContinue() {
    if (!selected || !token) return;
    setLoading(true);
    setError("");

    try {
      await setRole(token, selected);
      await refreshUser();
      if (selected === "recruiter") {
        router.push("/dashboard/my-jobs");
      } else {
        router.push("/dashboard/jobs");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to set role");
    } finally {
      setLoading(false);
    }
  }

  if (!token && !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4">
        <Card className="w-full max-w-md text-center">
          <CardHeader>
            <CardTitle>Not logged in</CardTitle>
            <CardDescription>Please log in to select your role.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push("/login")} className="w-full">
              Go to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            How will you use Hire<span className="text-primary">AI</span>?
          </h1>
          <p className="text-muted-foreground">
            Select your role to personalize your experience.
          </p>
        </div>

        {error && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md mb-6 text-center">
            {error}
          </div>
        )}

        <div className="grid sm:grid-cols-2 gap-6 mb-8">
          {roles.map((role) => (
            <Card
              key={role.value}
              className={`cursor-pointer transition-all hover:shadow-md ${
                selected === role.value
                  ? "ring-2 ring-primary shadow-md"
                  : "hover:border-primary/50"
              }`}
              onClick={() => setSelected(role.value)}
            >
              <CardHeader className="text-center pb-2">
                <div className="mx-auto mb-3 w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-primary"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d={role.icon}
                    />
                  </svg>
                </div>
                <CardTitle className="text-xl">{role.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground text-center">
                  {role.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="flex flex-col items-center gap-4">
          <Button
            size="lg"
            className="w-full max-w-xs"
            disabled={!selected || loading}
            onClick={handleContinue}
          >
            {loading ? "Setting up..." : "Continue"}
          </Button>
          <Button variant="ghost" onClick={logout} className="text-sm">
            Sign out
          </Button>
        </div>
      </div>
    </div>
  );
}
