"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login, authGoogle } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { Sparkles, ArrowRight } from "lucide-react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setAuth } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const justRegistered = searchParams.get("registered") === "true";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await login(email, password);
      setAuth(data.access_token, data.user);

      if (!data.user.role) {
        router.push("/role-selection");
      } else {
        router.push("/dashboard");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSuccess(credentialResponse: any) {
    if (!credentialResponse.credential) return;
    setError("");
    setLoading(true);
    try {
      const decoded: any = jwtDecode(credentialResponse.credential);
      const data = await authGoogle(decoded.email, decoded.name, decoded.picture);
      setAuth(data.access_token, data.user);

      if (!data.user.role) {
        router.push("/role-selection");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(typeof err.message === "object" ? JSON.stringify(err.message) : (err.message || "Google authentication failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-md animate-in fade-in zoom-in-95 duration-500">
      <div className="flex flex-col items-center mb-8 text-center">
        <Link href="/" className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary/10 text-primary mb-4 shadow-sm border border-primary/20 hover:scale-105 transition-transform">
          <Sparkles className="w-6 h-6" />
        </Link>
        <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">Welcome back to HireAI</h1>
        <p className="text-muted-foreground">Sign in to your account to continue</p>
      </div>

      <Card className="rounded-3xl border border-border/50 bg-card/60 backdrop-blur-xl shadow-2xl overflow-hidden">
        <div className="h-1 w-full bg-gradient-to-r from-primary/80 to-accent-soft/80" />
        
        <form onSubmit={handleSubmit} className="p-2">
          <CardContent className="space-y-5 p-6 sm:p-8">
            {justRegistered && (
              <div className="bg-emerald-500/10 text-emerald-500 text-sm font-medium p-3 rounded-xl border border-emerald-500/20 text-center animate-in slide-in-from-top-2">
                Account created securely. Please sign in below.
              </div>
            )}
            {error && (
              <div className="bg-destructive/10 text-destructive text-sm font-medium p-3 rounded-xl border border-destructive/20 text-center animate-in slide-in-from-top-2">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-12 bg-secondary/30 border-border/50 rounded-xl px-4 focus-visible:ring-primary/50 transition-all text-base"
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Password</Label>
                <Link href="#" className="text-xs font-medium text-primary hover:text-primary/80 transition-colors">Forgot password?</Link>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-12 bg-secondary/30 border-border/50 rounded-xl px-4 focus-visible:ring-primary/50 transition-all text-base tracking-widest placeholder:tracking-normal"
              />
            </div>

            <Button type="submit" className="w-full h-12 rounded-xl text-base font-medium shadow-md group mt-2" disabled={loading}>
              {loading ? (
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin inline-block"></span>
                  Authenticating...
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2 w-full">
                  Sign In
                  <ArrowRight className="w-4 h-4 opacity-70 group-hover:translate-x-1 transition-transform" />
                </div>
              )}
            </Button>

            <div className="relative my-6 text-center text-xs after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border/50">
              <span className="relative z-10 bg-card px-3 text-muted-foreground uppercase tracking-widest font-semibold">
                Or continue with
              </span>
            </div>

            <div className="flex justify-center w-full pb-2 relative z-20">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => setError("Google authentication failed")}
                useOneTap
                theme="filled_black"
                shape="rectangular"
                size="large"
                logo_alignment="center"
              />
            </div>
          </CardContent>
          <CardFooter className="px-8 pb-8 pt-0 flex justify-center border-t border-border/50 bg-secondary/5 mt-4 pt-6">
            <p className="text-sm text-muted-foreground">
              Don&apos;t have an account?{" "}
              <Link href="/signup" className="text-primary font-semibold hover:underline decoration-2 underline-offset-4 transition-all">
                Sign up
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[url('/bg-gradient.svg')] bg-cover bg-center relative px-4 sm:px-6">
      <div className="absolute inset-0 bg-background/80 backdrop-blur-[100px] pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 via-transparent to-accent-soft/5 pointer-events-none" />
      
      <div className="relative z-10 w-full flex justify-center py-12">
        <Suspense fallback={<div className="w-10 h-10 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>}>
          <LoginForm />
        </Suspense>
      </div>
    </div>
  );
}
