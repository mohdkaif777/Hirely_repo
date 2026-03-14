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
import { Rocket, FileSearch, ArrowRight, Sparkles, Building2 } from "lucide-react";
import { cn } from "@/lib/utils";

const roles = [
  {
    value: "job_seeker" as const,
    title: "Job Seeker",
    description:
      "I'm looking for opportunities. I want to match with relevant positions automatically using AI.",
    icon: FileSearch,
  },
  {
    value: "recruiter" as const,
    title: "Recruiter",
    description:
      "I'm hiring talent. I want to post jobs and let the AI find the best candidates for my team.",
    icon: Building2,
  },
];

export default function RoleSelectionPage() {
  const router = useRouter();
  const { user, token, logout, refreshUser } = useAuth();
  const [selected, setSelected] = useState<"job_seeker" | "recruiter" | null>(null);
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
      <div className="min-h-screen flex items-center justify-center bg-[url('/bg-gradient.svg')] bg-cover bg-center px-4 relative">
        <div className="absolute inset-0 bg-background/80 backdrop-blur-[100px] pointer-events-none" />
        <Card className="w-full max-w-md text-center relative z-10 rounded-3xl border-border/50 bg-card/60 backdrop-blur-xl shadow-2xl">
          <CardHeader className="pt-8">
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>Please log in securely to select your account role.</CardDescription>
          </CardHeader>
          <CardContent className="pb-8">
            <Button onClick={() => router.push("/login")} className="w-full h-12 rounded-xl text-base font-medium mt-4">
              Return to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[url('/bg-gradient.svg')] bg-cover bg-center px-4 sm:px-6 relative">
      <div className="absolute inset-0 bg-background/80 backdrop-blur-[100px] pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent-soft/5 pointer-events-none" />
      
      <div className="w-full max-w-4xl relative z-10 py-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex flex-col items-center mb-12 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary/10 text-primary mb-6 shadow-sm border border-primary/20">
            <Rocket className="w-6 h-6" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground mb-3">
            How will you use Hire<span className="text-primary">AI</span>?
          </h1>
          <p className="text-muted-foreground text-base max-w-lg">
            Select your role to personalize your AI hiring experience. You cannot change this later.
          </p>
        </div>

        {error && (
          <div className="max-w-md mx-auto bg-destructive/10 text-destructive text-sm font-medium p-4 rounded-xl border border-destructive/20 mb-8 text-center animate-in slide-in-from-top-2">
            {error}
          </div>
        )}

        <div className="grid sm:grid-cols-2 gap-6 mb-10 max-w-3xl mx-auto">
          {roles.map((role) => {
            const isSelected = selected === role.value;
            const Icon = role.icon;
            return (
              <Card
                key={role.value}
                className={cn(
                  "cursor-pointer transition-all duration-300 rounded-3xl overflow-hidden group border-2",
                  isSelected
                    ? "border-primary bg-primary/5 shadow-xl shadow-primary/10"
                    : "border-border/50 bg-card/40 backdrop-blur-md hover:border-primary/50 hover:bg-card/60"
                )}
                onClick={() => setSelected(role.value)}
              >
                <div className={cn("h-1.5 w-full transition-colors", isSelected ? "bg-primary" : "bg-transparent")} />
                <CardContent className="p-8 sm:p-10 text-center flex flex-col items-center h-full pt-8">
                  <div className={cn(
                    "mb-6 w-20 h-20 rounded-2xl flex items-center justify-center transition-all duration-300",
                    isSelected ? "bg-primary text-primary-foreground shadow-lg" : "bg-secondary/50 text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary"
                  )}>
                    <Icon className="w-10 h-10" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-2xl font-bold mb-3">{role.title}</h3>
                  <p className={cn(
                    "text-sm leading-relaxed",
                    isSelected ? "text-foreground" : "text-muted-foreground"
                  )}>
                    {role.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="flex flex-col items-center gap-6 max-w-xs mx-auto">
          <Button
            size="lg"
            className="w-full h-14 rounded-2xl text-base font-semibold shadow-lg group transition-all"
            disabled={!selected || loading}
            onClick={handleContinue}
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin inline-block"></span>
                Setting up workspace...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                Continue to Dashboard
                <ArrowRight className="w-4 h-4 opacity-70 group-hover:translate-x-1 transition-transform" />
              </div>
            )}
          </Button>
          <button 
            onClick={logout} 
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Sign out instead
          </button>
        </div>
      </div>
    </div>
  );
}
