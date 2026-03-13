"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";

export default function LandingPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold tracking-tight">
                Hire<span className="text-primary">AI</span>
              </span>
              <Badge variant="secondary" className="text-xs">
                Beta
              </Badge>
            </div>
            <div className="flex items-center gap-4">
              {user ? (
                <Link href="/role-selection">
                  <Button>Dashboard</Button>
                </Link>
              ) : (
                <>
                  <Link href="/login">
                    <Button variant="ghost">Log in</Button>
                  </Link>
                  <Link href="/signup">
                    <Button>Get Started</Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <main className="flex-1">
        <section className="py-24 sm:py-32">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <Badge variant="outline" className="mb-6">
              AI-Powered Matching
            </Badge>
            <h1 className="text-4xl sm:text-6xl font-bold tracking-tight mb-6">
              Find the perfect
              <br />
              <span className="text-primary">job or candidate</span>
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
              HireAI uses advanced AI to match job seekers with the right
              opportunities and help recruiters find top talent — faster and
              smarter than ever.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup">
                <Button size="lg" className="w-full sm:w-auto text-lg px-8">
                  Start for Free
                </Button>
              </Link>
              <Link href="/login">
                <Button
                  size="lg"
                  variant="outline"
                  className="w-full sm:w-auto text-lg px-8"
                >
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="py-20 bg-muted/50">
          <div className="max-w-6xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">
              Why HireAI?
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  title: "AI-Powered Matching",
                  desc: "Our semantic search engine understands your skills and experience to find the best matches — not just keyword matches.",
                },
                {
                  title: "For Job Seekers",
                  desc: "Upload your resume and get matched with relevant jobs instantly. No more scrolling through hundreds of irrelevant listings.",
                },
                {
                  title: "For Recruiters",
                  desc: "Post jobs and let our AI surface the most qualified candidates from a pool of talented professionals.",
                },
              ].map((f) => (
                <div
                  key={f.title}
                  className="bg-card rounded-xl border p-6 shadow-sm"
                >
                  <h3 className="text-xl font-semibold mb-3">{f.title}</h3>
                  <p className="text-muted-foreground">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-muted-foreground text-sm">
          &copy; {new Date().getFullYear()} HireAI. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
